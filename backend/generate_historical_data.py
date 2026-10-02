import random
import math
import numpy as np
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
import app.models  # Register all models including HistoricalSupplyChainData
from app.models.historical_data import HistoricalSupplyChainData


# Controlled Constants
RANDOM_SEED = 42
TOTAL_TARGET_RECORDS = 4000
START_DATE = date(2024, 1, 1)
END_DATE = date(2026, 9, 28)

PRODUCT_PROFILES = {
    "Mango": {
        "category": "Fruits",
        "base_demand_kg": 800.0,
        "base_price_rs": 120.0,
        "base_shelf_life_days": 14,
        "optimal_temp_c": 12.0,
        "seasonal_multipliers": {"Summer": 1.8, "Monsoon": 0.8, "Winter": 0.3, "Spring": 1.1},
    },
    "Tomato": {
        "category": "Vegetables",
        "base_demand_kg": 1200.0,
        "base_price_rs": 35.0,
        "base_shelf_life_days": 10,
        "optimal_temp_c": 14.0,
        "seasonal_multipliers": {"Summer": 1.0, "Monsoon": 1.3, "Winter": 1.2, "Spring": 1.0},
    },
    "Potato": {
        "category": "Vegetables",
        "base_demand_kg": 2000.0,
        "base_price_rs": 25.0,
        "base_shelf_life_days": 60,
        "optimal_temp_c": 18.0,
        "seasonal_multipliers": {"Summer": 1.0, "Monsoon": 1.1, "Winter": 1.1, "Spring": 1.0},
    },
    "Onion": {
        "category": "Vegetables",
        "base_demand_kg": 1800.0,
        "base_price_rs": 30.0,
        "base_shelf_life_days": 45,
        "optimal_temp_c": 20.0,
        "seasonal_multipliers": {"Summer": 1.1, "Monsoon": 1.2, "Winter": 1.0, "Spring": 1.0},
    },
    "Banana": {
        "category": "Fruits",
        "base_demand_kg": 1500.0,
        "base_price_rs": 40.0,
        "base_shelf_life_days": 8,
        "optimal_temp_c": 15.0,
        "seasonal_multipliers": {"Summer": 1.2, "Monsoon": 1.0, "Winter": 0.9, "Spring": 1.1},
    },
    "Grapes": {
        "category": "Fruits",
        "base_demand_kg": 600.0,
        "base_price_rs": 90.0,
        "base_shelf_life_days": 12,
        "optimal_temp_c": 10.0,
        "seasonal_multipliers": {"Summer": 1.3, "Monsoon": 0.4, "Winter": 1.2, "Spring": 1.6},
    },
    "Apple": {
        "category": "Fruits",
        "base_demand_kg": 1000.0,
        "base_price_rs": 140.0,
        "base_shelf_life_days": 30,
        "optimal_temp_c": 6.0,
        "seasonal_multipliers": {"Summer": 0.9, "Monsoon": 1.0, "Winter": 1.5, "Spring": 1.1},
    },
    "Orange": {
        "category": "Fruits",
        "base_demand_kg": 900.0,
        "base_price_rs": 60.0,
        "base_shelf_life_days": 20,
        "optimal_temp_c": 10.0,
        "seasonal_multipliers": {"Summer": 0.8, "Monsoon": 0.9, "Winter": 1.7, "Spring": 1.2},
    },
}


def get_season(month: int) -> str:
    if month in (3, 4, 5):
        return "Summer"
    elif month in (6, 7, 8, 9):
        return "Monsoon"
    elif month in (10, 11):
        return "Spring"
    else:
        return "Winter"


