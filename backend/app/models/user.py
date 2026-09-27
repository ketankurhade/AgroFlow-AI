from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    COLLECTION_MANAGER = "collection_manager"
    WAREHOUSE_MANAGER = "warehouse_manager"
    DISTRIBUTOR = "distributor"
    RETAILER = "retailer"
    ADMIN = "admin"
    CONSUMER = "consumer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.CONSUMER.value)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    batches = relationship("Batch", back_populates="farmer", foreign_keys="[Batch.farmer_id]")
    orders = relationship("Order", back_populates="buyer", foreign_keys="[Order.buyer_id]")
