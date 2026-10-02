from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.schemas.intelligence import (
    IntelligenceAnalyzeRequest,
    IntelligenceAnalyzeResponse,
)
from app.services.intelligence_service import analyze_inventory_intelligence
from app.services.auth_service import require_roles

router = APIRouter(prefix="/intelligence", tags=["Intelligence Integration & Decision Layer"])


@router.post("/analyze", response_model=IntelligenceAnalyzeResponse)
def analyze_intelligence(
    payload: IntelligenceAnalyzeRequest,
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer"))
):
    """
    Orchestrates existing intelligence modules (Demand ML, Price ML, Rule-Based Spoilage,
    ML Spoilage Classifier, and optional Route Optimization) into a unified operational decision.
    """
    try:
        payload_dict = payload.dict()
        result = analyze_inventory_intelligence(payload_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence Analysis Error: {str(e)}")

