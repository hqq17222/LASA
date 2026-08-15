"""语音转写（ASR）服务。

DeepSeek 暂无 ASR API。方案：本地 faster-whisper（OpenAI Whisper 的
faster 实现，CPU 可用，数据不出服务器）。

faster-whisper 是可选依赖：未安装时 VOICE_ASR_ENABLED=false，
接口仍会保存音频文件，转写文本留空并返回 warning。
"""
import logging
from typing import Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_whisper_model = None  # 懒加载单例


def _get_model():
    """懒加载 faster-whisper 模型（进程内只加载一次）。"""
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except ImportError:
            logger.warning("未安装 faster-whisper，语音转写不可用（pip install faster-whisper）")
            return None
        # 服务器内存小：int8 量化 + 单线程，避免 OOM
        try:
            _whisper_model = WhisperModel(
                settings.WHISPER_MODEL,
                device="cpu",
                compute_type="int8",
                cpu_threads=2,
            )
        except Exception as e:
            logger.warning(f"加载 whisper 模型失败: {e}")
            return None
    return _whisper_model


def transcribe(audio_path: str, language: str = "zh") -> Dict:
    """转写音频文件为文本。

    返回: {"text": str, "language": str, "duration": float, "error": str}
    """
    if not settings.VOICE_ASR_ENABLED:
        return {"text": "", "language": "", "duration": None,
                "error": "语音转写未启用（VOICE_ASR_ENABLED=false）"}
    model = _get_model()
    if model is None:
        return {"text": "", "language": "", "duration": None,
                "error": "faster-whisper 未安装或加载失败"}
    try:
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=3,
            vad_filter=True,   # 过滤静音段，节省时间
        )
        text = "".join(seg.text for seg in segments).strip()
        return {
            "text": text,
            "language": getattr(info, "language", "") or "",
            "duration": getattr(info, "duration", None),
            "error": "",
        }
    except Exception as e:
        logger.exception("whisper 转写失败")
        return {"text": "", "language": "", "duration": None, "error": str(e)}
