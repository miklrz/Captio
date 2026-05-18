import datetime
import hashlib
import logging
from pathlib import Path
from urllib.parse import urlparse

import requests
from fastapi import HTTPException, UploadFile, status

from .settings import get_settings

logger = logging.getLogger(__name__)


def _safe_suffix(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    allowed = {item.lower() for item in get_settings().allowed_video_extensions}
    if suffix and suffix in allowed:
        return suffix
    if suffix:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Формат файла {suffix} не поддерживается",
        )
    return ".mp4"


def _write_stream_with_limit(chunks, path: Path) -> None:
    settings = get_settings()
    path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with open(path, "wb") as file:
        for chunk in chunks:
            if not chunk:
                continue
            total += len(chunk)
            if total > settings.max_upload_size_bytes:
                path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Файл больше {settings.max_upload_size_mb} МБ",
                )
            file.write(chunk)


def load_video_from_yd(url: str, path: Path) -> bool:
    try:
        download_url = _get_yandex_disk_download_url(url)
        path.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(download_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            _write_stream_with_limit(r.iter_content(chunk_size=1024 * 1024), path)
        logger.info("Файл загружен: %s", path)
        return True
    except Exception as e:
        logger.error("Ошибка при загрузке видео: %s", e)
        return False


def load_video_from_youtube(url: str, path: Path) -> bool:
    try:
        import yt_dlp

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "outtmpl": str(path),
            "quiet": True,
            "no_warnings": True,
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if path.exists() and path.stat().st_size > get_settings().max_upload_size_bytes:
            path.unlink(missing_ok=True)
            raise RuntimeError(f"Файл больше {get_settings().max_upload_size_mb} МБ")

        logger.info("Видео загружено: %s", path)
        return True
    except Exception as e:
        logger.error("Ошибка при загрузке видео: %s", e)
        return False


def load_video_from_direct_url(url: str, path: Path) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > get_settings().max_upload_size_bytes:
                raise RuntimeError(f"Файл больше {get_settings().max_upload_size_mb} МБ")
            _write_stream_with_limit(response.iter_content(chunk_size=1024 * 1024), path)
        logger.info("Файл загружен: %s", path)
        return True
    except Exception as e:
        logger.error("Ошибка при прямой загрузке видео: %s", e)
        return False


async def save_uploaded_video(file: UploadFile) -> Path:
    suffix = _safe_suffix(file.filename)
    settings = get_settings()
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_hash = hashlib.sha256((file.filename or now).encode("utf-8")).hexdigest()[:12]
    path = settings.uploads_dir / f"upload_{now}_{filename_hash}{suffix}"
    total = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > settings.max_upload_size_bytes:
                path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Файл больше {settings.max_upload_size_mb} МБ",
                )
            out.write(chunk)
    if total == 0:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Пустой файл")
    return path


def cleanup_old_uploads() -> int:
    settings = get_settings()
    cutoff = datetime.datetime.now().timestamp() - settings.cleanup_uploads_after_hours * 3600
    removed = 0
    for folder in (settings.uploads_dir, settings.outputs_dir):
        for path in folder.glob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
                removed += 1
    return removed


def detect_source_type(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "disk.yandex" in host or "yadi.sk" in host:
        return "yandex"
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    return "direct"


def download_video(url: str, path: Path, source_type: str = "auto") -> bool:
    actual_source = detect_source_type(url) if source_type == "auto" else source_type
    if actual_source == "yandex":
        return load_video_from_yd(url, path)
    if actual_source == "youtube":
        return load_video_from_youtube(url, path)
    return load_video_from_direct_url(url, path)


def get_new_video_path(url: str, type: str = "auto") -> Path:
    settings = get_settings()
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    source_type = detect_source_type(url) if type == "auto" else type
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    filename = f"{source_type}_{now}_{url_hash}.mp4"
    full_path = settings.uploads_dir / filename
    logger.info("Полный путь, по которому будет загружено видео: %s", full_path)
    return full_path


def _get_yandex_disk_download_url(public_url: str) -> str:
    YANDEX_DISK_API = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    response = requests.get(
        YANDEX_DISK_API, params={"public_key": public_url}, timeout=10
    )
    response.raise_for_status()
    return response.json()["href"]


def normalize_segments(result: dict) -> list[dict]:
    segments = []
    for segment in result.get("segments", []):
        segments.append(
            {
                "start": float(segment.get("start", 0)),
                "end": float(segment.get("end", 0)),
                "text": str(segment.get("text", "")).strip(),
            }
        )
    return segments


def format_srt_time(seconds: float) -> str:
    milliseconds = round((seconds - int(seconds)) * 1000)
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def segments_to_srt(segments: list[dict], fallback_text: str = "") -> str:
    if not segments:
        return fallback_text

    blocks = []
    for index, segment in enumerate(segments, start=1):
        blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{format_srt_time(segment['start'])} --> {format_srt_time(segment['end'])}",
                    segment["text"],
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def write_srt_file(job_id: int, segments: list[dict], text: str) -> Path:
    settings = get_settings()
    path = settings.outputs_dir / f"job_{job_id}.srt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(segments_to_srt(segments, text), encoding="utf-8")
    return path
