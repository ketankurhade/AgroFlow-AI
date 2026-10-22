import os
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.shipment import Shipment
from app.models.order import Order
from app.models.batch import Batch
from app.models.user import User
from app.models.inventory import Inventory
from app.models.traceability import TraceabilityEvent
from app.schemas.shipment import ShipmentCreate, ShipmentResponse, ShipmentStatusUpdate
from app.services.auth_service import require_roles

router = APIRouter(prefix="/shipments", tags=["Shipments"])


def get_demo_delivery_minutes() -> float:
    try:
        val = float(os.getenv("AGROFLOW_DEMO_DELIVERY_MINUTES", "1"))
        return val if val > 0 else 1.0
    except Exception:
        return 1.0


def credit_retailer_inventory_if_needed(shipment: Shipment, db: Session) -> bool:
    """
    Credits retailer inventory for a wholesale shipment exactly once and records
    the automatic 'Retail Outlet Delivery' provenance event.
    Uses shipment.is_inventory_credited to guarantee idempotency across all reconciliation and status update paths.
    """
    if getattr(shipment, "is_inventory_credited", False):
        return False

    if not shipment.order:
        return False

    order = shipment.order
    buyer = order.buyer
    if buyer and buyer.role == "retailer" and order.retailer_id is None:
        ret_id = order.buyer_id

        # DB level double-check on shipment.is_inventory_credited
        db_shipment = db.query(Shipment).filter(Shipment.id == shipment.id).first()
        if db_shipment and db_shipment.is_inventory_credited:
            shipment.is_inventory_credited = True
            return False

        existing_inv_list = (
            db.query(Inventory)
            .filter(Inventory.batch_id == shipment.batch_id, Inventory.owner_id == ret_id)
            .order_by(Inventory.id.asc())
            .all()
        )
        if existing_inv_list:
            target_inv = existing_inv_list[0]
            target_inv.quantity += order.total_quantity
            if shipment.destination:
                target_inv.warehouse_location = shipment.destination
            if len(existing_inv_list) > 1:
                for dup in existing_inv_list[1:]:
                    target_inv.quantity += dup.quantity
                    db.delete(dup)
        else:
            new_inv = Inventory(
                batch_id=shipment.batch_id,
                warehouse_location=shipment.destination or "Retail Outlet",
                quantity=order.total_quantity,
                owner_id=ret_id,
                temperature=18.0,
                humidity=65.0,
            )
            db.add(new_inv)

        shipment.is_inventory_credited = True
        if db_shipment:
            db_shipment.is_inventory_credited = True

        # Automatically record 'Retail Outlet Delivery' provenance event exactly once
        existing_outlet_event = (
            db.query(TraceabilityEvent)
            .filter(
                TraceabilityEvent.batch_id == shipment.batch_id,
                TraceabilityEvent.stage == "Retail Outlet Delivery"
            )
            .first()
        )
        if not existing_outlet_event:
            ret_name = buyer.name if buyer else "Retail Store"
            dest_loc = shipment.destination or "Retail Store Outlet"
            event = TraceabilityEvent(
                batch_id=shipment.batch_id,
                stage="Retail Outlet Delivery",
                location=dest_loc,
                description=f"Wholesale shipment for Order #{order.order_number} ({order.total_quantity} kg) delivered and received into store inventory for {ret_name}.",
                timestamp=shipment.delivered_at or datetime.now(timezone.utc)
            )
            db.add(event)

        return True

    return False


def reconcile_overdue_shipments(db: Session):
    """
    Reconciles overdue In Transit wholesale shipments based on expected_delivery_at / demo minutes.
    Transitions status to 'Delivered' and credits retailer inventory EXACTLY ONCE.
    """
    now = datetime.now(timezone.utc)
    in_transit_shipments = (
        db.query(Shipment)
        .filter(Shipment.status.in_(["In Transit", "Dispatched"]), Shipment.is_inventory_credited == False)
        .all()
    )

    if not in_transit_shipments:
        return

    updated = False
    for shipment in in_transit_shipments:
        disp_at = shipment.dispatched_at
        if not disp_at:
            disp_at = now
            shipment.dispatched_at = now

        exp_at = shipment.expected_delivery_at
        if not exp_at:
            exp_at = disp_at + timedelta(minutes=get_demo_delivery_minutes())
            shipment.expected_delivery_at = exp_at

        # Check if simulated transit time has elapsed
        if now >= exp_at:
            shipment.status = "Delivered"
            shipment.delivered_at = exp_at
            if shipment.order:
                shipment.order.status = "Delivered"
                credit_retailer_inventory_if_needed(shipment, db)
            updated = True

    if updated:
        db.commit()


@router.get("", response_model=List[ShipmentResponse])
def get_shipments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "supply_chain_manager", "distributor", "retailer", "consumer"))
):
    reconcile_overdue_shipments(db)
    query = db.query(Shipment)
    if current_user.role in ["consumer", "retailer"]:
        query = query.join(Order, Shipment.order_id == Order.id).filter(Order.buyer_id == current_user.id)
    shipments = query.offset(skip).limit(limit).all()
    return shipments


