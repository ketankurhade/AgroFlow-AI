from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.historical_data import HistoricalSupplyChainData
from app.models.user import User
from app.schemas.historical_data import HistoricalDataSummary
from app.services.auth_service import require_roles

router = APIRouter(prefix="/historical-data", tags=["Historical Data"])


@router.get("/summary", response_model=HistoricalDataSummary)
def get_historical_data_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Returns summary statistics for the synthetic historical supply chain dataset stored in PostgreSQL.
    """
    count = db.query(HistoricalSupplyChainData).count()
    if count == 0:
        return HistoricalDataSummary(
            total_records=0,
            start_date="N/A",
            end_date="N/A",
            products=[],
            categories=[],
            avg_demand_kg=0.0,
            avg_price_per_kg=0.0,
            avg_temperature_c=0.0,
            avg_humidity_pct=0.0,
            spoilage_rate_pct=0.0,
        )

    min_date = db.query(HistoricalSupplyChainData.record_date).order_by(HistoricalSupplyChainData.record_date.asc()).first()[0]
    max_date = db.query(HistoricalSupplyChainData.record_date).order_by(HistoricalSupplyChainData.record_date.desc()).first()[0]

    products = [p[0] for p in db.query(HistoricalSupplyChainData.product_name).distinct().all()]
    categories = [c[0] for c in db.query(HistoricalSupplyChainData.category).distinct().all()]

    all_demands = db.query(HistoricalSupplyChainData.target_demand_quantity_kg).all()
    avg_demand = round(sum(d[0] for d in all_demands) / count, 1)

    all_prices = db.query(HistoricalSupplyChainData.target_price_per_kg).all()
    avg_price = round(sum(p[0] for p in all_prices) / count, 2)

    all_temps = db.query(HistoricalSupplyChainData.temperature).all()
    avg_temp = round(sum(t[0] for t in all_temps) / count, 1)

    all_hums = db.query(HistoricalSupplyChainData.humidity).all()
    avg_hum = round(sum(h[0] for h in all_hums) / count, 1)

    spoilage_items = db.query(HistoricalSupplyChainData.target_spoilage_indicator).all()
    spoilage_count = sum(s[0] for s in spoilage_items)
    spoilage_rate = round((spoilage_count / count) * 100, 1)

    return HistoricalDataSummary(
        total_records=count,
        start_date=str(min_date),
        end_date=str(max_date),
        products=products,
        categories=categories,
        avg_demand_kg=avg_demand,
        avg_price_per_kg=avg_price,
        avg_temperature_c=avg_temp,
        avg_humidity_pct=avg_hum,
        spoilage_rate_pct=spoilage_rate,
    )

