from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from app.database import Base


class HistoricalSupplyChainData(Base):
    __tablename__ = "historical_supply_chain_data"

    id = Column(Integer, primary_key=True, index=True)
    record_date = Column(Date, nullable=False, index=True)
    product_name = Column(String(120), nullable=False, index=True)
    category = Column(String(80), nullable=False, index=True)

    # Date / Seasonal Features
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    month = Column(Integer, nullable=False)         # 1 to 12
    season = Column(String(30), nullable=False)     # Summer, Monsoon, Winter, Spring

    # Environmental & Operational Features
    temperature = Column(Float, nullable=False)     # Storage / ambient temp °C
    humidity = Column(Float, nullable=False)        # Relative humidity %
    inventory_age_days = Column(Integer, nullable=False)
    remaining_shelf_life_days = Column(Integer, nullable=False)
    inventory_quantity_kg = Column(Float, nullable=False)
    historical_demand_kg = Column(Float, nullable=False)  # Lagged / historical demand feature
    supply_quantity_kg = Column(Float, nullable=False)

    # Distinct Target Columns for Future ML Predictions
    target_demand_quantity_kg = Column(Float, nullable=False)  # Target A: Demand Forecasting
    target_price_per_kg = Column(Float, nullable=False)        # Target B: Price Forecasting
    target_spoilage_indicator = Column(Integer, nullable=False) # Target C: Spoilage Classification (0 or 1)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
