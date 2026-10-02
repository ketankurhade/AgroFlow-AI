from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class HistoricalDataResponse(BaseModel):
    id: int
    record_date: date
    product_name: str
    category: str
    day_of_week: int
    month: int
    season: str
    temperature: float
    humidity: float
    inventory_age_days: int
    remaining_shelf_life_days: int
    inventory_quantity_kg: float
    historical_demand_kg: float
    supply_quantity_kg: float
    target_demand_quantity_kg: float
    target_price_per_kg: float
    target_spoilage_indicator: int

    class Config:
        from_attributes = True


class HistoricalDataSummary(BaseModel):
    total_records: int
    start_date: str
    end_date: str
    products: List[str]
    categories: List[str]
    avg_demand_kg: float
    avg_price_per_kg: float
    avg_temperature_c: float
    avg_humidity_pct: float
    spoilage_rate_pct: float
    disclaimer: str = (
        "This dataset is synthetically generated for AgroFlow AI development and demonstration. "
        "It is not a representation of actual market, agricultural, weather, or spoilage statistics."
    )
