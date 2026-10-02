import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_farmer_provenance_workflow():
    print("=" * 70)
    print("AGROFLOW AI — FARMER PROVENANCE & RBAC END-TO-END TEST SUITE")
    print("=" * 70)

    # 1. Register & Login as Farmer 1
    unique_1 = str(uuid.uuid4())[:8]
    farmer1_email = f"farmer.prov1.{unique_1}@agroflow.com"
    farmer1_pwd = "Farmer1_Password123!"

    reg1 = client.post("/api/auth/register", json={
        "name": "Farmer Ramesh One",
        "email": farmer1_email,
        "password": farmer1_pwd,
        "role": "farmer"
    })
    assert reg1.status_code == 201
    farmer1_id = reg1.json()["id"]

    login1 = client.post("/api/auth/login", json={
        "email": farmer1_email,
        "password": farmer1_pwd
    })
    assert login1.status_code == 200
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    print(f"[TEST 1] Registered & Logged in Farmer 1 (ID: {farmer1_id})")

    # 2. Product Catalog Expansion Test
    res_products = client.get("/api/products", headers=headers1)
    assert res_products.status_code == 200, f"GET /api/products failed: {res_products.text}"
    products = res_products.json()
    product_names = [p["name"] for p in products]
    
    print(f"[TEST 2] Product catalog contains {len(products)} products:")
    for name in product_names:
        print(f"  - {name}")

    assert "Organic Alphonso Mangoes" in product_names, "Organic Alphonso Mangoes missing"
    assert "Fresh Desi Tomatoes" in product_names, "Fresh Desi Tomatoes missing"
    assert "Red Onions" in product_names, "Red Onions missing"
    assert "Cold Storage Potatoes" in product_names, "Cold Storage Potatoes missing"
    assert len(products) >= 8, f"Expected at least 8 expanded products, found {len(products)}"
    print("[TEST 2 PASSED] Expanded product catalog verified!")

    # 3. Create Batch as Farmer 1 and Verify Auto 'Farmer Harvest' Provenance Event
    batch_payload = {
        "batch_code": f"BATCH-PROV-{unique_1}",
        "product_id": products[2]["id"],  # e.g., Red Onions
        "farmer_id": farmer1_id,
        "quantity": 1500.0,
        "quality_grade": "Grade A+",
        "harvest_date": "2026-09-29",
        "expiry_date": "2026-10-29",
        "origin_location": "Nashik Organic Farm, MH",
        "status": "Harvested"
    }

    create_batch_res = client.post("/api/batches", json=batch_payload, headers=headers1)
    assert create_batch_res.status_code == 201, f"Batch creation failed: {create_batch_res.text}"
    batch = create_batch_res.json()
    batch_id = batch["id"]
    print(f"[TEST 3a] Farmer 1 created batch '{batch['batch_code']}' (ID: {batch_id})")

    # Fetch traceability events for the new batch
    trace_res = client.get(f"/api/traceability/batch/{batch_id}", headers=headers1)
    assert trace_res.status_code == 200, f"GET traceability failed: {trace_res.text}"
    events = trace_res.json()
    print(f"[TEST 3b] Traceability timeline retrieved for batch {batch_id}: {len(events)} event(s)")
    assert len(events) == 1, f"Expected exactly 1 auto-generated event, got {len(events)}"
    assert events[0]["stage"] == "Farmer Harvest", f"Expected stage 'Farmer Harvest', got '{events[0]['stage']}'"
    assert events[0]["location"] == "Nashik Organic Farm, MH"
    assert events[0]["batch_id"] == batch_id
    print("[TEST 3 PASSED] Auto 'Farmer Harvest' provenance event verified!")

    # 3c. Verify 0 Initial Inventory Creation for the New Batch (Farmer has no inventory records)
    inv_res = client.get("/api/inventory", headers=headers1)
    assert inv_res.status_code == 200, f"GET /api/inventory failed: {inv_res.text}"
    inv_items = inv_res.json()
    assert len(inv_items) == 0, f"Farmers must have 0 inventory records, got {len(inv_items)}"
    print("[TEST 3c PASSED] Verified no Farmer Inventory record was created!")

    # 3d. Verify Farmer CANNOT create inventory records (POST /api/inventory returns HTTP 403)
    farmer_inv_post = client.post("/api/inventory", headers=headers1, json={
        "batch_id": batch_id,
        "warehouse_location": "Unauthorized Farm Storage",
        "quantity": 1500.0
    })
    assert farmer_inv_post.status_code == 403, f"Farmer must be blocked from creating inventory (403), got {farmer_inv_post.status_code}"
    print("[TEST 3d PASSED] Farmer inventory creation blocked with HTTP 403 Forbidden!")

    # 4. Attempt Manual Provenance Event Creation as Farmer -> MUST RETURN HTTP 403 FORBIDDEN
    manual_event_payload = {
        "batch_id": batch_id,
        "stage": "Cold Storage Intake",
        "location": "Unauthorized Manual Hub",
        "description": "Attempting manual step addition from Farmer role"
    }
    manual_res = client.post("/api/traceability/events", json=manual_event_payload, headers=headers1)
    assert manual_res.status_code == 403, f"Expected 403 Forbidden for Farmer manual event, got {manual_res.status_code}"
    print(f"[TEST 4 PASSED] Backend correctly rejected Farmer manual event creation with HTTP 403 Forbidden!")

    # 5. Register & Login as Farmer 2 -> Verify Isolation and 403 on foreign batch traceability
    unique_2 = str(uuid.uuid4())[:8]
    farmer2_email = f"farmer.prov2.{unique_2}@agroflow.com"
    farmer2_pwd = "Farmer2_Password123!"

    reg2 = client.post("/api/auth/register", json={
        "name": "Farmer Suresh Two",
        "email": farmer2_email,
        "password": farmer2_pwd,
        "role": "farmer"
    })
    assert reg2.status_code == 201
    farmer2_id = reg2.json()["id"]

    login2 = client.post("/api/auth/login", json={
        "email": farmer2_email,
        "password": farmer2_pwd
    })
    assert login2.status_code == 200
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Farmer 2 tries to view Farmer 1's batch traceability -> MUST RETURN 403 FORBIDDEN
    foreign_trace_res = client.get(f"/api/traceability/batch/{batch_id}", headers=headers2)
    assert foreign_trace_res.status_code == 403, f"Expected 403 when viewing foreign batch trace, got {foreign_trace_res.status_code}"
    print("[TEST 5a PASSED] Farmer 2 blocked from viewing Farmer 1's batch traceability (403 Forbidden)!")

    # Farmer 2 GET /api/inventory does NOT contain Farmer 1's batch inventory
    farmer2_inv_res = client.get("/api/inventory", headers=headers2)
    assert farmer2_inv_res.status_code == 200
    farmer2_inv_items = farmer2_inv_res.json()
    farmer2_matching = [i for i in farmer2_inv_items if i["batch_id"] == batch_id]
    assert len(farmer2_matching) == 0, f"Farmer 2 should not see Farmer 1's batch inventory, but saw {len(farmer2_matching)}"
    print("[TEST 5b PASSED] Farmer 2 cannot see Farmer 1's initial inventory (Isolation Verified!)")

    # 6. Admin Provenance Event Creation Test -> MUST WORK (201 Created)
    admin_login = client.post("/api/auth/login", json={
        "email": "admin@agroflow.com",
        "password": "admin123"
    })
    assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
    admin_token = admin_login.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    admin_event_payload = {
        "batch_id": batch_id,
        "stage": "Quality Inspection",
        "location": "Nashik Quality Control Center",
        "description": "Passed grade inspection by certified auditor."
    }
    admin_event_res = client.post("/api/traceability/events", json=admin_event_payload, headers=headers_admin)
    assert admin_event_res.status_code == 201, f"Admin event creation failed: {admin_event_res.text}"
    print("[TEST 6 PASSED] Admin successfully added Quality Inspection provenance step!")

    # Verify Farmer 1 can now see BOTH events (Farmer Harvest + Quality Inspection) on their batch
    updated_trace_res = client.get(f"/api/traceability/batch/{batch_id}", headers=headers1)
    assert updated_trace_res.status_code == 200
    updated_events = updated_trace_res.json()
    assert len(updated_events) == 2
    assert updated_events[0]["stage"] == "Farmer Harvest"
    assert updated_events[1]["stage"] == "Quality Inspection"
    print("[TEST 7 PASSED] Farmer 1 can view updated timeline containing later supply chain events!")

    print("\n" + "=" * 70)
    print("ALL FARMER PROVENANCE & RBAC TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    test_farmer_provenance_workflow()
