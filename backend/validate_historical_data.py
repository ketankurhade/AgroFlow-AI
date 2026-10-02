import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.historical_data import HistoricalSupplyChainData

EXPECTED_PRODUCTS = {"Mango", "Tomato", "Potato", "Onion", "Banana", "Grapes", "Apple", "Orange"}


def validate_historical_data():
    db: Session = SessionLocal()
    errors = []

    try:
        print("==================================================")
        print("RUNNING HISTORICAL DATASET QUALITY VALIDATION")
        print("==================================================")

        records = db.query(HistoricalSupplyChainData).all()
        total_count = len(records)

        # 1. Expected row count
        print(f"1. Checking row count ({total_count} records)...")
        if total_count < 3000 or total_count > 5000:
            errors.append(f"Row count out of bounds: expected 3,000–5,000, got {total_count}")

        # 2. Null values check
        print("2. Checking for null values...")
        null_fields = 0
        for r in records:
            if any(getattr(r, col) is None for col in [
                "record_date", "product_name", "category", "day_of_week", "month", "season",
                "temperature", "humidity", "inventory_age_days", "remaining_shelf_life_days",
                "inventory_quantity_kg", "historical_demand_kg", "supply_quantity_kg",
                "target_demand_quantity_kg", "target_price_per_kg", "target_spoilage_indicator"
            ]):
                null_fields += 1
        if null_fields > 0:
            errors.append(f"Found {null_fields} records with unexpected null values.")

        # 3. Non-negative quantities check
        print("3. Checking for non-negative quantities...")
        neg_qty = [r.id for r in records if r.inventory_quantity_kg < 0 or r.supply_quantity_kg < 0 or r.target_demand_quantity_kg < 0]
        if neg_qty:
            errors.append(f"Found {len(neg_qty)} records with negative quantities: IDs {neg_qty[:5]}")

        # 4. Positive prices check
        print("4. Checking positive prices...")
        invalid_prices = [r.id for r in records if r.target_price_per_kg <= 0]
        if invalid_prices:
            errors.append(f"Found {len(invalid_prices)} records with non-positive price: IDs {invalid_prices[:5]}")

        # 5. Temperature bounds check (4.0°C to 45.0°C)
        print("5. Checking temperature bounds (4°C - 45°C)...")
        bad_temps = [r.id for r in records if r.temperature < 4.0 or r.temperature > 45.0]
        if bad_temps:
            errors.append(f"Found {len(bad_temps)} records with out-of-bounds temperature: IDs {bad_temps[:5]}")

        # 6. Humidity bounds check (0% to 100%)
        print("6. Checking humidity bounds (0% - 100%)...")
        bad_hums = [r.id for r in records if r.humidity < 0.0 or r.humidity > 100.0]
        if bad_hums:
            errors.append(f"Found {len(bad_hums)} records with out-of-bounds humidity: IDs {bad_hums[:5]}")

        # 7. Valid dates check
        print("7. Checking date range validity...")
        dates = [r.record_date for r in records]
        min_d, max_d = min(dates), max(dates)
        if min_d.year < 2024 or max_d.year > 2026:
            errors.append(f"Date range invalid: {min_d} to {max_d}")

        # 8. Spoilage indicator values check (0 or 1)
        print("8. Checking spoilage indicator values (0 or 1)...")
        bad_spoilage = [r.id for r in records if r.target_spoilage_indicator not in (0, 1)]
        if bad_spoilage:
            errors.append(f"Found {len(bad_spoilage)} records with invalid spoilage indicator: IDs {bad_spoilage[:5]}")

        # 9. Duplicate rows check
        print("9. Checking duplicate row signatures...")
        signatures = set()
        duplicates = 0
        for r in records:
            sig = (r.record_date, r.product_name, r.inventory_quantity_kg, r.temperature, r.humidity)
            if sig in signatures:
                duplicates += 1
            signatures.add(sig)
        if duplicates > 0:
            errors.append(f"Found {duplicates} duplicate record signatures.")

        # 10. Product distribution check
        print("10. Checking product distribution...")
        found_products = {r.product_name for r in records}
        missing_products = EXPECTED_PRODUCTS - found_products
        if missing_products:
            errors.append(f"Missing expected products: {missing_products}")
        for p in EXPECTED_PRODUCTS:
            count = sum(1 for r in records if r.product_name == p)
            if count < 300:
                errors.append(f"Product '{p}' has insufficient observations: {count} < 300")

        # Summary
        if errors:
            print("\n❌ DATA VALIDATION FAILED WITH ERRORS:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        else:
            print("\n==================================================")
            print("SUCCESS: ALL 10 DATA QUALITY VALIDATIONS PASSED 100%")
            print("==================================================")
            sys.exit(0)

    finally:
        db.close()


if __name__ == "__main__":
    validate_historical_data()
