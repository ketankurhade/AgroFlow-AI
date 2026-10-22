from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.traceability import TraceabilityEvent
from app.models.batch import Batch
from app.models.user import User
from app.schemas.traceability import TraceabilityEventCreate, TraceabilityEventResponse
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/traceability", tags=["Traceability"])


from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.shipment import Shipment


@router.get("/batch/{batch_id}", response_model=List[TraceabilityEventResponse])
def get_traceability_events_by_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {batch_id} not found"
        )
    if current_user.role == "farmer" and batch.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Farmers can only view traceability events for their own batches."
        )
    if current_user.role == "retailer":
        is_ret_inv = db.query(Inventory).filter(Inventory.batch_id == batch.id, Inventory.owner_id == current_user.id).first()
        is_ret_order = (
            db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(OrderItem.batch_id == batch.id, (Order.buyer_id == current_user.id) | (Order.retailer_id == current_user.id))
            .first()
        )
        is_ret_ship = (
            db.query(Shipment)
            .join(Order, Shipment.order_id == Order.id)
            .filter(Shipment.batch_id == batch.id, (Order.buyer_id == current_user.id) | (Order.retailer_id == current_user.id))
            .first()
        )
        is_upstream_avail = (batch.quantity > 0 and batch.status not in ["Consumed", "Depleted"])
        if not (is_ret_inv or is_ret_order or is_ret_ship or is_upstream_avail):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Retailers can only view traceability events for their own inventory, orders, or available stock."
            )
    if current_user.role == "consumer":
        is_cons_order = (
            db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(OrderItem.batch_id == batch.id, Order.buyer_id == current_user.id)
            .first()
        )
        is_ret_avail = (
            db.query(Inventory)
            .join(User, Inventory.owner_id == User.id)
            .filter(Inventory.batch_id == batch.id, User.role == "retailer", Inventory.quantity > 0)
            .first()
        )
        if not (is_cons_order or is_ret_avail):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Consumers can only view traceability events for their purchased orders or available retail stock."
            )

    events = (
        db.query(TraceabilityEvent)
        .filter(TraceabilityEvent.batch_id == batch_id)
        .order_by(TraceabilityEvent.timestamp.asc())
        .all()
    )
    return events


@router.post("/events", response_model=TraceabilityEventResponse, status_code=status.HTTP_201_CREATED)
def create_traceability_event(
    event_data: TraceabilityEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    batch = db.query(Batch).filter(Batch.id == event_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {event_data.batch_id} not found"
        )
    
    event = TraceabilityEvent(
        batch_id=event_data.batch_id,
        stage=event_data.stage,
        location=event_data.location,
        description=event_data.description
    )
    if event_data.timestamp:
        event.timestamp = event_data.timestamp

    db.add(event)
    db.commit()
    db.refresh(event)
    return event

