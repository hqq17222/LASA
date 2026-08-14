"""Patrol photo/video upload, EXIF extraction, grouping and defect annotation."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Body, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from pathlib import Path
import shutil, uuid, json, os
from app.core.config import settings
from app.core.database import get_db
from app.models import PatrolPhoto
from app.services.exif_extractor import extract_exif, guess_flight_route, guess_flight_date

router = APIRouter(prefix="/patrol-photos", tags=["巡检媒体"])

IMG_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".bmp", ".tif", ".tiff"}
VID_EXTS = {".mp4", ".mov", ".m4v", ".3gp", ".avi", ".mkv", ".webm"}


def _media_type_of(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in VID_EXTS:
        return "video"
    return "photo"


class LocationUpdate(BaseModel):
    lon: Optional[float] = None
    lat: Optional[float] = None
    altitude: Optional[float] = None


def _save_upload(file: UploadFile, project_id: int) -> tuple:
    """Save uploaded file and return (saved_path, relative_url)."""
    ext = Path(file.filename).suffix.lower()
    uid = uuid.uuid4().hex[:12]
    dest_name = f"patrol_{project_id}_{uid}{ext}"
    dest_path = settings.UPLOAD_DIR / dest_name
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    rel_url = f"/static/{dest_name}"
    return str(dest_path), rel_url, dest_name


@router.post("/upload", summary="上传巡检照片/录像（照片自动提取EXIF GPS）")
def upload_patrol_photo(
    request: Request,
    project_id: int = Form(...),
    file: UploadFile = File(...),
    flight_date: Optional[str] = Form(""),
    flight_route: Optional[str] = Form(""),
    duration: Optional[float] = Form(None),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext and ext not in IMG_EXTS | VID_EXTS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型：{ext}")
    media_type = _media_type_of(file.filename or "")
    abs_path, rel_url, dest_name = _save_upload(file, project_id)
    file_size = os.path.getsize(abs_path) if os.path.exists(abs_path) else None

    # 仅照片尝试 EXIF 解析；录像 GPS 极少内嵌且 PIL 无法读取，跳过
    exif = {}
    if media_type == "photo":
        try:
            exif = extract_exif(abs_path)
        except Exception:
            exif = {}

    # Use provided or guessed values
    actual_flight_date = flight_date or guess_flight_date(exif.get("photo_time"), file.filename)
    actual_flight_route = flight_route or guess_flight_route(file.filename)

    photo = PatrolPhoto(
        project_id=project_id,
        file_path=rel_url,
        original_name=file.filename,
        lon=exif.get("lon"),
        lat=exif.get("lat"),
        altitude=exif.get("altitude"),
        flight_date=actual_flight_date,
        flight_route=actual_flight_route,
        photo_time=exif.get("photo_time"),
        camera_make=exif.get("camera_make", ""),
        camera_model=exif.get("camera_model", ""),
        image_width=exif.get("width"),
        image_height=exif.get("height"),
        media_type=media_type,
        duration=duration if media_type == "video" else None,
        file_size=file_size,
        uploaded_by=getattr(getattr(request.state, "user", None), "username", "") or "",
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return _serialize(photo)


@router.post("/batch-upload", summary="批量上传巡检照片")
def batch_upload_patrol_photos(
    request: Request,
    project_id: int = Form(...),
    files: List[UploadFile] = File(...),
    flight_date: Optional[str] = Form(""),
    flight_route: Optional[str] = Form(""),
    db: Session = Depends(get_db),
):
    results = []
    for file in files:
        try:
            r = upload_patrol_photo(
                request=request,
                project_id=project_id,
                file=file,
                flight_date=flight_date,
                flight_route=flight_route,
                db=db,
            )
            results.append({"success": True, "data": r})
        except Exception as e:
            results.append({"success": False, "error": str(e), "filename": file.filename})
    return {"total": len(files), "results": results}


@router.get("", summary="巡检照片列表")
def list_photos(
    project_id: int = Query(0),
    flight_date: Optional[str] = Query(None),
    flight_route: Optional[str] = Query(None),
    defect_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(PatrolPhoto)
    if project_id:
        q = q.filter(PatrolPhoto.project_id == project_id)
    if flight_date:
        q = q.filter(PatrolPhoto.flight_date == flight_date)
    if flight_route:
        q = q.filter(PatrolPhoto.flight_route == flight_route)
    if defect_type:
        q = q.filter(PatrolPhoto.defect_type == defect_type)
    photos = q.order_by(PatrolPhoto.photo_time.desc()).all()
    return [_serialize(p) for p in photos]


@router.get("/grouped", summary="按日期和航线分组")
def list_grouped(
    project_id: int = Query(0),
    db: Session = Depends(get_db),
):
    q = db.query(PatrolPhoto)
    if project_id:
        q = q.filter(PatrolPhoto.project_id == project_id)
    photos = q.order_by(PatrolPhoto.flight_date.desc(), PatrolPhoto.flight_route, PatrolPhoto.photo_time).all()

    # Group by date -> route -> photos
    groups = {}
    for p in photos:
        date = p.flight_date or "未知日期"
        route = p.flight_route or "默认航线"
        if date not in groups:
            groups[date] = {}
        if route not in groups[date]:
            groups[date][route] = []
        groups[date][route].append(_serialize(p))

    # Convert to ordered list
    result = []
    for date in sorted(groups.keys(), reverse=True):
        date_node = {"date": date, "routes": []}
        for route in sorted(groups[date].keys()):
            date_node["routes"].append({
                "route": route,
                "count": len(groups[date][route]),
                "photos": groups[date][route],
            })
        date_node["total_count"] = sum(r["count"] for r in date_node["routes"])
        result.append(date_node)
    return result


@router.get("/map-layers", summary="地图图层数据（所有带GPS的照片）")
def map_layers(
    project_id: int = Query(0),
    db: Session = Depends(get_db),
):
    q = db.query(PatrolPhoto).filter(PatrolPhoto.lon.isnot(None), PatrolPhoto.lat.isnot(None))
    if project_id:
        q = q.filter(PatrolPhoto.project_id == project_id)
    photos = q.all()
    features = []
    for p in photos:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [p.lon, p.lat]},
            "properties": {
                "id": p.id,
                "original_name": p.original_name,
                "file_path": p.file_path,
                "flight_date": p.flight_date,
                "flight_route": p.flight_route,
                "defect_type": p.defect_type,
                "defect_desc": p.defect_desc,
                "defect_confidence": p.defect_confidence,
                "photo_time": p.photo_time.isoformat() if p.photo_time else "",
                "altitude": p.altitude,
                "media_type": p.media_type or "photo",
            },
        })
    return {
        "type": "FeatureCollection",
        "features": features,
    }


@router.get("/{photo_id}", summary="照片详情")
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    p = db.query(PatrolPhoto).get(photo_id)
    if not p:
        raise HTTPException(status_code=404, detail="照片不存在")
    return _serialize(p)


@router.put("/{photo_id}/defect", summary="标注缺陷")
def update_defect(
    photo_id: int,
    defect_type: str = Form(...),
    defect_desc: Optional[str] = Form(""),
    defect_confidence: Optional[float] = Form(0.0),
    inspector_note: Optional[str] = Form(""),
    db: Session = Depends(get_db),
):
    p = db.query(PatrolPhoto).get(photo_id)
    if not p:
        raise HTTPException(status_code=404, detail="照片不存在")
    p.defect_type = defect_type
    p.defect_desc = defect_desc
    p.defect_confidence = defect_confidence
    p.inspector_note = inspector_note
    db.commit()
    db.refresh(p)
    return _serialize(p)


@router.patch("/{photo_id}/location", summary="手动补标/修改拍摄位置（地图选点）")
def update_location(
    photo_id: int,
    payload: LocationUpdate = Body(...),
    db: Session = Depends(get_db),
):
    p = db.query(PatrolPhoto).get(photo_id)
    if not p:
        raise HTTPException(status_code=404, detail="照片不存在")
    # 经纬度成对设置；传 null 表示清除定位
    if payload.lon is None or payload.lat is None:
        p.lon = None
        p.lat = None
        p.altitude = None
    else:
        if not (-180 <= payload.lon <= 180) or not (-90 <= payload.lat <= 90):
            raise HTTPException(status_code=400, detail="经纬度超出合法范围")
        p.lon = payload.lon
        p.lat = payload.lat
        p.altitude = payload.altitude
    db.commit()
    db.refresh(p)
    return _serialize(p)


@router.post("/batch-delete", summary="批量删除照片/录像")
def batch_delete_photos(
    ids: List[int] = Body(...),
    db: Session = Depends(get_db),
):
    deleted = 0
    for pid in ids:
        p = db.query(PatrolPhoto).get(pid)
        if not p:
            continue
        try:
            fp = settings.UPLOAD_DIR / Path(p.file_path).name
            if fp.exists():
                fp.unlink()
        except Exception:
            pass
        db.delete(p)
        deleted += 1
    db.commit()
    return {"deleted": deleted}


@router.delete("/{photo_id}", summary="删除照片")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    p = db.query(PatrolPhoto).get(photo_id)
    if not p:
        raise HTTPException(status_code=404, detail="照片不存在")
    # Delete file
    try:
        fp = settings.UPLOAD_DIR / Path(p.file_path).name
        if fp.exists():
            fp.unlink()
    except Exception:
        pass
    db.delete(p)
    db.commit()
    return {"detail": "deleted"}


@router.get("/stats/summary", summary="巡检照片统计")
def photo_stats(
    project_id: int = Query(0),
    db: Session = Depends(get_db),
):
    q = db.query(PatrolPhoto)
    if project_id:
        q = q.filter(PatrolPhoto.project_id == project_id)
    total = q.count()
    with_gps = q.filter(PatrolPhoto.lon.isnot(None)).count()
    with_defect = q.filter(PatrolPhoto.defect_type != "").count()
    videos = q.filter(PatrolPhoto.media_type == "video").count()
    # Defect breakdown
    defect_counts = db.query(PatrolPhoto.defect_type, func.count(PatrolPhoto.id)).filter(
        PatrolPhoto.defect_type != ""
    )
    if project_id:
        defect_counts = defect_counts.filter(PatrolPhoto.project_id == project_id)
    defect_counts = defect_counts.group_by(PatrolPhoto.defect_type).all()
    return {
        "total": total,
        "photos": total - videos,
        "videos": videos,
        "with_gps": with_gps,
        "without_gps": total - with_gps,
        "with_defect": with_defect,
        "defect_breakdown": [{"type": d[0], "count": d[1]} for d in defect_counts],
    }


def _serialize(p: PatrolPhoto) -> dict:
    return {
        "id": p.id,
        "project_id": p.project_id,
        "file_path": p.file_path,
        "original_name": p.original_name,
        "lon": p.lon,
        "lat": p.lat,
        "altitude": p.altitude,
        "flight_date": p.flight_date,
        "flight_route": p.flight_route,
        "photo_time": p.photo_time.isoformat() if p.photo_time else None,
        "camera_make": p.camera_make,
        "camera_model": p.camera_model,
        "image_width": p.image_width,
        "image_height": p.image_height,
        "defect_type": p.defect_type,
        "defect_desc": p.defect_desc,
        "defect_confidence": p.defect_confidence,
        "inspector_note": p.inspector_note,
        "media_type": p.media_type or "photo",
        "duration": p.duration,
        "file_size": p.file_size,
        "uploaded_by": p.uploaded_by or "",
        "created_at": p.created_at.isoformat(),
    }
