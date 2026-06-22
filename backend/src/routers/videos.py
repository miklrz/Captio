from pathlib import Path
from typing import Annotated
import json
import sqlite3

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, JSONResponse

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
from ..languages import (
    SUPPORTED_LANGUAGES,
    ensure_supported_language,
    get_language_label,
)
from ..model import load_whisper_model, transcribe_audio, translate_segments
from ..pydantic_models import (
    LanguagesResponse,
    TaskMode,
    VideoJobPublic,
    VideoRequest,
    VideoResponse,
)
from ..serializers import serialize_video_job
from ..settings import get_settings

router = APIRouter(tags=["videos"])

STAGE_MESSAGES = {
    "queued": "Задача поставлена в очередь",
    "download_queued": "Задача поставлена в очередь на загрузку видео",
    "upload_saved": "Файл загружен, задача поставлена в очередь",
    "downloading": "Скачиваем видеофайл",
    "preparing": "Подготавливаем файл к обработке",
    "loading_model": "Загружаем модель распознавания речи Whisper",
    "transcribing": "Распознаём речь и строим таймкоды",
    "translating": "Переводим распознанный текст на выбранный язык",
    "writing_srt": "Формируем файл субтитров SRT",
    "done": "Обработка завершена",
    "failed": "Во время обработки произошла ошибка",
}


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
    stage: str = "queued",
    progress: int = 0,
    status_message: str | None = None,
) -> int:
    now = utc_now()
    cursor = db.execute(
        """
        INSERT INTO video_jobs (
            user_id, source_url, source_type, stored_path, status, stage, progress,
            status_message, task_mode, language, target_language, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user["id"] if user else None,
            source_url,
            source_type,
            stored_path,
            stage,
            progress,
            status_message or STAGE_MESSAGES.get(stage, STAGE_MESSAGES["queued"]),
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


def _set_job_state(
    db: sqlite3.Connection,
    job_id: int,
    *,
    status_value: str = "processing",
    stage: str,
    progress: int,
    message: str | None = None,
    **extra: object,
) -> None:
    _update_job(
        db,
        job_id,
        status=status_value,
        stage=stage,
        progress=max(0, min(100, progress)),
        status_message=message or STAGE_MESSAGES.get(stage, stage),
        **extra,
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
    target_language = target_language or "en"
    try:
        language = ensure_supported_language(language, field_name="language")
        target_language = (
            ensure_supported_language(target_language, field_name="target_language")
            or "en"
        )
    except ValueError as exc:
        with get_connection() as db:
            _set_job_state(
                db,
                job_id,
                status_value="failed",
                stage="failed",
                progress=0,
                message=str(exc),
                error_message=str(exc),
                finished_at=utc_now(),
            )
        return

    with get_connection() as db:
        try:
            cleanup_old_uploads()
            _set_job_state(
                db,
                job_id,
                stage="preparing",
                progress=15,
                stored_path=video_path,
                error_message=None,
            )

            _set_job_state(db, job_id, stage="loading_model", progress=30)
            settings = get_settings()
            model = load_whisper_model(model_name=settings.whisper_model, device="auto")

            # Whisper умеет переводить напрямую только на английский. Для остальных
            # языков сначала делаем обычную транскрибацию, затем переводим текст.
            whisper_task = (
                "translate"
                if task == "translate" and target_language == "en"
                else "transcribe"
            )

            _set_job_state(db, job_id, stage="transcribing", progress=55)
            result = transcribe_audio(
                model,
                audio_path=Path(video_path),
                task=whisper_task,
                language=language,
            )
            text = result.get("text", "").strip()
            segments = normalize_segments(result)

            if task == "translate" and target_language != "en":
                _set_job_state(
                    db,
                    job_id,
                    stage="translating",
                    progress=80,
                    message=f"Переводим субтитры на {get_language_label(target_language)}",
                )
                text, segments = translate_segments(text, segments, target_language)

            _set_job_state(db, job_id, stage="writing_srt", progress=92)
            srt_path = write_srt_file(job_id, segments, text)
            _set_job_state(
                db,
                job_id,
                status_value="done",
                stage="done",
                progress=100,
                transcript_text=text,
                segments_json=json.dumps(segments, ensure_ascii=False),
                srt_path=str(srt_path),
                finished_at=utc_now(),
                error_message=None,
            )
        except Exception as exc:
            _set_job_state(
                db,
                job_id,
                status_value="failed",
                stage="failed",
                progress=0,
                message=f"Ошибка: {exc}",
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
    try:
        with get_connection() as db:
            _set_job_state(
                db,
                job_id,
                stage="downloading",
                progress=10,
                stored_path=str(video_path),
            )
        success = download_video(url, video_path, source_type)
        if not success:
            raise RuntimeError("Не удалось загрузить видео")
        _process_existing_file(job_id, str(video_path), task, language, target_language)
    except Exception as exc:
        with get_connection() as db:
            _set_job_state(
                db,
                job_id,
                status_value="failed",
                stage="failed",
                progress=0,
                message=f"Ошибка: {exc}",
                error_message=str(exc),
                finished_at=utc_now(),
            )


def _job_response(
    job_id: int, stage: str = "queued", progress: int = 0
) -> VideoResponse:
    return VideoResponse(
        job_id=job_id,
        status="pending",
        stage=stage,
        progress=progress,
        status_message=STAGE_MESSAGES.get(stage, STAGE_MESSAGES["queued"]),
        text="",
        segments=[],
        srt=None,
        srt_url=None,
    )


@router.get("/api/videos/languages", response_model=LanguagesResponse)
def list_languages() -> LanguagesResponse:
    return LanguagesResponse(languages=SUPPORTED_LANGUAGES)


@router.post("/upload-video", response_model=VideoResponse)
@router.post(
    "/api/videos", response_model=VideoResponse, status_code=status.HTTP_202_ACCEPTED
)
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
        raise HTTPException(
            status_code=400, detail="Для файла используйте /api/videos/upload"
        )
    job_id = _create_video_job(
        db,
        source_url=request.video_url,
        user=user,
        source_type=source_type,
        task=request.task,
        language=request.language,
        target_language=request.target_language or "en",
        stage="download_queued",
        progress=0,
    )
    background_tasks.add_task(
        _download_and_process_job,
        job_id,
        request.video_url,
        source_type,
        request.task,
        request.language,
        request.target_language or "en",
    )
    return _job_response(job_id, stage="download_queued", progress=0)


@router.post(
    "/api/videos/upload",
    response_model=VideoResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_video_file(
    background_tasks: BackgroundTasks,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    user: Annotated[dict | None, Depends(optional_current_user)],
    file: UploadFile = File(...),
    task: TaskMode = Form("transcribe"),
    language: str | None = Form(None),
    target_language: str | None = Form("en"),
) -> VideoResponse:
    try:
        language = ensure_supported_language(language, field_name="language")
        target_language = (
            ensure_supported_language(
                target_language or "en", field_name="target_language"
            )
            or "en"
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        ) from exc

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
        stage="upload_saved",
        progress=5,
    )
    background_tasks.add_task(
        _process_existing_file,
        job_id,
        str(path),
        task,
        language,
        target_language,
    )
    return _job_response(job_id, stage="upload_saved", progress=5)


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
        rows = db.execute("""
            SELECT * FROM video_jobs
            WHERE user_id IS NULL
            ORDER BY created_at DESC, id DESC
            """).fetchall()
    return [serialize_video_job(dict(row)) for row in rows]


@router.get("/api/videos/{job_id}")
@router.get("/api/videos/{job_id}/status")
def get_video_job(
    job_id: int,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    user: Annotated[dict | None, Depends(optional_current_user)],
) -> JSONResponse:
    job = _get_job_or_404(db, job_id)
    _ensure_can_view_job(user, job)
    public = serialize_video_job(job)
    code = (
        status.HTTP_202_ACCEPTED
        if public.status in {"pending", "processing"}
        else status.HTTP_200_OK
    )
    return JSONResponse(status_code=code, content=public.model_dump())


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
