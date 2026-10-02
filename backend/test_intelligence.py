import os
import sys
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)


def run_intelligence_layer_tests():
    print("=" * 70)
    print("AGROFLOW AI - PART 4.7 INTELLIGENCE INTEGRATION SUITE")
    print("=" * 70)

    # Scenario Inputs
    scenario_a_low_spoil_high_demand = {
        "product_name": "Mango",
        "category": "Fruits",
        "temperature": 15.0,
        "humidity": 60.0,
        "inventory_age_days": 2,
        "remaining_shelf_life_days": 15,
        "inventory_quantity_kg": 1000.0,
        "historical_demand_kg": 1800.0,
        "supply_quantity_kg": 1000.0,
        "day_of_week": 1,
        "month": 6,
        "season": "Summer",
    }

    scenario_b_high_spoil_high_demand = {
        "product_name": "Mango",
        "category": "Fruits",
        "temperature": 32.0,
        "humidity": 85.0,
        "inventory_age_days": 14,
        "remaining_shelf_life_days": 1,
        "inventory_quantity_kg": 1500.0,
        "historical_demand_kg": 1800.0,
        "supply_quantity_kg": 1000.0,
        "day_of_week": 2,
        "month": 6,
        "season": "Summer",
    }

    scenario_c_high_spoil_low_demand = {
        "product_name": "Mango",
        "category": "Fruits",
        "temperature": 32.0,
        "humidity": 85.0,
        "inventory_age_days": 14,
        "remaining_shelf_life_days": 1,
        "inventory_quantity_kg": 1500.0,
        "historical_demand_kg": 400.0,
        "supply_quantity_kg": 1800.0,
        "day_of_week": 3,
        "month": 6,
        "season": "Summer",
    }

    scenario_d_low_spoil_low_demand = {
        "product_name": "Potato",
        "category": "Vegetables",
        "temperature": 12.0,
        "humidity": 55.0,
        "inventory_age_days": 2,
        "remaining_shelf_life_days": 40,
        "inventory_quantity_kg": 3000.0,
        "historical_demand_kg": 300.0,
        "supply_quantity_kg": 500.0,
        "day_of_week": 4,
        "month": 1,
        "season": "Winter",
    }

    login_resp = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "Admin@AgroFlow2026!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. SCENARIO A: Low Spoilage + High Demand
    print("\n[TEST 1] Scenario A (Low Spoilage + High Demand)...")
    res_a = client.post("/api/intelligence/analyze", json=scenario_a_low_spoil_high_demand, headers=headers)
    assert res_a.status_code == 200, f"Error {res_a.status_code}: {res_a.text}"
    data_a = res_a.json()
    assert data_a["demand"]["predicted_demand_kg"] > 0
    assert data_a["price"]["predicted_price_per_kg"] >= 0
    assert data_a["rule_based_spoilage"]["risk_level"] in ["Low", "Medium"]
    assert "demand" in data_a and "price" in data_a and "ml_spoilage" in data_a
    assert data_a["decision"]["priority"] in ["NORMAL", "MONITOR"]
    print(f"  [OK] Scenario A Verified -> Priority: {data_a['decision']['priority']}, Recommendation: {data_a['decision']['recommendation']}")

    # 2. SCENARIO B: High Spoilage + High Demand
    print("\n[TEST 2] Scenario B (High Spoilage + High Demand)...")
    res_b = client.post("/api/intelligence/analyze", json=scenario_b_high_spoil_high_demand, headers=headers)
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["rule_based_spoilage"]["risk_level"] == "High" or data_b["ml_spoilage"]["spoilage_probability"] >= 0.70
    assert data_b["decision"]["priority"] == "CRITICAL"
    assert "dispatch" in data_b["decision"]["recommendation"].lower()
    print(f"  [OK] Scenario B Verified -> Priority: {data_b['decision']['priority']}, Recommendation: {data_b['decision']['recommendation']}")

    # 3. SCENARIO C: High Spoilage + Low Demand
    print("\n[TEST 3] Scenario C (High Spoilage + Low Demand)...")
    res_c = client.post("/api/intelligence/analyze", json=scenario_c_high_spoil_low_demand, headers=headers)
    assert res_c.status_code == 200
    data_c = res_c.json()
    assert data_c["decision"]["priority"] == "HIGH"
    assert "liquidation" in data_c["decision"]["recommendation"].lower() or "redistribution" in data_c["decision"]["recommendation"].lower()
    print(f"  [OK] Scenario C Verified -> Priority: {data_c['decision']['priority']}, Recommendation: {data_c['decision']['recommendation']}")

    # 4. SCENARIO D: Low Spoilage + Low Demand + High Stock
    print("\n[TEST 4] Scenario D (Low Spoilage + Low Demand + Surplus Stock)...")
    res_d = client.post("/api/intelligence/analyze", json=scenario_d_low_spoil_low_demand, headers=headers)
    assert res_d.status_code == 200
    data_d = res_d.json()
    assert data_d["decision"]["priority"] == "MONITOR"
    assert "avoid" in data_d["decision"]["recommendation"].lower() or "replenishment" in data_d["decision"]["recommendation"].lower()
    print(f"  [OK] Scenario D Verified -> Priority: {data_d['decision']['priority']}, Recommendation: {data_d['decision']['recommendation']}")

    # 5. TEST INVALID PAYLOAD REJECTION
    print("\n[TEST 5] Invalid Payload Validation...")
    res_invalid = client.post("/api/intelligence/analyze", json={"product_name": "Mango", "temperature": 150.0}, headers=headers)
    assert res_invalid.status_code == 422, "Invalid payload must be rejected by Pydantic schema validation"
    print("  [OK] Invalid payload correctly rejected with status 422 Unprocessable Entity.")

    # 6. TEST EXISTING ROUTE OPTIMIZATION STILL WORKS
    print("\n[TEST 6] Existing Route Optimization Integration...")
    payload_with_route = dict(scenario_a_low_spoil_high_demand)
    payload_with_route["stops"] = [{"name": "Ratnagiri"}, {"name": "Pune"}, {"name": "Mumbai"}]
    res_route = client.post("/api/intelligence/analyze", json=payload_with_route, headers=headers)
    assert res_route.status_code == 200
    data_route = res_route.json()
    assert data_route["route"] is not None
    assert data_route["route"]["route_distance_km"] > 0
    print(f"  [OK] Route integration verified: distance = {data_route['route']['route_distance_km']} km")

    # 7. TEST EXISTING SPOILAGE AND ML APIS STILL WORK
    print("\n[TEST 7] Regression Check on Existing APIs...")
    res_rule = client.get("/api/spoilage/risk", headers=headers)
    assert res_rule.status_code == 200
    res_ml = client.get("/api/spoilage/ml-model-summary", headers=headers)
    assert res_ml.status_code == 200
    print("  [OK] Existing Part 4.2 and Part 4.6 APIs continue functioning 100%.")

    print("\n" + "=" * 70)
    print("ALL PART 4.7 INTELLIGENCE INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_intelligence_layer_tests()
