from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_full_suite():
    print("--- 1. Health Check ---")
    r = client.get("/api/health")
    assert r.status_code == 200
    print("Health OK:", r.json())

    import os
    admin_email = os.getenv("ADMIN_EMAIL", "admin@agroflow.com")
    admin_pwd = os.getenv("ADMIN_PASSWORD", "Admin@AgroFlow2026!")
    r = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login OK, Token received:", token[:20] + "...")

    print("\n--- 3. Products API ---")
    r = client.get("/api/products", headers=headers)
    assert r.status_code == 200
    print(f"Products count: {len(r.json())}")

    print("\n--- 4. Batches API ---")
    r = client.get("/api/batches", headers=headers)
    assert r.status_code == 200
    print(f"Batches count: {len(r.json())}")

    print("\n--- 5. Inventory API ---")
    r = client.get("/api/inventory", headers=headers)
    assert r.status_code == 200
    print(f"Inventory count: {len(r.json())}")

    print("\n--- 6. Orders API ---")
    r = client.get("/api/orders", headers=headers)
    assert r.status_code == 200
    print(f"Orders count: {len(r.json())}")

    print("\n--- 7. Shipments API ---")
    r = client.get("/api/shipments", headers=headers)
    assert r.status_code == 200
    print(f"Shipments count: {len(r.json())}")

    print("\n--- 8. Supported Route Locations ---")
    r = client.get("/api/routes/locations", headers=headers)
    assert r.status_code == 200
    print(f"Supported locations count: {len(r.json())}")

    print("\n--- 9. Route Optimization API ---")
    payload = {
        "stops": [
            {"name": "Ratnagiri"},
            {"name": "Pune"},
            {"name": "Navi Mumbai"},
            {"name": "Mumbai"}
        ]
    }
    r = client.post("/api/routes/optimize", json=payload, headers=headers)
    assert r.status_code == 200
    res = r.json()
    print("Optimized sequence:", [s["name"] for s in res["optimized_route"]])
    print(f"Total Distance: {res['total_distance_km']} km")
    print(f"Duration: {res['estimated_duration_formatted']}")
    print(f"Legs count: {len(res['legs'])}")

    print("\n--- 10. Route Optimization Input Validation ---")
    # Single stop validation error check
    r_single = client.post("/api/routes/optimize", json={"stops": [{"name": "Pune"}]}, headers=headers)
    assert r_single.status_code == 400
    print("Single stop error handling verified (HTTP 400):", r_single.json()["detail"])

    # Invalid location error check
    r_invalid = client.post("/api/routes/optimize", json={"stops": [{"name": "InvalidCityXYZ"}, {"name": "Pune"}]}, headers=headers)
    assert r_invalid.status_code == 400
    print("Invalid location error handling verified (HTTP 400):", r_invalid.json()["detail"])

    print("\n==========================================")
    print("ALL AGROFLOW ENDPOINTS VERIFIED WORKING 100%")
    print("==========================================")



if __name__ == "__main__":
    run_full_suite()
