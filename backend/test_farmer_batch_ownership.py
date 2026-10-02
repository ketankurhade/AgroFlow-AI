import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_farmer_batch_ownership_and_visibility():
    print("=" * 70)
    print("AGROFLOW AI — FARMER BATCH OWNERSHIP & VISIBILITY TEST SUITE")
    print("=" * 70)

    # 1. Register & Login as Brand New Farmer A
    unique_a = str(uuid.uuid4())[:8]
    farmer_a_email = f"farmer.a.{unique_a}@agroflow.com"
    farmer_a_pwd = "FarmerA_Password123!"

    reg_a = client.post("/api/auth/register", json={
        "name": "Farmer Ramesh A",
        "email": farmer_a_email,
        "password": farmer_a_pwd,
        "role": "farmer"
    })
    assert reg_a.status_code == 201, f"Farmer A registration failed: {reg_a.text}"
    farmer_a_id = reg_a.json()["id"]

    login_a = client.post("/api/auth/login", json={
        "email": farmer_a_email,
        "password": farmer_a_pwd
    })
    assert login_a.status_code == 200, f"Farmer A login failed: {login_a.text}"
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"[TEST 1] Registered & Logged in Farmer A (ID: {farmer_a_id})")

    # 2. GET /api/batches as Brand New Farmer A
    res_batches_a = client.get("/api/batches", headers=headers_a)
    assert res_batches_a.status_code == 200, f"GET /api/batches failed: {res_batches_a.text}"
    batches_a = res_batches_a.json()
    assert len(batches_a) == 0, f"Brand-new farmer should see 0 batches, but saw {len(batches_a)}"
    print("[TEST 2] GET /api/batches for new Farmer A returned 0 batches (Passed!)")

    # 3. Register & Login as Farmer B
    unique_b = str(uuid.uuid4())[:8]
    farmer_b_email = f"farmer.b.{unique_b}@agroflow.com"
    farmer_b_pwd = "FarmerB_Password123!"

    reg_b = client.post("/api/auth/register", json={
        "name": "Farmer Suresh B",
        "email": farmer_b_email,
        "password": farmer_b_pwd,
        "role": "farmer"
    })
    assert reg_b.status_code == 201
    farmer_b_id = reg_b.json()["id"]

    login_b = client.post("/api/auth/login", json={
        "email": farmer_b_email,
        "password": farmer_b_pwd
    })
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"[TEST 3] Registered & Logged in Farmer B (ID: {farmer_b_id})")

    # 4. Farmer B creates a batch
    batch_b_payload = {
        "batch_code": f"BATCH-TEST-FB-{unique_b}",
        "product_id": 1,
        "farmer_id": farmer_b_id,
        "quantity": 1200.0,
        "quality_grade": "Grade A+",
        "harvest_date": "2026-09-28",
        "expiry_date": "2026-10-28",
        "origin_location": "Suresh Farm, Sangli",
        "status": "Harvested"
    }
    create_b_res = client.post("/api/batches", json=batch_b_payload, headers=headers_b)
    assert create_b_res.status_code == 201, f"Farmer B batch creation failed: {create_b_res.text}"
    created_b = create_b_res.json()
    assert created_b["farmer_id"] == farmer_b_id
    print(f"[TEST 4] Farmer B created batch (ID: {created_b['id']}, Code: {created_b['batch_code']})")

    # 5. Verify Farmer A STILL sees 0 batches
    res_batches_a_again = client.get("/api/batches", headers=headers_a)
    assert res_batches_a_again.status_code == 200
    assert len(res_batches_a_again.json()) == 0
    print("[TEST 5] Farmer A cannot see Farmer B's batch (Isolation Verified!)")

    # 6. Verify Farmer B sees ONLY their batch
    res_batches_b = client.get("/api/batches", headers=headers_b)
    assert res_batches_b.status_code == 200
    batches_b = res_batches_b.json()
    assert len(batches_b) == 1
    assert batches_b[0]["id"] == created_b["id"]
    print("[TEST 6] Farmer B sees exactly 1 batch belonging to them (Verified!)")

    # 7. Attempting batch creation where Farmer A passes Farmer B's ID in payload -> HTTP 403
    tampered_payload = {
        "batch_code": f"BATCH-TAMPER-{unique_a}",
        "product_id": 1,
        "farmer_id": farmer_b_id, # Attempting spoofing of Farmer B
        "quantity": 500.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-28",
        "expiry_date": "2026-10-28",
        "origin_location": "Ramesh Farm, Nashik",
        "status": "Harvested"
    }
    create_tampered_res = client.post("/api/batches", json=tampered_payload, headers=headers_a)
    assert create_tampered_res.status_code == 403, f"Expected 403 Forbidden when specifying foreign farmer_id, got {create_tampered_res.status_code}"
    print("[TEST 7a] Backend strictly rejects spoofed farmer_id with HTTP 403 Forbidden!")

    # Now create valid batch for Farmer A (farmer_id omitted or matching farmer_a_id)
    valid_a_payload = {
        "batch_code": f"BATCH-OWNED-{unique_a}",
        "product_id": 1,
        "farmer_id": farmer_a_id,
        "quantity": 500.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-28",
        "expiry_date": "2026-10-28",
        "origin_location": "Ramesh Farm, Nashik",
        "status": "Harvested"
    }
    create_valid_a_res = client.post("/api/batches", json=valid_a_payload, headers=headers_a)
    assert create_valid_a_res.status_code == 201
    created_valid_a = create_valid_a_res.json()
    assert created_valid_a["farmer_id"] == farmer_a_id
    print("[TEST 7b] Valid batch created using authenticated Farmer A ID (Verified!)")

    # 8. Login as Admin and confirm Admin sees all batches
    admin_login = client.post("/api/auth/login", json={
        "email": "admin@agroflow.com",
        "password": "admin123"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    res_admin_batches = client.get("/api/batches?limit=500", headers=headers_admin)
    assert res_admin_batches.status_code == 200
    admin_batches = res_admin_batches.json()
    # Admin must see all batches created (at least Farmer B's and Farmer A's batches)
    admin_batch_ids = [b["id"] for b in admin_batches]
    assert created_b["id"] in admin_batch_ids
    assert created_valid_a["id"] in admin_batch_ids
    print(f"[TEST 8] Admin sees all system batches ({len(admin_batches)} total batches visible to Admin)")

    print("\n" + "=" * 70)
    print("ALL FARMER BATCH OWNERSHIP & VISIBILITY TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    test_farmer_batch_ownership_and_visibility()
