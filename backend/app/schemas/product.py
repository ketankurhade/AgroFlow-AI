from datetime import datetime
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    category: str
    unit: str = "kg"


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    unit: str
    created_at: datetime

    class Config:
        from_attributes = True
