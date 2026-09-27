from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.traceability import TraceabilityEvent
from app.models.batch import Batch
from app.schemas.traceability import TraceabilityEventCreate, TraceabilityEventResponse

router = APIRouter(prefix="/traceability", tags=["Traceability"])


@router.get("/batch/{batch_id}", response_model=List[TraceabilityEventResponse])
def get_traceability_events_by_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {batch_id} not found"
        )
    events = (
        db.query(TraceabilityEvent)
        .filter(TraceabilityEvent.batch_id == batch_id)
        .order_by(TraceabilityEvent.timestamp.asc())
        .all()
    )
    return events


@router.post("/events", response_model=TraceabilityEventResponse, status_code=status.HTTP_201_CREATED)
def create_traceability_event(event_data: TraceabilityEventCreate, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == event_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {event_data.batch_id} not found"
        )
    
    event = TraceabilityEvent(
        batch_id=event_data.batch_id,
        stage=event_data.stage,
        location=event_data.location,
        description=event_data.description
    )
    if event_data.timestamp:
        event.timestamp = event_data.timestamp

    db.add(event)
    db.commit()
    db.refresh(event)
    return event
