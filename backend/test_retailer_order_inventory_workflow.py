import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.product import Product
from app.models.user import User

client = TestClient(app)

def test_retailer_order_inventory_workflow():
    print("=" * 70)
    print("AGROFLOW AI — ISSUE #4: RETAILER ORDER + INVENTORY WORKFLOW TEST SUITE")
    print("=" * 70)

    unique_suffix = str(uuid.uuid4())[:8]

    # Setup Product in DB using canonical product
    db = SessionLocal()

    from app.models.shipment import Shipment
    from app.models.order import Order, OrderItem
    from app.models.inventory import Inventory
    from app.models.traceability import TraceabilityEvent
    from app.models.batch import Batch

    db.query(Shipment).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Inventory).delete()
    db.query(TraceabilityEvent).delete()
    db.query(Batch).delete()
    db.commit()

    product = db.query(Product).filter(Product.name == "Onion").first() or db.query(Product).first()
    assert product is not None, "Canonical product 'Onion' must exist in database"
    product_id = product.id
    official_price = product.price if hasattr(product, 'price') and product.price else 35.0
    db.close()

    # 1. Setup Users (Retailer A, Retailer B, Farmer, Distributor)
    # Retailer A
    ret_a_email = f"retailer.a.{unique_suffix}@agroflow.com"
    ret_a_pwd = "RetailerAPass123!"
    reg_a = client.post("/api/auth/register", json={
        "name": "FreshMart Retailer A",
        "email": ret_a_email,
        "password": ret_a_pwd,
        "role": "retailer"
    })
    assert reg_a.status_code == 201
    ret_a_id = reg_a.json()["id"]
    token_a = client.post("/api/auth/login", json={"email": ret_a_email, "password": ret_a_pwd}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Retailer B
    ret_b_email = f"retailer.b.{unique_suffix}@agroflow.com"
    ret_b_pwd = "RetailerBPass123!"
    reg_b = client.post("/api/auth/register", json={
        "name": "Organic Retailer B",
        "email": ret_b_email,
        "password": ret_b_pwd,
        "role": "retailer"
    })
    assert reg_b.status_code == 201
    ret_b_id = reg_b.json()["id"]
    token_b = client.post("/api/auth/login", json={"email": ret_b_email, "password": ret_b_pwd}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Farmer
    farmer_email = f"farmer.ret.{unique_suffix}@agroflow.com"
    farmer_pwd = "FarmerPass123!"
    reg_farmer = client.post("/api/auth/register", json={
        "name": "Produce Farmer",
        "email": farmer_email,
        "password": farmer_pwd,
        "role": "farmer"
    })
    assert reg_farmer.status_code == 201
    token_farmer = client.post("/api/auth/login", json={"email": farmer_email, "password": farmer_pwd}).json()["access_token"]
    headers_farmer = {"Authorization": f"Bearer {token_farmer}"}

    # Distributor
    dist_email = f"distributor.ret.{unique_suffix}@agroflow.com"
    dist_pwd = "DistributorPass123!"
    reg_dist = client.post("/api/auth/register", json={
        "name": "Cold Fleet Distributor",
        "email": dist_email,
        "password": dist_pwd,
        "role": "distributor"
    })
    assert reg_dist.status_code == 201
    token_dist = client.post("/api/auth/login", json={"email": dist_email, "password": dist_pwd}).json()["access_token"]
    headers_dist = {"Authorization": f"Bearer {token_dist}"}

    print("[TEST 1] Registered Retailer A, Retailer B, Farmer, Distributor (Passed!)")

    # 2. Farmer creates Batch with 200 kg initial inventory
    batch_code = f"BATCH-RET-{unique_suffix}"
    res_batch = client.post("/api/batches", headers=headers_farmer, json={
        "batch_code": batch_code,
        "product_id": product_id,
        "quantity": 200.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-29",
        "expiry_date": "2026-10-25",
        "origin_location": "Nashik Organic Farm Hub",
        "status": "Harvested"
    })
    assert res_batch.status_code == 201
    batch_id = res_batch.json()["id"]
    print(f"[TEST 2] Farmer created Batch #{batch_id} (Code: {batch_code}, Qty: 200 kg) (Passed!)")

    # 3. Test Invalid Quantity <= 0 (Rejected with 400 Bad Request)
    res_zero = client.post("/api/orders", headers=headers_a, json={
        "order_number": f"ORD-ZERO-{unique_suffix}",
        "buyer_id": ret_a_id,
        "items": [{"product_id": product_id, "quantity": 0.0, "price": 45.0}]
    })
    assert res_zero.status_code == 400, f"Quantity <= 0 must return 400! Got: {res_zero.status_code}"

    res_neg = client.post("/api/orders", headers=headers_a, json={
        "order_number": f"ORD-NEG-{unique_suffix}",
        "buyer_id": ret_a_id,
        "items": [{"product_id": product_id, "quantity": -50.0, "price": 45.0}]
    })
    assert res_neg.status_code == 400, f"Negative quantity must return 400! Got: {res_neg.status_code}"
    print("[TEST 3] Zero and negative purchase quantities rejected with 400 Bad Request (Passed!)")

    # 4. Test Insufficient Stock Rejection (> 200 kg)
    res_exceed = client.post("/api/orders", headers=headers_a, json={
        "order_number": f"ORD-EXCEED-{unique_suffix}",
        "buyer_id": ret_a_id,
        "items": [{"product_id": product_id, "quantity": 500.0, "price": 45.0}]
    })
    assert res_exceed.status_code == 400, f"Quantity exceeding stock must return 400! Got: {res_exceed.status_code}"
    print("[TEST 4] Insufficient inventory stock rejected with 400 Bad Request (Passed!)")

    # 5. Authenticated Retailer Identity & Security Checks: Retailer A trying to submit Retailer B's buyer_id
    res_impersonate = client.post("/api/orders", headers=headers_a, json={
        "order_number": f"ORD-IMP-{unique_suffix}",
        "buyer_id": ret_b_id,  # Attempts to impersonate Retailer B
        "items": [{"product_id": product_id, "quantity": 30.0, "price": 45.0}]
    })
    assert res_impersonate.status_code == 201
    # Backend must FORCE buyer_id = ret_a_id
    order_imp_data = res_impersonate.json()
    assert order_imp_data["buyer_id"] == ret_a_id, f"Buyer ID must be forced to authenticated Retailer A ({ret_a_id}), but was {order_imp_data['buyer_id']}"
    print("[TEST 5] Authenticated identity enforced: Buyer ID forced to JWT user (Passed!)")

    # 6. Price Control & Initial Status Control Test
    res_manipulated = client.post("/api/orders", headers=headers_a, json={
        "order_number": f"ORD-MANIP-{unique_suffix}",
        "buyer_id": ret_a_id,
        "status": "Delivered",  # Attempted status override
        "items": [{"product_id": product_id, "quantity": 20.0, "price": 1.0}]  # Attempted 1.0 Rs price manipulation
    })
    assert res_manipulated.status_code == 201
    order_m_data = res_manipulated.json()
    assert order_m_data["status"] == "Confirmed", f"Retailer status must be forced to 'Confirmed', got '{order_m_data['status']}'"
    item_price = order_m_data["items"][0]["price"]
    assert item_price == official_price, f"Product price must be trusted catalog price ({official_price}), got {item_price}"
    expected_amount = 20.0 * official_price
    assert order_m_data["total_amount"] == expected_amount, f"Total amount must be calculated from trusted price ({expected_amount}), got {order_m_data['total_amount']}"
    print(f"[TEST 6] Price & Status control verified: trusted unit price Rs.{official_price}/kg, status forced to Confirmed (Passed!)")

    # 7. Inventory Accounting & Atomicity Verification (200 - 30 - 20 = 150 kg remaining)
    res_batch_check = client.get(f"/api/batches/{batch_id}", headers=headers_farmer)
    assert res_batch_check.status_code == 200
    current_batch_qty = res_batch_check.json()["quantity"]
    assert current_batch_qty == 150.0, f"Stock should be exactly 150 kg after purchases (200 - 30 - 20), got {current_batch_qty}"
    print(f"[TEST 7] Inventory accounting verified: Batch stock deducted cleanly to {current_batch_qty} kg (Passed!)")

    # 8. Ownership Isolation: Retailer A sees only their own orders, Retailer B sees 0 orders
    res_orders_a = client.get("/api/orders", headers=headers_a)
    assert res_orders_a.status_code == 200
    orders_a = res_orders_a.json()
    assert all(o["buyer_id"] == ret_a_id for o in orders_a), "Retailer A must only see their own orders!"

    res_orders_b = client.get("/api/orders", headers=headers_b)
    assert res_orders_b.status_code == 200
    orders_b = res_orders_b.json()
    assert len(orders_b) == 0, f"Retailer B should see 0 orders, got {len(orders_b)}"
    print("[TEST 8] Retailer order ownership isolation verified (Passed!)")

    # 9. Distributor Fulfillment Compatibility (Issue #1 workflow compatibility check)
    target_order_id = order_m_data["id"]
    res_shipment = client.post("/api/shipments", headers=headers_dist, json={
        "order_id": target_order_id,
        "batch_id": batch_id,
        "source": "Nashik Farm Hub",
        "destination": "FreshMart Hub",
        "vehicle_number": "MH-15-AB-1234",
        "status": "In Transit"
    })
    assert res_shipment.status_code == 201, f"Distributor fulfillment failed for Retailer Order: {res_shipment.text}"
    shipment_data = res_shipment.json()
    assert shipment_data["order_id"] == target_order_id
    assert shipment_data["status"] == "In Transit"

    # Check order status transitioned to In Transit
    res_check_order = client.get(f"/api/orders/{target_order_id}", headers=headers_a)
    assert res_check_order.status_code == 200
    assert res_check_order.json()["status"] == "In Transit"
    print(f"[TEST 9] Distributor fulfillment compatibility verified: Shipment #{shipment_data['id']} created and order status updated to 'In Transit' (Passed!)")

    print("=" * 70)
    print("ALL ISSUE #4 RETAILER ORDER + INVENTORY WORKFLOW TESTS PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_retailer_order_inventory_workflow()
