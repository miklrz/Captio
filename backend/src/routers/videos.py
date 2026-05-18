from typing import Annotated
import json
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from ..database import get_db, row_to_dict, utc_now
from ..deps import optional_current_user
from ..helpers import (
    detect_source_type,
    download_video,
    get_new_video_path,
    normalize_segments,
    write_srt_file,
)
from ..model import load_whisper_model, transcribe_audio
from ..pydantic_models import VideoJobPublic, VideoRequest, VideoResponse
from ..serializers import serialize_video_job
from ..settings import get_settings


router = APIRouter(tags=["videos"])


def _create_video_job(
    db: sqlite3.Connection,
    request: VideoRequest,
    user: dict | None,
    source_type: str,
) -> int:
    now = utc_now()
    cursor = db.execute(
        """
        INSERT INTO video_jobs (
            user_id, source_url, source_type, status, task_mode, language,
            target_language, created_at, updated_at
        )
        VALUES (?, ?, ?, 'pending', ?, ?, ?, ?, ?)
        """,
        (
            user["id"] if user else None,
            request.video_url,
            source_type,
            request.task,
            request.language,
            request.target_language,
            now,
            now,
        ),
    )
    return int(cursor.lastrowid)


def _update_job(db: sqlite3.Connection, job_id: int, **fields: object) -> None:
    if not fields:
        return
    fields["updated_at"] = utc_now()
    assignments = ", ".join(f"{key} = ?" for key in fields)
    db.execute(
        f"UPDATE video_jobs SET {assignments} WHERE id = ?",
        (*fields.values(), job_id),
    )


def _get_job_or_404(db: sqlite3.Connection, job_id: int) -> dict:
    job = row_to_dict(
        db.execute("SELECT * FROM video_jobs WHERE id = ?", (job_id,)).fetchone()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись обработки не найдена",
        )
    return job


def _ensure_can_view_job(user: dict | None, job: dict) -> None:
    if job["user_id"] is None:
        return
    if user and (user["role"] == "admin" or user["id"] == job["user_id"]):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Нет прав на просмотр этой обработки",
    )


@router.post("/upload-video", response_model=VideoResponse)
@router.post("/api/videos", response_model=VideoResponse)
def upload_video(
    request: VideoRequest,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    user: Annotated[dict | None, Depends(optional_current_user)],
) -> VideoResponse:
    source_type = (
        detect_source_type(request.video_url)
        if request.source_type == "auto"
        else request.source_type
    )
    job_id = _create_video_job(db, request, user, source_type)
    video_path = get_new_video_path(request.video_url, source_type)

    try:
        _update_job(
            db,
            job_id,
            status="processing",
            stored_path=str(video_path),
        )
        success = download_video(request.video_url, video_path, source_type)
        if not success:
            raise RuntimeError("Не удалось загрузить видео")

        model = load_whisper_model(model_name=get_settings().whisper_model, device="auto")
        result = transcribe_audio(
            model,
            audio_path=video_path,
            task=request.task,
            language=request.language,
        )
        text = result.get("text", "").strip()
        segments = normalize_segments(result)
        srt_path = write_srt_file(job_id, segments, text)

        _update_job(
            db,
            job_id,
            status="done",
            transcript_text=text,
            segments_json=json.dumps(segments, ensure_ascii=False),
            srt_path=str(srt_path),
            finished_at=utc_now(),
        )
        return VideoResponse(
            job_id=job_id,
            status="done",
            text=text,
            segments=segments,
            srt=srt_path.read_text(encoding="utf-8"),
            srt_url=f"/api/videos/{job_id}/srt",
        )
    except Exception as exc:
        _update_job(
            db,
            job_id,
            status="failed",
            error_message=str(exc),
            finished_at=utc_now(),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обработки видео: {exc}",
        ) from exc


@router.get("/api/videos/history", response_model=list[VideoJobPublic])
def list_video_history(
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    user: Annotated[dict | None, Depends(optional_current_user)],
) -> list[VideoJobPublic]:
    if user and user["role"] == "admin":
        rows = db.execute(
            "SELECT * FROM video_jobs ORDER BY created_at DESC, id DESC"
        ).fetchall()
    elif user:
        rows = db.execute(
            """
            SELECT * FROM video_jobs
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user["id"],),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT * FROM video_jobs
            WHERE user_id IS NULL
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return [serialize_video_job(dict(row)) for row in rows]


@router.get("/api/videos/{job_id}", response_model=VideoJobPublic)
def get_video_job(
    job_id: int,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    user: Annotated[dict | None, Depends(optional_current_user)],
) -> VideoJobPublic:
    job = _get_job_or_404(db, job_id)
    _ensure_can_view_job(user, job)
    return serialize_video_job(job)


@router.get("/api/videos/{job_id}/srt")
def download_srt(
    job_id: int,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    user: Annotated[dict | None, Depends(optional_current_user)],
) -> FileResponse:
    job = _get_job_or_404(db, job_id)
    _ensure_can_view_job(user, job)
    if not job.get("srt_path"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SRT-файл ещё не создан",
        )
    return FileResponse(
        job["srt_path"],
        media_type="text/plain; charset=utf-8",
        filename=f"captio_job_{job_id}.srt",
    )
