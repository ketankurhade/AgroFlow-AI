import uuid
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.product import Product
from app.models.user import User

client = TestClient(app)

def test_consumer_order_and_tracking_workflow():
    print("=" * 70)
    print("AGROFLOW AI — ISSUE #5: CONSUMER ORDER + TRACKING TEST SUITE")
    print("=" * 70)

    unique_suffix = str(uuid.uuid4())[:8]

    # Setup Product in DB using canonical Onion product
    db = SessionLocal()
    product = db.query(Product).filter(Product.name == "Onion").first() or db.query(Product).first()
    assert product is not None, "Canonical product 'Onion' must exist in database"
    product_id = product.id
    official_price = product.price if hasattr(product, 'price') and product.price else 35.0
    db.close()

    # 1. Register Users: Consumer A, Consumer B, Farmer, Distributor
    # Consumer A
    cons_a_email = f"consumer.a.{unique_suffix}@agroflow.com"
    cons_a_pwd = "ConsumerA_Pass123!"
    reg_a = client.post("/api/auth/register", json={
        "name": "Consumer Anita A",
        "email": cons_a_email,
        "password": cons_a_pwd,
        "role": "consumer"
    })
    assert reg_a.status_code == 201, f"Consumer A reg failed: {reg_a.text}"
    cons_a_id = reg_a.json()["id"]
    token_a = client.post("/api/auth/login", json={"email": cons_a_email, "password": cons_a_pwd}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Consumer B
    cons_b_email = f"consumer.b.{unique_suffix}@agroflow.com"
    cons_b_pwd = "ConsumerB_Pass123!"
    reg_b = client.post("/api/auth/register", json={
        "name": "Consumer Bharat B",
        "email": cons_b_email,
        "password": cons_b_pwd,
        "role": "consumer"
    })
    assert reg_b.status_code == 201
    cons_b_id = reg_b.json()["id"]
    token_b = client.post("/api/auth/login", json={"email": cons_b_email, "password": cons_b_pwd}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Farmer
    farmer_email = f"farmer.c.{unique_suffix}@agroflow.com"
    farmer_pwd = "Farmer_Pass123!"
    reg_farmer = client.post("/api/auth/register", json={
        "name": "Farmer Chandu",
        "email": farmer_email,
        "password": farmer_pwd,
        "role": "farmer"
    })
    assert reg_farmer.status_code == 201
    farmer_id = reg_farmer.json()["id"]
    farmer_token = client.post("/api/auth/login", json={"email": farmer_email, "password": farmer_pwd}).json()["access_token"]
    headers_farmer = {"Authorization": f"Bearer {farmer_token}"}

    # Distributor
    dist_email = f"distributor.c.{unique_suffix}@agroflow.com"
    dist_pwd = "Distributor_Pass123!"
    reg_dist = client.post("/api/auth/register", json={
        "name": "Distributor Dinesh",
        "email": dist_email,
        "password": dist_pwd,
        "role": "distributor"
    })
    assert reg_dist.status_code == 201
    dist_token = client.post("/api/auth/login", json={"email": dist_email, "password": dist_pwd}).json()["access_token"]
    headers_dist = {"Authorization": f"Bearer {dist_token}"}

    print(f"[TEST 1] Registered Consumer A ({cons_a_id}), Consumer B ({cons_b_id}), Farmer, Distributor (Passed!)")

    # 2. Farmer creates Harvest Batch
    batch_code = f"BATCH-CONS-{unique_suffix}"
    res_batch = client.post("/api/batches", headers=headers_farmer, json={
        "batch_code": batch_code,
        "product_id": product_id,
        "quantity": 500.0,
        "quality_grade": "Grade A+",
        "harvest_date": "2026-09-29",
        "expiry_date": "2026-10-29",
        "origin_location": "Sangli Organic Hub",
        "status": "Harvested"
    })
    assert res_batch.status_code == 201
    batch_id = res_batch.json()["id"]
    print(f"[TEST 2] Farmer created Harvest Batch #{batch_id} (Passed!)")

    # Register Retailer & Stock Inventory
    ret_email = f"retailer.track.{unique_suffix}@agroflow.com"
    reg_ret = client.post("/api/auth/register", json={
        "name": "Tracking Retailer",
        "email": ret_email,
        "password": "RetailerPassword123!",
        "role": "retailer"
    })
    ret_id = reg_ret.json()["id"]
    token_ret = client.post("/api/auth/login", json={"email": ret_email, "password": "RetailerPassword123!"}).json()["access_token"]
    headers_ret = {"Authorization": f"Bearer {token_ret}"}

    # Fulfill wholesale to retailer so retailer has stock
    ret_wholesale_order = client.post("/api/orders", headers=headers_ret, json={
        "order_number": f"ORD-WHOLESALE-TRACK-{unique_suffix}",
        "buyer_id": ret_id,
        "items": [{"product_id": product_id, "quantity": 100.0, "price": 45.0}]
    }).json()
    wh_ship = client.post("/api/shipments", headers=headers_dist, json={
        "order_id": ret_wholesale_order["id"],
        "batch_id": batch_id,
        "source": "Sangli Hub",
        "destination": "Tracking Retailer Store",
        "vehicle_number": "MH-12-WH-100",
        "status": "In Transit"
    }).json()
    client.patch(f"/api/shipments/{wh_ship['id']}/status", headers=headers_dist, json={"status": "Delivered"})

    # 3. Consumer A places Order via Marketplace workflow
    order_num_a = f"ORD-CONS-{unique_suffix}"
    payload_a = {
        "order_number": order_num_a,
        "buyer_id": cons_b_id, # Attempt to spoof Consumer B
        "status": "Delivered", # Attempt to override initial status
        "items": [
            {
                "product_id": product_id,
                "quantity": 10.0,
                "price": 1.0 # Attempted price manipulation
            }
        ]
    }
    res_create_a = client.post("/api/orders", headers=headers_a, json=payload_a)
    assert res_create_a.status_code == 201, f"Order creation failed: {res_create_a.text}"
    order_a_data = res_create_a.json()
    order_a_id = order_a_data["id"]

    # Verify identity & status control
    assert order_a_data["buyer_id"] == cons_a_id, f"Buyer ID must be forced to authenticated Consumer A ({cons_a_id}), got {order_a_data['buyer_id']}"
    assert order_a_data["status"] == "Confirmed", f"Status must be forced to 'Confirmed', got {order_a_data['status']}"
    import math
    expected_consumer_price = math.ceil(official_price * 1.50)
    assert order_a_data["items"][0]["price"] == expected_consumer_price, f"Item price must use trusted consumer price ({expected_consumer_price}), got {order_a_data['items'][0]['price']}"
    print(f"[TEST 3] Consumer A created Order #{order_a_id}: Identity derived from JWT, status=Confirmed, price=Rs.{expected_consumer_price} (Passed!)")

    # 4. Ownership Isolation: Consumer A sees Order A, Consumer B sees 0 orders
    res_orders_a = client.get("/api/orders", headers=headers_a)
    assert res_orders_a.status_code == 200
    orders_a = res_orders_a.json()
    assert any(o["id"] == order_a_id for o in orders_a), "Consumer A must see their own order"

    res_orders_b = client.get("/api/orders", headers=headers_b)
    assert res_orders_b.status_code == 200
    orders_b = res_orders_b.json()
    assert not any(o["id"] == order_a_id for o in orders_b), "Consumer B must NOT see Consumer A's order!"

    res_get_a_by_b = client.get(f"/api/orders/{order_a_id}", headers=headers_b)
    assert res_get_a_by_b.status_code == 403, "Consumer B must be rejected with 403 when requesting Consumer A's order!"
    print("[TEST 4] Ownership isolation verified: Consumer B cannot view Consumer A's orders (Passed!)")

    # 5. Tracking State 1: Order Confirmed, 0 Shipments created yet
    res_shipments_a1 = client.get("/api/shipments", headers=headers_a)
    assert res_shipments_a1.status_code == 200
    shipments_a1 = res_shipments_a1.json()
    assert len(shipments_a1) == 0, "No shipment should exist yet for Consumer A's order"
    print("[TEST 5] Initial Tracking State verified: Order Confirmed, Shipment Pending (Passed!)")

    # 6. Consumer Security Check: Consumer CANNOT create or update shipments
    res_create_ship = client.post("/api/shipments", headers=headers_a, json={
        "order_id": order_a_id,
        "batch_id": batch_id,
        "source": "Sangli Hub",
        "destination": "Consumer Home",
        "vehicle_number": "MH-12-FAKE-1234",
        "status": "In Transit"
    })
    assert res_create_ship.status_code == 403, "Consumer must NOT be able to create shipments!"

    print("[TEST 6] Security Check: Consumer rejected from creating shipments with HTTP 403 (Passed!)")

    # 7. Distributor CANNOT create Shipment for Consumer A's order
    res_dist_ship = client.post("/api/shipments", headers=headers_dist, json={
        "order_id": order_a_id,
        "batch_id": batch_id,
        "source": "Sangli Regional Hub",
        "destination": "Pune Consumer Distribution Hub",
        "vehicle_number": "MH-12-RE-8899",
        "status": "In Transit"
    })
    assert res_dist_ship.status_code == 400, "Distributor shipment creation for consumer order must fail with HTTP 400!"
    print("[TEST 7] Verified: Distributor CANNOT create shipment for Consumer order (Passed!)")

    # 8, 9, 10. Assigned Retailer updates Consumer Order status to Out for Delivery and then Delivered
    from app.models.order import Order
    db_temp = SessionLocal()
    db_ord = db_temp.query(Order).filter(Order.id == order_a_id).first()
    db_ord.retailer_id = ret_id
    db_temp.commit()
    db_temp.close()

    res_out = client.patch(f"/api/orders/{order_a_id}/status", headers=headers_ret, json={"status": "Out for Delivery"})
    assert res_out.status_code == 200, f"Out for Delivery failed ({res_out.status_code}): {res_out.text}"
    assert res_out.json()["status"] == "Out for Delivery"

    res_deliv = client.patch(f"/api/orders/{order_a_id}/status", headers=headers_ret, json={"status": "Delivered"})
    assert res_deliv.status_code == 200
    assert res_deliv.json()["status"] == "Delivered"

    # 11. Tracking State 3: Delivered
    res_order_check = client.get(f"/api/orders/{order_a_id}", headers=headers_a)
    assert res_order_check.status_code == 200
    assert res_order_check.json()["status"] == "Delivered"
    print("[TEST 8, 9, 10 & 11] Delivered Tracking State verified: Consumer Order status updated to Delivered by Retailer (Passed!)")

    # 12. Consumer QR Traceability
    res_trace_events = client.get(f"/api/traceability/batch/{batch_id}", headers=headers_a)
    assert res_trace_events.status_code == 200
    events = res_trace_events.json()
    assert len(events) >= 2, f"Should have Farmer Harvest and Dispatch & Transport events, got {len(events)}"
    
    # Chronological ordering check
    timestamps = [datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")) for e in events]
    assert timestamps == sorted(timestamps), "Traceability timeline must be strictly chronological!"
    print(f"[TEST 12] Consumer QR Traceability verified: {len(events)} chronological provenance events loaded (Passed!)")

    # 13. Consumer Security Check: Consumer CANNOT create provenance events
    res_create_event_a = client.post("/api/traceability/events", headers=headers_a, json={
        "batch_id": batch_id,
        "stage": "Retail Outlet Delivery",
        "location": "Consumer Doorstep",
        "description": "Attempted consumer manual provenance insertion."
    })
    assert res_create_event_a.status_code == 403, "Consumer must NOT be able to create provenance events!"
    print("[TEST 13] Security Check: Consumer rejected from creating provenance events with HTTP 403 (Passed!)")

    print("\n" + "=" * 70)
    print("ALL CONSUMER ORDER & TRACKING WORKFLOW TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    test_consumer_order_and_tracking_workflow()
