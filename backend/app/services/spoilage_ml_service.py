import os
import json
import joblib
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "ml"))
MODEL_PATH = os.path.join(ML_DIR, "models", "spoilage_prediction_pipeline.joblib")
REPORT_PATH = os.path.join(ML_DIR, "reports", "spoilage_model_report.json")

_PIPELINE_CACHE = None


def get_pipeline():
    """
    Singleton loader for the trained scikit-learn Spoilage Classification pipeline.
    Loads artifact once from disk into memory.
    """
    global _PIPELINE_CACHE
    if _PIPELINE_CACHE is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Trained model artifact not found at {MODEL_PATH}. Run 'python ml/train_spoilage_model.py' first."
            )
        _PIPELINE_CACHE = joblib.load(MODEL_PATH)
    return _PIPELINE_CACHE


def predict_spoilage_single(feature_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs feature dictionary through saved preprocessing and Random Forest Classifier pipeline
    to predict spoilage indicator (0 = Healthy, 1 = Spoiled) and class probabilities.
    """
    pipeline = get_pipeline()
    
    # Extract prediction (0 or 1)
    pred_class = int(pipeline.predict([feature_dict])[0])
    
    # Extract probabilities: index 0 -> healthy, index 1 -> spoiled
    probs = pipeline.predict_proba([feature_dict])[0]
    healthy_prob = round(float(probs[0]), 4)
    spoilage_prob = round(float(probs[1]), 4)
    
    return {
        "predicted_spoilage": pred_class,
        "spoilage_probability": spoilage_prob,
        "healthy_probability": healthy_prob,
        "model_name": "RandomForestClassifier",
    }


def get_spoilage_ml_model_summary() -> Dict[str, Any]:
    """
    Returns metadata report containing model metrics, baseline performance,
    class distribution, feature importances, train/test ranges, and disclaimers.
    """
    if not os.path.exists(REPORT_PATH):
        raise FileNotFoundError(
            f"Model metadata report not found at {REPORT_PATH}. Run 'python ml/train_spoilage_model.py' first."
        )
    with open(REPORT_PATH, "r") as f:
        data = json.load(f)
    return data
