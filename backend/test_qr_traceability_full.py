import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.batch import Batch
from app.models.shipment import Shipment

client = TestClient(app)

def test_qr_traceability_comprehensive_workflow():
    print("=" * 70)
    print("AGROFLOW AI — FULL QR TRACEABILITY & RETAIL OUTLET DELIVERY SUITE")
    print("=" * 70)

    db = SessionLocal()
    product = db.query(Product).filter(Product.name == "Onion").first() or db.query(Product).first()
    assert product is not None, "Canonical Onion product must exist in database"
    product_id = product.id
    db.close()

    suffix = str(uuid.uuid4())[:8]

    # Register Roles: Farmer, Manager, Distributor, Retailer 1, Retailer 2, Consumer
    # 1. Farmer
    r_farmer = client.post("/api/auth/register", json={
        "name": "QR Farmer", "email": f"farmer.qr.{suffix}@agroflow.com", "password": "FarmerPassword123!", "role": "farmer"
    }).json()
    t_farmer = client.post("/api/auth/login", json={"email": f"farmer.qr.{suffix}@agroflow.com", "password": "FarmerPassword123!"}).json()["access_token"]
    h_farmer = {"Authorization": f"Bearer {t_farmer}"}

    # 2. Storage Manager
    r_mgr = client.post("/api/auth/register", json={
        "name": "QR Manager", "email": f"manager.qr.{suffix}@agroflow.com", "password": "ManagerPassword123!", "role": "supply_chain_manager"
    }).json()
    t_mgr = client.post("/api/auth/login", json={"email": f"manager.qr.{suffix}@agroflow.com", "password": "ManagerPassword123!"}).json()["access_token"]
    h_mgr = {"Authorization": f"Bearer {t_mgr}"}

    # 3. Distributor
    r_dist = client.post("/api/auth/register", json={
        "name": "QR Distributor", "email": f"dist.qr.{suffix}@agroflow.com", "password": "DistPassword123!", "role": "distributor"
    }).json()
    t_dist = client.post("/api/auth/login", json={"email": f"dist.qr.{suffix}@agroflow.com", "password": "DistPassword123!"}).json()["access_token"]
    h_dist = {"Authorization": f"Bearer {t_dist}"}

    # 4. Retailer 1
    r_ret1 = client.post("/api/auth/register", json={
        "name": "QR Retailer One", "email": f"ret1.qr.{suffix}@agroflow.com", "password": "Ret1Password123!", "role": "retailer"
    }).json()
    t_ret1 = client.post("/api/auth/login", json={"email": f"ret1.qr.{suffix}@agroflow.com", "password": "Ret1Password123!"}).json()["access_token"]
    h_ret1 = {"Authorization": f"Bearer {t_ret1}"}

    # 5. Retailer 2 (Unrelated)
    r_ret2 = client.post("/api/auth/register", json={
        "name": "QR Retailer Two", "email": f"ret2.qr.{suffix}@agroflow.com", "password": "Ret2Password123!", "role": "retailer"
    }).json()
    t_ret2 = client.post("/api/auth/login", json={"email": f"ret2.qr.{suffix}@agroflow.com", "password": "Ret2Password123!"}).json()["access_token"]
    h_ret2 = {"Authorization": f"Bearer {t_ret2}"}

    # 6. Consumer
    r_cons = client.post("/api/auth/register", json={
        "name": "QR Consumer", "email": f"cons.qr.{suffix}@agroflow.com", "password": "ConsPassword123!", "role": "consumer"
    }).json()
    t_cons = client.post("/api/auth/login", json={"email": f"cons.qr.{suffix}@agroflow.com", "password": "ConsPassword123!"}).json()["access_token"]
    h_cons = {"Authorization": f"Bearer {t_cons}"}

    # -------------------------------------------------------------------
    # TEST 1: Farmer creates batch -> Farmer Harvest event exists
    # -------------------------------------------------------------------
    batch_code = f"BATCH-QR-{suffix}"
    r_batch = client.post("/api/batches", headers=h_farmer, json={
        "batch_code": batch_code,
        "product_id": product_id,
        "quantity": 500.0,
        "quality_grade": "Grade A+",
        "harvest_date": "2026-09-30",
        "expiry_date": "2026-10-30",
        "origin_location": "Nasik Farmers Hub",
        "status": "Harvested"
    })
    assert r_batch.status_code == 201
    batch_id = r_batch.json()["id"]

    r_events1 = client.get(f"/api/traceability/batch/{batch_id}", headers=h_farmer).json()
    assert len(r_events1) == 1
    assert r_events1[0]["stage"] == "Farmer Harvest"
    print(f"[TEST 1 PASSED] Farmer Harvest event created automatically for Batch #{batch_id}")

    # -------------------------------------------------------------------
    # TEST 2: Storage Manager performs Cold Storage Intake -> Cold Storage Intake exists exactly once
    # -------------------------------------------------------------------
    r_intake = client.post("/api/inventory", headers=h_mgr, json={
        "batch_id": batch_id,
        "warehouse_location": "Pune Cold Hub Bay 2",
        "quantity": 500.0,
        "temperature": 18.0,
        "humidity": 65.0
    })
    assert r_intake.status_code == 201

    r_events2 = client.get(f"/api/traceability/batch/{batch_id}", headers=h_mgr).json()
    stages2 = [e["stage"] for e in r_events2]
    assert stages2 == ["Farmer Harvest", "Cold Storage Intake"]
    print(f"[TEST 2 PASSED] Cold Storage Intake event created exactly once")

    # -------------------------------------------------------------------
    # TEST 3: Distributor dispatches shipment -> Dispatch & Transport exists exactly once
    # -------------------------------------------------------------------
    # Retailer 1 places wholesale order
    r_order1 = client.post("/api/orders", headers=h_ret1, json={
        "order_number": f"ORD-WH-{suffix}",
        "buyer_id": r_ret1["id"],
        "items": [{"product_id": product_id, "quantity": 500.0, "price": 35.0}]
    }).json()

    # Distributor dispatches shipment
    r_ship1 = client.post("/api/shipments", headers=h_dist, json={
        "order_id": r_order1["id"],
        "batch_id": batch_id,
        "source": "Pune Cold Hub",
        "destination": "Retailer One Store",
        "vehicle_number": "MH-12-QR-100",
        "status": "In Transit"
    }).json()

    r_events3 = client.get(f"/api/traceability/batch/{batch_id}", headers=h_dist).json()
    stages3 = [e["stage"] for e in r_events3]
    assert stages3 == ["Farmer Harvest", "Cold Storage Intake", "Dispatch & Transport"]
    print(f"[TEST 3 PASSED] Dispatch & Transport event created exactly once")

    # -------------------------------------------------------------------
    # TEST 4 & TEST 5: Wholesale shipment delivered to Retailer 1 -> Retailer inventory credited & Retail Outlet Delivery exists exactly once (with idempotency)
    # -------------------------------------------------------------------
    # Transition shipment status to Delivered
    r_deliv = client.patch(f"/api/shipments/{r_ship1['id']}/status", headers=h_dist, json={"status": "Delivered"})
    assert r_deliv.status_code == 200

    r_events4 = client.get(f"/api/traceability/batch/{batch_id}", headers=h_ret1).json()
    stages4 = [e["stage"] for e in r_events4]
    assert stages4 == ["Farmer Harvest", "Cold Storage Intake", "Dispatch & Transport", "Retail Outlet Delivery"]
    print(f"[TEST 4 PASSED] Retail Outlet Delivery event created automatically upon delivery! Timeline has all 4 stages.")

    # Idempotency check: trigger reconciliation / delivery status patch again
    client.patch(f"/api/shipments/{r_ship1['id']}/status", headers=h_dist, json={"status": "Delivered"})
    r_events5 = client.get(f"/api/traceability/batch/{batch_id}", headers=h_ret1).json()
    assert len(r_events5) == 4, f"Re-triggering delivery must NOT duplicate events (got {len(r_events5)})"
    print(f"[TEST 5 PASSED] Re-running delivery simulation did NOT create duplicate Retail Outlet Delivery events")

    # -------------------------------------------------------------------
    # TEST 6: Retailer QR Traceability
    # -------------------------------------------------------------------
    # Retailer 1 owns inventory for this batch and can list and view its timeline
    r_ret1_batches = client.get("/api/batches", headers=h_ret1).json()
    assert any(b["id"] == batch_id for b in r_ret1_batches), "Retailer 1 must see batch in their batches list"

    r_ret1_batch_single = client.get(f"/api/batches/{batch_id}", headers=h_ret1)
    assert r_ret1_batch_single.status_code == 200, "Retailer 1 must be authorized to GET /api/batches/{id}"

    r_events_ret1 = client.get(f"/api/traceability/batch/{batch_id}", headers=h_ret1).json()
    assert len(r_events_ret1) == 4
    print(f"[TEST 6 PASSED] Retailer 1 successfully fetched eligible batch and viewed all 4 provenance stages")

    # -------------------------------------------------------------------
    # TEST 7: Consumer purchases produce -> Consumer QR Traceability
    # -------------------------------------------------------------------
    db_temp = SessionLocal()
    db_temp.query(Inventory).filter(Inventory.batch_id != batch_id).update({Inventory.quantity: 0.0}, synchronize_session=False)
    db_temp.commit()
    db_temp.close()

    r_cons_order = client.post("/api/orders", headers=h_cons, json={
        "order_number": f"ORD-CONS-QR-{suffix}",
        "items": [{"product_id": product_id, "quantity": 10.0, "price": 53.0}]
    })
    assert r_cons_order.status_code == 201

    r_cons_batches = client.get("/api/batches", headers=h_cons).json()
    assert any(b["id"] == batch_id for b in r_cons_batches), "Consumer must see purchased batch in their batches list"

    r_events_cons = client.get(f"/api/traceability/batch/{batch_id}", headers=h_cons).json()
    assert len(r_events_cons) == 4
    print(f"[TEST 7 PASSED] Consumer who purchased produce successfully retrieved batch and viewed provenance history")

    # -------------------------------------------------------------------
    # TEST 8: Consumed Batch Traceability
    # -------------------------------------------------------------------
    # Now retailer stock is 0 kg and batch status is Consumed
    db_temp = SessionLocal()
    b_obj = db_temp.query(Batch).filter(Batch.id == batch_id).first()
    b_obj.quantity = 0.0
    b_obj.status = "Consumed"
    invs = db_temp.query(Inventory).filter(Inventory.batch_id == batch_id).all()
    for inv in invs:
        inv.quantity = 0.0
    db_temp.commit()
    db_temp.close()

    # Marketplace available_only=True hides consumed batch from stock
    r_mkt_avail = client.get("/api/batches?available_only=true", headers=h_ret1).json()
    assert not any(b["id"] == batch_id for b in r_mkt_avail), "Marketplace available_only must NOT return consumed batch"

    # Traceability default GET /api/batches still allows authorized Retailer 1 & Consumer to view consumed batch history!
    r_ret1_hist = client.get("/api/batches", headers=h_ret1).json()
    assert any(b["id"] == batch_id for b in r_ret1_hist), "Retailer 1 must still see historical consumed batch for QR traceability"

    r_cons_hist = client.get("/api/batches", headers=h_cons).json()
    assert any(b["id"] == batch_id for b in r_cons_hist), "Consumer must still see historical consumed batch for QR traceability"
    print(f"[TEST 8 PASSED] Consumed batch (0 kg) hidden from marketplace stock, but fully traceable in historical QR view!")

    # -------------------------------------------------------------------
    # TEST 9: Unauthorized Visibility Checks
    # -------------------------------------------------------------------
    # Retailer 2 did NOT purchase/receive this batch and must be denied
    r_ret2_events = client.get(f"/api/traceability/batch/{batch_id}", headers=h_ret2)
    assert r_ret2_events.status_code == 403, "Unrelated Retailer 2 must be rejected with 403"

    # Unrelated Consumer (who has 0 orders) registered now
    r_cons2 = client.post("/api/auth/register", json={
        "name": "QR Consumer Two", "email": f"cons2.qr.{suffix}@agroflow.com", "password": "Cons2Password123!", "role": "consumer"
    }).json()
    t_cons2 = client.post("/api/auth/login", json={"email": f"cons2.qr.{suffix}@agroflow.com", "password": "Cons2Password123!"}).json()["access_token"]
    h_cons2 = {"Authorization": f"Bearer {t_cons2}"}

    r_cons2_events = client.get(f"/api/traceability/batch/{batch_id}", headers=h_cons2)
    assert r_cons2_events.status_code == 403, "Unrelated Consumer 2 must be rejected with 403 from viewing private batch provenance"
    print(f"[TEST 9 PASSED] Unauthorized access controls verified: Unrelated Retailer 2 & Consumer 2 rejected with HTTP 403")

    # -------------------------------------------------------------------
    # TEST 10: Existing Farmer, Manager, Distributor QR functionality working
    # -------------------------------------------------------------------
    assert client.get(f"/api/traceability/batch/{batch_id}", headers=h_farmer).status_code == 200
    assert client.get(f"/api/traceability/batch/{batch_id}", headers=h_mgr).status_code == 200
    assert client.get(f"/api/traceability/batch/{batch_id}", headers=h_dist).status_code == 200
    print(f"[TEST 10 PASSED] Farmer, Manager, Distributor QR traceability APIs operating cleanly!")

    # Final DB Product Count Check
    db_check = SessionLocal()
    p_count = db_check.query(Product).count()
    db_check.close()
    assert p_count == 4, f"Product count must be exactly 4, got {p_count}"

    print("\n" + "=" * 70)
    print("ALL 10 QR TRACEABILITY & PROVENANCE WORKFLOW TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    test_qr_traceability_comprehensive_workflow()
