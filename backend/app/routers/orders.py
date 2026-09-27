from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # Check duplicate order number
    existing = db.query(Order).filter(Order.order_number == order_data.order_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order number '{order_data.order_number}' already exists"
        )

    # Check buyer exists
    buyer = db.query(User).filter(User.id == order_data.buyer_id).first()
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Buyer (User) with id {order_data.buyer_id} not found"
        )

    total_qty = sum(item.quantity for item in order_data.items)
    total_amt = sum(item.quantity * item.price for item in order_data.items)

    order = Order(
        order_number=order_data.order_number,
        buyer_id=order_data.buyer_id,
        status=order_data.status,
        total_quantity=total_qty,
        total_amount=total_amt
    )
    db.add(order)
    db.flush()  # get order.id

    for item_data in order_data.items:
        prod = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not prod:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item_data.product_id} not found"
            )
        item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=item_data.price
        )
        db.add(item)

    db.commit()
    db.refresh(order)
    return order


@router.get("/{id}", response_model=OrderResponse)
def get_order(id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    return order
