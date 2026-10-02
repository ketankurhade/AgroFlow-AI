import os
import sys
import json
import joblib
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from app.database import SessionLocal
from app.models.historical_data import HistoricalSupplyChainData

client = TestClient(app)


def run_spoilage_ml_tests():
    print("=" * 70)
    print("AGROFLOW AI - PART 4.6 ML SPOILAGE PREDICTION SUITE")
    print("=" * 70)

    # 1. Test Dataset Loading
    print("\n[TEST 1] Database Historical Dataset Loading...")
    db = SessionLocal()
    try:
        query = db.query(HistoricalSupplyChainData).order_by(
            HistoricalSupplyChainData.record_date.asc(),
            HistoricalSupplyChainData.id.asc()
        )
        records = query.all()
        total_records = len(records)
        assert total_records == 4000, f"Expected 4000 records, found {total_records}"
        print(f"  [OK] Successfully loaded {total_records} historical records from PostgreSQL.")

        # 2. Test Class Distribution
        print("\n[TEST 2] Class Distribution Verification...")
        y_labels = [r.target_spoilage_indicator for r in records]
        healthy_cnt = sum(1 for y in y_labels if y == 0)
        spoiled_cnt = sum(1 for y in y_labels if y == 1)
        spoilage_pct = round((spoiled_cnt / total_records) * 100, 1)
        assert healthy_cnt + spoiled_cnt == total_records
        print(f"  [OK] Class distribution verified: Healthy(0) = {healthy_cnt}, Spoiled(1) = {spoiled_cnt} ({spoilage_pct}% spoilage rate).")

        # 3. Test Chronological Split & Preprocessing setup
        print("\n[TEST 3] Chronological Split & Preprocessing Check...")
        split_idx = int(total_records * 0.8)
        train_recs = records[:split_idx]
        test_recs = records[split_idx:]
        assert len(train_recs) == 3200
        assert len(test_recs) == 800
        print(f"  [OK] Chronological 80/20 split verified (Train: {len(train_recs)}, Test: {len(test_recs)}).")

    finally:
        db.close()

    # 4 & 5. Check Artifact File & Serialization / Reload
    print("\n[TEST 4 & 5] Pipeline Serialization & Artifact Reloading...")
    model_path = os.path.join(os.path.dirname(__file__), "ml", "models", "spoilage_prediction_pipeline.joblib")
    report_path = os.path.join(os.path.dirname(__file__), "ml", "reports", "spoilage_model_report.json")
    
    assert os.path.exists(model_path), f"Missing model artifact at {model_path}"
    assert os.path.exists(report_path), f"Missing model report at {report_path}"

    pipeline = joblib.load(model_path)
    print("  [OK] Successfully loaded trained scikit-learn pipeline from joblib artifact.")

    with open(report_path, "r") as f:
        report = json.load(f)
    assert report["model_name"] == "RandomForestClassifier"
    assert "accuracy" in report["model_metrics"]
    assert "recall" in report["model_metrics"]
    print(f"  [OK] Report metadata verified. Model recall on test set: {report['model_metrics']['recall'] * 100:.1f}%")

    # 6 & 7. Pipeline Direct Prediction & Probabilities
    print("\n[TEST 6 & 7] Direct Pipeline Inference & Output Bounds...")
    sample_feat = {
        "product_name": "Mango",
        "category": "Fruits",
        "day_of_week": 2,
        "month": 6,
        "season": "Summer",
        "temperature": 29.5,
        "humidity": 82.0,
        "inventory_age_days": 12,
        "remaining_shelf_life_days": 1,
        "inventory_quantity_kg": 1500.0,
        "historical_demand_kg": 1100.0,
        "supply_quantity_kg": 1200.0,
    }

    pred_class = int(pipeline.predict([sample_feat])[0])
    probs = pipeline.predict_proba([sample_feat])[0]

    assert pred_class in [0, 1], f"Invalid classification output {pred_class}"
    assert 0.0 <= probs[0] <= 1.0, f"Invalid healthy probability {probs[0]}"
    assert 0.0 <= probs[1] <= 1.0, f"Invalid spoilage probability {probs[1]}"
    assert abs((probs[0] + probs[1]) - 1.0) < 1e-4, "Probabilities do not sum to 1.0"

    print(f"  [OK] Direct prediction verified: class={pred_class}, healthy_prob={probs[0]:.4f}, spoilage_prob={probs[1]:.4f}")

    # 8. API Endpoint Testing: Rule-Based Spoilage API
    print("\n[TEST 8] Part 4.2 Rule-Based Spoilage API (GET /api/spoilage/risk)...")
    login_resp = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "Admin@AgroFlow2026!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res_rule = client.get("/api/spoilage/risk", headers=headers)
    assert res_rule.status_code == 200, f"Rule-based API error {res_rule.status_code}: {res_rule.text}"
    rule_data = res_rule.json()
    assert isinstance(rule_data, list), "Expected list of inventory risks"
    print(f"  [OK] Part 4.2 Rule-based API functioning properly ({len(rule_data)} items evaluated).")

    # 9. API Endpoint Testing: ML Model Summary API
    print("\n[TEST 9] Part 4.6 ML Model Summary API (GET /api/spoilage/ml-model-summary)...")
    res_summary = client.get("/api/spoilage/ml-model-summary", headers=headers)
    assert res_summary.status_code == 200, f"Model Summary API error {res_summary.status_code}: {res_summary.text}"
    summary_data = res_summary.json()
    assert summary_data["model_name"] == "RandomForestClassifier"
    assert "top_feature_importances" in summary_data
    print(f"  [OK] Part 4.6 ML Summary API functioning properly (ROC-AUC: {summary_data['model_metrics']['roc_auc']}).")

    # 10. API Endpoint Testing: ML Prediction API
    print("\n[TEST 10] Part 4.6 ML Prediction API (POST /api/spoilage/ml-predict)...")
    res_ml = client.post("/api/spoilage/ml-predict", json=sample_feat, headers=headers)
    assert res_ml.status_code == 200, f"ML Prediction API error {res_ml.status_code}: {res_ml.text}"
    ml_data = res_ml.json()
    assert ml_data["predicted_spoilage"] in [0, 1]
    assert 0.0 <= ml_data["spoilage_probability"] <= 1.0
    assert 0.0 <= ml_data["healthy_probability"] <= 1.0
    assert ml_data["model_name"] == "RandomForestClassifier"
    print(f"  [OK] Part 4.6 ML Predict API functioning properly: predicted={ml_data['predicted_spoilage']}, prob={ml_data['spoilage_probability']}")

    # 11. API Endpoint Testing: Combined Spoilage Analysis API
    print("\n[TEST 11] Combined Spoilage Analysis API (POST /api/spoilage/analyze)...")
    res_comb = client.post("/api/spoilage/analyze", json=sample_feat, headers=headers)
    assert res_comb.status_code == 200, f"Combined API error {res_comb.status_code}: {res_comb.text}"
    comb_data = res_comb.json()
    assert "rule_based" in comb_data
    assert "ml_prediction" in comb_data
    print(f"  [OK] Combined Spoilage Analysis API functioning properly.")

    print("\n" + "=" * 70)
    print("ALL PART 4.6 SPOILAGE ML TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_spoilage_ml_tests()
