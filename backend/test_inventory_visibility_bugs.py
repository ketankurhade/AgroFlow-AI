import uuid
import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.batch import Batch
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.shipment import Shipment
from app.models.traceability import TraceabilityEvent
from app.services.auth_service import create_access_token, get_password_hash

client = TestClient(app)

def get_auth_headers(email: str, role: str, user_id: int):
    token = create_access_token({"sub": email, "role": role, "id": user_id})
    return {"Authorization": f"Bearer {token}"}


def get_or_create_user(db, name: str, email: str, role: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(name=name, email=email, password_hash=get_password_hash("pass"), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_or_create_product(db, name: str, category: str = "Vegetables", unit: str = "kg", price: float = 40.0):
    name_lower = name.lower()
    if "potato" in name_lower:
        canonical_name = "Potato"
    elif "apple" in name_lower:
        canonical_name = "Apple"
    elif "mango" in name_lower:
        canonical_name = "Mango"
    else:
        canonical_name = "Onion"

    prod = db.query(Product).filter(Product.name == canonical_name).first()
    if not prod:
        prod = Product(name=canonical_name, category=category, unit=unit, price=price)
        db.add(prod)
        db.commit()
        db.refresh(prod)
    return prod


def clear_operational_data(db):
    db.query(Shipment).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(TraceabilityEvent).delete()
    db.query(Batch).delete()
    db.commit()


def test_manager_inventory_scope():
    db = SessionLocal()
    try:
        clear_operational_data(db)
        suffix = uuid.uuid4().hex[:6]
        manager = get_or_create_user(db, "Storage Manager Test", f"mgr_{suffix}@example.com", "supply_chain_manager")
        farmer = get_or_create_user(db, "Farmer Test M1", f"farmer_m1_{suffix}@example.com", "farmer")
        retailer_a = get_or_create_user(db, "Retailer A Test", f"ret_a_{suffix}@example.com", "retailer")

        p_onion = get_or_create_product(db, f"Onion M1 {suffix}", "Vegetables", "kg", 35.0)
        p_potato = get_or_create_product(db, f"Potato M1 {suffix}", "Vegetables", "kg", 30.0)

        # Create batches
        b_onion = Batch(batch_code=f"B-ONION-{suffix}", product_id=p_onion.id, farmer_id=farmer.id, quantity=0.0, harvest_date=date(2026,10,1), expiry_date=date(2026,11,1), origin_location="Hub M1", status="Consumed")
        b_potato = Batch(batch_code=f"B-POTATO-{suffix}", product_id=p_potato.id, farmer_id=farmer.id, quantity=300.0, harvest_date=date(2026,10,1), expiry_date=date(2026,11,1), origin_location="Hub M1", status="In Cold Storage")
        db.add_all([b_onion, b_potato])
        db.commit()

        # Upstream 0 kg Onion
        inv_upstream_onion = Inventory(batch_id=b_onion.id, warehouse_location="Storage A", quantity=0.0, owner_id=None)
        # Upstream 300 kg Potato
        inv_upstream_potato = Inventory(batch_id=b_potato.id, warehouse_location="Storage A", quantity=300.0, owner_id=None)
        # Retailer A 400 kg Onion
        inv_retailer_onion = Inventory(batch_id=b_onion.id, warehouse_location="Retail Store A", quantity=400.0, owner_id=retailer_a.id)
        db.add_all([inv_upstream_onion, inv_upstream_potato, inv_retailer_onion])
        db.commit()

        headers = get_auth_headers(manager.email, manager.role, manager.id)
        res = client.get("/api/inventory", headers=headers)
        assert res.status_code == 200
        data = res.json()

        # Extract items by batch_id
        item_batch_ids = [i["batch_id"] for i in data]
        assert b_potato.id in item_batch_ids, "300 kg Potato must appear for Manager"
        assert inv_upstream_onion.id not in [i["id"] for i in data], "0 kg Upstream Onion must NOT appear for Manager"
        assert inv_retailer_onion.id not in [i["id"] for i in data], "400 kg Retailer-owned Onion must NOT appear for Manager"
    finally:
        db.close()


def test_retailer_inventory_scope():
    db = SessionLocal()
    try:
        clear_operational_data(db)
        suffix = uuid.uuid4().hex[:6]
        retailer_a = get_or_create_user(db, "Retailer A Test 2", f"ret_a2_{suffix}@example.com", "retailer")
        farmer = get_or_create_user(db, "Farmer Test R2", f"farmer_r2_{suffix}@example.com", "farmer")

        p_onion = get_or_create_product(db, f"Onion R2 {suffix}", "Vegetables", "kg", 35.0)
        p_potato = get_or_create_product(db, f"Potato R2 {suffix}", "Vegetables", "kg", 30.0)
        p_apple = get_or_create_product(db, f"Apple R2 {suffix}", "Fruits", "kg", 120.0)

        b_onion = Batch(batch_code=f"B-O-R2-{suffix}", product_id=p_onion.id, farmer_id=farmer.id, quantity=400.0, harvest_date=date(2026,10,1), expiry_date=date(2026,11,1), origin_location="Hub R2", status="In Cold Storage")
        b_potato = Batch(batch_code=f"B-P-R2-{suffix}", product_id=p_potato.id, farmer_id=farmer.id, quantity=250.0, harvest_date=date(2026,10,1), expiry_date=date(2026,11,1), origin_location="Hub R2", status="In Cold Storage")
        b_apple = Batch(batch_code=f"B-A-R2-{suffix}", product_id=p_apple.id, farmer_id=farmer.id, quantity=0.0, harvest_date=date(2026,10,1), expiry_date=date(2026,11,1), origin_location="Hub R2", status="Consumed")
        db.add_all([b_onion, b_potato, b_apple])
        db.commit()

        inv_onion = Inventory(batch_id=b_onion.id, warehouse_location="Retail Store A", quantity=400.0, owner_id=retailer_a.id)
        inv_potato = Inventory(batch_id=b_potato.id, warehouse_location="Retail Store A", quantity=250.0, owner_id=retailer_a.id)
        inv_apple = Inventory(batch_id=b_apple.id, warehouse_location="Retail Store A", quantity=0.0, owner_id=retailer_a.id)
        db.add_all([inv_onion, inv_potato, inv_apple])
        db.commit()

        headers = get_auth_headers(retailer_a.email, retailer_a.role, retailer_a.id)
        res = client.get("/api/inventory", headers=headers)
        assert res.status_code == 200
        data = res.json()

        returned_ids = [i["id"] for i in data]
        assert inv_onion.id in returned_ids, "Retailer Onion 400 kg must appear"
        assert inv_potato.id in returned_ids, "Retailer Potato 250 kg must appear"
        assert inv_apple.id not in returned_ids, "Retailer Apple 0 kg must NOT appear"
    finally:
        db.close()


def test_retailer_cannot_see_other_retailer_stock():
    db = SessionLocal()
    try:
        clear_operational_data(db)
        suffix = uuid.uuid4().hex[:6]
        retailer_a = get_or_create_user(db, "Retailer A Test 3", f"ret_a3_{suffix}@example.com", "retailer")
        retailer_b = get_or_create_user(db, "Retailer B Test 3", f"ret_b3_{suffix}@example.com", "retailer")
        farmer = get_or_create_user(db, "Farmer Test R3", f"farmer_r3_{suffix}@example.com", "farmer")

        p_onion = get_or_create_product(db, f"Onion R3 {suffix}", "Vegetables", "kg", 35.0)
        b_onion = Batch(batch_code=f"B-O-R3-{suffix}", product_id=p_onion.id, farmer_id=farmer.id, quantity=700.0, harvest_date=date(2026,10,1), expiry_date=date(2026,11,1), origin_location="Hub R3", status="In Cold Storage")
        db.add(b_onion)
        db.commit()

        inv_a = Inventory(batch_id=b_onion.id, warehouse_location="Store A", quantity=400.0, owner_id=retailer_a.id)
        inv_b = Inventory(batch_id=b_onion.id, warehouse_location="Store B", quantity=300.0, owner_id=retailer_b.id)
        db.add_all([inv_a, inv_b])
        db.commit()

        headers_a = get_auth_headers(retailer_a.email, retailer_a.role, retailer_a.id)
        res_a = client.get("/api/inventory", headers=headers_a)
        assert res_a.status_code == 200
        data_a = res_a.json()
        returned_ids_a = [i["id"] for i in data_a]

        assert inv_a.id in returned_ids_a, "Retailer A's 400 kg must appear for Retailer A"
        assert inv_b.id not in returned_ids_a, "Retailer B's 300 kg must NOT appear for Retailer A"
    finally:
        db.close()


def test_marketplace_regression_scopes():
    db = SessionLocal()
    try:
        clear_operational_data(db)
        suffix = uuid.uuid4().hex[:6]
        retailer = get_or_create_user(db, "Retailer M4", f"ret_m4_{suffix}@example.com", "retailer")
        consumer = get_or_create_user(db, "Consumer M4", f"cons_m4_{suffix}@example.com", "consumer")
        farmer = get_or_create_user(db, "Farmer M4", f"farmer_m4_{suffix}@example.com", "farmer")
        product = get_or_create_product(db, f"Mango M4 {suffix}", "Fruits", "kg", 120.0)

        batch = Batch(batch_code=f"B-M4-{suffix}", product_id=product.id, farmer_id=farmer.id, quantity=1000.0, harvest_date=date(2026,10,1), expiry_date=date(2026,11,1), origin_location="Hub M4", status="In Cold Storage")
        db.add(batch)
        db.commit()

        inv_upstream = Inventory(batch_id=batch.id, warehouse_location="Storage M4", quantity=600.0, owner_id=None)
        inv_retailer = Inventory(batch_id=batch.id, warehouse_location="Retail Store M4", quantity=400.0, owner_id=retailer.id)
        db.add_all([inv_upstream, inv_retailer])
        db.commit()

        # Retailer Marketplace request: GET /api/inventory?scope=upstream
        ret_headers = get_auth_headers(retailer.email, retailer.role, retailer.id)
        res_ret_mkt = client.get("/api/inventory?scope=upstream", headers=ret_headers)
        assert res_ret_mkt.status_code == 200
        upstream_items = [i for i in res_ret_mkt.json() if i["batch"]["product_id"] == product.id]
        assert len(upstream_items) == 1
        assert upstream_items[0]["id"] == inv_upstream.id
        assert upstream_items[0]["quantity"] == 600.0

        # Consumer Marketplace request: GET /api/inventory as consumer
        cons_headers = get_auth_headers(consumer.email, consumer.role, consumer.id)
        res_cons_mkt = client.get("/api/inventory", headers=cons_headers)
        assert res_cons_mkt.status_code == 200
        cons_items = [i for i in res_cons_mkt.json() if i["batch"]["product_id"] == product.id]
        assert len(cons_items) == 1
        assert cons_items[0]["id"] == inv_retailer.id
        assert cons_items[0]["quantity"] == 400.0
    finally:
        db.close()
