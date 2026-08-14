from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Equipment
from app.schemas import EquipmentBase, EquipmentResponse

router = APIRouter(prefix="/equipments", tags=["设备清单"])

@router.get("", response_model=List[EquipmentResponse], summary="设备列表")
def list_equipments(project_id: int = 0, category: str = "", db: Session = Depends(get_db)):
    q = db.query(Equipment)
    if project_id:
        q = q.filter(Equipment.project_id == project_id)
    if category:
        q = q.filter(Equipment.category == category)
    return q.order_by(Equipment.category, Equipment.id).all()

@router.post("", response_model=EquipmentResponse, summary="创建设备")
def create_equipment(data: EquipmentBase, db: Session = Depends(get_db)):
    e = Equipment(**data.dict())
    db.add(e); db.commit(); db.refresh(e)
    return e

@router.put("/{equipment_id}", response_model=EquipmentResponse, summary="更新设备")
def update_equipment(equipment_id: int, data: EquipmentBase, db: Session = Depends(get_db)):
    e = db.query(Equipment).get(equipment_id)
    if not e:
        raise HTTPException(status_code=404, detail="设备不存在")
    for k, v in data.dict().items():
        setattr(e, k, v)
    db.commit(); db.refresh(e)
    return e

@router.delete("/{equipment_id}", summary="删除设备")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    e = db.query(Equipment).get(equipment_id)
    if not e:
        raise HTTPException(status_code=404, detail="设备不存在")
    db.delete(e); db.commit()
    return {"detail": "deleted"}
