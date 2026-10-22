import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.product import Product
from app.models.user import User

client = TestClient(app)

def test_distributor_qr_traceability_workflow():
    print("=" * 70)
    print("AGROFLOW AI — ISSUE #3: DISTRIBUTOR QR TRACEABILITY TEST SUITE")
    print("=" * 70)

    unique_suffix = str(uuid.uuid4())[:8]

    # Setup Product in DB using canonical product
    db = SessionLocal()
    product = db.query(Product).filter(Product.name == "Onion").first() or db.query(Product).first()
    assert product is not None, "Canonical product 'Onion' must exist in database"
    product_id = product.id
    db.close()

    # 1. Register & Login Users (Distributor, Farmer, Manager, Admin)
    # Distributor
    dist_email = f"distributor.qr.{unique_suffix}@agroflow.com"
    dist_pwd = "DistributorPass123!"
    reg_dist = client.post("/api/auth/register", json={
        "name": "Distributor QR Tester",
        "email": dist_email,
        "password": dist_pwd,
        "role": "distributor"
    })
    assert reg_dist.status_code == 201
    dist_token = client.post("/api/auth/login", json={"email": dist_email, "password": dist_pwd}).json()["access_token"]
    dist_headers = {"Authorization": f"Bearer {dist_token}"}

    # Farmer
    farmer_email = f"farmer.qr.{unique_suffix}@agroflow.com"
    farmer_pwd = "FarmerPass123!"
    reg_farmer = client.post("/api/auth/register", json={
        "name": "Nashik QR Farmer",
        "email": farmer_email,
        "password": farmer_pwd,
        "role": "farmer"
    })
    assert reg_farmer.status_code == 201
    farmer_token = client.post("/api/auth/login", json={"email": farmer_email, "password": farmer_pwd}).json()["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}

    # Retailer (Buyer)
    ret_email = f"retailer.qr.{unique_suffix}@agroflow.com"
    ret_pwd = "RetailerPass123!"
    reg_ret = client.post("/api/auth/register", json={
        "name": "FreshMart Retail Buyer",
        "email": ret_email,
        "password": ret_pwd,
        "role": "retailer"
    })
    assert reg_ret.status_code == 201
    ret_user_id = reg_ret.json()["id"]
    ret_token = client.post("/api/auth/login", json={"email": ret_email, "password": ret_pwd}).json()["access_token"]
    ret_headers = {"Authorization": f"Bearer {ret_token}"}

    # Supply Chain Manager
    mgr_email = f"manager.qr.{unique_suffix}@agroflow.com"
    mgr_pwd = "ManagerPass123!"
    reg_mgr = client.post("/api/auth/register", json={
        "name": "Cold Chain Manager",
        "email": mgr_email,
        "password": mgr_pwd,
        "role": "supply_chain_manager"
    })
    assert reg_mgr.status_code == 201
    mgr_token = client.post("/api/auth/login", json={"email": mgr_email, "password": mgr_pwd}).json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    # Admin (created directly in DB session because public registration forbids admin role)
    admin_email = f"admin.qr.{unique_suffix}@agroflow.com"
    admin_pwd = "AdminPass123!"
    db_session = SessionLocal()
    from app.services.auth_service import get_password_hash
    admin_user = User(
        name="System Admin QR",
        email=admin_email,
        password_hash=get_password_hash(admin_pwd),
        role="admin"
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.close()

    admin_token = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd}).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    print("[TEST 1] Registered & Authenticated Distributor, Farmer, Manager, Admin (Passed!)")

    # 2. Distributor can retrieve eligible batches (GET /api/batches)
    res_batches = client.get("/api/batches", headers=dist_headers)
    assert res_batches.status_code == 200, f"GET /api/batches failed: {res_batches.text}"
    print("[TEST 2] Distributor can retrieve batch list (Passed!)")

    # 3. Step 1: Farmer creates Batch -> Automatic "Farmer Harvest" provenance event created
    batch_code = f"BATCH-QR-{unique_suffix}"
    res_batch = client.post("/api/batches", headers=farmer_headers, json={
        "batch_code": batch_code,
        "product_id": product_id,
        "quantity": 300.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-28",
        "expiry_date": "2026-10-20",
        "origin_location": "Nashik Organic Farm",
        "status": "Harvested"
    })
    assert res_batch.status_code == 201
    batch_id = res_batch.json()["id"]

    # Verify Traceability for Batch at Stage 1
    res_trace1 = client.get(f"/api/traceability/batch/{batch_id}", headers=dist_headers)
    assert res_trace1.status_code == 200
    events1 = res_trace1.json()
    stages1 = [e["stage"] for e in events1]
    assert "Farmer Harvest" in stages1
    assert "Cold Storage Intake" not in stages1
    assert "Dispatch & Transport" not in stages1
    print(f"[TEST 3] Stage 1: Batch #{batch_id} shows ONLY 'Farmer Harvest' event (Passed!)")

    # 4. Step 2: Retailer creates Wholesale Order & Distributor creates Shipment Dispatch -> Automatic "Dispatch & Transport" provenance event created
    res_order = client.post("/api/orders", headers=ret_headers, json={
        "order_number": f"ORD-QR-{unique_suffix}",
        "buyer_id": ret_user_id,
        "status": "Confirmed",
        "items": [{"product_id": product_id, "quantity": 100.0, "price": 40.0}]
    })
    assert res_order.status_code == 201
    order_id = res_order.json()["id"]

    res_shipment = client.post("/api/shipments", headers=dist_headers, json={
        "order_id": order_id,
        "batch_id": batch_id,
        "source": "Nashik Farm Hub",
        "destination": "FreshMart Mumbai Hub",
        "vehicle_number": "MH-15-AB-1234",
        "status": "In Transit"
    })
    assert res_shipment.status_code == 201

    # Verify Traceability for Batch at Stage 2 (Dispatch & Transport added)
    res_trace2 = client.get(f"/api/traceability/batch/{batch_id}", headers=dist_headers)
    assert res_trace2.status_code == 200
    events2 = res_trace2.json()
    stages2 = [e["stage"] for e in events2]
    assert "Farmer Harvest" in stages2
    assert "Dispatch & Transport" in stages2
    print(f"[TEST 4] Stage 2: Batch #{batch_id} shows 'Farmer Harvest' + 'Dispatch & Transport' (Passed!)")

    # 5. Chronological Ordering Verification
    timestamps = [e["timestamp"] for e in events2]
    assert timestamps == sorted(timestamps), "Traceability events MUST be returned in chronological order!"
    print("[TEST 5] Provenance timeline verified to be strictly chronological (Passed!)")

    # 6. View-Only Enforcement: Distributor cannot manually create provenance events
    res_dist_manual = client.post("/api/traceability/events", headers=dist_headers, json={
        "batch_id": batch_id,
        "stage": "Distributor Manual Stage",
        "location": "Unauthorized Facility"
    })
    assert res_dist_manual.status_code == 403, f"Distributor manual provenance creation must return 403! Got {res_dist_manual.status_code}"
    print("[TEST 6] Distributor prohibited from creating manual provenance events (Passed!)")

    # 7. Admin privileged manual provenance capability remains intact
    res_admin_manual = client.post("/api/traceability/events", headers=admin_headers, json={
        "batch_id": batch_id,
        "stage": "Quality Certification",
        "location": "Central Lab",
        "description": "Passed lab pesticide purity inspection."
    })
    assert res_admin_manual.status_code == 201, f"Admin manual provenance creation failed: {res_admin_manual.text}"
    print("[TEST 7] Admin privileged manual provenance creation verified (Passed!)")

    # 8. Farmer ownership protection: Farmer cannot view another farmer's batch traceability
    res_farmer_own = client.get(f"/api/traceability/batch/{batch_id}", headers=farmer_headers)
    assert res_farmer_own.status_code == 200  # This farmer owns this batch!

    # Create another batch owned by a different farmer
    farmer2_email = f"farmer2.qr.{unique_suffix}@agroflow.com"
    reg_f2 = client.post("/api/auth/register", json={
        "name": "Farmer 2",
        "email": farmer2_email,
        "password": "Farmer2Password123!",
        "role": "farmer"
    })
    f2_token = client.post("/api/auth/login", json={"email": farmer2_email, "password": "Farmer2Password123!"}).json()["access_token"]
    f2_headers = {"Authorization": f"Bearer {f2_token}"}

    res_f2_access = client.get(f"/api/traceability/batch/{batch_id}", headers=f2_headers)
    assert res_f2_access.status_code == 403, "Farmer 2 should NOT access Farmer 1's batch traceability!"
    print("[TEST 8] Farmer batch ownership isolation verified (Passed!)")

    print("=" * 70)
    print("ALL ISSUE #3 DISTRIBUTOR QR TRACEABILITY TESTS PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_distributor_qr_traceability_workflow()
