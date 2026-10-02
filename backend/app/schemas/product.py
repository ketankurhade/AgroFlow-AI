from datetime import datetime
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    category: str
    unit: str = "kg"
    price: float = 45.0


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    unit: str
    price: float = 45.0
    created_at: datetime

    class Config:
        from_attributes = True
