from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)
    category = Column(String(80), nullable=False)
    unit = Column(String(20), nullable=False, default="kg")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    batches = relationship("Batch", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
