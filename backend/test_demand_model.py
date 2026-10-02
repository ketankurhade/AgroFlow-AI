import os
import joblib
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_model_artifact_and_reloading():
    print("--- 1. Testing Model Serialization & Reloading ---")
    model_path = os.path.join(os.path.dirname(__file__), "ml", "models", "demand_forecasting_pipeline.joblib")
    assert os.path.exists(model_path), "Model pipeline joblib artifact must exist!"

    pipeline = joblib.load(model_path)
    assert pipeline is not None

    # Test raw pipeline prediction with sample feature dict
    sample_feat = {
        "product_name": "Mango",
        "category": "Fruits",
        "day_of_week": 2,
        "month": 5,
        "season": "Summer",
        "temperature": 28.5,
        "humidity": 70.0,
        "inventory_age_days": 4,
        "remaining_shelf_life_days": 12,
        "inventory_quantity_kg": 1500.0,
        "historical_demand_kg": 1350.0,
        "supply_quantity_kg": 1200.0,
    }

    pred = pipeline.predict([sample_feat])[0]
    assert isinstance(pred, (int, float))
    assert pred >= 0.0
    print(f"[OK] Raw pipeline reload & prediction successful! Output: {pred:.2f} kg")


def get_auth_headers():
    login_resp = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "Admin@AgroFlow2026!"})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_demand_predict_api():
    print("\n--- 2. Testing POST /api/demand/predict Endpoint ---")
    headers = get_auth_headers()
    payload = {
        "product_name": "Tomato",
        "category": "Vegetables",
        "day_of_week": 3,
        "month": 7,
        "season": "Monsoon",
        "temperature": 24.0,
        "humidity": 85.0,
        "inventory_age_days": 3,
        "remaining_shelf_life_days": 7,
        "inventory_quantity_kg": 2000.0,
        "historical_demand_kg": 1200.0,
        "supply_quantity_kg": 1800.0,
    }

    r = client.post("/api/demand/predict", json=payload, headers=headers)
    assert r.status_code == 200
    res = r.json()

    assert "predicted_demand_quantity_kg" in res
    assert isinstance(res["predicted_demand_quantity_kg"], (int, float))
    assert res["predicted_demand_quantity_kg"] >= 0.0
    assert res["model_name"] == "RandomForestRegressor"
    assert res["unit"] == "kg"
    assert "disclaimer" in res
    print(f"[OK] POST /api/demand/predict Passed! Output: {res['predicted_demand_quantity_kg']} kg")


def test_demand_model_summary_api():
    print("\n--- 3. Testing GET /api/demand/model-summary Endpoint ---")
    headers = get_auth_headers()
    r = client.get("/api/demand/model-summary", headers=headers)
    assert r.status_code == 200
    res = r.json()

    assert res["model_name"] == "RandomForestRegressor"
    assert res["training_records"] == 3200
    assert res["testing_records"] == 800
    assert "model_metrics" in res
    assert res["model_metrics"]["r2"] > 0.8
    assert res["model_metrics"]["mae"] < 200.0
    assert "top_feature_importances" in res
    assert len(res["top_feature_importances"]) > 0

    print("[OK] GET /api/demand/model-summary Passed! Baseline R2:", res["baseline_metrics"]["r2"], "-> Model R2:", res["model_metrics"]["r2"])


def test_demand_forecast_api():
    print("\n--- 4. Testing GET /api/demand/forecast Endpoint ---")
    headers = get_auth_headers()
    r = client.get("/api/demand/forecast?product_name=Mango", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["product_name"] == "Mango"
    assert len(res["forecasts"]) == 7
    print("[OK] GET /api/demand/forecast Passed! 7-day multi-day ML predictions returned.")


if __name__ == "__main__":
    test_model_artifact_and_reloading()
    test_demand_predict_api()
    test_demand_model_summary_api()
    test_demand_forecast_api()
    print("\n==========================================")
    print("ALL ML DEMAND FORECASTING TESTS PASSED 100%")
    print("==========================================")
