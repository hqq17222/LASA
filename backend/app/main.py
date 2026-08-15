# 主入口
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db, close_db, SessionLocal
from app.core import security as sec
from loguru import logger

# 确保数据目录
for d in [settings.DATA_DIR, settings.UPLOAD_DIR, settings.LOG_DIR, settings.REPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logger.add(
    settings.LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="7 days",
    level=settings.LOG_LEVEL,
    enqueue=True,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started")
    yield
    close_db()
    logger.info("Shutdown complete")

app = FastAPI(
    title=settings.APP_NAME,
    description="拉萨南北山生态网络监测评估系统集成平台",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 认证中间件：除白名单外，所有 API 必须携带有效令牌 =====
AUTH_WHITELIST_PREFIXES = (
    "/api/v1/health",
    "/api/v1/auth/login",
    "/docs", "/redoc", "/openapi.json",
    "/uploads",  # 照片文件直链（前端 <img> 无法带请求头）
)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if request.method == "OPTIONS":
        return await call_next(request)
    if not path.startswith(settings.API_PREFIX) and not path.startswith("/uploads"):
        return await call_next(request)
    if any(path.startswith(p) for p in AUTH_WHITELIST_PREFIXES):
        return await call_next(request)
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not token and request.method == "GET":
        token = request.query_params.get("token", "")  # iframe/img 无法带请求头，支持 query 令牌
    db = SessionLocal()
    try:
        user = sec.get_user_by_token(db, token)
        if not user:
            return JSONResponse({"detail": "未登录或登录已过期"}, status_code=401)
        level = sec.role_level(user.role)
        if path.startswith(f"{settings.API_PREFIX}/users") and level < 4:
            return JSONResponse({"detail": "需要管理员权限"}, status_code=403)
        if request.method not in ("GET", "HEAD") and level < 2:
            return JSONResponse({"detail": "只读账户无写入权限"}, status_code=403)
        request.state.user = user
    finally:
        db.close()
    return await call_next(request)

# 注册路由
prefix = settings.API_PREFIX
from app.routers import health, projects, data_sources, observations, indicators, alarms, reports, map, models, equipments, phase_plans, patrol_photos, field_survey, auth, users, voice

app.include_router(health.router, prefix=prefix, tags=["系统"])
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)
app.include_router(projects.router, prefix=prefix)
app.include_router(data_sources.router, prefix=prefix)
app.include_router(observations.router, prefix=prefix)
app.include_router(indicators.router, prefix=prefix)
app.include_router(alarms.router, prefix=prefix)
app.include_router(reports.router, prefix=prefix)
app.include_router(map.router, prefix=prefix)
app.include_router(models.router, prefix=prefix)
app.include_router(equipments.router, prefix=prefix)
app.include_router(phase_plans.router, prefix=prefix)
app.include_router(patrol_photos.router, prefix=prefix)
app.include_router(field_survey.router, prefix=prefix)
app.include_router(voice.router, prefix=prefix)

logger.info(f"Registered {len(app.routes)} routes")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
