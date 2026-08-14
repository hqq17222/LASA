from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import ModelService
from app.schemas import ModelServiceRegister, ModelServiceResponse

router = APIRouter(prefix="/models", tags=["模型集成网关"])

@router.get("", response_model=List[ModelServiceResponse], summary="已注册模型")
def list_models(db: Session = Depends(get_db)):
    return db.query(ModelService).order_by(ModelService.id.desc()).all()

@router.post("/register", response_model=ModelServiceResponse, summary="注册模型服务")
def register_model(payload: ModelServiceRegister, db: Session = Depends(get_db)):
    if db.query(ModelService).filter(ModelService.model_id == payload.model_id).first():
        raise HTTPException(status_code=400, detail="model_id 已存在")
    m = ModelService(**payload.model_dump())
    db.add(m); db.commit(); db.refresh(m)
    return m

@router.post("/{model_id}/run", summary="调用模型（占位）")
def run_model(model_id: str, body: Dict[Any, Any] = Body(...), db: Session = Depends(get_db)):
    m = db.query(ModelService).filter(ModelService.model_id == model_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="模型未注册")
    # TODO: 异步调用外部 REST API / 容器
    return {
        "task_id": f"task_{model_id}_{id(body)}",
        "model_id": model_id,
        "status": "processing",
        "message": "模型调用已入队（当前为占位实现，可扩展为 Celery/HTTP 调用）",
        "params": body,
    }
