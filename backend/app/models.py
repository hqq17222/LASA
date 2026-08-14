# SQLAlchemy 模型定义
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, DateTime, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, default="")
    geometry_geojson: Mapped[Optional[str]] = mapped_column(Text, default="")
    coordinate_system: Mapped[str] = mapped_column(String(100), default="CGCS2000 / 高斯-克吕格3度带 91°30′E")
    vertical_datum: Mapped[str] = mapped_column(String(50), default="1985国家高程基准")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(200))
    source_type: Mapped[str] = mapped_column(String(50), default="sample")
    format: Mapped[str] = mapped_column(String(20), default="csv")
    file_path: Mapped[Optional[str]] = mapped_column(String(500), default="")
    naming_rule: Mapped[Optional[str]] = mapped_column(Text, default="")
    quality_level: Mapped[str] = mapped_column(String(2), default="A")
    version: Mapped[str] = mapped_column(String(10), default="V1.0")
    coordinate_system: Mapped[Optional[str]] = mapped_column(String(100), default="")
    meta_json: Mapped[Optional[str]] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Observation(Base):
    __tablename__ = "observations"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    indicator_name: Mapped[str] = mapped_column(String(100), index=True)
    sample_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value_text: Mapped[Optional[str]] = mapped_column(Text, default="")
    source_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    meta_json: Mapped[Optional[str]] = mapped_column(Text, default="")

class IndicatorResult(Base):
    __tablename__ = "indicator_results"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(200), default="")
    symbol: Mapped[str] = mapped_column(String(50), default="")
    dimension: Mapped[str] = mapped_column(String(50), default="structure")
    category: Mapped[str] = mapped_column(String(50), default="core")
    unit: Mapped[str] = mapped_column(String(50), default="")
    formula: Mapped[Optional[str]] = mapped_column(Text, default="")
    data_source: Mapped[Optional[str]] = mapped_column(Text, default="")
    target_threshold: Mapped[Optional[str]] = mapped_column(Text, default="")
    period: Mapped[str] = mapped_column(String(20), default="2026")
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    value_text: Mapped[Optional[str]] = mapped_column(Text, default="")
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Equipment(Base):
    __tablename__ = "equipments"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    category: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))
    model_no: Mapped[Optional[str]] = mapped_column(String(200), default="")
    specs: Mapped[Optional[str]] = mapped_column(Text, default="")
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    frequency: Mapped[Optional[str]] = mapped_column(String(100), default="")
    purpose: Mapped[Optional[str]] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="planned")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PhasePlan(Base):
    __tablename__ = "phase_plans"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    phase_no: Mapped[int] = mapped_column(Integer, default=0)
    name: Mapped[str] = mapped_column(String(200))
    time_range: Mapped[str] = mapped_column(String(100))
    goal: Mapped[Optional[str]] = mapped_column(Text, default="")
    key_tasks: Mapped[Optional[str]] = mapped_column(Text, default="")
    deliverables: Mapped[Optional[str]] = mapped_column(Text, default="")
    milestones: Mapped[Optional[str]] = mapped_column(Text, default="")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Alarm(Base):
    __tablename__ = "alarms"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    alarm_type: Mapped[str] = mapped_column(String(50), default="deviation")
    level: Mapped[str] = mapped_column(String(10), default="yellow")
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[Optional[str]] = mapped_column(Text, default="")
    indicator_name: Mapped[Optional[str]] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    handled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(200))
    report_type: Mapped[str] = mapped_column(String(50), default="annual")
    period: Mapped[str] = mapped_column(String(20), default="2026")
    file_path: Mapped[Optional[str]] = mapped_column(String(500), default="")
    html_content: Mapped[Optional[str]] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ModelService(Base):
    __tablename__ = "model_services"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    model_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    endpoint_url: Mapped[Optional[str]] = mapped_column(String(500), default="")
    schema_json: Mapped[Optional[str]] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class FieldTrack(Base):
    __tablename__ = "field_tracks"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    src: Mapped[str] = mapped_column(String(20), default="record")  # record/gpx/gpx-wpt/kml/csv/photos/app
    points_json: Mapped[str] = mapped_column(Text, default="[]")   # [[lat, lon, alt, time], ...]
    point_count: Mapped[int] = mapped_column(Integer, default=0)
    distance_km: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    duration_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gain_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), default="")
    display_name: Mapped[Optional[str]] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SamplePlot(Base):
    """样地（外业调查目标点）"""
    __tablename__ = "sample_plots"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    code: Mapped[str] = mapped_column(String(50))          # 样地编号，如 NT-01
    name: Mapped[Optional[str]] = mapped_column(String(200), default="")
    lon: Mapped[float] = mapped_column(Float)
    lat: Mapped[float] = mapped_column(Float)
    radius: Mapped[float] = mapped_column(Float, default=25.0)  # 判定半径（米）
    note: Mapped[Optional[str]] = mapped_column(Text, default="")
    created_by: Mapped[Optional[str]] = mapped_column(String(50), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProjectLayer(Base):
    """项目共享矢量图层（所有用户可见，区别于浏览器本地的个人图层）"""
    __tablename__ = "project_layers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(200))
    fmt: Mapped[str] = mapped_column(String(10), default="geojson")  # geojson/kml/gpx
    content: Mapped[str] = mapped_column(Text)   # 原文内容
    color: Mapped[str] = mapped_column(String(10), default="#e67e22")
    created_by: Mapped[Optional[str]] = mapped_column(String(50), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PatrolPhoto(Base):
    __tablename__ = "patrol_photos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    file_path: Mapped[str] = mapped_column(String(500))
    original_name: Mapped[str] = mapped_column(String(200))
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    altitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    flight_date: Mapped[Optional[str]] = mapped_column(String(20), default="")
    flight_route: Mapped[Optional[str]] = mapped_column(String(100), default="")
    photo_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    camera_make: Mapped[Optional[str]] = mapped_column(String(50), default="")
    camera_model: Mapped[Optional[str]] = mapped_column(String(50), default="")
    image_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    defect_type: Mapped[Optional[str]] = mapped_column(String(50), default="")
    defect_desc: Mapped[Optional[str]] = mapped_column(Text, default="")
    defect_confidence: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    inspector_note: Mapped[Optional[str]] = mapped_column(Text, default="")
    media_type: Mapped[str] = mapped_column(String(10), default="photo")  # photo / video
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 录像时长（秒）
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 字节
    uploaded_by: Mapped[Optional[str]] = mapped_column(String(50), default="")  # 上传者用户名
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    display_name: Mapped[str] = mapped_column(String(100), default="")
    role: Mapped[str] = mapped_column(String(20), default="viewer")  # admin/manager/analyst/viewer
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AuthToken(Base):
    __tablename__ = "auth_tokens"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
