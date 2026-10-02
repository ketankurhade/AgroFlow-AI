import os
import joblib
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_price_model_artifact_and_reloading():
    print("--- 1. Testing Price Model Serialization & Reloading ---")
    model_path = os.path.join(os.path.dirname(__file__), "ml", "models", "price_forecasting_pipeline.joblib")
    assert os.path.exists(model_path), "Price model pipeline joblib artifact must exist!"

    pipeline = joblib.load(model_path)
    assert pipeline is not None

    sample_feat = {
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

    pred = pipeline.predict([sample_feat])[0]
    assert isinstance(pred, (int, float))
    assert pred >= 0.0
    print(f"[OK] Raw price pipeline reload & prediction successful! Output: Rs {pred:.2f} / kg")


def test_price_predict_api():
    print("\n--- 2. Testing POST /api/v1/price/predict Endpoint ---")
    login_resp = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "Admin@AgroFlow2026!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
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

    r = client.post("/api/price/predict", json=payload, headers=headers)
    assert r.status_code == 200
    res = r.json()

    assert "predicted_price_per_kg" in res
    assert isinstance(res["predicted_price_per_kg"], (int, float))
    assert res["predicted_price_per_kg"] >= 0.0
    assert res["model_name"] == "RandomForestRegressor"
    assert res["unit"] == "INR/kg"
    assert "disclaimer" in res
    print(f"[OK] POST /api/price/predict Passed! Output: Rs {res['predicted_price_per_kg']} / kg")


def test_price_model_summary_api():
    print("\n--- 3. Testing GET /api/price/model-summary Endpoint ---")
    login_resp = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "Admin@AgroFlow2026!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/api/price/model-summary", headers=headers)
    assert r.status_code == 200
    res = r.json()

    assert res["model_name"] == "RandomForestRegressor"
    assert res["target_column"] == "target_price_per_kg"
    assert "target_demand_quantity_kg" in res["excluded_target_columns"]
    assert res["training_records"] == 3200
    assert res["testing_records"] == 800
    assert "model_metrics" in res
    assert res["model_metrics"]["r2"] > 0.9
    assert res["model_metrics"]["mae"] < 10.0
    assert "leakage_prevention" in res
    assert "top_feature_importances" in res

    print("[OK] GET /api/price/model-summary Passed! Baseline R2:", res["baseline_metrics"]["r2"], "-> Price Model R2:", res["model_metrics"]["r2"])


def test_price_forecast_api():
    print("\n--- 4. Testing GET /api/price/forecast Endpoint ---")
    login_resp = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "Admin@AgroFlow2026!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/api/price/forecast?product_name=Tomato", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["product_name"] == "Tomato"
    assert len(res["forecasts"]) == 12
    print("[OK] GET /api/v1/price/forecast Passed! 12-month ML price predictions returned.")


if __name__ == "__main__":
    test_price_model_artifact_and_reloading()
    test_price_predict_api()
    test_price_model_summary_api()
    test_price_forecast_api()
    print("\n==========================================")
    print("ALL ML PRICE FORECASTING TESTS PASSED 100%")
    print("==========================================")
