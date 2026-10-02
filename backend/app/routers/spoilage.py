from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.batch import Batch
from app.models.inventory import Inventory
from app.schemas.spoilage import (
    InventorySpoilageRisk,
    SpoilageSummary,
    SpoilageMLPredictRequest,
    SpoilageMLPredictResponse,
    SpoilageMLModelSummaryResponse,
    CombinedSpoilageAnalysisResponse,
)
from app.services.spoilage_service import (
    get_all_spoilage_evaluations,
    get_spoilage_summary_analytics,
)
from app.services.spoilage_ml_service import (
    predict_spoilage_single,
    get_spoilage_ml_model_summary,
)
from app.services.auth_service import require_roles

router = APIRouter(prefix="/spoilage", tags=["Spoilage Intelligence"])


# ==========================================
# PART 4.2 RULE-BASED SPOILAGE ENDPOINTS
# ==========================================

@router.get("/risk", response_model=List[InventorySpoilageRisk])
def get_spoilage_risk(
    inventory_id: Optional[int] = Query(None, description="Filter risk for a specific inventory ID"),
    batch_id: Optional[int] = Query(None, description="Filter risk for a specific batch ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Evaluates rule-based spoilage risk for active PostgreSQL inventory items.
    Returns 0-100 risk score, risk level ('High', 'Medium', 'Low'), explainable risk factors,
    and operational supply-chain recommendations.
    """
    if current_user.role == "farmer":
        if batch_id is not None:
            target_batch = db.query(Batch).filter(Batch.id == batch_id).first()
            if target_batch and target_batch.farmer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only view risk data for your own batches."
                )
        if inventory_id is not None:
            target_inv = db.query(Inventory).filter(Inventory.id == inventory_id).first()
            if target_inv and target_inv.batch and target_inv.batch.farmer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only view risk data for your own inventory."
                )
        evaluations = get_all_spoilage_evaluations(
            db,
            inventory_id=inventory_id,
            batch_id=batch_id,
            farmer_id=current_user.id
        )
    else:
        evaluations = get_all_spoilage_evaluations(
            db,
            inventory_id=inventory_id,
            batch_id=batch_id
        )
    return evaluations


@router.get("/summary", response_model=SpoilageSummary)
def get_spoilage_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Returns aggregate spoilage-risk metrics across inventory lots in PostgreSQL,
    including total count, risk breakdown, average risk score, and highest-risk batches.
    """
    if current_user.role == "farmer":
        summary = get_spoilage_summary_analytics(db, farmer_id=current_user.id)
    else:
        summary = get_spoilage_summary_analytics(db)
    return summary


# ==========================================
# PART 4.6 ML SPOILAGE ENDPOINTS
# ==========================================

@router.post("/ml-predict", response_model=SpoilageMLPredictResponse)
def predict_spoilage_ml(
    payload: SpoilageMLPredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Predicts binary spoilage classification indicator (0=Healthy, 1=Spoiled)
    and output probabilities using trained Random Forest Classifier pipeline.
    """
    if current_user.role == "farmer":
        if payload.batch_id is not None:
            batch = db.query(Batch).filter(Batch.id == payload.batch_id).first()
            if batch and batch.farmer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only request ML spoilage predictions for your own batches."
                )
        if payload.inventory_id is not None:
            inv = db.query(Inventory).filter(Inventory.id == payload.inventory_id).first()
            if inv and inv.batch and inv.batch.farmer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only request ML spoilage predictions for your own inventory."
                )
    try:
        res = predict_spoilage_single(payload.dict())
        return SpoilageMLPredictResponse(
            predicted_spoilage=res["predicted_spoilage"],
            spoilage_probability=res["spoilage_probability"],
            healthy_probability=res["healthy_probability"],
            model_name=res["model_name"],
            disclaimer="ML spoilage prediction trained on synthetic demonstration dataset."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Spoilage Prediction Error: {str(e)}")


@router.get("/ml-model-summary", response_model=SpoilageMLModelSummaryResponse)
def get_spoilage_model_summary_api(
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Returns trained Random Forest Spoilage model metrics, class distribution,
    baseline performance, top feature importances, and train/test metadata.
    """
    try:
        summary = get_spoilage_ml_model_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load ML model summary: {str(e)}")


@router.post("/analyze", response_model=CombinedSpoilageAnalysisResponse)
def analyze_spoilage_combined(
    payload: SpoilageMLPredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Combined analysis endpoint returning BOTH Part 4.2 Rule-Based Risk Intelligence
    and Part 4.6 ML Classification probabilities for given item parameters.
    """
    if current_user.role == "farmer":
        if payload.batch_id is not None:
            batch = db.query(Batch).filter(Batch.id == payload.batch_id).first()
            if batch and batch.farmer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only request spoilage analysis for your own batches."
                )
        if payload.inventory_id is not None:
            inv = db.query(Inventory).filter(Inventory.id == payload.inventory_id).first()
            if inv and inv.batch and inv.batch.farmer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only request spoilage analysis for your own inventory."
                )
    try:
        # ML Prediction
        ml_res = predict_spoilage_single(payload.dict())
        ml_response = SpoilageMLPredictResponse(
            predicted_spoilage=ml_res["predicted_spoilage"],
            spoilage_probability=ml_res["spoilage_probability"],
            healthy_probability=ml_res["healthy_probability"],
            model_name=ml_res["model_name"],
            disclaimer="ML spoilage prediction trained on synthetic demonstration dataset."
        )

        # Basic Rule-Based estimation for given request inputs
        temp = payload.temperature
        hum = payload.humidity
        rem_days = payload.remaining_shelf_life_days
        age_days = payload.inventory_age_days

        factors = []
        score = 0
        if rem_days <= 2:
            score += 35
            factors.append({"factor": "Shelf Life", "impact": 35, "message": f"Critical shelf-life: {rem_days} days left."})
        elif rem_days <= 5:
            score += 25
            factors.append({"factor": "Shelf Life", "impact": 25, "message": f"Short shelf-life: {rem_days} days left."})

        if temp >= 22.0:
            score += 30
            factors.append({"factor": "Temperature", "impact": 30, "message": f"Storage temp of {temp}°C is elevated."})
        elif temp >= 18.0:
            score += 18
            factors.append({"factor": "Temperature", "impact": 18, "message": f"Storage temp of {temp}°C slightly warm."})

        if hum > 75.0:
            score += 15
            factors.append({"factor": "Humidity", "impact": 15, "message": f"Humidity of {hum}% increases mold risk."})

        if age_days > 10:
            score += 15
            factors.append({"factor": "Inventory Age", "impact": 15, "message": f"Inventory age {age_days} days."})

        final_score = min(max(score, 0), 100)
        risk_lvl = "High" if final_score >= 60 else ("Medium" if final_score >= 30 else "Low")

        rule_based_res = {
            "risk_score": final_score,
            "risk_level": risk_lvl,
            "factors": factors,
            "recommendation": "Priority dispatch required" if final_score >= 60 else "Routine cold chain monitoring"
        }

        return CombinedSpoilageAnalysisResponse(
            rule_based=rule_based_res,
            ml_prediction=ml_response,
            disclaimer="Combined analysis featuring both Part 4.2 Rule-Based Risk Intelligence and Part 4.6 ML Classification."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Combined Spoilage Analysis Error: {str(e)}")

