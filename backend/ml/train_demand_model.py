import os
import sys

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import joblib
import math
import numpy as np
from datetime import datetime, timezone
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.database import SessionLocal
from app.models.historical_data import HistoricalSupplyChainData

# Directory paths for saving artifacts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

MODEL_PATH = os.path.join(MODEL_DIR, "demand_forecasting_pipeline.joblib")
REPORT_PATH = os.path.join(REPORT_DIR, "demand_model_report.json")

# Model configuration constants
RANDOM_STATE = 42
TARGET_COL = "target_demand_quantity_kg"
FEATURE_KEYS = [
    "product_name",
    "category",
    "day_of_week",
    "month",
    "season",
    "temperature",
    "humidity",
    "inventory_age_days",
    "remaining_shelf_life_days",
    "inventory_quantity_kg",
    "historical_demand_kg",
    "supply_quantity_kg",
]


def safe_mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1.0) -> float:
    """
    Computes Mean Absolute Percentage Error (MAPE) with zero-division protection.
    """
    denom = np.maximum(np.abs(y_true), epsilon)
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))
    mape = safe_mape(y_true, y_pred)
    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "mape": round(mape, 2),
    }


def train_and_evaluate_demand_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    db = SessionLocal()
    try:
        print("1. Fetching historical dataset from PostgreSQL...")
        query = db.query(HistoricalSupplyChainData).order_by(
            HistoricalSupplyChainData.record_date.asc(),
            HistoricalSupplyChainData.id.asc()
        )
        records = query.all()
        total_records = len(records)
        if total_records == 0:
            raise ValueError("No records found in historical_supply_chain_data table! Run generator first.")

        # Extract features and targets into python dict structures
        X_dicts = []
        y_list = []
        dates_list = []

        for r in records:
            dates_list.append(str(r.record_date))
            y_list.append(r.target_demand_quantity_kg)
            X_dicts.append({
                "product_name": r.product_name,
                "category": r.category,
                "day_of_week": r.day_of_week,
                "month": r.month,
                "season": r.season,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "inventory_age_days": r.inventory_age_days,
                "remaining_shelf_life_days": r.remaining_shelf_life_days,
                "inventory_quantity_kg": r.inventory_quantity_kg,
                "historical_demand_kg": r.historical_demand_kg,
                "supply_quantity_kg": r.supply_quantity_kg,
            })

        y_array = np.array(y_list, dtype=float)
        products_set = sorted(list({d["product_name"] for d in X_dicts}))
        print(f"Dataset loaded: {total_records} observations across {len(products_set)} products.")

        # 2. Chronological Train / Test Split (80% Train, 20% Test)
        split_idx = int(total_records * 0.8)

        X_train_dicts = X_dicts[:split_idx]
        y_train = y_array[:split_idx]

        X_test_dicts = X_dicts[split_idx:]
        y_test = y_array[split_idx:]

        train_records = len(X_train_dicts)
        test_records = len(X_test_dicts)

        train_date_min = dates_list[0]
        train_date_max = dates_list[split_idx - 1]
        test_date_min = dates_list[split_idx]
        test_date_max = dates_list[-1]

        print(f"Train Split: {train_records} records ({train_date_min} to {train_date_max})")
        print(f"Test Split:  {test_records} records ({test_date_min} to {test_date_max})")

        # 3. Baseline Model (Predict Mean Training Demand)
        mean_train_demand = float(np.mean(y_train))
        y_pred_baseline = np.full_like(y_test, fill_value=mean_train_demand)
        baseline_metrics = calculate_metrics(y_test, y_pred_baseline)

        print("\n--- Baseline Model (Mean Demand) ---")
        print(f"Baseline MAE:  {baseline_metrics['mae']} kg")
        print(f"Baseline RMSE: {baseline_metrics['rmse']} kg")
        print(f"Baseline R²:   {baseline_metrics['r2']}")

        # 4. Feature Preprocessing & ML Pipeline
        vectorizer = DictVectorizer(sparse=False)
        regressor = RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            random_state=RANDOM_STATE,
            n_jobs=-1
        )

        pipeline = Pipeline(
            steps=[
                ("vectorizer", vectorizer),
                ("regressor", regressor),
            ]
        )

        # 5. Train Random Forest Model
        print("\nTraining Random Forest Regressor pipeline...")
        pipeline.fit(X_train_dicts, y_train)

        # 6. Evaluate on Test Set
        y_pred_rf = pipeline.predict(X_test_dicts)
        rf_metrics = calculate_metrics(y_test, y_pred_rf)

        print("\n--- Random Forest Regressor Model ---")
        print(f"RF MAE:  {rf_metrics['mae']} kg")
        print(f"RF RMSE: {rf_metrics['rmse']} kg")
        print(f"RF R²:   {rf_metrics['r2']}")
        print(f"RF MAPE: {rf_metrics['mape']}%")

        # 7. Extract Top Feature Importances
        feature_names = vectorizer.get_feature_names_out()
        importances = regressor.feature_importances_

        feature_importance_list = [
            {"feature": name, "importance": round(float(imp), 4)}
            for name, imp in zip(feature_names, importances)
        ]
        feature_importance_list.sort(key=lambda x: x["importance"], reverse=True)

        print("\nTop 7 Feature Importances:")
        for fi in feature_importance_list[:7]:
            print(f"  - {fi['feature']}: {fi['importance'] * 100:.1f}%")

        # 8. Save Pipeline Artifact
        joblib.dump(pipeline, MODEL_PATH)
        print(f"\nTrained ML pipeline successfully saved to: {MODEL_PATH}")

        # 9. Save Metadata JSON Report
        report_data = {
            "model_name": "RandomForestRegressor",
            "target_column": TARGET_COL,
            "feature_columns": FEATURE_KEYS,
            "training_records": train_records,
            "testing_records": test_records,
            "training_date_range": f"{train_date_min} to {train_date_max}",
            "testing_date_range": f"{test_date_min} to {test_date_max}",
            "random_state": RANDOM_STATE,
            "baseline_metrics": baseline_metrics,
            "model_metrics": rf_metrics,
            "top_feature_importances": feature_importance_list[:10],
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "disclaimer": (
                "This demand forecasting model is trained on a synthetic demonstration dataset. "
                "It serves as a functional ML prototype for AgroFlow AI and is not a representation "
                "of real-world market predictions."
            ),
        }

        with open(REPORT_PATH, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"Model metadata report saved to: {REPORT_PATH}")
        return report_data

    finally:
        db.close()


if __name__ == "__main__":
    train_and_evaluate_demand_model()
