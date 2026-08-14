# 模型集成网关（占位，可扩展为 Celery/HTTP/容器调用）
import httpx
from typing import Dict, Any
from app.core.config import settings

async def call_external(endpoint: str, payload: Dict[str, Any], timeout: int = None) -> Dict[str, Any]:
    timeout = timeout or settings.MODEL_GATEWAY_TIMEOUT
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(endpoint, json=payload)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}
