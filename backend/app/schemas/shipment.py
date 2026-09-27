from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.order import OrderResponse
from app.schemas.batch import BatchResponse


class ShipmentCreate(BaseModel):
    order_id: int
    batch_id: int
    source: str
    destination: str
    vehicle_number: str
    status: str = "In Transit"
    dispatched_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    batch_id: int
    source: str
    destination: str
    vehicle_number: str
    status: str
    dispatched_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    order: Optional[OrderResponse] = None
    batch: Optional[BatchResponse] = None

    class Config:
        from_attributes = True
