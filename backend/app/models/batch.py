from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_code = Column(String(80), unique=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    quality_grade = Column(String(20), nullable=False, default="Grade A")
    harvest_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    origin_location = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="Harvested")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="batches")
    farmer = relationship("User", back_populates="batches", foreign_keys=[farmer_id])
    inventory_records = relationship("Inventory", back_populates="batch", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="batch", cascade="all, delete-orphan")
    traceability_events = relationship("TraceabilityEvent", back_populates="batch", cascade="all, delete-orphan")
