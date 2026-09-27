from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.inventory import Inventory
from app.models.batch import Batch
from app.schemas.inventory import InventoryCreate, InventoryResponse

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=List[InventoryResponse])
def get_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    inventory_items = db.query(Inventory).offset(skip).limit(limit).all()
    return inventory_items


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory(inventory_data: InventoryCreate, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == inventory_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {inventory_data.batch_id} not found"
        )
    
    inventory_item = Inventory(
        batch_id=inventory_data.batch_id,
        warehouse_location=inventory_data.warehouse_location,
        quantity=inventory_data.quantity,
        temperature=inventory_data.temperature,
        humidity=inventory_data.humidity
    )
    db.add(inventory_item)
    db.commit()
    db.refresh(inventory_item)
    return inventory_item


@router.get("/{id}", response_model=InventoryResponse)
def get_inventory_item(id: int, db: Session = Depends(get_db)):
    item = db.query(Inventory).filter(Inventory.id == id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record with id {id} not found"
        )
    return item
