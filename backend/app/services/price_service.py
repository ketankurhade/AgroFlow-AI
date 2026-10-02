import os
import json
import joblib
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "ml"))
MODEL_PATH = os.path.join(ML_DIR, "models", "price_forecasting_pipeline.joblib")
REPORT_PATH = os.path.join(ML_DIR, "reports", "price_model_report.json")

_PRICE_PIPELINE_CACHE = None


def get_price_pipeline():
    """
    Singleton loader for the trained scikit-learn Price Forecasting pipeline.
    Loads artifact once from disk into memory.
    """
    global _PRICE_PIPELINE_CACHE
    if _PRICE_PIPELINE_CACHE is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Trained price model artifact not found at {MODEL_PATH}. Run 'python ml/train_price_model.py' first."
            )
        _PRICE_PIPELINE_CACHE = joblib.load(MODEL_PATH)
    return _PRICE_PIPELINE_CACHE


def predict_price_single(feature_dict: Dict[str, Any]) -> float:
    """
    Runs feature dictionary through saved preprocessing and Random Forest pipeline to predict price in INR/kg.
    Safely enforces non-negativity at inference layer.
    """
    pipeline = get_price_pipeline()
    prediction = pipeline.predict([feature_dict])[0]
    # Enforce non-negative price output
    return round(float(max(0.0, prediction)), 2)


def get_price_model_summary() -> Dict[str, Any]:
    """
    Returns metadata, baseline metrics, model metrics, leakage prevention statement, and feature importances.
    """
    if not os.path.exists(REPORT_PATH):
        raise FileNotFoundError(
            f"Price model metadata report not found at {REPORT_PATH}. Run 'python ml/train_price_model.py' first."
        )
    with open(REPORT_PATH, "r") as f:
        data = json.load(f)
    return data


def generate_ml_price_forecasts(product_name: str = "Tomato") -> List[Dict[str, Any]]:
    """
    Generates multi-day ML price predictions for a specified crop product using trained Random Forest price model.
    """
    product_category_map = {
        "Mango": ("Fruits", 14, "Summer", 28.5),
        "Tomato": ("Vegetables", 10, "Monsoon", 24.0),
        "Potato": ("Vegetables", 60, "Winter", 18.0),
        "Onion": ("Vegetables", 45, "Winter", 20.0),
        "Banana": ("Fruits", 8, "Summer", 26.0),
        "Grapes": ("Fruits", 12, "Spring", 22.0),
        "Apple": ("Fruits", 30, "Winter", 15.0),
        "Orange": ("Fruits", 20, "Winter", 16.0),
    }

    cat, shelf, season, temp = product_category_map.get(
        product_name, ("Vegetables", 15, "Summer", 25.0)
    )

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    results = []

    for idx, month_str in enumerate(months):
        month_num = idx + 1
        feat = {
            "product_name": product_name,
            "category": cat,
            "day_of_week": 3,
            "month": month_num,
            "season": season,
            "temperature": temp,
            "humidity": 65.0,
            "inventory_age_days": 5,
            "remaining_shelf_life_days": shelf,
            "inventory_quantity_kg": 1500.0,
            "historical_demand_kg": 1200.0,
            "supply_quantity_kg": 1300.0 * (1.0 + (idx * 0.03)),
        }

        predicted_price = predict_price_single(feat)

        results.append({
            "month": month_str,
            "product_name": product_name,
            "predicted_price_per_kg": predicted_price,
            "unit": "INR/kg",
            "is_ml_prediction": True,
        })

    return results
