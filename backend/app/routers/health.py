from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health", summary="健康检查")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "api_prefix": settings.API_PREFIX,
    }

@router.get("/info", summary="系统信息")
async def system_info():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "modules": [
            {"id": "data", "name": "数据汇聚与时空数据库"},
            {"id": "indicator", "name": "评估指标计算引擎"},
            {"id": "model", "name": "模型集成网关"},
            {"id": "map", "name": "生态一张图"},
            {"id": "alarm", "name": "偏离度预警与工单"},
            {"id": "report", "name": "评估报告自动生成"},
        ],
    }
