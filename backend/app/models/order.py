from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(80), unique=True, index=True, nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    retailer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(50), nullable=False, default="Pending")
    total_quantity = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False, default=0.0)
    order_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    buyer = relationship("User", back_populates="orders", foreign_keys=[buyer_id])
    retailer = relationship("User", foreign_keys=[retailer_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    quantity = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=False, default=0.0)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    batch = relationship("Batch", foreign_keys=[batch_id])
