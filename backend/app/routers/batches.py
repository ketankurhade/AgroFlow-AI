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
from app.models.order import Order, OrderItem
from app.models.shipment import Shipment
from app.schemas.batch import BatchCreate, BatchResponse
from app.services.auth_service import require_roles

router = APIRouter(prefix="/batches", tags=["Batches"])


@router.get("", response_model=List[BatchResponse])
def get_batches(
    farmer_id: Optional[int] = Query(None, description="Optional filter by farmer ID"),
    available_only: bool = Query(False, description="Filter only active non-zero available batches"),
    unintaked_only: bool = Query(False, description="Filter batches eligible for initial storage intake (no active storage inventory)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer", "consumer"))
):
    query = db.query(Batch)
    if unintaked_only:
        active_storage_batch_ids = [
            r[0] for r in db.query(Inventory.batch_id)
            .filter(Inventory.owner_id.is_(None), Inventory.quantity > 0)
            .all() if r[0]
        ]
        query = query.filter(
            Batch.id.notin_(active_storage_batch_ids),
            Batch.quantity > 0,
            Batch.status.notin_(["Consumed", "Depleted", "Dispatched", "In Transit", "Delivered"])
        )

    if current_user.role == "farmer":
        query = query.filter(Batch.farmer_id == current_user.id)
    elif farmer_id is not None:
        query = query.filter(Batch.farmer_id == farmer_id)
    elif current_user.role == "retailer":
        if available_only:
            query = query.filter(Batch.quantity > 0, Batch.status.notin_(["Consumed", "Depleted"]))
        else:
            # Batches owned by retailer via inventory OR orders/shipments
            ret_inv_batch_ids = [r[0] for r in db.query(Inventory.batch_id).filter(Inventory.owner_id == current_user.id).all() if r[0]]
            ret_order_batch_ids = [
                r[0] for r in db.query(OrderItem.batch_id)
                .join(Order, OrderItem.order_id == Order.id)
                .filter((Order.buyer_id == current_user.id) | (Order.retailer_id == current_user.id))
                .filter(OrderItem.batch_id.isnot(None)).all() if r[0]
            ]
            ret_shipment_batch_ids = [
                r[0] for r in db.query(Shipment.batch_id)
                .join(Order, Shipment.order_id == Order.id)
                .filter((Order.buyer_id == current_user.id) | (Order.retailer_id == current_user.id))
                .filter(Shipment.batch_id.isnot(None)).all() if r[0]
            ]
            allowed_ids = list(set(ret_inv_batch_ids + ret_order_batch_ids + ret_shipment_batch_ids))
            query = query.filter(Batch.id.in_(allowed_ids))
    elif current_user.role == "consumer":
        if available_only:
            ret_avail_batch_ids = [
                r[0] for r in db.query(Inventory.batch_id)
                .join(User, Inventory.owner_id == User.id)
                .filter(User.role == "retailer", Inventory.quantity > 0).all() if r[0]
            ]
            query = query.filter(Batch.id.in_(ret_avail_batch_ids))
        else:
            cons_order_batch_ids = [
                r[0] for r in db.query(OrderItem.batch_id)
                .join(Order, OrderItem.order_id == Order.id)
                .filter(Order.buyer_id == current_user.id)
                .filter(OrderItem.batch_id.isnot(None)).all() if r[0]
            ]
            ret_avail_batch_ids = [
                r[0] for r in db.query(Inventory.batch_id)
                .join(User, Inventory.owner_id == User.id)
                .filter(User.role == "retailer", Inventory.quantity > 0).all() if r[0]
            ]
            allowed_ids = list(set(cons_order_batch_ids + ret_avail_batch_ids))
            query = query.filter(Batch.id.in_(allowed_ids))

    if available_only and current_user.role not in ["retailer", "consumer"]:
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
                detail="Access denied: Retailers can only access batches in their inventory, orders, or upstream catalog."
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
                detail="Access denied: Consumers can only access batches for their purchased orders or available retail stock."
            )
    return batch

