import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_manager_provenance_workflow():
    print("=" * 80)
    print("AGROFLOW AI — SUPPLY CHAIN / STORAGE MANAGER PROVENANCE & RBAC TEST SUITE")
    print("=" * 80)

    # 1. Register & Login as Farmer
    unique_f = str(uuid.uuid4())[:8]
    farmer_email = f"farmer.mgrtest.{unique_f}@agroflow.com"
    farmer_pwd = "Farmer_Password123!"

    reg_f = client.post("/api/auth/register", json={
        "name": "Farmer Ramesh ManagerTest",
        "email": farmer_email,
        "password": farmer_pwd,
        "role": "farmer"
    })
    assert reg_f.status_code == 201
    farmer_id = reg_f.json()["id"]

    login_f = client.post("/api/auth/login", json={"email": farmer_email, "password": farmer_pwd})
    assert login_f.status_code == 200
    token_f = login_f.json()["access_token"]
    headers_f = {"Authorization": f"Bearer {token_f}"}
    print(f"[TEST 1] Registered & Logged in Farmer (ID: {farmer_id})")

    # Get product list for batch creation
    prod_res = client.get("/api/products", headers=headers_f)
    assert prod_res.status_code == 200
    products = prod_res.json()
    product_id = products[0]["id"]

    # 2. Farmer creates Batch 1
    batch_payload_1 = {
        "batch_code": f"BATCH-MGR-1-{unique_f}",
        "product_id": product_id,
        "farmer_id": farmer_id,
        "quantity": 800.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-29",
        "expiry_date": "2026-10-29",
        "origin_location": "Sangli Grape Farm, MH",
        "status": "Harvested"
    }
    create_b1_res = client.post("/api/batches", json=batch_payload_1, headers=headers_f)
    assert create_b1_res.status_code == 201
    batch1 = create_b1_res.json()
    batch1_id = batch1["id"]
    print(f"[TEST 2] Farmer created Batch 1 (ID: {batch1_id}, Code: {batch1['batch_code']})")

    # Verify initial Farmer Harvest event & farm-origin inventory
    trace_b1 = client.get(f"/api/traceability/batch/{batch1_id}", headers=headers_f).json()
    assert len(trace_b1) == 1
    assert trace_b1[0]["stage"] == "Farmer Harvest"
    print("[TEST 2a] Verified exactly 1 auto 'Farmer Harvest' event on batch creation.")

    inv_b1 = client.get("/api/inventory", headers=headers_f).json()
    assert len(inv_b1) == 0, "Farmer should have 0 inventory records upon batch creation."
    print("[TEST 2b] Verified 0 farmer inventory records created for Batch 1.")

    # 3. Register & Login as Supply Chain Manager
    unique_m = str(uuid.uuid4())[:8]
    manager_email = f"manager.anita.{unique_m}@agroflow.com"
    manager_pwd = "Manager_Password123!"

    reg_m = client.post("/api/auth/register", json={
        "name": "Manager Anita Sharma",
        "email": manager_email,
        "password": manager_pwd,
        "role": "supply_chain_manager"
    })
    assert reg_m.status_code == 201
    manager_id = reg_m.json()["id"]

    login_m = client.post("/api/auth/login", json={"email": manager_email, "password": manager_pwd})
    assert login_m.status_code == 200
    token_m = login_m.json()["access_token"]
    headers_m = {"Authorization": f"Bearer {token_m}"}
    print(f"[TEST 3] Registered & Logged in Supply Chain Manager (ID: {manager_id})")

    # 4. Supply Chain Manager attempts MANUAL provenance creation -> MUST RETURN HTTP 403 FORBIDDEN
    manual_payload = {
        "batch_id": batch1_id,
        "stage": "Cold Storage Intake",
        "location": "Manual Hub",
        "description": "Attempting manual provenance creation"
    }
    manual_res = client.post("/api/traceability/events", json=manual_payload, headers=headers_m)
    assert manual_res.status_code == 403, f"Expected 403 Forbidden for Manager manual event creation, got {manual_res.status_code}"
    print("[TEST 4 PASSED] Manager strictly rejected from manual provenance creation with HTTP 403 Forbidden!")

    # 5. Manager performs ACTUAL Cold Storage Intake (POST /api/inventory)
    cold_storage_payload = {
        "batch_id": batch1_id,
        "warehouse_location": "Pune Cold Facility - Bay B2",
        "quantity": 800.0,
        "temperature": 16.5,
        "humidity": 68.0
    }
    intake_res = client.post("/api/inventory", json=cold_storage_payload, headers=headers_m)
    assert intake_res.status_code == 201, f"Manager cold storage intake failed: {intake_res.text}"
    updated_inv = intake_res.json()
    assert updated_inv["batch_id"] == batch1_id
    assert updated_inv["warehouse_location"] == "Pune Cold Facility - Bay B2"
    assert updated_inv["temperature"] == 16.5
    print(f"[TEST 5] Manager stored Batch 1 in cold storage (Location: {updated_inv['warehouse_location']}, Temp: 16.5°C).")

    # 6. Verify Chronological Timeline: Farmer Harvest -> Cold Storage Intake
    trace_b1_after = client.get(f"/api/traceability/batch/{batch1_id}", headers=headers_m).json()
    print(f"[TEST 6] Retrieved Batch 1 timeline: {len(trace_b1_after)} event(s)")
    assert len(trace_b1_after) == 2, f"Expected exactly 2 events in timeline, got {len(trace_b1_after)}"
    assert trace_b1_after[0]["stage"] == "Farmer Harvest", f"Event 0 must be Farmer Harvest, got '{trace_b1_after[0]['stage']}'"
    assert trace_b1_after[1]["stage"] == "Cold Storage Intake", f"Event 1 must be Cold Storage Intake, got '{trace_b1_after[1]['stage']}'"
    assert trace_b1_after[1]["location"] == "Pune Cold Facility - Bay B2"
    print("[TEST 6 PASSED] Chronological timeline 'Farmer Harvest' -> 'Cold Storage Intake' verified!")

    # 7. Idempotency Check: Manager retries/re-submits cold storage intake for same batch
    intake_retry_res = client.post("/api/inventory", json=cold_storage_payload, headers=headers_m)
    assert intake_retry_res.status_code == 201
    trace_b1_retry = client.get(f"/api/traceability/batch/{batch1_id}", headers=headers_m).json()
    assert len(trace_b1_retry) == 2, f"Retry must NOT create duplicate Cold Storage Intake events (got {len(trace_b1_retry)} events)"
    print("[TEST 7 PASSED] Retrying cold storage intake did NOT produce duplicate events!")

    # 8. Create Batch 2 as Farmer (Unrelated Batch) & verify it does NOT have Cold Storage Intake yet
    batch_payload_2 = {
        "batch_code": f"BATCH-MGR-2-{unique_f}",
        "product_id": product_id,
        "farmer_id": farmer_id,
        "quantity": 500.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-29",
        "expiry_date": "2026-10-29",
        "origin_location": "Nashik Organic Plot, MH",
        "status": "Harvested"
    }
    create_b2_res = client.post("/api/batches", json=batch_payload_2, headers=headers_f)
    assert create_b2_res.status_code == 201
    batch2_id = create_b2_res.json()["id"]

    trace_b2 = client.get(f"/api/traceability/batch/{batch2_id}", headers=headers_m).json()
    assert len(trace_b2) == 1
    assert trace_b2[0]["stage"] == "Farmer Harvest"
    print("[TEST 8 PASSED] Unstored Batch 2 has only 'Farmer Harvest' event (no unearned Cold Storage Intake)!")

    # 9. Admin manual provenance creation remains intact
    admin_login = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "admin123"})
    assert admin_login.status_code == 200
    headers_admin = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    admin_event_res = client.post("/api/traceability/events", json={
        "batch_id": batch1_id,
        "stage": "Quality Inspection",
        "location": "Central Audit Center",
        "description": "Admin manual correction"
    }, headers=headers_admin)
    assert admin_event_res.status_code == 201
    print("[TEST 9 PASSED] Admin retains manual provenance creation capability (201 Created)!")

    # 10. Manager RBAC Endpoint Restrictions Test (Batches POST, Orders POST, Routes OPTIMIZE)
    mgr_batch_res = client.post("/api/batches", json={
        "batch_code": f"BATCH-TAMPER-MGR-{unique_m}",
        "product_id": product_id,
        "farmer_id": farmer_id,
        "quantity": 100.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-29",
        "expiry_date": "2026-10-29",
        "origin_location": "Unauthorized Origin",
        "status": "Harvested"
    }, headers=headers_m)
    assert mgr_batch_res.status_code == 403, f"Expected 403 for Manager batch creation, got {mgr_batch_res.status_code}"

    mgr_order_res = client.post("/api/orders", json={
        "order_number": f"ORD-TAMPER-MGR-{unique_m}",
        "buyer_id": manager_id,
        "status": "Confirmed",
        "items": [{"product_id": product_id, "quantity": 10.0, "price": 50.0}]
    }, headers=headers_m)
    assert mgr_order_res.status_code == 403, f"Expected 403 for Manager order creation, got {mgr_order_res.status_code}"

    mgr_route_res = client.post("/api/routes/optimize", json={
        "stops": [{"name": "Nashik Organic Farm, MH"}, {"name": "Mumbai Cold Storage Facility - Bay 4"}]
    }, headers=headers_m)
    assert mgr_route_res.status_code == 403, f"Expected 403 for Manager route optimization, got {mgr_route_res.status_code}"
    print("[TEST 10 PASSED] Manager strictly blocked from batch creation, order creation, and route optimization (HTTP 403 Forbidden)!")

    print("\n" + "=" * 80)
    print("ALL SUPPLY CHAIN / STORAGE MANAGER TESTS PASSED 100%!")
    print("=" * 80)

if __name__ == "__main__":
    test_manager_provenance_workflow()
