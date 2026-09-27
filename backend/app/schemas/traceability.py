from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TraceabilityEventCreate(BaseModel):
    batch_id: int
    stage: str
    location: str
    description: Optional[str] = None
    timestamp: Optional[datetime] = None


class TraceabilityEventResponse(BaseModel):
    id: int
    batch_id: int
    stage: str
    location: str
    description: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
