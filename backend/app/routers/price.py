from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.models.user import User
from app.schemas.price import (
    PricePredictRequest,
    PricePredictResponse,
    PriceModelSummaryResponse,
)
from app.services.price_service import (
    predict_price_single,
    get_price_model_summary,
    generate_ml_price_forecasts,
)
from app.services.auth_service import require_roles

router = APIRouter(prefix="/price", tags=["ML Price Forecasting"])


@router.post("/predict", response_model=PricePredictResponse)
def predict_price(
    payload: PricePredictRequest,
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Accepts validated pre-target feature input for an agricultural crop and predicts expected wholesale price per kg using the trained Random Forest Regressor pipeline.
    """
    try:
        feature_dict = payload.model_dump()
        predicted_price = predict_price_single(feature_dict)

        return PricePredictResponse(
            predicted_price_per_kg=predicted_price,
            model_name="RandomForestRegressor",
            unit="INR/kg",
            disclaimer="ML price model prediction trained on synthetic demonstration dataset."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Price forecasting inference failed: {str(e)}"
        )


@router.get("/model-summary", response_model=PriceModelSummaryResponse)
def get_model_summary(
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Returns training metadata, dataset date ranges, leakage prevention statement, baseline vs Random Forest metrics (MAE, RMSE, R²), and feature importances.
    """
    try:
        summary_data = get_price_model_summary()
        return summary_data
    except FileNotFoundError as fnf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnf)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve price model summary: {str(e)}"
        )


@router.get("/forecast")
def get_ml_price_forecast(
    product_name: str = Query("Tomato", description="Agricultural crop product name"),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Returns monthly ML wholesale price predictions for the specified agricultural crop product.
    """
    try:
        forecasts = generate_ml_price_forecasts(product_name=product_name)
        return {
            "product_name": product_name,
            "model": "RandomForestRegressor",
            "unit": "INR/kg",
            "forecasts": forecasts,
            "disclaimer": "ML Price Forecast — Synthetic Demonstration"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate price forecast points: {str(e)}"
        )

