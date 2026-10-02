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
    prod = db.query(Product).filter(Product.name == name).first()
    if not prod:
        prod = Product(name=name, category=category, unit=unit, price=price)
        db.add(prod)
        db.commit()
        db.refresh(prod)
    return prod


def test_bug1_full_batch_consumption():
    """
    TEST 1 — FULL BATCH CONSUMPTION
    Create a batch/storage inventory of 500 kg.
    Retailer purchases all 500 kg.
    Verify:
    - upstream available quantity = 0
    - batch status is Consumed / quantity is 0
    - batch is not available for another purchase
    - zero quantity does not appear as available marketplace stock
    - traceability history remains intact
    """
    db = SessionLocal()
    try:
        # Clean operational test data
        db.query(Shipment).delete()
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(Inventory).delete()
        db.query(TraceabilityEvent).delete()
        db.query(Batch).delete()
        db.commit()

        suffix = uuid.uuid4().hex[:6]
        retailer = get_or_create_user(db, "Retailer B1", f"ret_b1_{suffix}@example.com", "retailer")
        farmer = get_or_create_user(db, "Farmer B1", f"farmer_b1_{suffix}@example.com", "farmer")
        product = get_or_create_product(db, f"Test Onion {suffix}", "Vegetables", "kg", 40.0)

        # 1. Create batch of 500 kg
        batch = Batch(
            batch_code=f"BATCH-B1-{suffix}",
            product_id=product.id,
            farmer_id=farmer.id,
            quantity=500.0,
            quality_grade="Grade A",
            harvest_date=date(2026, 10, 1),
            expiry_date=date(2026, 11, 1),
            origin_location="Farm Hub B1",
            status="In Cold Storage"
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)

        event = TraceabilityEvent(batch_id=batch.id, stage="Farmer Harvest", location="Farm", description="Harvest logged")
        inv = Inventory(batch_id=batch.id, warehouse_location="Storage A", quantity=500.0, owner_id=None)
        db.add_all([event, inv])
        db.commit()

        # 2. Retailer purchases all 500 kg
        headers = get_auth_headers(retailer.email, retailer.role, retailer.id)
        payload = {
            "order_number": f"ORD-B1-{suffix}",
            "buyer_id": retailer.id,
            "status": "Confirmed",
            "items": [{"product_id": product.id, "quantity": 500.0, "price": 40.0}]
        }
        res = client.post("/api/orders", json=payload, headers=headers)
        assert res.status_code == 201, res.text

        # 3. Verify Batch state
        db.refresh(batch)
        db.refresh(inv)
        assert batch.quantity == 0.0
        assert batch.status in ["Consumed", "Depleted"]
        assert inv.quantity == 0.0

        # 4. Verify batch cannot be purchased again
        payload_again = {
            "order_number": f"ORD-B1-AGAIN-{suffix}",
            "buyer_id": retailer.id,
            "status": "Confirmed",
            "items": [{"product_id": product.id, "quantity": 1.0, "price": 40.0}]
        }
        res_again = client.post("/api/orders", json=payload_again, headers=headers)
        assert res_again.status_code == 400
        assert "exceeds available stock" in res_again.text

        # 5. Verify zero quantity does not appear in Retailer Marketplace upstream inventory query
        res_mkt = client.get("/api/inventory?scope=upstream", headers=headers)
        assert res_mkt.status_code == 200
        upstream_items = [i for i in res_mkt.json() if i["batch"]["product_id"] == product.id]
        assert len(upstream_items) == 0

        # 6. Verify traceability history remains intact
        res_trace = client.get(f"/api/traceability/batch/{batch.id}", headers=headers)
        assert res_trace.status_code == 200
        assert len(res_trace.json()) >= 1
    finally:
        db.close()


def test_bug2_exactly_once_retailer_credit():
    """
    TEST 2 — EXACTLY-ONCE RETAILER CREDIT
    Retailer orders 500 kg. Distributor dispatches.
    Trigger shipment reconciliation/delivery multiple times.
    Verify: Retailer inventory increases by exactly 500 kg (NOT 1000 kg or 1500 kg).
    """
    db = SessionLocal()
    try:
        db.query(Shipment).delete()
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(Inventory).delete()
        db.query(TraceabilityEvent).delete()
        db.query(Batch).delete()
        db.commit()

        suffix = uuid.uuid4().hex[:6]
        retailer = get_or_create_user(db, "Retailer B2", f"ret_b2_{suffix}@example.com", "retailer")
        distributor = get_or_create_user(db, "Distributor B2", f"dist_b2_{suffix}@example.com", "distributor")
        farmer = get_or_create_user(db, "Farmer B2", f"farmer_b2_{suffix}@example.com", "farmer")
        product = get_or_create_product(db, f"Test Potato {suffix}", "Vegetables", "kg", 30.0)

        batch = Batch(
            batch_code=f"BATCH-B2-{suffix}",
            product_id=product.id,
            farmer_id=farmer.id,
            quantity=500.0,
            quality_grade="Grade A",
            harvest_date=date(2026, 10, 1),
            expiry_date=date(2026, 11, 1),
            origin_location="Hub B2",
            status="In Cold Storage"
        )
        db.add(batch)
        db.commit()

        inv = Inventory(batch_id=batch.id, warehouse_location="Storage B2", quantity=500.0, owner_id=None)
        db.add(inv)
        db.commit()

        # Retailer places order for 500 kg
        ret_headers = get_auth_headers(retailer.email, retailer.role, retailer.id)
        order_payload = {
            "order_number": f"ORD-B2-{suffix}",
            "buyer_id": retailer.id,
            "status": "Confirmed",
            "items": [{"product_id": product.id, "quantity": 500.0, "price": 30.0}]
        }
        res_ord = client.post("/api/orders", json=order_payload, headers=ret_headers)
        assert res_ord.status_code == 201
        order_id = res_ord.json()["id"]

        # Distributor dispatches shipment
        dist_headers = get_auth_headers(distributor.email, distributor.role, distributor.id)
        shipment_payload = {
            "order_id": order_id,
            "batch_id": batch.id,
            "source": "Storage B2",
            "destination": "Retail Store B2",
            "vehicle_number": "MH-12-AB-1234",
            "status": "In Transit"
        }
        res_ship = client.post("/api/shipments", json=shipment_payload, headers=dist_headers)
        assert res_ship.status_code == 201
        shipment_id = res_ship.json()["id"]

        # Mark Delivered via API status update
        res_del1 = client.patch(f"/api/shipments/{shipment_id}/status", json={"status": "Delivered"}, headers=dist_headers)
        assert res_del1.status_code == 200

        # Call status update AND GET endpoints multiple times (simulating polling)
        client.patch(f"/api/shipments/{shipment_id}/status", json={"status": "Delivered"}, headers=dist_headers)
        client.get("/api/shipments", headers=ret_headers)
        client.get("/api/orders", headers=ret_headers)
        client.get("/api/inventory", headers=ret_headers)

        # Verify Retailer Inventory = exactly 500 kg
        ret_invs = db.query(Inventory).filter(Inventory.owner_id == retailer.id, Inventory.batch_id == batch.id).all()
        total_ret_qty = sum(i.quantity for i in ret_invs)
        assert total_ret_qty == 500.0, f"Expected 500.0 kg retailer inventory, found {total_ret_qty} kg"
    finally:
        db.close()