def generate_synthetic_dataset() -> list[HistoricalSupplyChainData]:
    """
    Generates a deterministic synthetic dataset of historical supply chain observations
    with realistic relationships between seasons, weather, age, demand, price, and spoilage.
    """
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    total_days = (END_DATE - START_DATE).days + 1
    products = list(PRODUCT_PROFILES.keys())

    records = []

    for i in range(TOTAL_TARGET_RECORDS):
        # Sample random date within range
        day_offset = random.randint(0, total_days - 1)
        curr_date = START_DATE + timedelta(days=day_offset)

        day_of_week = curr_date.weekday()
        month = curr_date.month
        season = get_season(month)

        # Sample product
        product_name = random.choice(products)
        profile = PRODUCT_PROFILES[product_name]
        category = profile["category"]

        # Environmental Features (Temperature & Humidity with seasonal variance)
        if season == "Summer":
            temp = float(np.random.normal(30.0, 3.5))
            hum = float(np.random.normal(55.0, 8.0))
        elif season == "Monsoon":
            temp = float(np.random.normal(25.0, 2.5))
            hum = float(np.random.normal(85.0, 6.0))
        elif season == "Winter":
            temp = float(np.random.normal(16.0, 3.0))
            hum = float(np.random.normal(60.0, 7.0))
        else:  # Spring
            temp = float(np.random.normal(23.0, 3.0))
            hum = float(np.random.normal(62.0, 7.0))

        temp = round(max(4.0, min( temp, 42.0)), 1)
        hum = round(max(20.0, min(hum, 98.0)), 1)

        # Inventory Storage State
        max_shelf = profile["base_shelf_life_days"]
        age_days = random.randint(1, max(2, int(max_shelf * 1.2)))
        remaining_shelf = max_shelf - age_days

        inv_qty = round(float(np.random.normal(profile["base_demand_kg"] * 1.2, 200.0)), 1)
        inv_qty = max(100.0, inv_qty)

        supply_qty = round(float(np.random.normal(profile["base_demand_kg"] * 1.1, 180.0)), 1)
        supply_qty = max(100.0, supply_qty)

        # Historical Demand (Lagged feature)
        hist_demand = round(float(np.random.normal(profile["base_demand_kg"], 150.0)), 1)
        hist_demand = max(50.0, hist_demand)

        # Target A: Demand Quantity
        season_mult = profile["seasonal_multipliers"][season]
        weekend_mult = 1.2 if day_of_week in (5, 6) else 1.0
        demand_noise = np.random.normal(0, profile["base_demand_kg"] * 0.08)

        target_demand = (profile["base_demand_kg"] * season_mult * weekend_mult) + demand_noise
        target_demand = round(max(50.0, target_demand), 1)

        # Target B: Price Per Kg
        price_noise = np.random.normal(0, profile["base_price_rs"] * 0.06)
        supply_demand_ratio = target_demand / supply_qty
        target_price = profile["base_price_rs"] * (1.0 + 0.25 * (supply_demand_ratio - 1.0)) + price_noise
        target_price = round(max(10.0, target_price), 2)

        # Target C: Spoilage Indicator (Logistic Probability)
        z = (
            -3.8
            + 0.12 * (temp - profile["optimal_temp_c"])
            + 0.06 * (hum - 65.0)
            + 0.18 * (age_days - 5)
            - 0.22 * remaining_shelf
        )
        prob_spoilage = 1.0 / (1.0 + math.exp(-z))
        target_spoilage = 1 if random.random() < prob_spoilage else 0

        rec = HistoricalSupplyChainData(
            record_date=curr_date,
            product_name=product_name,
            category=category,
            day_of_week=day_of_week,
            month=month,
            season=season,
            temperature=temp,
            humidity=hum,
            inventory_age_days=age_days,
            remaining_shelf_life_days=remaining_shelf,
            inventory_quantity_kg=inv_qty,
            historical_demand_kg=hist_demand,
            supply_quantity_kg=supply_qty,
            target_demand_quantity_kg=target_demand,
            target_price_per_kg=target_price,
            target_spoilage_indicator=target_spoilage,
        )
        records.append(rec)

    # Sort records chronologically
    records.sort(key=lambda r: (r.record_date, r.product_name))
    return records


def main():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        print("Clearing prior synthetic historical observations...")
        db.query(HistoricalSupplyChainData).delete()
        db.commit()

        print(f"Generating {TOTAL_TARGET_RECORDS} reproducible synthetic historical observations (Seed={RANDOM_SEED})...")
        records = generate_synthetic_dataset()

        print(f"Inserting {len(records)} records into PostgreSQL database...")
        db.add_all(records)
        db.commit()

        # Compute Summary Statistics
        count = db.query(HistoricalSupplyChainData).count()
        min_date = db.query(HistoricalSupplyChainData.record_date).order_by(HistoricalSupplyChainData.record_date.asc()).first()[0]
        max_date = db.query(HistoricalSupplyChainData.record_date).order_by(HistoricalSupplyChainData.record_date.desc()).first()[0]
        products = db.query(HistoricalSupplyChainData.product_name).distinct().all()
        product_list = [p[0] for p in products]

        avg_demand = db.query(HistoricalSupplyChainData.target_demand_quantity_kg).all()
        avg_demand_val = round(sum(d[0] for d in avg_demand) / count, 1)

        avg_price = db.query(HistoricalSupplyChainData.target_price_per_kg).all()
        avg_price_val = round(sum(p[0] for p in avg_price) / count, 2)

        avg_temp = db.query(HistoricalSupplyChainData.temperature).all()
        avg_temp_val = round(sum(t[0] for t in avg_temp) / count, 1)

        avg_hum = db.query(HistoricalSupplyChainData.humidity).all()
        avg_hum_val = round(sum(h[0] for h in avg_hum) / count, 1)

        spoilage_items = db.query(HistoricalSupplyChainData.target_spoilage_indicator).all()
        spoilage_count = sum(s[0] for s in spoilage_items)
        spoilage_rate = round((spoilage_count / count) * 100, 1)

        print("\n==================================================")
        print("SYNTHETIC HISTORICAL DATA GENERATION COMPLETE")
        print("==================================================")
        print(f"Total records inserted: {count}")
        print(f"Date range: {min_date} to {max_date}")
        print(f"Products ({len(product_list)}): {', '.join(product_list)}")
        print(f"Average target demand: {avg_demand_val} kg")
        print(f"Average target price: Rs {avg_price_val} / kg")
        print(f"Average temperature: {avg_temp_val} C")
        print(f"Average humidity: {avg_hum_val} %")
        print(f"Spoilage rate: {spoilage_rate} % ({spoilage_count}/{count} lots spoiled)")
        print("==================================================")

    except Exception as e:
        db.rollback()
        print(f"Generation failed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    main()
