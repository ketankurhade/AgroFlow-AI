from datetime import date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.inventory import Inventory
from app.models.batch import Batch
from app.models.product import Product


def evaluate_inventory_spoilage_risk(item: Inventory) -> Dict[str, Any]:
    """
    Evaluates rule-based spoilage risk for a single Inventory item and its associated Batch.
    Calculates a 0-100 risk score, risk level ('High', 'Medium', 'Low'), explainable risk factors,
    and operational supply-chain recommendations.
    """
    batch: Optional[Batch] = item.batch
    today = date.today()

    batch_code = batch.batch_code if batch else f"BATCH-{item.batch_id}"
    product_name = batch.product.name if batch and batch.product else "Agricultural Produce"
    category = batch.product.category if batch and batch.product else "General"
    harvest_date_str = str(batch.harvest_date) if batch and batch.harvest_date else str(today)
    expiry_date_str = str(batch.expiry_date) if batch and batch.expiry_date else str(today)

    # Date Calculations
    if batch and batch.expiry_date:
        remaining_days = (batch.expiry_date - today).days
    else:
        remaining_days = 30

    if batch and batch.harvest_date:
        inventory_age_days = max((today - batch.harvest_date).days, 0)
    else:
        inventory_age_days = 0

    factors = []
    total_impact = 0

    # 1. SHELF-LIFE RISK FACTOR (Max 50 points)
    if remaining_days < 0:
        impact = 50
        msg = f"Batch is EXPIRED by {abs(remaining_days)} day(s)!"
    elif remaining_days == 0:
        impact = 45
        msg = "Batch expires TODAY!"
    elif remaining_days <= 2:
        impact = 35
        msg = f"Critical shelf-life remaining: only {remaining_days} day(s) left before expiry."
    elif remaining_days <= 5:
        impact = 25
        msg = f"Short shelf-life: {remaining_days} day(s) remaining before expiry."
    elif remaining_days <= 10:
        impact = 15
        msg = f"Moderate shelf-life left: {remaining_days} day(s) remaining."
    else:
        impact = 0
        msg = f"Healthy shelf-life remaining: {remaining_days} day(s)."

    if impact > 0:
        factors.append({
            "factor": "Shelf Life",
            "impact": impact,
            "message": msg
        })
    total_impact += impact

    # 2. TEMPERATURE RISK FACTOR (Max 30 points)
    temp = item.temperature
    if temp is not None:
        # Category-aware baseline threshold (e.g. Grains tolerate higher temp than Fruits/Veg)
        if "grain" in category.lower() or "pulse" in category.lower():
            temp_high_thresh = 28.0
            temp_warn_thresh = 22.0
        else:
            temp_high_thresh = 22.0
            temp_warn_thresh = 18.0

        if temp >= temp_high_thresh:
            impact = 30
            msg = f"Storage temperature of {temp}°C exceeds max safe limit ({temp_high_thresh}°C)."
        elif temp >= temp_warn_thresh:
            impact = 18
            msg = f"Elevated storage temperature of {temp}°C above target limit ({temp_warn_thresh}°C)."
        elif temp > 15.0:
            impact = 8
            msg = f"Slightly warm storage temperature of {temp}°C."
        else:
            impact = 0
            msg = f"Storage temperature of {temp}°C is optimal."

        if impact > 0:
            factors.append({
                "factor": "Temperature",
                "impact": impact,
                "message": msg
            })
        total_impact += impact

    # 3. HUMIDITY RISK FACTOR (Max 15 points)
    hum = item.humidity
    if hum is not None:
        if hum > 80.0:
            impact = 15
            msg = f"High relative humidity of {hum}% increases fungal/mold growth risk."
        elif hum > 72.0:
            impact = 8
            msg = f"Moderate relative humidity of {hum}% slightly above optimal."
        else:
            impact = 0
            msg = f"Relative humidity of {hum}% is within safe bounds."

        if impact > 0:
            factors.append({
                "factor": "Humidity",
                "impact": impact,
                "message": msg
            })
        total_impact += impact

    # 4. INVENTORY AGE RISK FACTOR (Max 15 points)
    if inventory_age_days > 14:
        impact = 15
        msg = f"Batch is {inventory_age_days} days old since harvest."
    elif inventory_age_days > 7:
        impact = 8
        msg = f"Batch was harvested {inventory_age_days} days ago."
    else:
        impact = 0
        msg = f"Recently harvested ({inventory_age_days} days ago)."

    if impact > 0:
        factors.append({
            "factor": "Inventory Age",
            "impact": impact,
            "message": msg
        })
    total_impact += impact

    # Final score bounded strictly to 0..100
    risk_score = min(max(total_impact, 0), 100)

    # Risk level classification
    if risk_score >= 60:
        risk_level = "High"
        recommendation = "Prioritize immediate dispatch, liquidation, or sale within 24-48 hours."
    elif risk_score >= 30:
        risk_level = "Medium"
        recommendation = "Monitor storage conditions closely and consider earlier dispatch allocation."
    else:
        risk_level = "Low"
        recommendation = "Normal cold chain monitoring recommended."

    return {
        "inventory_id": item.id,
        "batch_id": item.batch_id,
        "batch_code": batch_code,
        "product_name": product_name,
        "category": category,
        "warehouse_location": item.warehouse_location,
        "quantity": item.quantity,
        "temperature": item.temperature,
        "humidity": item.humidity,
        "harvest_date": harvest_date_str,
        "expiry_date": expiry_date_str,
        "remaining_shelf_life_days": remaining_days,
        "inventory_age_days": inventory_age_days,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "factors": factors,
        "recommendation": recommendation,
    }


