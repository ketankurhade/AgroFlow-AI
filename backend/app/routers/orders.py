import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.product import Product
from app.models.shipment import Shipment
from app.models.batch import Batch
from app.models.inventory import Inventory
from app.schemas.order import OrderCreate, OrderResponse
from app.services.auth_service import require_roles
from app.routers.shipments import reconcile_overdue_shipments

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_trusted_catalog_price(product: Product) -> float:
    if hasattr(product, 'price') and product.price and product.price > 0:
        return float(product.price)
    
    CATALOG_PRICES = {
        "Onion": 35.0,
        "Potato": 30.0,
        "Apple": 150.0,
        "Mango": 120.0,
        "Organic Alphonso Mangoes": 120.0,
        "Cavendish Bananas": 40.0,
        "Hass Avocados": 150.0,
        "Fresh Desi Tomatoes": 45.0,
        "Red Onions": 35.0,
        "Cold Storage Potatoes": 30.0,
        "Hydroponic Spinach": 50.0,
        "Super Basmati Rice": 65.0,
    }
    if product.name in CATALOG_PRICES:
        return CATALOG_PRICES[product.name]
    if product.category == "Fruits":
        return 120.0
    elif product.category == "Vegetables":
        return 45.0
    return 45.0


@router.get("", response_model=List[OrderResponse])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer", "consumer"))
):
    reconcile_overdue_shipments(db)
    query = db.query(Order)
    if current_user.role == "farmer":
        query = (
            query.join(Shipment, Order.id == Shipment.order_id)
            .join(Batch, Shipment.batch_id == Batch.id)
            .filter(Batch.farmer_id == current_user.id)
            .distinct()
        )
    elif current_user.role == "consumer":
        query = query.filter(Order.buyer_id == current_user.id)
    elif current_user.role == "retailer":
        query = query.filter(
            (Order.buyer_id == current_user.id) | (Order.retailer_id == current_user.id)
        )
    elif current_user.role == "distributor":
        query = (
            query.join(User, Order.buyer_id == User.id)
            .filter(Order.retailer_id.is_(None), User.role == "retailer")
        )
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "retailer", "consumer"))
):
    # 1. Identity & Status Control: For retailer/consumer, derive buyer_id from JWT & force status
    if current_user.role in ["retailer", "consumer"]:
        buyer_id = current_user.id
        initial_status = "Confirmed"
    else:
        buyer_id = order_data.buyer_id if order_data.buyer_id else current_user.id
        initial_status = order_data.status if order_data.status else "Confirmed"

    buyer = db.query(User).filter(User.id == buyer_id).first()
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Buyer (User) with id {buyer_id} not found"
        )

    # 2. Order Number Control: Ensure uniqueness or auto-generate
    order_num = order_data.order_number.strip() if order_data.order_number else f"ORD-2026-{uuid.uuid4().hex[:8].upper()}"
    existing = db.query(Order).filter(Order.order_number == order_num).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order number '{order_num}' already exists"
        )

    # 3. Item & Quantity Validation + Price Control + Inventory Reservation/Deduction
    if not order_data.items or len(order_data.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one product item."
        )

    prepared_items = []
    total_qty = 0.0
    total_amt = 0.0
    assigned_retailer_id = None

    if current_user.role == "consumer":
        # Consumer purchase from available retailer stock
        for item_data in order_data.items:
            if item_data.quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order quantity must be greater than 0."
                )

            prod = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not prod:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {item_data.product_id} not found"
                )

            trusted_price = get_trusted_catalog_price(prod)
            item_total = item_data.quantity * trusted_price

            # Require stock from explicitly retailer-owned inventory records
            retailer_invs = (
                db.query(Inventory)
                .join(User, Inventory.owner_id == User.id)
                .join(Batch, Inventory.batch_id == Batch.id)
                .filter(User.role == "retailer", Batch.product_id == prod.id, Inventory.quantity > 0)
                .all()
            )

            total_available = sum(inv.quantity for inv in retailer_invs)
            if item_data.quantity > total_available or total_available <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Requested quantity ({item_data.quantity} kg) exceeds available retailer stock ({total_available} kg) for '{prod.name}'."
                )

            target_inv = retailer_invs[0]
            target_inv.quantity -= item_data.quantity
            assigned_retailer_id = target_inv.owner_id

            total_qty += item_data.quantity
            total_amt += item_total
            prepared_items.append((prod.id, target_inv.batch_id, item_data.quantity, trusted_price))

    else:
        # Retailer wholesale order from upstream supply chain
        for item_data in order_data.items:
            if item_data.quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order quantity must be greater than 0."
                )

            prod = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not prod:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {item_data.product_id} not found"
                )

            trusted_price = get_trusted_catalog_price(prod)
            item_total = item_data.quantity * trusted_price

            inv_records = (
                db.query(Inventory)
                .join(Batch, Inventory.batch_id == Batch.id)
                .filter(
                    Batch.product_id == prod.id,
                    Inventory.quantity > 0,
                    Inventory.owner_id.is_(None),
                    Batch.quantity > 0,
                    Batch.status.notin_(["Consumed", "Depleted"])
                )
                .all()
            )
            total_available = sum(inv.quantity for inv in inv_records)

            if total_available <= 0:
                avail_batches = (
                    db.query(Batch)
                    .filter(
                        Batch.product_id == prod.id,
                        Batch.quantity > 0,
                        Batch.status.notin_(["Consumed", "Depleted"])
                    )
                    .all()
                )
                total_available = sum(b.quantity for b in avail_batches)
                use_batches_only = True
            else:
                use_batches_only = False

            if item_data.quantity > total_available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Requested quantity ({item_data.quantity} kg) exceeds available stock ({total_available} kg) for '{prod.name}'."
                )

            remaining_deduct = item_data.quantity
            chosen_batch_id = None
            if not use_batches_only:
                for inv_rec in inv_records:
                    if remaining_deduct <= 0:
                        break
                    deduct = min(inv_rec.quantity, remaining_deduct)
                    inv_rec.quantity -= deduct
                    chosen_batch_id = inv_rec.batch_id
                    if inv_rec.batch:
                        if inv_rec.batch.quantity >= deduct:
                            inv_rec.batch.quantity -= deduct
                        else:
                            inv_rec.batch.quantity = 0.0
                        if inv_rec.batch.quantity <= 0:
                            inv_rec.batch.quantity = 0.0
                            inv_rec.batch.status = "Consumed"
                    remaining_deduct -= deduct
            else:
                for b in avail_batches:
                    if remaining_deduct <= 0:
                        break
                    deduct = min(b.quantity, remaining_deduct)
                    b.quantity -= deduct
                    chosen_batch_id = b.id
                    if b.quantity <= 0:
                        b.quantity = 0.0
                        b.status = "Consumed"
                    remaining_deduct -= deduct

            total_qty += item_data.quantity
            total_amt += item_total
            prepared_items.append((prod.id, chosen_batch_id, item_data.quantity, trusted_price))

    order = Order(
        order_number=order_num,
        buyer_id=buyer_id,
        retailer_id=assigned_retailer_id,
        status=initial_status,
        total_quantity=total_qty,
        total_amount=total_amt
    )
    db.add(order)
    db.flush()

    for prod_id, batch_id, qty, price_val in prepared_items:
        item = OrderItem(
            order_id=order.id,
            product_id=prod_id,
            batch_id=batch_id,
            quantity=qty,
            price=price_val
        )
        db.add(item)

    db.commit()
    db.refresh(order)
    return order


@router.patch("/{id}/status", response_model=OrderResponse)
def update_order_status(
    id: int,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "retailer"))
):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    if current_user.role == "retailer" and order.retailer_id != current_user.id and order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Retailers can only update status for their own orders."
        )
    new_status = status_data.get("status")
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status string is required."
        )
    order.status = new_status
    db.commit()
    db.refresh(order)
    return order


@router.get("/{id}", response_model=OrderResponse)
def get_order(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "farmer", "supply_chain_manager", "distributor", "retailer", "consumer"))
):
    reconcile_overdue_shipments(db)
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    if current_user.role == "consumer" and order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own orders."
        )
    if current_user.role == "retailer" and order.buyer_id != current_user.id and order.retailer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own orders."
        )
    if current_user.role == "distributor" and order.retailer_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Distributors cannot access consumer orders."
        )
    if current_user.role == "farmer":
        has_access = (
            db.query(Order)
            .join(Shipment, Order.id == Shipment.order_id)
            .join(Batch, Shipment.batch_id == Batch.id)
            .filter(Order.id == id, Batch.farmer_id == current_user.id)
            .first()
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own produce orders."
            )
    return order