@router.post("", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
def create_shipment(
    shipment_data: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "supply_chain_manager", "distributor"))
):
    reconcile_overdue_shipments(db)
    order = db.query(Order).filter(Order.id == shipment_data.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {shipment_data.order_id} not found"
        )

    if order.retailer_id is not None or (order.buyer and order.buyer.role == "consumer"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consumer orders are fulfilled directly by retailers and cannot have distributor shipments."
        )

    batch = db.query(Batch).filter(Batch.id == shipment_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {shipment_data.batch_id} not found"
        )

    # Batch-Order product matching validation
    order_product_ids = [item.product_id for item in order.items]
    if order_product_ids and batch.product_id not in order_product_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Selected batch product (ID: {batch.product_id}) does not match order item product."
        )

    # Duplicate shipment protection: check if active shipment exists for this order
    existing_shipment = db.query(Shipment).filter(
        Shipment.order_id == shipment_data.order_id,
        Shipment.status.in_(["Pending", "In Transit", "Dispatched"])
    ).first()
    if existing_shipment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order '{order.order_number}' already has an active shipment ({existing_shipment.status})."
        )

    now = datetime.now(timezone.utc)
    dispatched_at = shipment_data.dispatched_at or now
    expected_delivery_at = shipment_data.expected_delivery_at or (dispatched_at + timedelta(minutes=get_demo_delivery_minutes()))

    shipment = Shipment(
        order_id=shipment_data.order_id,
        batch_id=shipment_data.batch_id,
        source=shipment_data.source,
        destination=shipment_data.destination,
        vehicle_number=shipment_data.vehicle_number,
        status=shipment_data.status,
        dispatched_at=dispatched_at,
        expected_delivery_at=expected_delivery_at,
        delivered_at=shipment_data.delivered_at
    )
    db.add(shipment)

    # Sync order status
    order.status = shipment_data.status

    # Automatic provenance event creation for dispatch
    if shipment_data.status in ["In Transit", "Dispatched"]:
        existing_event = db.query(TraceabilityEvent).filter(
            TraceabilityEvent.batch_id == batch.id,
            TraceabilityEvent.stage == "Dispatch & Transport"
        ).first()
        if not existing_event:
            event = TraceabilityEvent(
                batch_id=batch.id,
                stage="Dispatch & Transport",
                location=shipment_data.source,
                description=f"Shipment dispatched via vehicle {shipment_data.vehicle_number} from {shipment_data.source} to {shipment_data.destination} for Order #{order.order_number}.",
                timestamp=dispatched_at
            )
            db.add(event)

    db.commit()
    db.refresh(shipment)
    return shipment


@router.get("/{id}", response_model=ShipmentResponse)
def get_shipment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "supply_chain_manager", "distributor", "retailer", "consumer"))
):
    reconcile_overdue_shipments(db)
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {id} not found"
        )
    if current_user.role in ["consumer", "retailer"]:
        if not shipment.order or shipment.order.buyer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view shipments for your own orders."
            )
    return shipment


@router.patch("/{id}/status", response_model=ShipmentResponse)
def update_shipment_status(
    id: int,
    status_update: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "supply_chain_manager", "distributor"))
):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {id} not found"
        )
    
    # Idempotency short-circuit: if already delivered and credited, return immediately
    if shipment.status == "Delivered" and status_update.status == "Delivered" and shipment.is_inventory_credited:
        return shipment

    reconcile_overdue_shipments(db)
    shipment = db.query(Shipment).filter(Shipment.id == id).first()

    previous_status = shipment.status
    shipment.status = status_update.status
    now = datetime.now(timezone.utc)

    if status_update.status in ["In Transit", "Dispatched"]:
        if not shipment.dispatched_at:
            shipment.dispatched_at = now
        if not shipment.expected_delivery_at:
            shipment.expected_delivery_at = shipment.dispatched_at + timedelta(minutes=get_demo_delivery_minutes())
        
        if shipment.order:
            shipment.order.status = status_update.status
        
        existing_event = db.query(TraceabilityEvent).filter(
            TraceabilityEvent.batch_id == shipment.batch_id,
            TraceabilityEvent.stage == "Dispatch & Transport"
        ).first()
        if not existing_event:
            order_num = shipment.order.order_number if shipment.order else f"Order #{shipment.order_id}"
            event = TraceabilityEvent(
                batch_id=shipment.batch_id,
                stage="Dispatch & Transport",
                location=shipment.source,
                description=f"Shipment #{shipment.id} dispatched via vehicle {shipment.vehicle_number} to {shipment.destination} for {order_num}.",
                timestamp=shipment.dispatched_at
            )
            db.add(event)
    elif status_update.status == "Delivered":
        if not shipment.delivered_at:
            shipment.delivered_at = now
        if shipment.order:
            shipment.order.status = "Delivered"
            credit_retailer_inventory_if_needed(shipment, db)

    db.commit()
    db.refresh(shipment)
    return shipment
