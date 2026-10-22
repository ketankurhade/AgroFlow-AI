import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.product import Product

client = TestClient(app)

def test_distributor_shipment_workflow():
    print("=" * 70)
    print("AGROFLOW AI — ISSUE #1: DISTRIBUTOR SHIPMENT WORKFLOW TEST SUITE")
    print("=" * 70)

    unique_suffix = str(uuid.uuid4())[:8]

    # Setup Product in DB using canonical product
    db = SessionLocal()
    product = db.query(Product).filter(Product.name == "Onion").first() or db.query(Product).first()
    assert product is not None, "Canonical product 'Onion' must exist in database"
    product_id = product.id
    db.close()

    # 1. Setup Users (Distributor, Retailer, Farmer, Consumer)
    # Distributor
    dist_email = f"distributor.{unique_suffix}@agroflow.com"
    dist_pwd = "DistributorPass123!"
    reg_dist = client.post("/api/auth/register", json={
        "name": "AgroDistributor Logistics",
        "email": dist_email,
        "password": dist_pwd,
        "role": "distributor"
    })
    assert reg_dist.status_code == 201, f"Distributor reg failed: {reg_dist.text}"
    dist_token = client.post("/api/auth/login", json={"email": dist_email, "password": dist_pwd}).json()["access_token"]
    dist_headers = {"Authorization": f"Bearer {dist_token}"}

    # Retailer
    ret_email = f"retailer.{unique_suffix}@agroflow.com"
    ret_pwd = "RetailerPass123!"
    reg_ret = client.post("/api/auth/register", json={
        "name": "FreshMart Retail",
        "email": ret_email,
        "password": ret_pwd,
        "role": "retailer"
    })
    assert reg_ret.status_code == 201
    ret_user_id = reg_ret.json()["id"]
    ret_token = client.post("/api/auth/login", json={"email": ret_email, "password": ret_pwd}).json()["access_token"]
    ret_headers = {"Authorization": f"Bearer {ret_token}"}

    # Farmer
    farmer_email = f"farmer.{unique_suffix}@agroflow.com"
    farmer_pwd = "FarmerPass123!"
    reg_farmer = client.post("/api/auth/register", json={
        "name": "Nashik Farmer",
        "email": farmer_email,
        "password": farmer_pwd,
        "role": "farmer"
    })
    assert reg_farmer.status_code == 201
    farmer_token = client.post("/api/auth/login", json={"email": farmer_email, "password": farmer_pwd}).json()["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}

    # Consumer
    cons_email = f"consumer.{unique_suffix}@agroflow.com"
    cons_pwd = "ConsumerPass123!"
    reg_cons = client.post("/api/auth/register", json={
        "name": "Agro Consumer",
        "email": cons_email,
        "password": cons_pwd,
        "role": "consumer"
    })
    assert reg_cons.status_code == 201
    cons_token = client.post("/api/auth/login", json={"email": cons_email, "password": cons_pwd}).json()["access_token"]
    cons_headers = {"Authorization": f"Bearer {cons_token}"}

    print("[TEST 1] Registered & Authenticated Distributor, Retailer, Farmer, Consumer (Passed!)")

    # 2. Farmer creates a Batch
    batch_code = f"BATCH-DIST-{unique_suffix}"
    res_batch = client.post("/api/batches", headers=farmer_headers, json={
        "batch_code": batch_code,
        "product_id": product_id,
        "quantity": 500.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-25",
        "expiry_date": "2026-10-15",
        "origin_location": "Nashik Organic Farm",
        "status": "Harvested"
    })
    assert res_batch.status_code == 201, f"Batch creation failed: {res_batch.text}"
    batch_id = res_batch.json()["id"]
    initial_batch_qty = res_batch.json()["quantity"]
    print(f"[TEST 2] Farmer created Batch #{batch_id} (Code: {batch_code}, Qty: {initial_batch_qty} kg) (Passed!)")

    # 3. Retailer creates a Wholesale Order
    order_num = f"ORD-DIST-{unique_suffix}"
    res_order = client.post("/api/orders", headers=ret_headers, json={
        "order_number": order_num,
        "buyer_id": ret_user_id,
        "status": "Confirmed",
        "items": [
            {
                "product_id": product_id,
                "quantity": 50.0,
                "price": 45.0
            }
        ]
    })
    assert res_order.status_code == 201, f"Order creation failed: {res_order.text}"
    order_id = res_order.json()["id"]
    print(f"[TEST 3] Retailer created Wholesale Order #{order_id} (Num: {order_num}) (Passed!)")

    # 4. Distributor can see wholesale orders (GET /api/orders)
    res_dist_orders = client.get("/api/orders?limit=500", headers=dist_headers)
    assert res_dist_orders.status_code == 200, f"GET /api/orders failed: {res_dist_orders.text}"
    fetched_orders = res_dist_orders.json()
    found_order = any(o["id"] == order_id for o in fetched_orders)
    assert found_order, f"Distributor should see Order #{order_id}"
    print("[TEST 4] Distributor can see eligible retailer wholesale order (Passed!)")

    # 5. Distributor can retrieve eligible batches (GET /api/batches - non empty!)
    res_dist_batches = client.get("/api/batches?limit=500", headers=dist_headers)
    assert res_dist_batches.status_code == 200, f"GET /api/batches for distributor returned {res_dist_batches.status_code}: {res_dist_batches.text}"
    fetched_batches = res_dist_batches.json()
    assert len(fetched_batches) > 0, "Harvest Batch list for Distributor must NOT be empty!"
    found_batch = any(b["id"] == batch_id for b in fetched_batches)
    assert found_batch, f"Distributor should see Batch #{batch_id}"
    print("[TEST 5] Harvest batch selector returned eligible stock for Distributor (Passed!)")

    # 6. Distributor creates & dispatches Shipment
    res_shipment = client.post("/api/shipments", headers=dist_headers, json={
        "order_id": order_id,
        "batch_id": batch_id,
        "source": "Nashik Farm Hub - Cold Storage A",
        "destination": "FreshMart Retail Hub - Mumbai",
        "vehicle_number": "MH-15-AB-1234",
        "status": "In Transit"
    })
    assert res_shipment.status_code == 201, f"Shipment creation failed: {res_shipment.text}"
    shipment_data = res_shipment.json()
    shipment_id = shipment_data["id"]
    assert shipment_data["order_id"] == order_id
    assert shipment_data["batch_id"] == batch_id
    assert shipment_data["status"] == "In Transit"
    assert shipment_data["vehicle_number"] == "MH-15-AB-1234"
    print(f"[TEST 6] Distributor created & dispatched Shipment #{shipment_id} persisted in PostgreSQL (Passed!)")

    # 7. Check Order status synced to 'In Transit'
    res_updated_order = client.get(f"/api/orders/{order_id}", headers=dist_headers)
    assert res_updated_order.status_code == 200
    assert res_updated_order.json()["status"] == "In Transit"
    print("[TEST 7] Shipment dispatch updated Order status to 'In Transit' (Passed!)")

    # 8. Check Automatic Traceability Provenance Event created
    res_trace = client.get(f"/api/traceability/batch/{batch_id}", headers=dist_headers)
    assert res_trace.status_code == 200
    events = res_trace.json()
    dispatch_events = [e for e in events if e["stage"] == "Dispatch & Transport"]
    assert len(dispatch_events) > 0, "Automatic 'Dispatch & Transport' provenance event must be created on dispatch!"
    print(f"[TEST 8] Automatic 'Dispatch & Transport' provenance event verified (Event ID: {dispatch_events[0]['id']}) (Passed!)")

    # 9. RBAC: Distributor CANNOT manually create arbitrary provenance event (admin-only)
    res_manual_prov = client.post("/api/traceability/events", headers=dist_headers, json={
        "batch_id": batch_id,
        "stage": "Arbitrary Manual Stage",
        "location": "Unauthorized Location"
    })
    assert res_manual_prov.status_code == 403, f"Distributor must NOT manually create provenance events! Got: {res_manual_prov.status_code}"
    print("[TEST 9] Distributor prohibited from manually creating arbitrary provenance events (Passed!)")

    # 10. RBAC: Farmer CANNOT create Distributor shipments
    res_farmer_ship = client.post("/api/shipments", headers=farmer_headers, json={
        "order_id": order_id,
        "batch_id": batch_id,
        "source": "Nashik",
        "destination": "Mumbai",
        "vehicle_number": "MH-01-XX-9999",
        "status": "In Transit"
    })
    assert res_farmer_ship.status_code == 403, "Farmer must NOT create shipments!"
    print("[TEST 10] Farmer prohibited from creating shipments (Passed!)")

    # 11. RBAC: Retailer CANNOT create Distributor shipments
    res_ret_ship = client.post("/api/shipments", headers=ret_headers, json={
        "order_id": order_id,
        "batch_id": batch_id,
        "source": "Nashik",
        "destination": "Mumbai",
        "vehicle_number": "MH-01-XX-9999",
        "status": "In Transit"
    })
    assert res_ret_ship.status_code == 403, "Retailer must NOT create shipments!"
    print("[TEST 11] Retailer prohibited from creating shipments (Passed!)")

    # 12. RBAC: Consumer CANNOT create Distributor shipments
    res_cons_ship = client.post("/api/shipments", headers=cons_headers, json={
        "order_id": order_id,
        "batch_id": batch_id,
        "source": "Nashik",
        "destination": "Mumbai",
        "vehicle_number": "MH-01-XX-9999",
        "status": "In Transit"
    })
    assert res_cons_ship.status_code == 403, "Consumer must NOT create shipments!"
    print("[TEST 12] Consumer prohibited from creating shipments (Passed!)")

    # 13. Invalid/nonexistent batch cannot be used
    res_invalid_batch = client.post("/api/shipments", headers=dist_headers, json={
        "order_id": order_id,
        "batch_id": 999999,
        "source": "Nashik",
        "destination": "Mumbai",
        "vehicle_number": "MH-15-AB-1234",
        "status": "In Transit"
    })
    assert res_invalid_batch.status_code == 404, "Invalid batch ID must return 404!"
    print("[TEST 13] Nonexistent batch ID rejected with 404 Not Found (Passed!)")

    # 14. Duplicate shipment protection for same order
    res_dup_shipment = client.post("/api/shipments", headers=dist_headers, json={
        "order_id": order_id,
        "batch_id": batch_id,
        "source": "Nashik",
        "destination": "Mumbai",
        "vehicle_number": "MH-15-AB-1234",
        "status": "In Transit"
    })
    assert res_dup_shipment.status_code == 400, f"Duplicate active shipment must return 400! Got: {res_dup_shipment.status_code}"
    print("[TEST 14] Duplicate active shipment attempt rejected with 400 Bad Request (Passed!)")

    # 15. Scope rule check: Verify NO inventory quantity was modified!
    res_check_batch = client.get(f"/api/batches/{batch_id}", headers=dist_headers)
    assert res_check_batch.status_code == 200
    current_batch_qty = res_check_batch.json()["quantity"]
    assert current_batch_qty == initial_batch_qty, f"Inventory batch quantity changed from {initial_batch_qty} to {current_batch_qty}! Issue #1 must NOT alter inventory!"
    print(f"[TEST 15] Verified Scope Rule: Batch quantity remained untouched ({current_batch_qty} kg) (Passed!)")

    print("=" * 70)
    print("ALL ISSUE #1 DISTRIBUTOR SHIPMENT WORKFLOW TESTS PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_distributor_shipment_workflow()
