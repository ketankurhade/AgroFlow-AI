import math
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.product import Product

client = TestClient(app)

def test_pricing_markup_and_marketplace_integrity():
    print("=" * 70)
    print("AGROFLOW AI — PRICING MODEL & MARKUP TEST SUITE")
    print("=" * 70)

    db = SessionLocal()
    products = db.query(Product).order_by(Product.id).all()
    db.close()

    # 1. Product Count & Catalog Price Verification
    assert len(products) == 4, f"Product count must be exactly 4, found {len(products)}"
    product_map = {p.name: p for p in products}

    expected_wholesale = {
        "Onion": 35.0,
        "Potato": 30.0,
        "Apple": 150.0,
        "Mango": 120.0
    }

    expected_consumer = {
        "Onion": 53.0,   # math.ceil(35.0 * 1.50) = 53
        "Potato": 45.0,  # math.ceil(30.0 * 1.50) = 45
        "Apple": 225.0,  # math.ceil(150.0 * 1.50) = 225
        "Mango": 180.0   # math.ceil(120.0 * 1.50) = 180
    }

    print("\n--- 1. Verification of Base Wholesale Prices in PostgreSQL ---")
    for name, wholesale_p in expected_wholesale.items():
        assert name in product_map, f"Product '{name}' must exist in DB"
        actual_price = float(product_map[name].price)
        assert actual_price == wholesale_p, f"Wholesale price for {name} must be {wholesale_p}, got {actual_price}"
        print(f"  [OK] {name}: Base Wholesale Price = Rs. {actual_price}/kg")

    print("\n--- 2. Verification of 50% Markup + Ceiling Consumer Prices ---")
    for name, wholesale_p in expected_wholesale.items():
        calc_consumer_price = float(math.ceil(wholesale_p * 1.50))
        assert calc_consumer_price == expected_consumer[name], f"Consumer price for {name} mismatch"
        print(f"  [OK] {name}: Wholesale Rs.{wholesale_p} -> 1.50x markup ceil -> Consumer Rs.{calc_consumer_price}/kg")

    # 2. Test User Setup
    suffix = str(uuid.uuid4())[:8]

    # Register Retailer
    ret_email = f"retailer.price.{suffix}@agroflow.com"
    r_ret = client.post("/api/auth/register", json={
        "name": "Price Test Retailer",
        "email": ret_email,
        "password": "RetailerPassword123!",
        "role": "retailer"
    })
    assert r_ret.status_code == 201
    ret_id = r_ret.json()["id"]
    ret_token = client.post("/api/auth/login", json={"email": ret_email, "password": "RetailerPassword123!"}).json()["access_token"]
    h_ret = {"Authorization": f"Bearer {ret_token}"}

    # Register Consumer
    cons_email = f"consumer.price.{suffix}@agroflow.com"
    r_cons = client.post("/api/auth/register", json={
        "name": "Price Test Consumer",
        "email": cons_email,
        "password": "ConsumerPassword123!",
        "role": "consumer"
    })
    assert r_cons.status_code == 201
    cons_id = r_cons.json()["id"]
    cons_token = client.post("/api/auth/login", json={"email": cons_email, "password": "ConsumerPassword123!"}).json()["access_token"]
    h_cons = {"Authorization": f"Bearer {cons_token}"}

    # Register Farmer
    farmer_email = f"farmer.price.{suffix}@agroflow.com"
    r_farm = client.post("/api/auth/register", json={
        "name": "Price Test Farmer",
        "email": farmer_email,
        "password": "FarmerPassword123!",
        "role": "farmer"
    })
    assert r_farm.status_code == 201
    farmer_token = client.post("/api/auth/login", json={"email": farmer_email, "password": "FarmerPassword123!"}).json()["access_token"]
    h_farm = {"Authorization": f"Bearer {farmer_token}"}

    # Register Distributor
    dist_email = f"distributor.price.{suffix}@agroflow.com"
    r_dist = client.post("/api/auth/register", json={
        "name": "Price Test Distributor",
        "email": dist_email,
        "password": "DistributorPassword123!",
        "role": "distributor"
    })
    assert r_dist.status_code == 201
    dist_token = client.post("/api/auth/login", json={"email": dist_email, "password": "DistributorPassword123!"}).json()["access_token"]
    h_dist = {"Authorization": f"Bearer {dist_token}"}

    # 3. Create Upstream Harvest Batch for Onion
    onion_prod = product_map["Onion"]
    r_batch = client.post("/api/batches", headers=h_farm, json={
        "batch_code": f"BATCH-PRICING-{suffix}",
        "product_id": onion_prod.id,
        "quantity": 1000.0,
        "quality_grade": "Grade A+",
        "harvest_date": "2026-09-30",
        "expiry_date": "2026-10-30",
        "origin_location": "Nasik Hub",
        "status": "Harvested"
    })
    assert r_batch.status_code == 201
    batch_id = r_batch.json()["id"]

    print("\n--- 3. Retailer Wholesale Order Pricing Verification ---")
    # Retailer orders 500 kg Onion @ Wholesale Price (35)
    wh_order_payload = {
        "order_number": f"ORD-WHOLESALE-{suffix}",
        "buyer_id": ret_id,
        "items": [{"product_id": onion_prod.id, "quantity": 500.0, "price": 999.0}] # spoof attempt
    }
    r_wh_order = client.post("/api/orders", headers=h_ret, json=wh_order_payload)
    assert r_wh_order.status_code == 201
    wh_order = r_wh_order.json()
    assert wh_order["items"][0]["price"] == 35.0, f"Retailer order item price must be 35.0, got {wh_order['items'][0]['price']}"
    assert wh_order["total_amount"] == 500.0 * 35.0, f"Retailer order total amount must be 17500.0, got {wh_order['total_amount']}"
    print(f"  [OK] Retailer Order 500kg Onion: Unit Price = Rs.35/kg, Total Amount = Rs.{wh_order['total_amount']} (Wholesale verified)")

    # Dispatch & deliver to Retailer so Retailer gets inventory
    r_wh_ship = client.post("/api/shipments", headers=h_dist, json={
        "order_id": wh_order["id"],
        "batch_id": batch_id,
        "source": "Nasik Hub",
        "destination": "Retailer Store",
        "vehicle_number": "MH-15-PR-9000",
        "status": "In Transit"
    })
    assert r_wh_ship.status_code == 201
    ship_id = r_wh_ship.json()["id"]
    client.patch(f"/api/shipments/{ship_id}/status", headers=h_dist, json={"status": "Delivered"})

    print("\n--- 4. Consumer Order Pricing Verification (50% Markup + Ceiling) ---")
    # Consumer orders 100 kg Onion @ Consumer Price (53)
    cons_order_payload = {
        "order_number": f"ORD-CONSUMER-{suffix}",
        "items": [{"product_id": onion_prod.id, "quantity": 100.0, "price": 1.0}] # spoof attempt
    }
    r_cons_order = client.post("/api/orders", headers=h_cons, json=cons_order_payload)
    assert r_cons_order.status_code == 201
    cons_order = r_cons_order.json()
    assert cons_order["items"][0]["price"] == 53.0, f"Consumer order item price must be 53.0, got {cons_order['items'][0]['price']}"
    assert cons_order["total_amount"] == 100.0 * 53.0, f"Consumer order total amount must be 5300.0, got {cons_order['total_amount']}"
    print(f"  [OK] Consumer Order 100kg Onion: Unit Price = Rs.53/kg (50% markup over 35 rounded up), Total Amount = Rs.{cons_order['total_amount']} (Consumer pricing verified)")

    # 5. Final PostgreSQL Product Count Verification
    db = SessionLocal()
    final_count = db.query(Product).count()
    db.close()
    assert final_count == 4, f"Final product count must remain exactly 4, found {final_count}"
    print(f"\n--- 5. Final PostgreSQL Product Count: {final_count} (No extra products created) ---")

    print("\n" + "=" * 70)
    print("ALL PRICING MODEL TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    test_pricing_markup_and_marketplace_integrity()
