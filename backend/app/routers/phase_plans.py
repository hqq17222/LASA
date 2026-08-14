from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import PhasePlan
from app.schemas import PhasePlanBase, PhasePlanResponse

router = APIRouter(prefix="/phase-plans", tags=["阶段计划"])

@router.get("", response_model=List[PhasePlanResponse], summary="阶段计划列表")
def list_plans(project_id: int = 0, db: Session = Depends(get_db)):
    q = db.query(PhasePlan)
    if project_id:
        q = q.filter(PhasePlan.project_id == project_id)
    return q.order_by(PhasePlan.phase_no).all()

@router.post("", response_model=PhasePlanResponse, summary="创建阶段计划")
def create_plan(data: PhasePlanBase, db: Session = Depends(get_db)):
    p = PhasePlan(**data.dict())
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.put("/{plan_id}", response_model=PhasePlanResponse, summary="更新阶段计划")
def update_plan(plan_id: int, data: PhasePlanBase, db: Session = Depends(get_db)):
    p = db.query(PhasePlan).get(plan_id)
    if not p:
        raise HTTPException(status_code=404, detail="阶段计划不存在")
    for k, v in data.dict().items():
        setattr(p, k, v)
    db.commit(); db.refresh(p)
    return p

@router.delete("/{plan_id}", summary="删除阶段计划")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    p = db.query(PhasePlan).get(plan_id)
    if not p:
        raise HTTPException(status_code=404, detail="阶段计划不存在")
    db.delete(p); db.commit()
    return {"detail": "deleted"}
