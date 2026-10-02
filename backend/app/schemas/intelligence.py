from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class IntelligenceAnalyzeRequest(BaseModel):
    product_name: str = Field(..., example="Mango", description="Crop product name")
    category: str = Field(..., example="Fruits", description="Product category")
    temperature: float = Field(..., ge=-20.0, le=60.0, example=28.5, description="Storage temperature in °C")
    humidity: float = Field(..., ge=0.0, le=100.0, example=78.0, description="Relative humidity in %")
    inventory_age_days: int = Field(..., ge=0, example=8, description="Days since harvest")
    remaining_shelf_life_days: int = Field(..., example=3, description="Days remaining before expiry")
    inventory_quantity_kg: float = Field(..., ge=0.0, example=1200.0, description="Inventory quantity in kg")
    historical_demand_kg: float = Field(..., ge=0.0, example=1100.0, description="Historical demand reference in kg")
    supply_quantity_kg: float = Field(..., ge=0.0, example=1000.0, description="Supply quantity in kg")
    day_of_week: int = Field(..., ge=0, le=6, example=2, description="Day of week (0=Mon, 6=Sun)")
    month: int = Field(..., ge=1, le=12, example=6, description="Month of year (1-12)")
    season: str = Field(..., example="Summer", description="Seasonal condition")
    stops: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional list of route stop locations [{'name': 'Pune'}, ...]"
    )


class DemandSection(BaseModel):
    predicted_demand_kg: float = Field(..., description="ML forecasted demand in kg")
    signal: str = Field(..., description="'HIGH' (>=1500kg), 'MEDIUM' (800-1499kg), or 'LOW' (<800kg)")
    thresholds: str = Field(
        default="HIGH >= 1500kg, MEDIUM 800-1499kg, LOW < 800kg (Operational demonstration thresholds)",
        description="Threshold rationale"
    )


class PriceSection(BaseModel):
    predicted_price_per_kg: float = Field(..., description="ML forecasted market price in INR/kg")
    signal: str = Field(default="FORECAST AVAILABLE", description="Price forecast availability signal")
    unit: str = Field(default="INR/kg", description="Currency per weight unit")


class RuleBasedSpoilageSection(BaseModel):
    risk_score: int = Field(..., ge=0, le=100, description="Part 4.2 heuristic risk score (0-100)")
    risk_level: str = Field(..., description="'High', 'Medium', or 'Low'")
    factors: List[Dict[str, Any]] = Field(default_factory=list, description="Contributing environmental/shelf-life risk factors")
    recommendation: str = Field(..., description="Heuristic operational recommendation")


class MLSpoilageSection(BaseModel):
    predicted_spoilage: int = Field(..., description="0 = Healthy, 1 = Spoiled")
    spoilage_probability: float = Field(..., ge=0.0, le=1.0, description="Part 4.6 ML classification spoilage probability")
    healthy_probability: float = Field(..., ge=0.0, le=1.0, description="Part 4.6 ML classification healthy probability")
    model_name: str = Field(default="RandomForestClassifier", description="ML model identifier")


class InventorySection(BaseModel):
    inventory_quantity_kg: float = Field(..., description="Current batch inventory stock in kg")
    signal: str = Field(..., description="'HIGH STOCK', 'BALANCED STOCK', or 'LOW STOCK'")


class DecisionSection(BaseModel):
    priority: str = Field(..., description="'CRITICAL', 'HIGH', 'NORMAL', or 'MONITOR'")
    recommendation: str = Field(..., description="Actionable operational decision support text")
    reasoning: List[str] = Field(default_factory=list, description="Transparent decision rule triggers")


class RouteSection(BaseModel):
    route_distance_km: Optional[float] = Field(None, description="OR-Tools TSP route distance")
    estimated_duration_minutes: Optional[int] = Field(None, description="Estimated transit duration")
    route_status: Optional[str] = Field(None, description="Route optimization status")


class IntelligenceAnalyzeResponse(BaseModel):
    product_name: str
    demand: DemandSection
    price: PriceSection
    rule_based_spoilage: RuleBasedSpoilageSection
    ml_spoilage: MLSpoilageSection
    inventory: InventorySection
    decision: DecisionSection
    route: Optional[RouteSection] = None
    disclaimer: str = Field(
        default="Operational decision support based on synthetic demonstration dataset and deterministic heuristics.",
        description="Dataset and operational disclaimer"
    )
