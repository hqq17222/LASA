# 拉萨南北山生态监测评估系统集成平台 - 后端配置
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "拉萨南北山生态监测评估系统集成平台"
    APP_SHORT_NAME: str = "lasa-nanshan"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 18481
    API_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///data/lasa_nanshan.db"
    DATA_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    LOG_DIR: Path = DATA_DIR / "logs"
    REPORT_DIR: Path = DATA_DIR / "reports"
    CORS_ORIGINS: list[str] = ["*"]
    LOG_LEVEL: str = "INFO"
    # GEE / 模型网关占位
    GEE_SERVICE_ACCOUNT: str = ""
    MODEL_GATEWAY_TIMEOUT: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
