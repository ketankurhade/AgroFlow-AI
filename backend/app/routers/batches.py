from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.batch import Batch
from app.models.product import Product
from app.models.user import User
from app.models.traceability import TraceabilityEvent
from app.models.inventory import Inventory
from app.schemas.batch import BatchCreate, BatchResponse
from app.services.auth_service import require_roles

router = APIRouter(prefix="/batches", tags=["Batches"])


@router.get("", response_model=List[BatchResponse])
def get_batches(
    farmer_id: Optional[int] = Query(None, description="Optional filter by farmer ID"),
    available_only: bool = Query(False, description="Filter only active non-zero available batches"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer", "consumer"))
):
    query = db.query(Batch)
    if current_user.role == "farmer":
        query = query.filter(Batch.farmer_id == current_user.id)
    elif farmer_id is not None:
        query = query.filter(Batch.farmer_id == farmer_id)

    if available_only or current_user.role in ["retailer", "consumer"]:
        query = query.filter(Batch.quantity > 0, Batch.status.notin_(["Consumed", "Depleted"]))

    batches = query.offset(skip).limit(limit).all()
    return batches


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(
    batch_data: BatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer"))
):
    if current_user.role == "farmer":
        if batch_data.farmer_id is not None and batch_data.farmer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Farmers can only create batches for themselves."
            )
        effective_farmer_id = current_user.id
    else:
        effective_farmer_id = batch_data.farmer_id if batch_data.farmer_id is not None else current_user.id

    # Check if batch_code exists
    existing = db.query(Batch).filter(Batch.batch_code == batch_data.batch_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch code '{batch_data.batch_code}' already exists"
        )
    
    # Check product exists
    product = db.query(Product).filter(Product.id == batch_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {batch_data.product_id} not found"
        )
    
    # Check farmer exists
    farmer = db.query(User).filter(User.id == effective_farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer (User) with id {effective_farmer_id} not found"
        )

    batch = Batch(
        batch_code=batch_data.batch_code,
        product_id=batch_data.product_id,
        farmer_id=effective_farmer_id,
        quantity=batch_data.quantity,
        quality_grade=batch_data.quality_grade,
        harvest_date=batch_data.harvest_date,
        expiry_date=batch_data.expiry_date,
        origin_location=batch_data.origin_location,
        status=batch_data.status
    )
    db.add(batch)
    db.flush()

    # Automatically create the initial Farmer Harvest provenance event within the same transaction
    existing_harvest_event = db.query(TraceabilityEvent).filter(
        TraceabilityEvent.batch_id == batch.id,
        TraceabilityEvent.stage == "Farmer Harvest"
    ).first()

    if not existing_harvest_event:
        harvest_event = TraceabilityEvent(
            batch_id=batch.id,
            stage="Farmer Harvest",
            location=batch.origin_location,
            description=f"Harvest batch {batch.batch_code} ({batch.quality_grade}) created and logged by farmer.",
            timestamp=datetime.now(timezone.utc)
        )
        db.add(harvest_event)

    db.commit()
    db.refresh(batch)
    return batch


@router.get("/{id}", response_model=BatchResponse)
def get_batch(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer", "consumer"))
):
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {id} not found"
        )
    if current_user.role == "farmer" and batch.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Farmers can only access their own batches."
        )
    return batch

