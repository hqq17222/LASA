"""野外科考：轨迹、样地、项目共享图层、外业人员状态。"""
import json
import math
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import FieldTrack, SamplePlot, ProjectLayer, PatrolPhoto
from app.schemas import (FieldTrackCreate, FieldTrackResponse, SamplePlotCreate,
                         SamplePlotResponse, ProjectLayerCreate, ProjectLayerResponse)

router = APIRouter(prefix="/field", tags=["野外科考"])


def _user_of(request: Request):
    u = getattr(request.state, "user", None)
    return (getattr(u, "username", "") or "", getattr(u, "display_name", "") or "")


def _haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


# ═══════════ 轨迹 ═══════════
@router.get("/tracks", response_model=List[FieldTrackResponse], summary="考察轨迹列表")
def list_tracks(db: Session = Depends(get_db)):
    return db.query(FieldTrack).order_by(FieldTrack.created_at.desc()).all()


@router.post("/tracks", response_model=FieldTrackResponse, summary="保存考察轨迹")
def create_track(data: FieldTrackCreate, request: Request, db: Session = Depends(get_db)):
    uname, dname = _user_of(request)
    t = FieldTrack(**data.dict(), username=uname, display_name=dname or uname)
    db.add(t); db.commit(); db.refresh(t)
    return t


@router.delete("/tracks/{track_id}", summary="删除考察轨迹")
def delete_track(track_id: int, db: Session = Depends(get_db)):
    t = db.query(FieldTrack).get(track_id)
    if not t:
        raise HTTPException(status_code=404, detail="轨迹不存在")
    db.delete(t); db.commit()
    return {"detail": "deleted"}


# ═══════════ 样地 ═══════════
def _plot_with_status(p: SamplePlot, photos: list, tracks: list) -> dict:
    """样地状态：半径内有带GPS照片 → done；有轨迹经过（无照片）→ visited（按 done 之外的提示）。"""
    photo_n = 0
    for ph in photos:
        if ph.lon is not None and ph.lat is not None and _haversine_m(p.lat, p.lon, ph.lat, ph.lon) <= max(p.radius, 1):
            photo_n += 1
    status = "done" if photo_n > 0 else "pending"
    d = {c.name: getattr(p, c.name) for c in p.__table__.columns}
    d["status"] = status
    d["photo_count"] = photo_n
    return d


@router.get("/plots", response_model=List[SamplePlotResponse], summary="样地列表（含调查状态）")
def list_plots(project_id: int = Query(0), db: Session = Depends(get_db)):
    q = db.query(SamplePlot)
    if project_id:
        q = q.filter(SamplePlot.project_id == project_id)
    plots = q.order_by(SamplePlot.code).all()
    photos = db.query(PatrolPhoto).filter(PatrolPhoto.lon.isnot(None)).all()
    return [_plot_with_status(p, photos, []) for p in plots]


@router.post("/plots", response_model=SamplePlotResponse, summary="创建样地")
def create_plot(data: SamplePlotCreate, request: Request, db: Session = Depends(get_db)):
    uname, _ = _user_of(request)
    p = SamplePlot(**data.dict(), created_by=uname)
    db.add(p); db.commit(); db.refresh(p)
    d = {c.name: getattr(p, c.name) for c in p.__table__.columns}
    d["status"] = "pending"; d["photo_count"] = 0
    return d


@router.post("/plots/import", summary="从 GeoJSON 点要素批量导入样地")
def import_plots(project_id: int = Query(...), payload: dict = None, db: Session = Depends(get_db)):
    """payload: {"geojson": {...}}，取 Point 要素，properties.code/name 作为编号与名称。"""
    gj = (payload or {}).get("geojson")
    if not gj:
        raise HTTPException(status_code=400, detail="缺少 geojson 内容")
    feats = gj.get("features", []) if gj.get("type") == "FeatureCollection" else [gj]
    created, skipped = 0, 0
    for i, f in enumerate(feats):
        g = f.get("geometry") or {}
        if g.get("type") != "Point":
            skipped += 1
            continue
        lon, lat = g["coordinates"][0], g["coordinates"][1]
        props = f.get("properties") or {}
        code = str(props.get("code") or props.get("name") or f"plot-{i + 1}")
        if db.query(SamplePlot).filter(SamplePlot.project_id == project_id, SamplePlot.code == code).first():
            skipped += 1
            continue
        db.add(SamplePlot(project_id=project_id, code=code, name=str(props.get("name") or ""),
                          lon=lon, lat=lat, radius=float(props.get("radius") or 25.0),
                          note=str(props.get("note") or "")))
        created += 1
    db.commit()
    return {"created": created, "skipped": skipped}