def get_all_spoilage_evaluations(
    db: Session,
    inventory_id: Optional[int] = None,
    batch_id: Optional[int] = None,
    farmer_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Queries inventory items from PostgreSQL database and computes spoilage risk evaluations for each.
    """
    query = db.query(Inventory).options(
        joinedload(Inventory.batch).joinedload(Batch.product)
    )

    if farmer_id is not None:
        query = query.join(Inventory.batch).filter(Batch.farmer_id == farmer_id)

    if inventory_id is not None:
        query = query.filter(Inventory.id == inventory_id)
    if batch_id is not None:
        query = query.filter(Inventory.batch_id == batch_id)

    inventory_items = query.all()
    results = [evaluate_inventory_spoilage_risk(item) for item in inventory_items]

    # Sort descending by risk_score
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results


def get_spoilage_summary_analytics(db: Session, farmer_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Computes summary statistics for spoilage risk across PostgreSQL inventory items.
    """
    evaluations = get_all_spoilage_evaluations(db, farmer_id=farmer_id)

    total_analyzed = len(evaluations)
    if total_analyzed == 0:
        return {
            "total_analyzed": 0,
            "low_risk_count": 0,
            "medium_risk_count": 0,
            "high_risk_count": 0,
            "average_risk_score": 0.0,
            "highest_risk_batches": [],
            "disclaimer": (
                "Rule-based spoilage-risk intelligence derived from current inventory temperature, "
                "humidity, harvest date, and expiry date stored in PostgreSQL. Not an ML model or "
                "scientifically certified guarantee."
            )
        }

    low_count = sum(1 for e in evaluations if e["risk_level"] == "Low")
    medium_count = sum(1 for e in evaluations if e["risk_level"] == "Medium")
    high_count = sum(1 for e in evaluations if e["risk_level"] == "High")

    total_score = sum(e["risk_score"] for e in evaluations)
    avg_score = round(total_score / total_analyzed, 1)

    # Top 5 highest risk items
    highest_risk = evaluations[:5]

    return {
        "total_analyzed": total_analyzed,
        "low_risk_count": low_count,
        "medium_risk_count": medium_count,
        "high_risk_count": high_count,
        "average_risk_score": avg_score,
        "highest_risk_batches": highest_risk,
        "disclaimer": (
            "Rule-based spoilage-risk intelligence derived from current inventory temperature, "
            "humidity, harvest date, and expiry date stored in PostgreSQL. Not an ML model or "
            "scientifically certified guarantee."
        )
    }
