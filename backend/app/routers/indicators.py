from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import IndicatorResult, Observation
from app.schemas import IndicatorComputeRequest, IndicatorResultResponse
from app.services import indicator_engine

router = APIRouter(prefix="/indicators", tags=["评估指标"])

@router.get("/meta", summary="指标元数据列表")
def list_meta():
    """返回拉萨南北山生态修复成效与稳定性评估指标体系（附录 A）。"""
    return indicator_engine.list_supported()

@router.get("", response_model=List[IndicatorResultResponse], summary="指标结果列表")
def list_results(project_id: int = 0, db: Session = Depends(get_db)):
    q = db.query(IndicatorResult)
    if project_id:
        q = q.filter(IndicatorResult.project_id == project_id)
    return q.order_by(IndicatorResult.computed_at.desc()).all()

@router.post("/compute", response_model=IndicatorResultResponse, summary="计算指标")
def compute(req: IndicatorComputeRequest, db: Session = Depends(get_db)):
    project_id = req.project_id
    name = req.indicator_name
    period = req.period or "2026"
    params = req.params or {}
    observations = db.query(Observation).filter(Observation.project_id == project_id).all()

    result = indicator_engine.compute(name, observations, params)
    if result is None:
        raise HTTPException(status_code=400, detail=f"指标 {name} 暂不支持或数据不足")

    meta = indicator_engine.INDICATOR_META.get(name, {})
    ir = IndicatorResult(
        project_id=project_id,
        name=name,
        display_name=meta.get("display_name", name),
        symbol=meta.get("symbol", ""),
        dimension=result.get("dimension", meta.get("dimension", "structure")),
        category="core",
        unit=result.get("unit", meta.get("unit", "")),
        formula=meta.get("formula", ""),
        data_source=meta.get("data_source", ""),
        target_threshold=meta.get("threshold", ""),
        period=period,
        value=result.get("value"),
        value_text=result.get("value_text", ""),
    )
    db.add(ir); db.commit(); db.refresh(ir)
    return ir

@router.delete("/{result_id}", summary="删除指标结果")
def delete_result(result_id: int, db: Session = Depends(get_db)):
    ir = db.query(IndicatorResult).get(result_id)
    if not ir:
        raise HTTPException(status_code=404, detail="指标结果不存在")
    db.delete(ir); db.commit()
    return {"detail": "deleted"}
