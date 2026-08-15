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

    # ── 植物图片识别（视觉模型）──
    # ⚠️ DeepSeek 官方 API 暂不支持图片输入（2026-08 实测确认），
    # 默认智谱 GLM-4V-Flash（免费，OpenAI 兼容）；换其他视觉服务只需改这两项。
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    DEEPSEEK_MODEL: str = "glm-4v-flash"
    DEEPSEEK_TIMEOUT: int = 120

    # ── 语音转写（ASR）──
    # DeepSeek 暂无 ASR API；默认使用本地 faster-whisper（数据不出服务器）。
    # 不安装 faster-whisper 时接口仍可保存音频，转写文本留空并返回 warning。
    VOICE_ASR_ENABLED: bool = True
    WHISPER_MODEL: str = "small"                  # tiny/base/small/medium；服务器内存小用 base
    VOICE_MAX_SIZE_MB: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
