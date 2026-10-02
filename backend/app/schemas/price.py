from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PricePredictRequest(BaseModel):
    product_name: str = Field(..., example="Tomato")
    category: str = Field(..., example="Vegetables")
    day_of_week: int = Field(..., ge=0, le=6, example=3)
    month: int = Field(..., ge=1, le=12, example=7)
    season: str = Field(..., example="Monsoon")
    temperature: float = Field(..., ge=-10.0, le=60.0, example=24.0)
    humidity: float = Field(..., ge=0.0, le=100.0, example=85.0)
    inventory_age_days: int = Field(..., ge=0, example=3)
    remaining_shelf_life_days: int = Field(..., example=7)
    inventory_quantity_kg: float = Field(..., ge=0.0, example=2000.0)
    historical_demand_kg: float = Field(..., ge=0.0, example=1200.0)
    supply_quantity_kg: float = Field(..., ge=0.0, example=1800.0)


class PricePredictResponse(BaseModel):
    predicted_price_per_kg: float
    model_name: str = "RandomForestRegressor"
    unit: str = "INR/kg"
    disclaimer: str = "ML model price prediction trained on synthetic demonstration dataset."


class ModelMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float
    mape: Optional[float] = None


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class PriceModelSummaryResponse(BaseModel):
    model_name: str
    target_column: str
    feature_columns: List[str]
    excluded_target_columns: List[str]
    training_records: int
    testing_records: int
    training_date_range: str
    testing_date_range: str
    random_state: int
    baseline_metrics: ModelMetrics
    model_metrics: ModelMetrics
    top_feature_importances: List[FeatureImportanceItem]
    leakage_prevention: str
    trained_at: str
    disclaimer: str