def test_bug3_and_4_marketplace_ownership_scopes():
    """
    TEST 3 & 4 — MARKETPLACE OWNERSHIP AND UPSTREAM AVAILABILITY
    Verify:
    - Retailer Marketplace does NOT count retailer-owned stock as upstream stock
    - Consumer Marketplace counts ONLY retailer-owned stock
    - If upstream still has stock, Retailer Marketplace shows remaining upstream stock
    """
    db = SessionLocal()
    try:
        db.query(Shipment).delete()
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(Inventory).delete()
        db.query(TraceabilityEvent).delete()
        db.query(Batch).delete()
        db.commit()

        suffix = uuid.uuid4().hex[:6]
        retailer = get_or_create_user(db, "Retailer B3", f"ret_b3_{suffix}@example.com", "retailer")
        consumer = get_or_create_user(db, "Consumer B3", f"cons_b3_{suffix}@example.com", "consumer")
        farmer = get_or_create_user(db, "Farmer B3", f"farmer_b3_{suffix}@example.com", "farmer")
        product = get_or_create_product(db, f"Test Apple {suffix}", "Fruits", "kg", 120.0)

        # Upstream stock: 800 kg total
        batch = Batch(
            batch_code=f"BATCH-B3-{suffix}",
            product_id=product.id,
            farmer_id=farmer.id,
            quantity=800.0,
            quality_grade="Grade A",
            harvest_date=date(2026, 10, 1),
            expiry_date=date(2026, 11, 1),
            origin_location="Hub B3",
            status="In Cold Storage"
        )
        db.add(batch)
        db.commit()

        inv_upstream = Inventory(batch_id=batch.id, warehouse_location="Storage B3", quantity=800.0, owner_id=None)
        db.add(inv_upstream)
        db.commit()

        # Retailer purchases 500 kg
        ret_headers = get_auth_headers(retailer.email, retailer.role, retailer.id)
        order_payload = {
            "order_number": f"ORD-B3-{suffix}",
            "buyer_id": retailer.id,
            "status": "Confirmed",
            "items": [{"product_id": product.id, "quantity": 500.0, "price": 120.0}]
        }
        res_ord = client.post("/api/orders", json=order_payload, headers=ret_headers)
        assert res_ord.status_code == 201

        # Simulate delivery of 500 kg to retailer inventory
        ret_inv = Inventory(batch_id=batch.id, warehouse_location="Retail Store B3", quantity=500.0, owner_id=retailer.id)
        db.add(ret_inv)
        db.commit()

        # TEST 3: Verify Retailer Marketplace query (`/api/inventory?scope=upstream`) returns ONLY upstream stock (300 kg)
        res_ret_mkt = client.get("/api/inventory?scope=upstream", headers=ret_headers)
        assert res_ret_mkt.status_code == 200
        upstream_inv_items = [i for i in res_ret_mkt.json() if i["batch"]["product_id"] == product.id]
        total_upstream = sum(i["quantity"] for i in upstream_inv_items)
        assert total_upstream == 300.0, f"Expected 300.0 kg upstream stock, found {total_upstream}"

        # TEST 4: Verify Consumer Marketplace query (`/api/inventory`) returns ONLY retailer-owned stock (500 kg)
        cons_headers = get_auth_headers(consumer.email, consumer.role, consumer.id)
        res_cons_mkt = client.get("/api/inventory", headers=cons_headers)
        assert res_cons_mkt.status_code == 200
        cons_inv_items = [i for i in res_cons_mkt.json() if i["batch"]["product_id"] == product.id]
        total_consumer_avail = sum(i["quantity"] for i in cons_inv_items)
        assert total_consumer_avail == 500.0, f"Expected 500.0 kg consumer available stock, found {total_consumer_avail}"
    finally:
        db.close()
