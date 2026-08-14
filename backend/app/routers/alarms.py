from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models import Alarm
from app.schemas import AlarmCreate, AlarmResponse

router = APIRouter(prefix="/alarms", tags=["预警与工单"])

@router.get("", response_model=List[AlarmResponse], summary="预警列表")
def list_alarms(project_id: int = 0, status: str = "", db: Session = Depends(get_db)):
    q = db.query(Alarm)
    if project_id:
        q = q.filter(Alarm.project_id == project_id)
    if status:
        q = q.filter(Alarm.status == status)
    return q.order_by(Alarm.created_at.desc()).all()

@router.post("", response_model=AlarmResponse, summary="创建预警")
def create_alarm(payload: AlarmCreate, db: Session = Depends(get_db)):
    a = Alarm(**payload.model_dump())
    db.add(a); db.commit(); db.refresh(a)
    return a

@router.post("/{alarm_id}/handle", response_model=AlarmResponse, summary="处理预警")
def handle_alarm(alarm_id: int, db: Session = Depends(get_db)):
    a = db.query(Alarm).get(alarm_id)
    if not a:
        raise HTTPException(status_code=404, detail="预警不存在")
    a.status = "processing" if a.status == "open" else "closed"
    a.handled_at = datetime.utcnow()
    db.commit(); db.refresh(a)
    return a

@router.delete("/{alarm_id}", summary="删除预警")
def delete_alarm(alarm_id: int, db: Session = Depends(get_db)):
    a = db.query(Alarm).get(alarm_id)
    if not a:
        raise HTTPException(status_code=404, detail="预警不存在")
    db.delete(a); db.commit()
    return {"detail": "deleted"}
