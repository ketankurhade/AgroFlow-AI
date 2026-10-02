from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_full_system():
    print("==================================================")
    print("AGROFLOW AI - FULL SYSTEM REGRESSION & FEATURE TEST")
    print("==================================================")

    # 1. Health
    r = client.get("/api/health")
    assert r.status_code == 200
    print("[OK] Health Check Passed:", r.json())

    import os
    admin_email = os.getenv("ADMIN_EMAIL", "admin@agroflow.com")
    admin_pwd = os.getenv("ADMIN_PASSWORD", "admin123")
    r = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Auth Login Passed! Token generated.")

    # 3. Products
    r = client.get("/api/products", headers=headers)
    assert r.status_code == 200
    print("[OK] Products API Passed! Items count:", len(r.json()))

    # 4. Batches
    r = client.get("/api/batches", headers=headers)
    assert r.status_code == 200
    print("[OK] Batches API Passed! Items count:", len(r.json()))

    # 5. Inventory
    r = client.get("/api/inventory", headers=headers)
    assert r.status_code == 200
    print("[OK] Inventory API Passed! Items count:", len(r.json()))

    # 6. Orders
    r = client.get("/api/orders", headers=headers)
    assert r.status_code == 200
    print("[OK] Orders API Passed! Items count:", len(r.json()))

    # 7. Shipments
    r = client.get("/api/shipments", headers=headers)
    assert r.status_code == 200
    print("[OK] Shipments API Passed! Items count:", len(r.json()))

    # 8. Route Optimization (Part 4.1)
    r = client.post("/api/routes/optimize", json={
        "stops": [{"name": "Ratnagiri"}, {"name": "Pune"}, {"name": "Mumbai"}, {"name": "Navi Mumbai"}]
    }, headers=headers)
    assert r.status_code == 200
    route_res = r.json()
    assert len(route_res["optimized_route"]) == 4
    assert route_res["total_distance_km"] > 0
    print("[OK] Part 4.1 Route Optimization Passed! Distance:", route_res["total_distance_km"], "km, Sequence:", [s["name"] for s in route_res["optimized_route"]])

    # 9. Spoilage Risk (Part 4.2)
    r = client.get("/api/spoilage/risk", headers=headers)
    assert r.status_code == 200
    evals = r.json()
    assert isinstance(evals, list)
    if len(evals) > 0:
        item = evals[0]
        assert "risk_score" in item
        assert "risk_level" in item
        assert "factors" in item
        assert "recommendation" in item
    print("[OK] Part 4.2 Spoilage Risk API Passed! Evaluated lots:", len(evals))

    # 10. Spoilage Summary (Part 4.2)
    r = client.get("/api/spoilage/summary", headers=headers)
    assert r.status_code == 200
    summary = r.json()
    assert "total_analyzed" in summary
    assert "high_risk_count" in summary
    assert "average_risk_score" in summary
    print("[OK] Part 4.2 Spoilage Summary API Passed! Analyzed:", summary["total_analyzed"], "High risk:", summary["high_risk_count"], "Avg Score:", summary["average_risk_score"])

    # 11. Historical Dataset Summary (Part 4.3)
    r = client.get("/api/historical-data/summary", headers=headers)
    assert r.status_code == 200
    hist_summary = r.json()
    assert hist_summary["total_records"] == 4000
    assert len(hist_summary["products"]) == 8
    print("[OK] Part 4.3 Historical Dataset Summary API Passed! Total records:", hist_summary["total_records"])

    # 12. ML Demand Forecasting (Part 4.4)
    r_ml = client.post("/api/demand/predict", json={
        "product_name": "Mango", "category": "Fruits", "day_of_week": 2, "month": 5, "season": "Summer",
        "temperature": 28.5, "humidity": 70.0, "inventory_age_days": 4, "remaining_shelf_life_days": 12,
        "inventory_quantity_kg": 1500.0, "historical_demand_kg": 1350.0, "supply_quantity_kg": 1200.0
    }, headers=headers)
    assert r_ml.status_code == 200
    ml_res = r_ml.json()
    assert ml_res["predicted_demand_quantity_kg"] > 0
    print("[OK] Part 4.4 ML Demand Prediction Passed! Predicted demand:", ml_res["predicted_demand_quantity_kg"], "kg")

    # 13. ML Price Forecasting (Part 4.5)
    r_price = client.post("/api/price/predict", json={
        "product_name": "Tomato", "category": "Vegetables", "day_of_week": 3, "month": 7, "season": "Monsoon",
        "temperature": 24.0, "humidity": 85.0, "inventory_age_days": 3, "remaining_shelf_life_days": 7,
        "inventory_quantity_kg": 2000.0, "historical_demand_kg": 1200.0, "supply_quantity_kg": 1800.0
    }, headers=headers)
    assert r_price.status_code == 200
    price_res = r_price.json()
    assert price_res["predicted_price_per_kg"] >= 0.0
    print("[OK] Part 4.5 ML Price Prediction Passed! Predicted price: Rs", price_res["predicted_price_per_kg"], "/ kg")

    # 14. ML Spoilage Prediction (Part 4.6)
    r_spoil_ml = client.post("/api/spoilage/ml-predict", json={
        "product_name": "Mango", "category": "Fruits", "day_of_week": 2, "month": 6, "season": "Summer",
        "temperature": 29.5, "humidity": 82.0, "inventory_age_days": 12, "remaining_shelf_life_days": 1,
        "inventory_quantity_kg": 1500.0, "historical_demand_kg": 1100.0, "supply_quantity_kg": 1200.0
    }, headers=headers)
    assert r_spoil_ml.status_code == 200
    spoil_ml_res = r_spoil_ml.json()
    assert spoil_ml_res["predicted_spoilage"] in [0, 1]
    assert 0.0 <= spoil_ml_res["spoilage_probability"] <= 1.0
    print("[OK] Part 4.6 ML Spoilage Prediction Passed! Class:", spoil_ml_res["predicted_spoilage"], "Prob:", spoil_ml_res["spoilage_probability"])

    # 15. ML Spoilage Model Summary (Part 4.6)
    r_spoil_sum = client.get("/api/spoilage/ml-model-summary", headers=headers)
    assert r_spoil_sum.status_code == 200
    spoil_sum_res = r_spoil_sum.json()
    assert spoil_sum_res["model_name"] == "RandomForestClassifier"
    print("[OK] Part 4.6 ML Spoilage Summary Passed! ROC-AUC:", spoil_sum_res["model_metrics"]["roc_auc"])

    # 16. Intelligence Integration & Decision Layer (Part 4.7)
    r_intel = client.post("/api/intelligence/analyze", json={
        "product_name": "Mango", "category": "Fruits", "temperature": 30.0, "humidity": 80.0,
        "inventory_age_days": 10, "remaining_shelf_life_days": 2, "inventory_quantity_kg": 1200.0,
        "historical_demand_kg": 1600.0, "supply_quantity_kg": 1100.0, "day_of_week": 2, "month": 6, "season": "Summer"
    }, headers=headers)
    assert r_intel.status_code == 200
    intel_res = r_intel.json()
    assert "demand" in intel_res and "price" in intel_res and "decision" in intel_res
    print("[OK] Part 4.7 Intelligence Integration Passed! Priority:", intel_res["decision"]["priority"], "Action:", intel_res["decision"]["recommendation"])

    print("\n==================================================")
    print("ALL 16 AGROFLOW SYSTEM MODULES PASSED REGRESSION 100%")
    print("==================================================")


if __name__ == "__main__":
    test_full_system()

