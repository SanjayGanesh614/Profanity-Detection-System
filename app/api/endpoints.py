from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LogCreate, LogResponse
from app.models import Log
from app.services.monitoring import process_violation
from typing import List

router = APIRouter()

@router.post("/events", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def report_event(log_data: LogCreate, db: Session = Depends(get_db)):
    try:
        db_log = await process_violation(
            db=db,
            speaker_id=log_data.speaker_id,
            transcript=log_data.transcript,
            toxicity_score=log_data.toxicity_score
        )
        return db_log
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_model=List[LogResponse])
async def get_logs(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(Log).order_by(Log.timestamp.desc()).limit(limit).all()
    return logs
