from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path
import shutil, uuid
from app.core.config import settings
from app.core.database import get_db
from app.models import DataSource
from app.schemas import DataSourceCreate, DataSourceResponse

router = APIRouter(prefix="/data-sources", tags=["数据源"])

@router.get("", response_model=List[DataSourceResponse], summary="数据源列表")
def list_sources(project_id: int = 0, db: Session = Depends(get_db)):
    q = db.query(DataSource)
    if project_id:
        q = q.filter(DataSource.project_id == project_id)
    return q.order_by(DataSource.created_at.desc()).all()

@router.post("", response_model=DataSourceResponse, summary="注册数据源")
def create_source(payload: DataSourceCreate, db: Session = Depends(get_db)):
    ds = DataSource(**payload.model_dump())
    db.add(ds); db.commit(); db.refresh(ds)
    return ds

@router.post("/upload", response_model=DataSourceResponse, summary="上传文件作为数据源")
def upload_file(
    project_id: int = Form(...),
    name: str = Form(...),
    source_type: str = Form("sample"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename).suffix
    uid = uuid.uuid4().hex[:12]
    dest_name = f"{source_type}_{uid}{ext}"
    dest_path = settings.UPLOAD_DIR / dest_name
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    ds = DataSource(
        project_id=project_id,
        name=name or file.filename,
        source_type=source_type,
        format=ext.lstrip(".").lower(),
        file_path=f"/static/{dest_name}",
        meta_json=f'"{{\"original_name\": \"{file.filename}\"}}"'
    )
    db.add(ds); db.commit(); db.refresh(ds)
    return ds

@router.get("/{source_id}", response_model=DataSourceResponse, summary="数据源详情")
def get_source(source_id: int, db: Session = Depends(get_db)):
    ds = db.query(DataSource).get(source_id)
    if not ds:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return ds

@router.delete("/{source_id}", summary="删除数据源")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    ds = db.query(DataSource).get(source_id)
    if not ds:
        raise HTTPException(status_code=404, detail="数据源不存在")
    db.delete(ds); db.commit()
    return {"detail": "deleted"}
