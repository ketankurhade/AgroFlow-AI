from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.batch import BatchResponse


class InventoryCreate(BaseModel):
    batch_id: int
    warehouse_location: str
    quantity: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    owner_id: Optional[int] = None


class InventoryResponse(BaseModel):
    id: int
    batch_id: int
    warehouse_location: str
    quantity: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    owner_id: Optional[int] = None
    updated_at: datetime
    batch: Optional[BatchResponse] = None

    class Config:
        from_attributes = True
