# Pydantic schemas
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = ""
    geometry_geojson: Optional[str] = ""
    coordinate_system: Optional[str] = "CGCS2000 / 高斯-克吕格3度带 91°30′E"
    vertical_datum: Optional[str] = "1985国家高程基准"

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class DataSourceBase(BaseModel):
    project_id: int
    name: str
    source_type: Optional[str] = "sample"
    format: Optional[str] = "csv"
    file_path: Optional[str] = ""
    naming_rule: Optional[str] = ""
    quality_level: Optional[str] = "A"
    version: Optional[str] = "V1.0"
    coordinate_system: Optional[str] = ""
    meta_json: Optional[str] = ""

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceResponse(DataSourceBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ObservationCreate(BaseModel):
    project_id: int
    indicator_name: str
    sample_time: Optional[datetime] = None
    lon: Optional[float] = None
    lat: Optional[float] = None
    value: Optional[float] = None
    value_text: Optional[str] = ""
    source_id: Optional[int] = None
    meta_json: Optional[str] = ""

class ObservationResponse(ObservationCreate):
    id: int
    class Config:
        from_attributes = True

class IndicatorComputeRequest(BaseModel):
    project_id: int
    indicator_name: str = Field(default="ndvi_change", description="ndvi_change/shannon/soil_improve/carbon/soil_conservation")
    period: Optional[str] = "2026"
    params: Optional[Dict[str, Any]] = {}

class IndicatorResultResponse(BaseModel):
    id: int
    project_id: int
    name: str
    display_name: str
    symbol: str
    dimension: str
    category: str
    unit: str
    formula: str
    data_source: str
    target_threshold: str
    period: str
    value: Optional[float]
    value_text: Optional[str]
    computed_at: datetime
    class Config:
        from_attributes = True

class AlarmCreate(BaseModel):
    project_id: int
    alarm_type: Optional[str] = "deviation"
    level: Optional[str] = "yellow"
    title: str
    message: Optional[str] = ""
    indicator_name: Optional[str] = ""

class AlarmResponse(AlarmCreate):
    id: int
    status: str
    created_at: datetime
    handled_at: Optional[datetime]
    class Config:
        from_attributes = True

class ReportCreate(BaseModel):
    project_id: int
    title: str
    report_type: Optional[str] = "annual"
    period: Optional[str] = "2026"

class EquipmentBase(BaseModel):
    project_id: int
    category: str
    name: str
    model_no: Optional[str] = ""
    specs: Optional[str] = ""
    quantity: Optional[int] = 1
    frequency: Optional[str] = ""
    purpose: Optional[str] = ""
    status: Optional[str] = "planned"

class EquipmentResponse(EquipmentBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class PhasePlanBase(BaseModel):
    project_id: int
    phase_no: Optional[int] = 0
    name: str
    time_range: str
    goal: Optional[str] = ""
    key_tasks: Optional[str] = ""
    deliverables: Optional[str] = ""
    milestones: Optional[str] = ""
    progress: Optional[float] = 0.0
    status: Optional[str] = "pending"

class PhasePlanResponse(PhasePlanBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ReportResponse(ReportCreate):
    id: int
    file_path: Optional[str]
    html_content: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class ModelServiceRegister(BaseModel):
    model_id: str
    name: str
    version: Optional[str] = "1.0"
    endpoint_url: Optional[str] = ""
    schema_json: Optional[str] = ""

class ModelServiceResponse(ModelServiceRegister):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

class MapLayerResponse(BaseModel):
    layer_id: str
    name: str
    layer_type: str
    geojson: Dict[str, Any]

class FieldTrackCreate(BaseModel):
    name: str
    src: Optional[str] = "record"
    points_json: Optional[str] = "[]"
    point_count: Optional[int] = 0
    distance_km: Optional[float] = 0.0
    duration_min: Optional[float] = None
    gain_m: Optional[float] = None

class FieldTrackResponse(FieldTrackCreate):
    id: int
    username: Optional[str] = ""
    display_name: Optional[str] = ""
    created_at: datetime
    class Config:
        from_attributes = True

class SamplePlotCreate(BaseModel):
    project_id: int
    code: str
    name: Optional[str] = ""
    lon: float
    lat: float
    radius: Optional[float] = 25.0
    note: Optional[str] = ""

class SamplePlotResponse(SamplePlotCreate):
    id: int
    created_by: Optional[str] = ""
    created_at: datetime
    # 服务器计算的调查状态
    status: Optional[str] = "pending"   # pending / done
    photo_count: Optional[int] = 0      # 半径内已采集照片数
    class Config:
        from_attributes = True

class ProjectLayerCreate(BaseModel):
    project_id: int
    name: str
    fmt: Optional[str] = "geojson"
    content: str
    color: Optional[str] = "#e67e22"

class ProjectLayerResponse(ProjectLayerCreate):
    id: int
    created_by: Optional[str] = ""
    created_at: datetime
    class Config:
        from_attributes = True

class LoginIn(BaseModel):
    username: str
    password: str

class UserInfo(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    class Config:
        from_attributes = True

class LoginOut(BaseModel):
    token: str
    user: UserInfo

class UserCreate(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = ""
    role: Optional[str] = "viewer"

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True
