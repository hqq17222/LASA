"""语音记录：上传外业语音备注（可选关联照片与定位），本地 faster-whisper 转写。"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import VoiceNote
from app.services.voice_transcriber import transcribe

router = APIRouter(prefix="/voice", tags=["语音记录"])

AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".webm", ".flac", ".amr", ".opus", ".wma"}


def _save_audio(file: UploadFile, project_id: int) -> tuple:
    """保存音频并返回 (绝对路径, 直链, 文件名)。"""
    ext = Path(file.filename or "").suffix.lower()
    if ext and ext not in AUDIO_EXTS:
        raise HTTPException(status_code=400, detail=f"不支持的音频格式：{ext}")
    if not ext:
        ext = ".webm"
    uid = uuid.uuid4().hex[:12]
    dest_name = f"voice_{project_id}_{uid}{ext}"
    dest_path = settings.UPLOAD_DIR / dest_name
    size_limit = settings.VOICE_MAX_SIZE_MB * 1024 * 1024
    with dest_path.open("wb") as buffer:
        copied = 0
        while chunk := file.file.read(1024 * 512):
            copied += len(chunk)
            if copied > size_limit:
                buffer.close()
                dest_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail=f"音频超过大小限制（{settings.VOICE_MAX_SIZE_MB}MB）")
            buffer.write(chunk)
    return str(dest_path), f"/static/{dest_name}", dest_name


def _serialize(n: VoiceNote) -> dict:
    return {
        "id": n.id,
        "project_id": n.project_id,
        "file_path": n.file_path or "",
        "duration": n.duration,
        "transcript": n.transcript or "",
        "asr_error": n.asr_error or "",
        "lon": n.lon,
        "lat": n.lat,
        "altitude": n.altitude,
        "photo_id": n.photo_id,
        "title": n.title or "",
        "uploaded_by": n.uploaded_by or "",
        "created_at": n.created_at.isoformat() if n.created_at else "",
    }


@router.post("/upload", summary="上传语音记录（自动转写为文字）")
def upload_voice(
    request: Request,
    project_id: int = Form(0),
    file: UploadFile = File(...),
    title: Optional[str] = Form(""),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    altitude: Optional[float] = Form(None),
    photo_id: Optional[int] = Form(None),
    language: Optional[str] = Form("zh"),
    db: Session = Depends(get_db),
):
    abs_path, rel_url, dest_name = _save_audio(file, project_id)
    duration = None
    try:
        import mutagen
        from mutagen.mp3 import MP3
        from mutagen.wave import WAVE
        from mutagen.ogg import OggVorbis
        p = Path(abs_path)
        ext = p.suffix.lower()
        if ext == ".mp3":
            duration = MP3(p).info.length
        elif ext in (".wav",):
            duration = WAVE(p).info.length
        elif ext in (".ogg", ".opus"):
            duration = OggVorbis(p).info.length
    except Exception:
        duration = None  # 解析不出时长不阻塞上传

    # 本地 whisper 转写
    result = transcribe(abs_path, language=language or "zh")

    note = VoiceNote(
        project_id=project_id,
        file_path=rel_url,
        duration=result.get("duration") or duration,
        transcript=result.get("text") or "",
        asr_error=result.get("error") or "",
        lon=lon,
        lat=lat,
        altitude=altitude,
        photo_id=photo_id,
        title=title or "",
        uploaded_by=getattr(getattr(request.state, "user", None), "username", "") or "",
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    data = _serialize(note)
    if result.get("error"):
        data["warning"] = result["error"]
    return data


@router.get("", summary="语音记录列表")
def list_voice(
    project_id: int = Query(0),
    photo_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(VoiceNote)
    if project_id:
        q = q.filter(VoiceNote.project_id == project_id)
    if photo_id is not None:
        q = q.filter(VoiceNote.photo_id == photo_id)
    notes = q.order_by(VoiceNote.created_at.desc()).all()
    return [_serialize(n) for n in notes]


@router.get("/{note_id}", summary="语音记录详情")
def get_voice(note_id: int, db: Session = Depends(get_db)):
    n = db.query(VoiceNote).get(note_id)
    if not n:
        raise HTTPException(status_code=404, detail="语音记录不存在")
    return _serialize(n)


@router.delete("/{note_id}", summary="删除语音记录")
def delete_voice(note_id: int, db: Session = Depends(get_db)):
    n = db.query(VoiceNote).get(note_id)
    if not n:
        raise HTTPException(status_code=404, detail="语音记录不存在")
    try:
        fp = settings.UPLOAD_DIR / Path(n.file_path).name
        if fp.exists():
            fp.unlink()
    except Exception:
        pass
    db.delete(n)
    db.commit()
    return {"detail": "deleted"}
