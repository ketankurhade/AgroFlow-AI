import os
import sys

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import joblib
import numpy as np
from datetime import datetime, timezone
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

from app.database import SessionLocal
from app.models.historical_data import HistoricalSupplyChainData

# Directory paths for saving artifacts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

MODEL_PATH = os.path.join(MODEL_DIR, "spoilage_prediction_pipeline.joblib")
REPORT_PATH = os.path.join(REPORT_DIR, "spoilage_model_report.json")

# Model configuration constants
RANDOM_STATE = 42
TARGET_COL = "target_spoilage_indicator"

EXCLUDED_TARGET_COLUMNS = [
    "target_spoilage_indicator",
    "target_demand_quantity_kg",
    "target_price_per_kg",
]

CATEGORICAL_FEATURES = ["product_name", "category", "season"]
NUMERICAL_FEATURES = [
    "day_of_week",
    "month",
    "temperature",
    "humidity",
    "inventory_age_days",
    "remaining_shelf_life_days",
    "inventory_quantity_kg",
    "historical_demand_kg",
    "supply_quantity_kg",
]
ALL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES


def calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> dict:
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    auc = None
    if y_prob is not None and len(np.unique(y_true)) > 1:
        try:
            auc = float(roc_auc_score(y_true, y_prob))
        except Exception:
            auc = None

    cm = confusion_matrix(y_true, y_pred).tolist()

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4) if auc is not None else None,
        "confusion_matrix": cm,  # [[TN, FP], [FN, TP]]
    }


def train_and_evaluate_spoilage_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    db = SessionLocal()
    try:
        print("1. Fetching historical dataset from PostgreSQL for Spoilage ML...")
        query = db.query(HistoricalSupplyChainData).order_by(
            HistoricalSupplyChainData.record_date.asc(),
            HistoricalSupplyChainData.id.asc()
        )
        records = query.all()
        total_records = len(records)
        if total_records == 0:
            raise ValueError("No records found in historical_supply_chain_data table!")

        X_dicts = []
        y_list = []
        dates_list = []

        for r in records:
            dates_list.append(str(r.record_date))
            y_list.append(r.target_spoilage_indicator)

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

        y_array = np.array(y_list, dtype=int)
        total_healthy = int(np.sum(y_array == 0))
        total_spoiled = int(np.sum(y_array == 1))
        spoilage_pct = round((total_spoiled / total_records) * 100, 1)

        print(f"Dataset loaded: {total_records} records.")
        print(f"Class Distribution: {total_healthy} Healthy (0), {total_spoiled} Spoiled (1) -> {spoilage_pct}% Spoilage Rate.")

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

        # 3. Baseline Classifier (Predict Majority Class in Training Set)
        majority_class = int(np.argmax(np.bincount(y_train)))
        y_pred_baseline = np.full_like(y_test, fill_value=majority_class)
        baseline_metrics = calculate_classification_metrics(y_test, y_pred_baseline)

        print("\n--- Baseline Classifier (Majority Class) ---")
        print(f"Baseline Accuracy:  {baseline_metrics['accuracy'] * 100:.1f}%")
        print(f"Baseline Precision: {baseline_metrics['precision']}")
        print(f"Baseline Recall:    {baseline_metrics['recall']}")
        print(f"Baseline F1-Score:  {baseline_metrics['f1_score']}")

        # 4. Feature Preprocessing & ML Pipeline
        vectorizer = DictVectorizer(sparse=False)
        classifier = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            random_state=RANDOM_STATE,
            class_weight="balanced",
            n_jobs=-1
        )

        pipeline = Pipeline(
            steps=[
                ("vectorizer", vectorizer),
                ("classifier", classifier),
            ]
        )

        # 5. Train Random Forest Classifier
        print("\nTraining Random Forest Classifier pipeline...")
        pipeline.fit(X_train_dicts, y_train)

        # 6. Evaluate on Test Set
        y_pred_rf = pipeline.predict(X_test_dicts)
        y_prob_rf = pipeline.predict_proba(X_test_dicts)[:, 1]  # Probability of class 1 (Spoiled)

        rf_metrics = calculate_classification_metrics(y_test, y_pred_rf, y_prob_rf)

        print("\n--- Random Forest Spoilage Classifier ---")
        print(f"RF Accuracy:  {rf_metrics['accuracy'] * 100:.1f}%")
        print(f"RF Precision: {rf_metrics['precision'] * 100:.1f}%")
        print(f"RF Recall:    {rf_metrics['recall'] * 100:.1f}% (Key Operational Metric)")
        print(f"RF F1-Score:  {rf_metrics['f1_score']}")
        print(f"RF ROC-AUC:   {rf_metrics['roc_auc']}")
        print(f"Confusion Matrix [TN, FP / FN, TP]: {rf_metrics['confusion_matrix']}")

        # 7. Extract Feature Importances
        feature_names = vectorizer.get_feature_names_out()
        importances = classifier.feature_importances_

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
        print(f"\nTrained Spoilage ML pipeline successfully saved to: {MODEL_PATH}")

        # 9. Save Metadata JSON Report
        report_data = {
            "model_name": "RandomForestClassifier",
            "target_column": TARGET_COL,
            "feature_columns": ALL_FEATURES,
            "excluded_target_columns": EXCLUDED_TARGET_COLUMNS,
            "training_records": train_records,
            "testing_records": test_records,
            "training_date_range": f"{train_date_min} to {train_date_max}",
            "testing_date_range": f"{test_date_min} to {test_date_max}",
            "class_distribution": {
                "total_healthy": total_healthy,
                "total_spoiled": total_spoiled,
                "spoilage_rate_pct": spoilage_pct,
            },
            "random_state": RANDOM_STATE,
            "model_parameters": {
                "n_estimators": 150,
                "max_depth": 12,
                "class_weight": "balanced",
            },
            "baseline_metrics": baseline_metrics,
            "model_metrics": rf_metrics,
            "top_feature_importances": feature_importance_list[:10],
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "leakage_prevention": (
                "Target columns target_spoilage_indicator, target_demand_quantity_kg, and target_price_per_kg "
                "were strictly excluded from feature inputs. Only pre-target storage and environmental features were used."
            ),
            "disclaimer": (
                "This spoilage classification model is trained on a synthetic demonstration dataset. "
                "It serves as a proof-of-concept ML prototype for AgroFlow AI and does not constitute "
                "a medically or scientifically certified food-safety guarantee."
            ),
        }

        with open(REPORT_PATH, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"Model metadata report saved to: {REPORT_PATH}")
        return report_data

    finally:
        db.close()


if __name__ == "__main__":
    train_and_evaluate_spoilage_model()
