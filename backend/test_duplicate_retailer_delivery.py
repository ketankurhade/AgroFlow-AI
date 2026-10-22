import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.batch import Batch
from app.models.shipment import Shipment
from app.models.traceability import TraceabilityEvent

client = TestClient(app)

def test_duplicate_retailer_delivery_regression_suite():
    print("=" * 70)
    print("AGROFLOW AI — REGRESSION SUITE: SINGLE INVENTORY CREDIT & SINGLE EVENT")
    print("=" * 70)

    db = SessionLocal()
    product = db.query(Product).filter(Product.name == "Mango").first() or db.query(Product).first()
    assert product is not None, "Canonical product must exist in database"
    product_id = product.id
    db.close()

    suffix = str(uuid.uuid4())[:8]

    # Setup User Roles: Farmer, Storage Manager, Distributor, Retailer, Consumer
    # 1. Farmer
    r_farmer = client.post("/api/auth/register", json={
        "name": "Dup Farmer", "email": f"farmer.dup.{suffix}@agroflow.com", "password": "FarmerPassword123!", "role": "farmer"
    }).json()
    t_farmer = client.post("/api/auth/login", json={"email": f"farmer.dup.{suffix}@agroflow.com", "password": "FarmerPassword123!"}).json()["access_token"]
    h_farmer = {"Authorization": f"Bearer {t_farmer}"}

    # 2. Storage Manager
    r_mgr = client.post("/api/auth/register", json={
        "name": "Dup Manager", "email": f"mgr.dup.{suffix}@agroflow.com", "password": "ManagerPassword123!", "role": "supply_chain_manager"
    }).json()
    t_mgr = client.post("/api/auth/login", json={"email": f"mgr.dup.{suffix}@agroflow.com", "password": "ManagerPassword123!"}).json()["access_token"]
    h_mgr = {"Authorization": f"Bearer {t_mgr}"}

    # 3. Distributor
    r_dist = client.post("/api/auth/register", json={
        "name": "Dup Distributor", "email": f"dist.dup.{suffix}@agroflow.com", "password": "DistPassword123!", "role": "distributor"
    }).json()
    t_dist = client.post("/api/auth/login", json={"email": f"dist.dup.{suffix}@agroflow.com", "password": "DistPassword123!"}).json()["access_token"]
    h_dist = {"Authorization": f"Bearer {t_dist}"}

    # 4. Retailer
    r_ret = client.post("/api/auth/register", json={
        "name": "Dup Retailer", "email": f"ret.dup.{suffix}@agroflow.com", "password": "RetPassword123!", "role": "retailer"
    }).json()
    t_ret = client.post("/api/auth/login", json={"email": f"ret.dup.{suffix}@agroflow.com", "password": "RetPassword123!"}).json()["access_token"]
    h_ret = {"Authorization": f"Bearer {t_ret}"}
    ret_id = r_ret["id"]

    # 5. Consumer
    r_cons = client.post("/api/auth/register", json={
        "name": "Dup Consumer", "email": f"cons.dup.{suffix}@agroflow.com", "password": "ConsPassword123!", "role": "consumer"
    }).json()
    t_cons = client.post("/api/auth/login", json={"email": f"cons.dup.{suffix}@agroflow.com", "password": "ConsPassword123!"}).json()["access_token"]
    h_cons = {"Authorization": f"Bearer {t_cons}"}

    # Upstream setup: Batch & Cold Storage Inventory (1000 kg initial)
    batch_code = f"BATCH-DUP-{suffix}"
    r_batch = client.post("/api/batches", headers=h_farmer, json={
        "batch_code": batch_code,
        "product_id": product_id,
        "quantity": 1000.0,
        "quality_grade": "Grade A+",
        "harvest_date": "2026-09-30",
        "expiry_date": "2026-10-30",
        "origin_location": "Ratnagiri Farms",
        "status": "Harvested"
    }).json()
    batch_id = r_batch["id"]

    client.post("/api/inventory", headers=h_mgr, json={
        "batch_id": batch_id,
        "warehouse_location": "Ratnagiri Storage Hub",
        "quantity": 1000.0,
        "temperature": 18.0,
        "humidity": 65.0
    })

    # Retailer places wholesale order for 500.0 kg
    r_order = client.post("/api/orders", headers=h_ret, json={
        "order_number": f"ORD-DUP-{suffix}",
        "buyer_id": ret_id,
        "items": [{"product_id": product_id, "quantity": 500.0, "price": 120.0}]
    }).json()
    order_id = r_order["id"]

    # Distributor dispatches shipment
    r_ship = client.post("/api/shipments", headers=h_dist, json={
        "order_id": order_id,
        "batch_id": batch_id,
        "source": "Ratnagiri Storage Hub",
        "destination": "Dup Retailer Outlet",
        "vehicle_number": "MH-08-DUP-500",
        "status": "In Transit"
    }).json()
    shipment_id = r_ship["id"]

    # -------------------------------------------------------------------
    # TEST 1: Delivery processing once -> Retailer receives exactly 500 kg
    # -------------------------------------------------------------------
    client.patch(f"/api/shipments/{shipment_id}/status", headers=h_dist, json={"status": "Delivered"})

    db = SessionLocal()
    ret_invs1 = db.query(Inventory).filter(Inventory.owner_id == ret_id, Inventory.batch_id == batch_id).all()
    db.close()
    assert len(ret_invs1) == 1, f"Should be exactly 1 inventory record, got {len(ret_invs1)}"
    assert ret_invs1[0].quantity == 500.0, f"Quantity should be exactly 500.0, got {ret_invs1[0].quantity}"
    print(f"[TEST 1 PASSED] Single delivery credited exactly 500.0 kg to 1 inventory row for Retailer.")

    # -------------------------------------------------------------------
    # TEST 2: Run delivery status patch TWICE -> Retailer still has 500 kg (NOT 1000 kg)
    # -------------------------------------------------------------------
    client.patch(f"/api/shipments/{shipment_id}/status", headers=h_dist, json={"status": "Delivered"})

    db = SessionLocal()
    ret_invs2 = db.query(Inventory).filter(Inventory.owner_id == ret_id, Inventory.batch_id == batch_id).all()
    total_qty2 = sum(i.quantity for i in ret_invs2)
    db.close()
    assert len(ret_invs2) == 1, f"Retrying delivery status update must NOT create a 2nd inventory row (got {len(ret_invs2)})"
    assert total_qty2 == 500.0, f"Total retailer inventory must remain 500.0 kg, got {total_qty2}"
    print(f"[TEST 2 PASSED] Retrying delivery status update maintained exactly 500.0 kg total stock on 1 row!")

    # -------------------------------------------------------------------
    # TEST 3: Run delivery processing / reconciliation MULTIPLE times (5x)
    # -------------------------------------------------------------------
    for _ in range(5):
        client.get("/api/shipments", headers=h_dist)
        client.get("/api/orders", headers=h_ret)
        client.patch(f"/api/shipments/{shipment_id}/status", headers=h_dist, json={"status": "Delivered"})

    db = SessionLocal()
    ret_invs3 = db.query(Inventory).filter(Inventory.owner_id == ret_id, Inventory.batch_id == batch_id).all()
    total_qty3 = sum(i.quantity for i in ret_invs3)
    db.close()
    assert len(ret_invs3) == 1, f"Repeated reconciliation must maintain 1 inventory row (got {len(ret_invs3)})"
    assert total_qty3 == 500.0, f"Repeated reconciliation must maintain 500.0 kg stock (got {total_qty3})"
    print(f"[TEST 3 PASSED] 5x repeated reconciliation polling maintained strictly 500.0 kg on 1 inventory row!")

    # -------------------------------------------------------------------
    # TEST 4 & TEST 5: Retail Outlet Delivery event count is exactly 1 (even with repeated reconciliation)
    # -------------------------------------------------------------------
    db = SessionLocal()
    outlet_events = db.query(TraceabilityEvent).filter(
        TraceabilityEvent.batch_id == batch_id,
        TraceabilityEvent.stage == "Retail Outlet Delivery"
    ).all()
    db.close()
    assert len(outlet_events) == 1, f"Must have exactly 1 Retail Outlet Delivery event, got {len(outlet_events)}"
    print(f"[TEST 4 & 5 PASSED] Exactly 1 'Retail Outlet Delivery' provenance event exists despite repeated calls!")

    # -------------------------------------------------------------------
    # TEST 6: Idempotent helper execution
    # -------------------------------------------------------------------
    from app.routers.shipments import credit_retailer_inventory_if_needed
    db = SessionLocal()
    s_obj = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    res_helper = credit_retailer_inventory_if_needed(s_obj, db)
    db.close()
    assert res_helper is False, "Helper call on already credited shipment must return False"
    print(f"[TEST 6 PASSED] Direct helper idempotency check returned False cleanly.")

    # -------------------------------------------------------------------
    # TEST 7: Consumer marketplace sees retailer stock correctly (500 kg)
    # -------------------------------------------------------------------
    r_cons_inv = client.get("/api/inventory", headers=h_cons).json()
    cons_matching_stock = sum(i["quantity"] for i in r_cons_inv if i["batch_id"] == batch_id and i["owner_id"] == ret_id)
    assert cons_matching_stock == 500.0, f"Consumer should see 500.0 kg available retailer stock, got {cons_matching_stock}"
    print(f"[TEST 7 PASSED] Consumer Marketplace correctly views 500.0 kg stock available from retailer.")

    # -------------------------------------------------------------------
    # TEST 8: Retailer Marketplace does NOT show retailer-owned stock as upstream stock
    # -------------------------------------------------------------------
    r_upstream_inv = client.get("/api/inventory?scope=upstream", headers=h_ret).json()
    ret_owned_in_upstream = [i for i in r_upstream_inv if i.get("owner_id") == ret_id]
    assert len(ret_owned_in_upstream) == 0, "Retailer Marketplace upstream query must NOT include retailer-owned stock"
    print(f"[TEST 8 PASSED] Retailer Marketplace upstream stock query excludes retailer-owned stock.")

    # -------------------------------------------------------------------
    # TEST 9: Upstream storage inventory was deducted only once (1000 - 500 = 500 remaining upstream)
    # -------------------------------------------------------------------
    db = SessionLocal()
    up_invs = db.query(Inventory).filter(Inventory.batch_id == batch_id, Inventory.owner_id.is_(None)).all()
    up_total = sum(i.quantity for i in up_invs)
    db.close()
    assert up_total == 500.0, f"Upstream inventory should have 500.0 kg remaining, got {up_total}"
    print(f"[TEST 9 PASSED] Upstream inventory deducted exactly once (500.0 kg remaining).")

    # -------------------------------------------------------------------
    # TEST 10: Existing QR traceability stages remain intact (all 4 stages, 1 event each)
    # -------------------------------------------------------------------
    db = SessionLocal()
    all_events = db.query(TraceabilityEvent).filter(TraceabilityEvent.batch_id == batch_id).order_by(TraceabilityEvent.timestamp.asc()).all()
    db.close()
    stages = [e.stage for e in all_events]
    assert stages == ["Farmer Harvest", "Cold Storage Intake", "Dispatch & Transport", "Retail Outlet Delivery"], f"Timeline stages mismatch: {stages}"
    print(f"[TEST 10 PASSED] Timeline contains all 4 distinct stages in chronological order with zero duplicate events!")

    print("\n" + "=" * 70)
    print("REGRESSION SUITE PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    test_duplicate_retailer_delivery_regression_suite()
