from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Report, Project, IndicatorResult, Alarm
from app.schemas import ReportCreate, ReportResponse
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["评估报告"])

@router.get("", response_model=List[ReportResponse], summary="报告列表")
def list_reports(project_id: int = 0, db: Session = Depends(get_db)):
    q = db.query(Report)
    if project_id:
        q = q.filter(Report.project_id == project_id)
    return q.order_by(Report.created_at.desc()).all()

@router.post("", response_model=ReportResponse, summary="生成报告")
def create_report(payload: ReportCreate, db: Session = Depends(get_db)):
    project = db.query(Project).get(payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    indicators = db.query(IndicatorResult).filter(IndicatorResult.project_id == payload.project_id).all()
    alarms = db.query(Alarm).filter(Alarm.project_id == payload.project_id).order_by(Alarm.created_at.desc()).limit(20).all()
    html = report_service.generate_html(project, indicators, alarms, payload.period)
    r = Report(
        project_id=payload.project_id,
        title=payload.title,
        report_type=payload.report_type,
        period=payload.period,
        html_content=html,
    )
    db.add(r); db.commit(); db.refresh(r)
    return r

@router.get("/{report_id}/html", summary="查看报告HTML")
def get_report_html(report_id: int, db: Session = Depends(get_db)):
    r = db.query(Report).get(report_id)
    if not r:
        raise HTTPException(status_code=404, detail="报告不存在")
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=r.html_content or "<p>报告内容为空</p>")

@router.delete("/{report_id}", summary="删除报告")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(Report).get(report_id)
    if not r:
        raise HTTPException(status_code=404, detail="报告不存在")
    db.delete(r); db.commit()
    return {"detail": "deleted"}
