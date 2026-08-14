from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Project, Observation, DataSource

router = APIRouter(prefix="/map", tags=["生态一张图"])

@router.get("/layers", summary="地图图层")
def map_layers(db: Session = Depends(get_db)):
    layers = []
    projects = db.query(Project).all()
    for p in projects:
        geom = {}
        if p.geometry_geojson:
            try:
                import json
                geom = json.loads(p.geometry_geojson)
            except Exception:
                pass
        layers.append({
            "layer_id": f"project-{p.id}",
            "name": p.name,
            "layer_type": "project",
            "geojson": geom or None,
        })
    # sample points: last 200 observations with coords
    obs = db.query(Observation).filter(Observation.lon.isnot(None), Observation.lat.isnot(None)).order_by(Observation.sample_time.desc()).limit(200).all()
    points = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [o.lon, o.lat]},
                "properties": {"indicator": o.indicator_name, "value": o.value, "time": o.sample_time.isoformat() if o.sample_time else ""},
            }
            for o in obs
        ],
    }
    layers.append({"layer_id": "observations", "name": "观测点位", "layer_type": "points", "geojson": points})
    return layers

@router.get("/projects/{project_id}/summary", summary="项目空间摘要")
def project_summary(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).get(project_id)
    from sqlalchemy import func
    from app.models import Observation, IndicatorResult, Alarm
    obs_count = db.query(func.count(Observation.id)).filter(Observation.project_id == project_id).scalar()
    ind_count = db.query(func.count(IndicatorResult.id)).filter(IndicatorResult.project_id == project_id).scalar()
    alarm_open = db.query(func.count(Alarm.id)).filter(Alarm.project_id == project_id, Alarm.status == "open").scalar()
    return {
        "project": {"id": p.id, "name": p.name, "code": p.code} if p else None,
        "obs_count": obs_count,
        "indicator_count": ind_count,
        "alarm_open": alarm_open,
    }
