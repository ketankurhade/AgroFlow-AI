import os
import sys
import uuid
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)


def run_rbac_test_matrix():
    print("=" * 80)
    print("AGROFLOW AI — PART 5.2 ROLE-BASED ACCESS CONTROL (RBAC) TEST SUITE")
    print("=" * 80)

    unique_id = str(uuid.uuid4())[:8]

    # Roles to setup and test
    roles = ["admin", "farmer", "supply_chain_manager", "distributor", "retailer", "consumer"]
    tokens = {}
    users = {}

    # 1. AUTHENTICATE / REGISTER ALL ROLES
    print("\n--- Phase 1: Authentication & User Tokens ---")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@agroflow.com")
    admin_pwd = os.getenv("ADMIN_PASSWORD", "Admin@AgroFlow2026!")
    r_admin = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd})
    assert r_admin.status_code == 200, f"Admin login failed: {r_admin.text}"
    tokens["admin"] = r_admin.json()["access_token"]
    users["admin"] = r_admin.json()["user"]
    print("  [OK] Admin authenticated cleanly.")

    for r in ["farmer", "supply_chain_manager", "distributor", "retailer", "consumer"]:
        email = f"{r}.rbac.{unique_id}@agroflow.com"
        pwd = f"Password123!{r}"
        reg_res = client.post("/api/auth/register", json={
            "name": f"Test {r.capitalize()}",
            "email": email,
            "password": pwd,
            "role": r
        })
        assert reg_res.status_code == 201, f"Failed to register role {r}: {reg_res.text}"
        login_res = client.post("/api/auth/login", json={"email": email, "password": pwd})
        assert login_res.status_code == 200, f"Failed to login role {r}: {login_res.text}"
        tokens[r] = login_res.json()["access_token"]
        users[r] = login_res.json()["user"]
        print(f"  [OK] Role '{r}' registered & authenticated (User ID: {users[r]['id']}).")

    headers = {r: {"Authorization": f"Bearer {tokens[r]}"} for r in roles}

    # 2. TEST ADMIN PERMISSIONS
    print("\n--- Phase 2: ADMIN Role Permissions (Full Access) ---")
    admin_h = headers["admin"]
    assert client.get("/api/products", headers=admin_h).status_code == 200
    assert client.get("/api/batches", headers=admin_h).status_code == 200
    assert client.get("/api/inventory", headers=admin_h).status_code == 200
    assert client.get("/api/orders", headers=admin_h).status_code == 200
    assert client.get("/api/shipments", headers=admin_h).status_code == 200
    assert client.get("/api/routes/locations", headers=admin_h).status_code == 200
    assert client.get("/api/spoilage/risk", headers=admin_h).status_code == 200
    assert client.get("/api/demand/forecast", headers=admin_h).status_code == 200
    assert client.get("/api/price/forecast", headers=admin_h).status_code == 200
    assert client.get("/api/historical-data/summary", headers=admin_h).status_code == 200
    print("  [OK] Admin has 100% verified access across all core routes.")

    # 3. TEST FARMER PERMISSIONS
    print("\n--- Phase 3: FARMER Role Permissions ---")
    farmer_h = headers["farmer"]
    assert client.get("/api/batches", headers=farmer_h).status_code == 200
    assert client.get("/api/inventory", headers=farmer_h).status_code == 200
    assert client.get("/api/orders", headers=farmer_h).status_code == 200
    assert client.get("/api/demand/forecast", headers=farmer_h).status_code == 200
    assert client.get("/api/spoilage/risk", headers=farmer_h).status_code == 200
    # Forbidden for farmer:
    assert client.get("/api/routes/locations", headers=farmer_h).status_code == 403
    assert client.post("/api/routes/optimize", json={"stops": [{"name": "Pune"}, {"name": "Mumbai"}]}, headers=farmer_h).status_code == 403
    print("  [OK] Farmer access verified (batches/inventory/forecasts allowed; routes forbidden).")

    # 4. TEST SUPPLY CHAIN MANAGER PERMISSIONS (COMBINED COLLECTION CENTER + WAREHOUSE)
    print("\n--- Phase 4: SUPPLY_CHAIN_MANAGER Role Permissions ---")
    scm_h = headers["supply_chain_manager"]
    assert client.get("/api/batches", headers=scm_h).status_code == 200
    assert client.get("/api/inventory", headers=scm_h).status_code == 200
    assert client.get("/api/shipments", headers=scm_h).status_code == 200
    assert client.get("/api/routes/locations", headers=scm_h).status_code == 200
    assert client.get("/api/spoilage/risk", headers=scm_h).status_code == 200
    assert client.get("/api/demand/forecast", headers=scm_h).status_code == 200
    print("  [OK] Supply Chain Manager access verified (batches/inventory/shipments/routes/forecasts allowed).")

    # 6. TEST DISTRIBUTOR PERMISSIONS
    print("\n--- Phase 6: DISTRIBUTOR Role Permissions ---")
    dist_h = headers["distributor"]
    assert client.get("/api/orders", headers=dist_h).status_code == 200
    assert client.get("/api/shipments", headers=dist_h).status_code == 200
    assert client.get("/api/routes/locations", headers=dist_h).status_code == 200
    assert client.get("/api/inventory", headers=dist_h).status_code == 200
    print("  [OK] Distributor access verified (orders/shipments/routes allowed).")

    # 7. TEST RETAILER PERMISSIONS
    print("\n--- Phase 7: RETAILER Role Permissions ---")
    ret_h = headers["retailer"]
    assert client.get("/api/products", headers=ret_h).status_code == 200
    assert client.get("/api/orders", headers=ret_h).status_code == 200
    assert client.get("/api/inventory", headers=ret_h).status_code == 200
    assert client.get("/api/demand/forecast", headers=ret_h).status_code == 200
    assert client.get("/api/routes/locations", headers=ret_h).status_code == 403
    print("  [OK] Retailer access verified (marketplace/orders allowed; routes forbidden).")

    # 8. TEST CONSUMER PERMISSIONS & STRICT RESTRICTIONS
    print("\n--- Phase 8: CONSUMER Role Permissions & Restrictions ---")
    cons_h = headers["consumer"]
    assert client.get("/api/products", headers=cons_h).status_code == 200
    assert client.get("/api/orders", headers=cons_h).status_code == 200
    # Traceability public batch read
    assert client.get("/api/traceability/batch/1", headers=cons_h).status_code in [200, 404]

    # Strictly forbidden operations for consumer
    print("  Testing Consumer Forbidden Endpoints (Must Return HTTP 403):")
    res_b = client.post("/api/batches", json={"batch_code": f"C-TEST-{unique_id}", "product_id": 1, "farmer_id": 1, "quantity": 100, "quality_grade": "Grade A", "harvest_date": "2026-09-28", "expiry_date": "2026-10-28", "origin_location": "Farm", "status": "Harvested"}, headers=cons_h)
    assert res_b.status_code == 403, f"Consumer POST batch expected 403, got {res_b.status_code}"
    print("    - POST /api/batches -> 403 Forbidden")

    res_i = client.post("/api/inventory", json={"batch_id": 1, "warehouse_location": "WH", "quantity": 50}, headers=cons_h)
    assert res_i.status_code == 403, f"Consumer POST inventory expected 403, got {res_i.status_code}"
    print("    - POST /api/inventory -> 403 Forbidden")

    res_r = client.post("/api/routes/optimize", json={"stops": [{"name": "Pune"}, {"name": "Mumbai"}]}, headers=cons_h)
    assert res_r.status_code == 403, f"Consumer POST routes expected 403, got {res_r.status_code}"
    print("    - POST /api/routes/optimize -> 403 Forbidden")

    res_d = client.post("/api/demand/predict", json={"product_id": 1, "storage_condition": "Cold", "inventory_level_kg": 500, "temperature_c": 18.0, "humidity_pct": 65.0, "price_per_kg": 40.0, "is_weekend": 0, "seasonality_index": 1.0}, headers=cons_h)
    assert res_d.status_code == 403, f"Consumer POST demand predict expected 403, got {res_d.status_code}"
    print("    - POST /api/demand/predict -> 403 Forbidden")

    res_sp = client.get("/api/spoilage/risk", headers=cons_h)
    assert res_sp.status_code == 403, f"Consumer GET spoilage risk expected 403, got {res_sp.status_code}"
    print("    - GET /api/spoilage/risk -> 403 Forbidden")

    res_h = client.get("/api/historical-data/summary", headers=cons_h)
    assert res_h.status_code == 403, f"Consumer GET historical summary expected 403, got {res_h.status_code}"
    print("    - GET /api/historical-data/summary -> 403 Forbidden")

    # 9. RESOURCE OWNERSHIP CHECKS
    print("\n--- Phase 9: Resource Ownership Checks ---")
    farmer_id = users["farmer"]["id"]
    # Farmer creating batch for another farmer ID should fail with 403
    bad_batch = {
        "batch_code": f"B-BAD-OWNER-{unique_id}",
        "product_id": 1,
        "farmer_id": farmer_id + 999,  # different farmer ID
        "quantity": 100,
        "quality_grade": "Grade A",
        "harvest_date": "2026-09-28",
        "expiry_date": "2026-10-28",
        "origin_location": "Farm",
        "status": "Harvested"
    }
    r_bad_owner = client.post("/api/batches", json=bad_batch, headers=headers["farmer"])
    assert r_bad_owner.status_code == 403, f"Farmer creating batch for another farmer should return 403, got {r_bad_owner.status_code}"
    print("  [OK] Farmer creating batch for another farmer strictly rejected (HTTP 403).")

    # Consumer placing order for another buyer ID should fail with 403
    bad_order = {
        "order_number": f"ORD-BAD-BUYER-{unique_id}",
        "buyer_id": farmer_id, # trying to place order as farmer
        "status": "Confirmed",
        "items": [{"product_id": 1, "quantity": 10, "price": 50.0}]
    }
    r_bad_buyer = client.post("/api/orders", json=bad_order, headers=headers["consumer"])
    if r_bad_buyer.status_code == 201:
        assert r_bad_buyer.json()["buyer_id"] == users["consumer"]["id"]
    else:
        assert r_bad_buyer.status_code == 403
    print("  [OK] Consumer buyer identity control verified (forced to authenticated user).")

    print("\n" + "=" * 80)
    print("ALL PART 5.2 ROLE-BASED ACCESS CONTROL (RBAC) TESTS PASSED 100%!")
    print("=" * 80)


if __name__ == "__main__":
    run_rbac_test_matrix()
