from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.shipment import Shipment
from app.models.order import Order
from app.models.batch import Batch
from app.schemas.shipment import ShipmentCreate, ShipmentResponse

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.get("", response_model=List[ShipmentResponse])
def get_shipments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    shipments = db.query(Shipment).offset(skip).limit(limit).all()
    return shipments


@router.post("", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
def create_shipment(shipment_data: ShipmentCreate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == shipment_data.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {shipment_data.order_id} not found"
        )
    
    batch = db.query(Batch).filter(Batch.id == shipment_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {shipment_data.batch_id} not found"
        )

    shipment = Shipment(
        order_id=shipment_data.order_id,
        batch_id=shipment_data.batch_id,
        source=shipment_data.source,
        destination=shipment_data.destination,
        vehicle_number=shipment_data.vehicle_number,
        status=shipment_data.status,
        dispatched_at=shipment_data.dispatched_at,
        delivered_at=shipment_data.delivered_at
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


@router.get("/{id}", response_model=ShipmentResponse)
def get_shipment(id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {id} not found"
        )
    return shipment
