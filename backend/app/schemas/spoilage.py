from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ==========================================
# PART 4.2 RULE-BASED SPOILAGE SCHEMAS
# ==========================================

class RiskFactor(BaseModel):
    factor: str = Field(..., description="Name of the risk dimension (e.g. Shelf Life, Temperature)")
    impact: int = Field(..., description="Numeric score contribution (0-50)")
    message: str = Field(..., description="Explainable rationale message")


class InventorySpoilageRisk(BaseModel):
    inventory_id: int
    batch_id: int
    batch_code: str
    product_name: str
    category: str
    warehouse_location: str
    quantity: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    harvest_date: str
    expiry_date: str
    remaining_shelf_life_days: int
    inventory_age_days: int
    risk_score: int = Field(..., ge=0, le=100, description="Overall risk score bounded 0 to 100")
    risk_level: str = Field(..., description="'High', 'Medium', or 'Low'")
    factors: List[RiskFactor] = Field(default_factory=list, description="List of contributing risk factors")
    recommendation: str = Field(..., description="Operational supply-chain recommendation")


class SpoilageSummary(BaseModel):
    total_analyzed: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    average_risk_score: float
    highest_risk_batches: List[InventorySpoilageRisk]
    disclaimer: str = (
        "Rule-based spoilage-risk intelligence derived from current inventory temperature, "
        "humidity, harvest date, and expiry date stored in PostgreSQL. Not an ML model or "
        "scientifically certified guarantee."
    )


# ==========================================
# PART 4.6 ML SPOILAGE PREDICTION SCHEMAS
# ==========================================

class SpoilageMLPredictRequest(BaseModel):
    batch_id: Optional[int] = Field(None, description="Optional batch ID to validate ownership")
    inventory_id: Optional[int] = Field(None, description="Optional inventory ID to validate ownership")
    product_name: str = Field(..., example="Mango", description="Crop product name")
    category: str = Field(..., example="Fruits", description="Product category")
    day_of_week: int = Field(..., ge=0, le=6, example=2, description="Day of week (0=Mon, 6=Sun)")
    month: int = Field(..., ge=1, le=12, example=6, description="Month of year (1-12)")
    season: str = Field(..., example="Summer", description="Seasonal condition")
    temperature: float = Field(..., ge=-20.0, le=60.0, example=28.5, description="Storage temperature in °C")
    humidity: float = Field(..., ge=0.0, le=100.0, example=75.0, description="Relative humidity in %")
    inventory_age_days: int = Field(..., ge=0, example=8, description="Days since harvest")
    remaining_shelf_life_days: int = Field(..., example=5, description="Days remaining before expiry")
    inventory_quantity_kg: float = Field(..., ge=0.0, example=1200.0, description="Inventory quantity in kg")
    historical_demand_kg: float = Field(..., ge=0.0, example=1000.0, description="Historical demand in kg")
    supply_quantity_kg: float = Field(..., ge=0.0, example=1100.0, description="Supply quantity in kg")


class SpoilageMLPredictResponse(BaseModel):
    predicted_spoilage: int = Field(..., description="0 = Healthy / Not Spoiled, 1 = Spoiled")
    spoilage_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of spoilage (0.0 - 1.0)")
    healthy_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of remaining healthy (0.0 - 1.0)")
    model_name: str = Field(default="RandomForestClassifier", description="ML model identifier")
    disclaimer: str = Field(
        default="ML spoilage prediction trained on synthetic demonstration dataset.",
        description="Dataset limitation disclaimer"
    )


class SpoilageMLModelSummaryResponse(BaseModel):
    model_name: str
    target_column: str
    feature_columns: List[str]
    excluded_target_columns: List[str]
    training_records: int
    testing_records: int
    training_date_range: str
    testing_date_range: str
    class_distribution: Dict[str, Any]
    random_state: int
    model_parameters: Dict[str, Any]
    baseline_metrics: Dict[str, Any]
    model_metrics: Dict[str, Any]
    top_feature_importances: List[Dict[str, Any]]
    trained_at: str
    leakage_prevention: str
    disclaimer: str


class CombinedSpoilageAnalysisResponse(BaseModel):
    inventory_id: Optional[int] = None
    batch_code: Optional[str] = None
    rule_based: Dict[str, Any]  # risk_score, risk_level, factors, recommendation
    ml_prediction: SpoilageMLPredictResponse
    disclaimer: str = Field(
        default="Combined analysis featuring both Part 4.2 Rule-Based Risk Intelligence and Part 4.6 ML Classification.",
        description="Combined analysis disclaimer"
    )
