from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.inventory import Inventory
from app.models.batch import Batch
from app.models.user import User
from app.models.traceability import TraceabilityEvent
from app.schemas.inventory import InventoryCreate, InventoryResponse
from app.services.auth_service import require_roles
from app.routers.shipments import reconcile_overdue_shipments

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=List[InventoryResponse])
def get_inventory(
    skip: int = 0,
    limit: int = 100,
    scope: Optional[str] = Query(None, description="Optional scope filter: 'upstream' for unowned storage inventory"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer", "consumer"))
):
    reconcile_overdue_shipments(db)
    if current_user.role == "farmer":
        return []

    query = db.query(Inventory)

    if scope == "upstream" or current_user.role in ["supply_chain_manager", "distributor"]:
        query = query.filter(Inventory.owner_id.is_(None), Inventory.quantity > 0)
    elif current_user.role == "retailer":
        query = query.filter(Inventory.owner_id == current_user.id, Inventory.quantity > 0)
    elif current_user.role == "consumer":
        query = query.join(User, Inventory.owner_id == User.id).filter(User.role == "retailer", Inventory.quantity > 0)
    else:
        query = query.filter(Inventory.quantity > 0)

    inventory_items = query.offset(skip).limit(limit).all()
    return inventory_items


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory(
    inventory_data: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "supply_chain_manager"))
):
    batch = db.query(Batch).filter(Batch.id == inventory_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {inventory_data.batch_id} not found"
        )

    if current_user.role == "farmer" and batch.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farmers can only add inventory for their own batches."
        )
    
    # Check if inventory record already exists for this batch
    existing_inventory = db.query(Inventory).filter(Inventory.batch_id == inventory_data.batch_id).first()
    if existing_inventory:
        existing_inventory.warehouse_location = inventory_data.warehouse_location
        existing_inventory.quantity = inventory_data.quantity
        existing_inventory.temperature = inventory_data.temperature
        existing_inventory.humidity = inventory_data.humidity
        inventory_item = existing_inventory
    else:
        inventory_item = Inventory(
            batch_id=inventory_data.batch_id,
            warehouse_location=inventory_data.warehouse_location,
            quantity=inventory_data.quantity,
            temperature=inventory_data.temperature,
            humidity=inventory_data.humidity
        )
        db.add(inventory_item)

    # Automatically create Cold Storage Intake provenance event for Manager/Admin storage operations
    user_role = current_user.role
    if user_role in ("admin", "supply_chain_manager", "collection_center", "warehouse"):
        if batch.status in ("Harvested", "Pending Storage"):
            batch.status = "In Cold Storage"

        # Check for duplicate Cold Storage Intake event to preserve idempotency
        existing_intake = db.query(TraceabilityEvent).filter(
            TraceabilityEvent.batch_id == batch.id,
            TraceabilityEvent.stage == "Cold Storage Intake"
        ).first()

        if not existing_intake:
            desc = f"Batch received into cold storage facility at {inventory_data.warehouse_location}."
            if inventory_data.temperature is not None:
                desc += f" Monitored temperature: {inventory_data.temperature}°C, RH: {inventory_data.humidity}%."

            intake_event = TraceabilityEvent(
                batch_id=batch.id,
                stage="Cold Storage Intake",
                location=inventory_data.warehouse_location,
                description=desc,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(intake_event)

    db.commit()
    db.refresh(inventory_item)
    return inventory_item


@router.get("/{id}", response_model=InventoryResponse)
def get_inventory_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer", "consumer"))
):
    item = db.query(Inventory).filter(Inventory.id == id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record with id {id} not found"
        )
    if current_user.role == "farmer":
        batch = db.query(Batch).filter(Batch.id == item.batch_id).first()
        if not batch or batch.farmer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Farmers can only access inventory associated with their own batches."
            )
    return item

