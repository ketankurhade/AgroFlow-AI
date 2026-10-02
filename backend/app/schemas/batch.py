from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.product import ProductResponse
from app.schemas.user import UserResponse


class BatchCreate(BaseModel):
    batch_code: str
    product_id: int
    farmer_id: Optional[int] = None
    quantity: float
    quality_grade: str = "Grade A"
    harvest_date: date
    expiry_date: date
    origin_location: str
    status: str = "Harvested"


class BatchResponse(BaseModel):
    id: int
    batch_code: str
    product_id: int
    farmer_id: int
    quantity: float
    quality_grade: str
    harvest_date: date
    expiry_date: date
    origin_location: str
    status: str
    created_at: datetime
    product: Optional[ProductResponse] = None
    farmer: Optional[UserResponse] = None

    class Config:
        from_attributes = True
