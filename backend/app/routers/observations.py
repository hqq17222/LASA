from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Observation
from app.schemas import ObservationCreate, ObservationResponse

router = APIRouter(prefix="/observations", tags=["观测数据"])

@router.get("", response_model=List[ObservationResponse], summary="观测数据列表")
def list_observations(project_id: int = 0, indicator_name: str = "", db: Session = Depends(get_db)):
    q = db.query(Observation)
    if project_id:
        q = q.filter(Observation.project_id == project_id)
    if indicator_name:
        q = q.filter(Observation.indicator_name == indicator_name)
    return q.order_by(Observation.sample_time.desc()).limit(500).all()

@router.post("", response_model=ObservationResponse, summary="新增观测")
def create_obs(payload: ObservationCreate, db: Session = Depends(get_db)):
    if payload.sample_time is None:
        from datetime import datetime
        payload.sample_time = datetime.utcnow()
    obs = Observation(**payload.model_dump())
    db.add(obs); db.commit(); db.refresh(obs)
    return obs

@router.post("/batch", response_model=List[ObservationResponse], summary="批量新增观测")
def create_obs_batch(payload: List[ObservationCreate], db: Session = Depends(get_db)):
    from datetime import datetime
    obs_list = []
    for item in payload:
        if item.sample_time is None:
            item.sample_time = datetime.utcnow()
        obs_list.append(Observation(**item.model_dump()))
    db.add_all(obs_list); db.commit()
    for o in obs_list:
        db.refresh(o)
    return obs_list

@router.delete("/{obs_id}", summary="删除观测")
def delete_obs(obs_id: int, db: Session = Depends(get_db)):
    obs = db.query(Observation).get(obs_id)
    if not obs:
        raise HTTPException(status_code=404, detail="观测不存在")
    db.delete(obs); db.commit()
    return {"detail": "deleted"}
