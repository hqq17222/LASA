"""植物物种识别：调用视觉大模型（chat/completions 图片输入）。

默认使用智谱 GLM-4V-Flash（免费，OpenAI 兼容）；DeepSeek 官方 API 暂不支持
图片输入（2026-08 实测确认）。任何 OpenAI 兼容视觉服务都可通过 .env 切换。
"""
import base64
import io
import json
import logging
from pathlib import Path
from typing import Dict, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# 识别结果的结构化字段（模型需按此 JSON 返回）
IDENTIFY_SYSTEM_PROMPT = (
    "你是一位林业植物分类专家，负责外业调查照片的植物物种识别。"
    "请仔细观察图片中的植物（重点关注：叶片形态/叶序/叶缘、花/果实/花序、树皮、树冠与整体株型、生境）。"
    "请尽力识别图中植物；若确实无法判断（如画面模糊、无植物主体），recognized 才为 false。\n\n"
    "请严格输出 JSON（不要 markdown 代码块），字段如下：\n"
    "{\n"
    '  "recognized": true/false,\n'           # 是否识别出植物
    '  "species": "中文物种名",\n'             # 如 油松 / 江孜沙棘；不确定时给最可能的常见名
    '  "scientific_name": "拉丁学名",\n'       # 可为空字符串
    '  "confidence": 0-1 之间的置信度,\n'
    '  "family": "科",\n'                     # 如 松科 / 胡颓子科
    '  "genus": "属",\n'                       # 如 松属 / 沙棘属
    '  "features": "识别依据的形态特征简述",\n'
    '  "note": "其他补充说明（如 是否为本地常见种、疑似病害等，可空）"\n'
    "}\n"
    "species 请用中国林业通用的中文名（优先《中国植物志》名称）。"
)

# 发送给模型的图片压缩目标：最长边像素、JPEG 质量。压缩后体积约 0.3-2MB。
MAX_SIDE_PX = 1280
JPEG_QUALITY = 80


def _compress_image(file_path: str) -> bytes:
    """读取图片并压缩为 JPEG bytes（限制最长边，控制体积）。

    智谱等视觉 API 对 base64 图片体积有上限（约 4-8MB），
    无人机原片常达 10MB+，必须压缩后再发送。
    """
    from PIL import Image, ImageOps

    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"图片不存在: {file_path}")
    with Image.open(p) as img:
        img = ImageOps.exif_transpose(img)  # 按 EXIF 方向纠正
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")
        w, h = img.size
        scale = min(1.0, MAX_SIDE_PX / max(w, h))
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=JPEG_QUALITY, optimize=True)
        return buf.getvalue()


def _image_to_base64(file_path: str) -> str:
    """读取图片文件为 base64 data URL（自动压缩控制体积）。"""
    data = _compress_image(file_path)
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def _parse_response(text: str) -> Dict:
    """从模型输出中稳健地提取 JSON（容忍 markdown 代码块包裹）。"""
    t = (text or "").strip()
    # 去掉 ```json ... ``` 包裹
    if t.startswith("```"):
        t = t.split("\n", 1)[-1]
        t = t.rsplit("```", 1)[0].strip()
    try:
        return json.loads(t)
    except Exception:
        # 退而求其次：截取第一个 { 到最后一个 }
        s, e = t.find("{"), t.rfind("}")
        if s >= 0 and e > s:
            try:
                return json.loads(t[s:e + 1])
            except Exception:
                pass
    return {"recognized": False, "species": "", "note": "模型输出无法解析"}


async def identify_plant(file_path: str, extra_context: str = "") -> Dict:
    """识别一张植物照片，返回结构化结果。

    返回 dict 至少包含: recognized, species, scientific_name, confidence,
    family, genus, features, note, raw (模型原文), error
    """
    base = {
        "recognized": False, "species": "", "scientific_name": "",
        "confidence": 0.0, "family": "", "genus": "",
        "features": "", "note": "", "raw": "", "error": "",
    }
    if not settings.DEEPSEEK_API_KEY:
        base["error"] = "未配置 DEEPSEEK_API_KEY（后端 .env 中设置）"
        return base
    try:
        img_url = _image_to_base64(file_path)
    except Exception as e:
        base["error"] = f"读取图片失败: {e}"
        return base

    user_content = "请识别这张外业植物照片并输出 JSON。"
    if extra_context:
        user_content += f"\n补充信息（仅供参考，不要照抄）：{extra_context}"

    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": IDENTIFY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": img_url}},
                    {"type": "text", "text": user_content},
                ],
            },
        ],
        "temperature": 0.2,
        "max_tokens": 900,
    }
    headers = {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"}
    url = settings.DEEPSEEK_BASE_URL.rstrip("/") + "/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=settings.DEEPSEEK_TIMEOUT) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        text = data["choices"][0]["message"]["content"]
        parsed = _parse_response(text)
        parsed["raw"] = text
        parsed["error"] = ""
        if not parsed.get("recognized") and not parsed.get("species"):
            parsed["note"] = parsed.get("note") or "模型未能识别出植物"
        # 归一化
        parsed.setdefault("scientific_name", "")
        parsed.setdefault("confidence", 0.0)
        parsed.setdefault("family", "")
        parsed.setdefault("genus", "")
        parsed.setdefault("features", "")
        return parsed
    except httpx.HTTPStatusError as e:
        body = ""
        try:
            body = e.response.text[:300]
        except Exception:
            pass
        base["error"] = f"DeepSeek 接口错误 {e.response.status_code}: {body}"
    except Exception as e:
        base["error"] = f"调用 DeepSeek 失败: {e}"
    return base
