from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    warehouse_location = Column(String(200), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    batch = relationship("Batch", back_populates="inventory_records")
    owner = relationship("User", foreign_keys=[owner_id])
