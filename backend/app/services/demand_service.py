import os
import json
import joblib
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "ml"))
MODEL_PATH = os.path.join(ML_DIR, "models", "demand_forecasting_pipeline.joblib")
REPORT_PATH = os.path.join(ML_DIR, "reports", "demand_model_report.json")

_PIPELINE_CACHE = None


def get_pipeline():
    """
    Singleton loader for the trained scikit-learn Demand Forecasting pipeline.
    Loads artifact once from disk into memory.
    """
    global _PIPELINE_CACHE
    if _PIPELINE_CACHE is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Trained model artifact not found at {MODEL_PATH}. Run 'python ml/train_demand_model.py' first."
            )
        _PIPELINE_CACHE = joblib.load(MODEL_PATH)
    return _PIPELINE_CACHE


def predict_demand_single(feature_dict: Dict[str, Any]) -> float:
    """
    Runs feature dictionary through saved preprocessing and Random Forest pipeline to predict demand in kg.
    """
    pipeline = get_pipeline()
    prediction = pipeline.predict([feature_dict])[0]
    # Ensure non-negative prediction output
    return round(float(max(0.0, prediction)), 2)


def get_demand_model_summary() -> Dict[str, Any]:
    """
    Returns metadata, baseline metrics, model metrics, feature importances, and train/test ranges.
    """
    if not os.path.exists(REPORT_PATH):
        raise FileNotFoundError(
            f"Model metadata report not found at {REPORT_PATH}. Run 'python ml/train_demand_model.py' first."
        )
    with open(REPORT_PATH, "r") as f:
        data = json.load(f)
    return data


def generate_ml_demand_forecasts(product_name: str = "Mango") -> List[Dict[str, Any]]:
    """
    Generates multi-day ML demand predictions for a specified crop product using trained Random Forest model.
    """
    pipeline = get_pipeline()
    results = []

    # Sample projection points over upcoming week
    product_category_map = {
        "Mango": ("Fruits", 120.0, 14, "Summer", 28.5),
        "Tomato": ("Vegetables", 35.0, 10, "Monsoon", 24.0),
        "Potato": ("Vegetables", 25.0, 60, "Winter", 18.0),
        "Onion": ("Vegetables", 30.0, 45, "Winter", 20.0),
        "Banana": ("Fruits", 40.0, 8, "Summer", 26.0),
        "Grapes": ("Fruits", 90.0, 12, "Spring", 22.0),
        "Apple": ("Fruits", 140.0, 30, "Winter", 15.0),
        "Orange": ("Fruits", 60.0, 20, "Winter", 16.0),
    }

    cat, price, shelf, season, temp = product_category_map.get(
        product_name, ("Fruits", 50.0, 15, "Summer", 25.0)
    )

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    base_hist_demand = 1200.0 if "Vegetables" in cat else 900.0

    for idx, day_str in enumerate(days):
        day_num = idx
        weekend_factor = 1.2 if day_num >= 5 else 1.0

        feat = {
            "product_name": product_name,
            "category": cat,
            "day_of_week": day_num,
            "month": 6,
            "season": season,
            "temperature": temp,
            "humidity": 65.0,
            "inventory_age_days": 4 + (idx % 3),
            "remaining_shelf_life_days": shelf - (idx % 3),
            "inventory_quantity_kg": 1500.0,
            "historical_demand_kg": base_hist_demand * (0.95 + (idx * 0.02)),
            "supply_quantity_kg": 1400.0,
        }

        predicted_kg = predict_demand_single(feat)

        results.append({
            "day": day_str,
            "product_name": product_name,
            "predicted_demand_kg": predicted_kg,
            "historical_reference_kg": round(feat["historical_demand_kg"], 1),
            "is_ml_prediction": True,
        })

    return results
