from pathlib import Path
from typing import Annotated
import json
import sqlite3

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from ..database import get_connection, get_db, row_to_dict, utc_now
from ..deps import optional_current_user
from ..helpers import (
    cleanup_old_uploads,
    detect_source_type,
    download_video,
    get_new_video_path,
    normalize_segments,
    save_uploaded_video,
    write_srt_file,
)
from ..model import load_whisper_model, transcribe_audio, translate_segments
from ..pydantic_models import TaskMode, VideoJobPublic, VideoRequest, VideoResponse
from ..serializers import serialize_video_job
from ..settings import get_settings


router = APIRouter(tags=["videos"])


def _create_video_job(
    db: sqlite3.Connection,
    *,
    source_url: str,
    user: dict | None,
    source_type: str,
    task: TaskMode,
    language: str | None,
    target_language: str | None,
    stored_path: str | None = None,
) -> int:
    now = utc_now()
    cursor = db.execute(
        """
        INSERT INTO video_jobs (
            user_id, source_url, source_type, stored_path, status, task_mode, language,
            target_language, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?)
        """,
        (
            user["id"] if user else None,
            source_url,
            source_type,
            stored_path,
            task,
            language,
            target_language,
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


def _process_existing_file(
    job_id: int,
    video_path: str,
    task: TaskMode,
    language: str | None,
    target_language: str | None,
) -> None:
    with get_connection() as db:
        try:
            cleanup_old_uploads()
            _update_job(db, job_id, status="processing", stored_path=video_path)

            whisper_task = "translate" if task == "translate" and (target_language or "en") == "en" else "transcribe"
            model = load_whisper_model(model_name=get_settings().whisper_model, device="auto")
            result = transcribe_audio(
                model,
                audio_path=Path(video_path),
                task=whisper_task,
                language=language,
            )
            text = result.get("text", "").strip()
            segments = normalize_segments(result)

            if task == "translate" and target_language and target_language != "en":
                text, segments = translate_segments(text, segments, target_language)

            srt_path = write_srt_file(job_id, segments, text)
            _update_job(
                db,
                job_id,
                status="done",
                transcript_text=text,
                segments_json=json.dumps(segments, ensure_ascii=False),
                srt_path=str(srt_path),
                finished_at=utc_now(),
                error_message=None,
            )
        except Exception as exc:
            _update_job(
                db,
                job_id,
                status="failed",
                error_message=str(exc),
                finished_at=utc_now(),
            )


def _download_and_process_job(
    job_id: int,
    url: str,
    source_type: str,
    task: TaskMode,
    language: str | None,
    target_language: str | None,
) -> None:
    video_path = get_new_video_path(url, source_type)
    with get_connection() as db:
        _update_job(db, job_id, status="processing", stored_path=str(video_path))
    try:
        success = download_video(url, video_path, source_type)
        if not success:
            raise RuntimeError("Не удалось загрузить видео")
        _process_existing_file(job_id, str(video_path), task, language, target_language)
    except Exception as exc:
        with get_connection() as db:
            _update_job(
                db,
                job_id,
                status="failed",
                error_message=str(exc),
                finished_at=utc_now(),
            )


def _job_response(job_id: int, status_value: str = "pending") -> VideoResponse:
    return VideoResponse(
        job_id=job_id,
        status=status_value,
        text="",
        segments=[],
        srt=None,
        srt_url=f"/api/videos/{job_id}/srt" if status_value == "done" else None,
    )


@router.post("/upload-video", response_model=VideoResponse)
@router.post("/api/videos", response_model=VideoResponse)
def upload_video(
    request: VideoRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    user: Annotated[dict | None, Depends(optional_current_user)],
) -> VideoResponse:
    source_type = (
        detect_source_type(request.video_url)
        if request.source_type == "auto"
        else request.source_type
    )
    if source_type == "upload":
        raise HTTPException(status_code=400, detail="Для файла используйте /api/videos/upload")
    job_id = _create_video_job(
        db,
        source_url=request.video_url,
        user=user,
        source_type=source_type,
        task=request.task,
        language=request.language,
        target_language=request.target_language,
    )
    background_tasks.add_task(
        _download_and_process_job,
        job_id,
        request.video_url,
        source_type,
        request.task,
        request.language,
        request.target_language,
    )
    return _job_response(job_id)


@router.post("/api/videos/upload", response_model=VideoResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_video_file(
    background_tasks: BackgroundTasks,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    user: Annotated[dict | None, Depends(optional_current_user)],
    file: UploadFile = File(...),
    task: TaskMode = Form("transcribe"),
    language: str | None = Form(None),
    target_language: str | None = Form("en"),
) -> VideoResponse:
    path = await save_uploaded_video(file)
    job_id = _create_video_job(
        db,
        source_url=file.filename or path.name,
        user=user,
        source_type="upload",
        task=task,
        language=language,
        target_language=target_language,
        stored_path=str(path),
    )
    background_tasks.add_task(
        _process_existing_file,
        job_id,
        str(path),
        task,
        language,
        target_language,
    )
    return _job_response(job_id)


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
@router.get("/api/videos/{job_id}/status", response_model=VideoJobPublic)
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
