from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DemandPredictRequest(BaseModel):
    product_name: str = Field(..., example="Mango")
    category: str = Field(..., example="Fruits")
    day_of_week: int = Field(..., ge=0, le=6, example=2)
    month: int = Field(..., ge=1, le=12, example=5)
    season: str = Field(..., example="Summer")
    temperature: float = Field(..., example=28.5)
    humidity: float = Field(..., example=70.0)
    inventory_age_days: int = Field(..., ge=0, example=4)
    remaining_shelf_life_days: int = Field(..., example=12)
    inventory_quantity_kg: float = Field(..., ge=0.0, example=1500.0)
    historical_demand_kg: float = Field(..., ge=0.0, example=1350.0)
    supply_quantity_kg: float = Field(..., ge=0.0, example=1200.0)


class DemandPredictResponse(BaseModel):
    predicted_demand_quantity_kg: float
    model_name: str = "RandomForestRegressor"
    unit: str = "kg"
    disclaimer: str = "ML model prediction trained on synthetic demonstration dataset."


class ModelMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float
    mape: Optional[float] = None


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class ModelSummaryResponse(BaseModel):
    model_name: str
    target_column: str
    feature_columns: List[str]
    training_records: int
    testing_records: int
    training_date_range: str
    testing_date_range: str
    random_state: int
    baseline_metrics: ModelMetrics
    model_metrics: ModelMetrics
    top_feature_importances: List[FeatureImportanceItem]
    trained_at: str
    disclaimer: str
