from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.models.user import User
from app.schemas.demand import (
    DemandPredictRequest,
    DemandPredictResponse,
    ModelSummaryResponse,
)
from app.services.demand_service import (
    predict_demand_single,
    get_demand_model_summary,
    generate_ml_demand_forecasts,
)
from app.services.auth_service import require_roles

router = APIRouter(prefix="/demand", tags=["ML Demand Forecasting"])


@router.post("/predict", response_model=DemandPredictResponse)
def predict_demand(
    payload: DemandPredictRequest,
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Accepts feature input for a specific agricultural product and storage state, and predicts expected demand in kg using the trained Random Forest Regressor pipeline.
    """
    try:
        feature_dict = payload.model_dump()
        predicted_kg = predict_demand_single(feature_dict)

        return DemandPredictResponse(
            predicted_demand_quantity_kg=predicted_kg,
            model_name="RandomForestRegressor",
            unit="kg",
            disclaimer="ML model prediction trained on synthetic demonstration dataset."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demand forecasting inference failed: {str(e)}"
        )


@router.get("/model-summary", response_model=ModelSummaryResponse)
def get_model_summary(
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Returns training metadata, dataset date ranges, baseline vs Random Forest metrics (MAE, RMSE, R²), and feature importances.
    """
    try:
        summary_data = get_demand_model_summary()
        return summary_data
    except FileNotFoundError as fnf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnf)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model summary: {str(e)}"
        )


@router.get("/forecast")
def get_ml_forecast(
    product_name: str = Query("Mango", description="Agricultural crop product name"),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Returns multi-day ML demand predictions for the specified agricultural crop product.
    """
    try:
        forecasts = generate_ml_demand_forecasts(product_name=product_name)
        return {
            "product_name": product_name,
            "model": "RandomForestRegressor",
            "unit": "kg",
            "forecasts": forecasts,
            "disclaimer": "ML Forecast based on synthetic demonstration dataset."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate demand forecast points: {str(e)}"
        )

