from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["项目管理"])

@router.get("", response_model=List[ProjectResponse], summary="项目列表")
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()

@router.post("", response_model=ProjectResponse, summary="创建项目")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    if db.query(Project).filter(Project.code == payload.code).first():
        raise HTTPException(status_code=400, detail="项目编码已存在")
    p = Project(**payload.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.get("/{project_id}", response_model=ProjectResponse, summary="项目详情")
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).get(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    return p

@router.put("/{project_id}", response_model=ProjectResponse, summary="更新项目")
def update_project(project_id: int, payload: ProjectCreate, db: Session = Depends(get_db)):
    p = db.query(Project).get(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    for k, v in payload.model_dump().items():
        setattr(p, k, v)
    db.commit(); db.refresh(p)
    return p

@router.delete("/{project_id}", summary="删除项目")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).get(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    db.delete(p); db.commit()
    return {"detail": "deleted"}
