from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    source = Column(String(200), nullable=False)
    destination = Column(String(200), nullable=False)
    vehicle_number = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="In Transit")
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    expected_delivery_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    is_inventory_credited = Column(Boolean, nullable=False, default=False)

    order = relationship("Order", back_populates="shipments")
    batch = relationship("Batch", back_populates="shipments")
