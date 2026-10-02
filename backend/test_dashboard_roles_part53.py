import os
import sys
import uuid
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)


def run_part53_dashboard_roles_suite():
    print("=" * 80)
    print("AGROFLOW AI — PART 5.3 ROLE-SPECIFIC DASHBOARDS & UI TEST SUITE")
    print("=" * 80)

    unique_id = str(uuid.uuid4())[:8]

    roles = ["admin", "farmer", "supply_chain_manager", "distributor", "retailer", "consumer"]
    tokens = {}
    users = {}

    # 1. AUTHENTICATION / REGISTRATION OF ALL 6 ROLES
    print("\n--- Step 1: Role Authentication & Token Setup ---")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@agroflow.com")
    admin_pwd = os.getenv("ADMIN_PASSWORD", "Admin@AgroFlow2026!")
    r_admin = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd})
    assert r_admin.status_code == 200, f"Admin login failed: {r_admin.text}"
    tokens["admin"] = r_admin.json()["access_token"]
    users["admin"] = r_admin.json()["user"]
    print("  [OK] Role 'admin' authenticated.")

    for r in ["farmer", "supply_chain_manager", "distributor", "retailer", "consumer"]:
        email = f"{r}.part53.{unique_id}@agroflow.com"
        pwd = f"Password123!{r}"
        reg_res = client.post("/api/auth/register", json={
            "name": f"Part53 {r.capitalize()}",
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

    # 2. ADMIN DASHBOARD ENDPOINTS
    print("\n--- Step 2: Admin Dashboard API Access ---")
    h_admin = headers["admin"]
    assert client.get("/api/inventory", headers=h_admin).status_code == 200
    assert client.get("/api/batches", headers=h_admin).status_code == 200
    assert client.get("/api/orders", headers=h_admin).status_code == 200
    assert client.get("/api/shipments", headers=h_admin).status_code == 200
    assert client.get("/api/spoilage/summary", headers=h_admin).status_code == 200
    assert client.get("/api/demand/forecast", headers=h_admin).status_code == 200
    assert client.get("/api/price/forecast", headers=h_admin).status_code == 200
    print("  [OK] Admin Dashboard APIs functioning 100%.")

    # 3. FARMER DASHBOARD ENDPOINTS
    print("\n--- Step 3: Farmer Dashboard API Access ---")
    h_farmer = headers["farmer"]
    assert client.get("/api/batches", headers=h_farmer).status_code == 200
    assert client.get("/api/inventory", headers=h_farmer).status_code == 200
    assert client.get("/api/orders", headers=h_farmer).status_code == 200
    assert client.get("/api/spoilage/risk", headers=h_farmer).status_code == 200
    assert client.get("/api/demand/forecast", headers=h_farmer).status_code == 200
    assert client.get("/api/price/forecast", headers=h_farmer).status_code == 200
    print("  [OK] Farmer Dashboard APIs functioning 100%.")

    # 4. SUPPLY CHAIN MANAGER DASHBOARD ENDPOINTS
    print("\n--- Step 4: Supply Chain Manager Dashboard API Access ---")
    h_scm = headers["supply_chain_manager"]
    assert client.get("/api/batches", headers=h_scm).status_code == 200
    assert client.get("/api/inventory", headers=h_scm).status_code == 200
    assert client.get("/api/orders", headers=h_scm).status_code == 200
    assert client.get("/api/shipments", headers=h_scm).status_code == 200
    assert client.get("/api/spoilage/risk", headers=h_scm).status_code == 200
    assert client.get("/api/demand/forecast", headers=h_scm).status_code == 200
    assert client.get("/api/price/forecast", headers=h_scm).status_code == 200
    print("  [OK] Supply Chain Manager Dashboard APIs functioning 100%.")

    # 6. DISTRIBUTOR DASHBOARD ENDPOINTS
    print("\n--- Step 6: Distributor Dashboard API Access ---")
    h_dist = headers["distributor"]
    assert client.get("/api/orders", headers=h_dist).status_code == 200
    assert client.get("/api/shipments", headers=h_dist).status_code == 200
    assert client.get("/api/inventory", headers=h_dist).status_code == 200
    assert client.get("/api/routes/locations", headers=h_dist).status_code == 200
    print("  [OK] Distributor Dashboard APIs functioning 100%.")

    # 7. RETAILER DASHBOARD ENDPOINTS
    print("\n--- Step 7: Retailer Dashboard API Access ---")
    h_ret = headers["retailer"]
    assert client.get("/api/orders", headers=h_ret).status_code == 200
    assert client.get("/api/inventory", headers=h_ret).status_code == 200
    assert client.get("/api/products", headers=h_ret).status_code == 200
    assert client.get("/api/shipments", headers=h_ret).status_code == 200
    print("  [OK] Retailer Dashboard APIs functioning 100%.")

    # 8. CONSUMER DASHBOARD ENDPOINTS & API SAFETY
    print("\n--- Step 8: Consumer Dashboard API Access & Security Boundaries ---")
    h_cons = headers["consumer"]
    assert client.get("/api/products", headers=h_cons).status_code == 200
    assert client.get("/api/orders", headers=h_cons).status_code == 200
    print("  [OK] Consumer Dashboard permitted APIs (products, orders) accessible.")

    # Verify Consumer strictly cannot hit internal operational endpoints (Must return 403)
    assert client.get("/api/spoilage/risk", headers=h_cons).status_code == 403
    assert client.get("/api/historical-data/summary", headers=h_cons).status_code == 403
    assert client.post("/api/routes/optimize", json={"stops": [{"name": "Pune"}, {"name": "Mumbai"}]}, headers=h_cons).status_code == 403
    assert client.post("/api/demand/predict", json={"product_id": 1}, headers=h_cons).status_code in [403, 422]
    print("  [OK] Consumer is strictly blocked (HTTP 403) from internal operational analytics.")

    # 9. UNAUTHENTICATED REQUEST BLOCK
    print("\n--- Step 9: Unauthenticated Request Boundary ---")
    assert client.get("/api/inventory").status_code == 401
    assert client.get("/api/orders").status_code == 401
    print("  [OK] Unauthenticated requests strictly return HTTP 401 Unauthorized.")

    print("\n" + "=" * 80)
    print("ALL PART 5.3 DASHBOARD ROLE TESTS PASSED 100%!")
    print("=" * 80)


if __name__ == "__main__":
    run_part53_dashboard_roles_suite()
