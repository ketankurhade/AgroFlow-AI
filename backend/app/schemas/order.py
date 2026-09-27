from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.user import UserResponse
from app.schemas.product import ProductResponse


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: float
    price: float


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: float
    price: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    order_number: str
    buyer_id: int
    items: List[OrderItemCreate]
    status: str = "Pending"


class OrderResponse(BaseModel):
    id: int
    order_number: str
    buyer_id: int
    status: str
    total_quantity: float
    total_amount: float
    order_date: datetime
    buyer: Optional[UserResponse] = None
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