@router.delete("/plots/{plot_id}", summary="删除样地")
def delete_plot(plot_id: int, db: Session = Depends(get_db)):
    p = db.query(SamplePlot).get(plot_id)
    if not p:
        raise HTTPException(status_code=404, detail="样地不存在")
    db.delete(p); db.commit()
    return {"detail": "deleted"}


# ═══════════ 项目共享图层 ═══════════
@router.get("/layers", response_model=List[ProjectLayerResponse], summary="项目共享矢量图层列表")
def list_layers(project_id: int = Query(0), db: Session = Depends(get_db)):
    q = db.query(ProjectLayer)
    if project_id:
        q = q.filter(ProjectLayer.project_id == project_id)
    return q.order_by(ProjectLayer.created_at).all()


@router.post("/layers", response_model=ProjectLayerResponse, summary="上传共享矢量图层")
def create_layer(data: ProjectLayerCreate, request: Request, db: Session = Depends(get_db)):
    if len(data.content) > 8_000_000:
        raise HTTPException(status_code=400, detail="图层内容过大（>8MB）")
    uname, _ = _user_of(request)
    lyr = ProjectLayer(**data.dict(), created_by=uname)
    db.add(lyr); db.commit(); db.refresh(lyr)
    return lyr


@router.delete("/layers/{layer_id}", summary="删除共享图层")
def delete_layer(layer_id: int, db: Session = Depends(get_db)):
    lyr = db.query(ProjectLayer).get(layer_id)
    if not lyr:
        raise HTTPException(status_code=404, detail="图层不存在")
    db.delete(lyr); db.commit()
    return {"detail": "deleted"}


# ═══════════ 外业人员状态（管理视角） ═══════════
@router.get("/team-status", summary="外业人员状态：最后位置、当日里程与采集量")
def team_status(db: Session = Depends(get_db)):
    tracks = db.query(FieldTrack).order_by(FieldTrack.created_at.desc()).all()
    photos = db.query(PatrolPhoto).all()
    today = datetime.utcnow().date()
    # 每人照片数
    photo_by_user = {}
    for ph in photos:
        if ph.uploaded_by:
            photo_by_user[ph.uploaded_by] = photo_by_user.get(ph.uploaded_by, 0) + 1
    team = {}
    for t in tracks:
        if not t.username:
            continue
        e = team.setdefault(t.username, {
            "username": t.username, "display_name": t.display_name or t.username,
            "track_count": 0, "today_tracks": 0, "today_km": 0.0,
            "last_time": None, "last_lat": None, "last_lon": None,
            "photo_count": photo_by_user.get(t.username, 0),
        })
        e["track_count"] += 1
        is_today = t.created_at.date() == today or (t.created_at + timedelta(hours=8)).date() == (datetime.utcnow() + timedelta(hours=8)).date()
        if is_today:
            e["today_tracks"] += 1
            e["today_km"] = round(e["today_km"] + (t.distance_km or 0), 2)
        # 最新位置：最新轨迹的末点
        if e["last_time"] is None or t.created_at.isoformat() > e["last_time"]:
            try:
                pts = json.loads(t.points_json or "[]")
            except Exception:
                pts = []
            if pts:
                e["last_time"] = t.created_at.isoformat()
                e["last_lat"], e["last_lon"] = pts[-1][0], pts[-1][1]
    return sorted(team.values(), key=lambda x: x["last_time"] or "", reverse=True)
