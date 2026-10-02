import os
import sys
import uuid
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)


def test_farmer_order_ownership_matrix():
    print("=" * 80)
    print("AGROFLOW AI — FARMER ORDER OWNERSHIP & VISIBILITY TEST SUITE")
    print("=" * 80)

    unique_id = str(uuid.uuid4())[:8]

    # 1. AUTHENTICATE ADMIN
    print("\n--- Step 1: Admin Authentication & Initial Global Orders Check ---")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@agroflow.com")
    admin_pwd = os.getenv("ADMIN_PASSWORD", "Admin@AgroFlow2026!")
    r_admin_login = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd})
    assert r_admin_login.status_code == 200, f"Admin login failed: {r_admin_login.text}"
    admin_token = r_admin_login.json()["access_token"]
    admin_h = {"Authorization": f"Bearer {admin_token}"}

    r_admin_orders = client.get("/api/orders", headers=admin_h)
    assert r_admin_orders.status_code == 200, f"Admin get orders failed: {r_admin_orders.text}"
    initial_admin_orders = r_admin_orders.json()
    print(f"  [OK] Admin sees all initial global orders (Count: {len(initial_admin_orders)}).")

    # 2. REGISTER & LOGIN FARMER A (NEW FARMER WITH NO ACTIVITY)
    print("\n--- Step 2: Register & Verify Brand-New Farmer A (0 Batches/Shipments/Orders) ---")
    farmer_a_email = f"farmer.a.{unique_id}@agroflow.com"
    pwd = "Password123!farmer"
    r_reg_a = client.post("/api/auth/register", json={
        "name": "Farmer Alice",
        "email": farmer_a_email,
        "password": pwd,
        "role": "farmer"
    })
    assert r_reg_a.status_code == 201, f"Failed to register Farmer A: {r_reg_a.text}"
    r_login_a = client.post("/api/auth/login", json={"email": farmer_a_email, "password": pwd})
    assert r_login_a.status_code == 200, f"Failed to login Farmer A: {r_login_a.text}"
    token_a = r_login_a.json()["access_token"]
    farmer_a_id = r_login_a.json()["user"]["id"]
    h_farmer_a = {"Authorization": f"Bearer {token_a}"}

    r_orders_a = client.get("/api/orders", headers=h_farmer_a)
    assert r_orders_a.status_code == 200, f"Farmer A GET /api/orders failed: {r_orders_a.text}"
    orders_a = r_orders_a.json()
    assert len(orders_a) == 0, f"Expected 0 orders for brand-new Farmer A, got {len(orders_a)}"
    print("  [OK] Farmer A receives 0 orders (No global seeded buyer orders returned).")

    # 3. REGISTER & LOGIN FARMER B (FARMER WITH PRODUCE BUT NO SHIPMENT YET)
    print("\n--- Step 3: Register Farmer B & Create Harvest Batch (No Shipment Yet) ---")
    farmer_b_email = f"farmer.b.{unique_id}@agroflow.com"
    r_reg_b = client.post("/api/auth/register", json={
        "name": "Farmer Bob",
        "email": farmer_b_email,
        "password": pwd,
        "role": "farmer"
    })
    assert r_reg_b.status_code == 201, f"Failed to register Farmer B: {r_reg_b.text}"
    r_login_b = client.post("/api/auth/login", json={"email": farmer_b_email, "password": pwd})
    assert r_login_b.status_code == 200, f"Failed to login Farmer B: {r_login_b.text}"
    token_b = r_login_b.json()["access_token"]
    farmer_b_id = r_login_b.json()["user"]["id"]
    h_farmer_b = {"Authorization": f"Bearer {token_b}"}

    # Farmer B creates a batch
    batch_b_code = f"BATCH-FB-{unique_id}"
    r_create_batch = client.post("/api/batches", json={
        "batch_code": batch_b_code,
        "product_id": 1,
        "farmer_id": farmer_b_id,
        "quantity": 500.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-29",
        "expiry_date": "2026-10-29",
        "origin_location": "Nashik Farm B",
        "status": "Harvested"
    }, headers=h_farmer_b)
    assert r_create_batch.status_code == 201, f"Farmer B batch creation failed: {r_create_batch.text}"
    batch_b_id = r_create_batch.json()["id"]
    print(f"  [OK] Farmer B created harvest Batch ID: {batch_b_id}")

    # Farmer B orders count before shipment link
    r_orders_b_preshipment = client.get("/api/orders", headers=h_farmer_b)
    assert r_orders_b_preshipment.status_code == 200
    assert len(r_orders_b_preshipment.json()) == 0, f"Farmer B should have 0 orders before shipment linking, got {len(r_orders_b_preshipment.json())}"
    print("  [OK] Farmer B receives 0 orders before shipment connection (Unrelated crop orders not shown).")

    # 4. CREATE AN ORDER AND CONNECT TO FARMER B'S BATCH VIA SHIPMENT
    print("\n--- Step 4: Create Order X and Shipment S (Order -> Shipment -> Batch B -> Farmer B) ---")
    order_x_number = f"ORD-FB-{unique_id}"
    r_create_order = client.post("/api/orders", json={
        "order_number": order_x_number,
        "buyer_id": 1, # Admin or retail buyer
        "status": "Confirmed",
        "items": [{"product_id": 1, "quantity": 100.0, "price": 40.0}]
    }, headers=admin_h)
    assert r_create_order.status_code == 201, f"Order X creation failed: {r_create_order.text}"
    order_x_id = r_create_order.json()["id"]

    r_create_shipment = client.post("/api/shipments", json={
        "order_id": order_x_id,
        "batch_id": batch_b_id,
        "source": "Nashik Farm B",
        "destination": "Mumbai Wholesale Market",
        "vehicle_number": "MH-15-FB-9999",
        "status": "In Transit"
    }, headers=admin_h)
    assert r_create_shipment.status_code == 201, f"Shipment creation failed: {r_create_shipment.text}"
    print(f"  [OK] Created Order X (ID: {order_x_id}) and linked to Batch B (ID: {batch_b_id}) via Shipment.")

    # 5. VERIFY FARMER B SEES ORDER X
    print("\n--- Step 5: Verify Farmer B Visibility ---")
    r_orders_b = client.get("/api/orders", headers=h_farmer_b)
    assert r_orders_b.status_code == 200
    orders_b = r_orders_b.json()
    assert len(orders_b) == 1, f"Farmer B should see exactly 1 order, got {len(orders_b)}"
    assert orders_b[0]["id"] == order_x_id, f"Farmer B should see Order X (ID {order_x_id}), got {orders_b[0]['id']}"
    print(f"  [OK] Farmer B successfully sees relevant produce Order X (Order #{order_x_number}).")

    # 6. VERIFY CROSS-FARMER ISOLATION (FARMER A MUST NOT SEE FARMER B'S ORDER)
    print("\n--- Step 6: Verify Cross-Farmer Isolation (Farmer A vs Farmer B) ---")
    r_orders_a_post = client.get("/api/orders", headers=h_farmer_a)
    assert r_orders_a_post.status_code == 200
    orders_a_post = r_orders_a_post.json()
    assert len(orders_a_post) == 0, f"Farmer A must still see 0 orders, got {len(orders_a_post)}"
    print("  [OK] Farmer A strictly does NOT see Farmer B's order.")

    # 7. DIRECT ORDER ACCESS CONTROLS (GET /api/orders/{id})
    print("\n--- Step 7: Direct Order Access Controls (GET /api/orders/{id}) ---")
    r_get_single_b = client.get(f"/api/orders/{order_x_id}", headers=h_farmer_b)
    assert r_get_single_b.status_code == 200
    assert r_get_single_b.json()["id"] == order_x_id
    print("  [OK] Farmer B can access their own order details.")

    r_get_single_a = client.get(f"/api/orders/{order_x_id}", headers=h_farmer_a)
    assert r_get_single_a.status_code == 403, f"Farmer A should be forbidden from accessing Order X, got {r_get_single_a.status_code}"
    print("  [OK] Farmer A direct access to Order X returns HTTP 403 Forbidden.")

    # 8. QUERY PARAMETER MANIPULATION CHECK
    print("\n--- Step 8: Query Parameter Manipulation Protection ---")
    r_tamper = client.get(f"/api/orders?farmer_id={farmer_b_id}&user_id={farmer_b_id}&buyer_id={farmer_b_id}", headers=h_farmer_a)
    assert r_tamper.status_code == 200
    assert len(r_tamper.json()) == 0, "Query parameter tampering attempt failed to bypass ownership check."
    print("  [OK] Farmer A attempting query parameter manipulation still receives 0 orders.")

    # 9. ADMIN UNFILTERED ACCESS VERIFICATION
    print("\n--- Step 9: Verify Admin Unfiltered Visibility ---")
    r_admin_final = client.get("/api/orders", headers=admin_h)
    assert r_admin_final.status_code == 200
    admin_orders_final = r_admin_final.json()
    assert len(admin_orders_final) == len(initial_admin_orders) + 1, "Admin should see all orders including newly created Order X."
    print(f"  [OK] Admin sees all orders (Total: {len(admin_orders_final)}).")

    print("\n" + "=" * 80)
    print("ALL FARMER ORDER OWNERSHIP & VISIBILITY TESTS PASSED 100%!")
    print("=" * 80)


if __name__ == "__main__":
    test_farmer_order_ownership_matrix()
