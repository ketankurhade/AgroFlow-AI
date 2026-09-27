from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.batch import Batch
from app.models.product import Product
from app.models.user import User
from app.schemas.batch import BatchCreate, BatchResponse

router = APIRouter(prefix="/batches", tags=["Batches"])


@router.get("", response_model=List[BatchResponse])
def get_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    batches = db.query(Batch).offset(skip).limit(limit).all()
    return batches


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(batch_data: BatchCreate, db: Session = Depends(get_db)):
    # Check if batch_code exists
    existing = db.query(Batch).filter(Batch.batch_code == batch_data.batch_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch code '{batch_data.batch_code}' already exists"
        )
    
    # Check product exists
    product = db.query(Product).filter(Product.id == batch_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {batch_data.product_id} not found"
        )
    
    # Check farmer exists
    farmer = db.query(User).filter(User.id == batch_data.farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer (User) with id {batch_data.farmer_id} not found"
        )

    batch = Batch(
        batch_code=batch_data.batch_code,
        product_id=batch_data.product_id,
        farmer_id=batch_data.farmer_id,
        quantity=batch_data.quantity,
        quality_grade=batch_data.quality_grade,
        harvest_date=batch_data.harvest_date,
        expiry_date=batch_data.expiry_date,
        origin_location=batch_data.origin_location,
        status=batch_data.status
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/{id}", response_model=BatchResponse)
def get_batch(id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {id} not found"
        )
    return batch
