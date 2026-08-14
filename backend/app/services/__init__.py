# 服务层包
from .indicator_engine import compute, list_supported
from .report_service import generate_html
from .model_gateway import call_external

__all__ = ["compute", "list_supported", "generate_html", "call_external"]
