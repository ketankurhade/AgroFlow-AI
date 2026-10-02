from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.user import UserResponse
from app.schemas.product import ProductResponse


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: float
    price: float
    batch_id: Optional[int] = None


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    batch_id: Optional[int] = None
    quantity: float
    price: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    order_number: Optional[str] = None
    buyer_id: Optional[int] = None
    retailer_id: Optional[int] = None
    items: List[OrderItemCreate]
    status: str = "Pending"


class OrderResponse(BaseModel):
    id: int
    order_number: str
    buyer_id: int
    retailer_id: Optional[int] = None
    status: str
    total_quantity: float
    total_amount: float
    order_date: datetime
    buyer: Optional[UserResponse] = None
    retailer: Optional[UserResponse] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
