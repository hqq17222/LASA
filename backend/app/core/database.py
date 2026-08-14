# 数据库初始化（SQLAlchemy 2.0 + SQLite，后续可平滑迁移到 PostgreSQL+PostGIS）
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine_url = settings.DATABASE_URL
if engine_url.startswith("sqlite://"):
    engine = create_engine(
        engine_url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    engine = create_engine(engine_url, echo=settings.DEBUG)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """创建数据目录和表结构"""
    # 延迟导入模型，避免循环导入
    from app import models  # noqa: F401
    for d in [settings.DATA_DIR, settings.UPLOAD_DIR, settings.LOG_DIR, settings.REPORT_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _migrate_columns()

def _migrate_columns():
    """轻量迁移：为已存在的旧表补充新增列（create_all 不会 ALTER）。"""
    new_cols = {
        "patrol_photos": [
            ("media_type", "VARCHAR(10) DEFAULT 'photo'"),
            ("duration", "FLOAT"),
            ("file_size", "INTEGER"),
            ("uploaded_by", "VARCHAR(50) DEFAULT ''"),
        ],
        "field_tracks": [
            ("username", "VARCHAR(50) DEFAULT ''"),
            ("display_name", "VARCHAR(100) DEFAULT ''"),
        ],
    }
    with engine.begin() as conn:
        for table, cols in new_cols.items():
            existing = {r[1] for r in conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()}
            for name, ddl in cols:
                if name not in existing:
                    conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")

def close_db():
    engine.dispose()
