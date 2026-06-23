import datetime
import hashlib
import logging
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from fastapi import HTTPException, UploadFile, status

from .settings import get_settings

logger = logging.getLogger("captio.download")


def _safe_url(url: str) -> str:
    """Return URL without query/fragment so secrets are not printed to logs."""
    parsed = urlparse(url)
    netloc = parsed.netloc or "-"
    path = parsed.path or "/"
    if len(path) > 120:
        path = path[:117] + "..."
    return f"{parsed.scheme}://{netloc}{path}" if parsed.scheme else url[:120]


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


def _write_stream_with_limit(chunks, path: Path, *, source: str = "unknown", url: str | None = None) -> int:
    settings = get_settings()
    path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    last_logged_mb = 0
    started = time.perf_counter()
    safe_url = _safe_url(url) if url else "-"
    logger.info(
        "download_write_started source=%s path=%s max_mb=%s url=%s",
        source,
        path,
        settings.max_upload_size_mb,
        safe_url,
    )
    with open(path, "wb") as file:
        for chunk in chunks:
            if not chunk:
                continue
            total += len(chunk)
            current_mb = total // (10 * 1024 * 1024)
            if current_mb > last_logged_mb:
                last_logged_mb = current_mb
                logger.info(
                    "download_progress source=%s path=%s downloaded_mb=%.1f url=%s",
                    source,
                    path,
                    total / 1024 / 1024,
                    safe_url,
                )
            if total > settings.max_upload_size_bytes:
                path.unlink(missing_ok=True)
                logger.warning(
                    "download_size_limit_exceeded source=%s path=%s downloaded_bytes=%s max_bytes=%s url=%s",
                    source,
                    path,
                    total,
                    settings.max_upload_size_bytes,
                    safe_url,
                )
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"Файл больше {settings.max_upload_size_mb} МБ",
                )
            file.write(chunk)
    duration_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "download_write_finished source=%s path=%s bytes=%s duration_ms=%.1f url=%s",
        source,
        path,
        total,
        duration_ms,
        safe_url,
    )
    return total


def load_video_from_yd(url: str, path: Path) -> bool:
    started = time.perf_counter()
    safe_url = _safe_url(url)
    logger.info("download_yandex_started url=%s path=%s", safe_url, path)
    try:
        download_url = _get_yandex_disk_download_url(url)
        logger.info("download_yandex_public_url_resolved url=%s path=%s", safe_url, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(download_url, stream=True, timeout=(10, 60)) as r:
            logger.info(
                "download_yandex_response url=%s status=%s content_length=%s content_type=%s",
                safe_url,
                r.status_code,
                r.headers.get("content-length", "-"),
                r.headers.get("content-type", "-"),
            )
            r.raise_for_status()
            _write_stream_with_limit(r.iter_content(chunk_size=1024 * 1024), path, source="yandex", url=url)
        logger.info(
            "download_yandex_finished url=%s path=%s exists=%s size=%s duration_ms=%.1f",
            safe_url,
            path,
            path.exists(),
            path.stat().st_size if path.exists() else 0,
            (time.perf_counter() - started) * 1000,
        )
        return True
    except Exception:
        logger.exception(
            "download_yandex_failed url=%s path=%s exists=%s size=%s duration_ms=%.1f",
            safe_url,
            path,
            path.exists(),
            path.stat().st_size if path.exists() else 0,
            (time.perf_counter() - started) * 1000,
        )
        return False


class _YtDlpLogger:
    def debug(self, msg):
        if msg and not str(msg).startswith("[debug]"):
            logger.debug("yt_dlp_debug message=%s", msg)

    def warning(self, msg):
        logger.warning("yt_dlp_warning message=%s", msg)

    def error(self, msg):
        logger.error("yt_dlp_error message=%s", msg)


def _get_ytdlp_cookiefile() -> Path | None:
    settings = get_settings()
    cookie_content: str | None = None
    cookie_source: str | None = None

    if settings.ytdlp_cookies_file:
        source_cookiefile = Path(settings.ytdlp_cookies_file)
        if source_cookiefile.is_file():
            cookie_content = source_cookiefile.read_text(encoding="utf-8")
            cookie_source = "file"
        else:
            logger.warning("download_youtube_cookies_file_missing path=%s", source_cookiefile)

    if cookie_content is None and settings.ytdlp_cookies_content:
        cookie_content = settings.ytdlp_cookies_content
        cookie_source = "env"

    if not cookie_content:
        return None

    if "\\n" in cookie_content and "\n" not in cookie_content:
        cookie_content = cookie_content.replace("\\n", "\n")
    cookie_content = cookie_content.replace("\r\n", "\n").replace("\r", "\n")
    if not cookie_content.endswith("\n"):
        cookie_content += "\n"

    cookiefile = settings.data_dir / "youtube_cookies.txt"
    cookiefile.parent.mkdir(parents=True, exist_ok=True)
    cookiefile.write_text(cookie_content, encoding="utf-8")
    cookiefile.chmod(0o600)
    logger.info("download_youtube_cookies_enabled source=%s runtime_file=%s", cookie_source, cookiefile)
    return cookiefile


def load_video_from_youtube(url: str, path: Path) -> bool:
    started = time.perf_counter()
    safe_url = _safe_url(url)
    logger.info("download_youtube_started url=%s path=%s", safe_url, path)
    try:
        import yt_dlp

        def progress_hook(data: dict) -> None:
            status_value = data.get("status")
            if status_value == "downloading":
                downloaded = data.get("downloaded_bytes") or 0
                total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
                logger.info(
                    "download_youtube_progress url=%s path=%s downloaded_mb=%.1f total_mb=%.1f speed=%s eta=%s",
                    safe_url,
                    path,
                    downloaded / 1024 / 1024,
                    total / 1024 / 1024 if total else 0,
                    data.get("speed", "-"),
                    data.get("eta", "-"),
                )
            elif status_value == "finished":
                logger.info(
                    "download_youtube_media_finished url=%s path=%s filename=%s bytes=%s",
                    safe_url,
                    path,
                    data.get("filename", "-"),
                    data.get("downloaded_bytes", "-"),
                )

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "outtmpl": str(path),
            "quiet": True,
            "no_warnings": False,
            "logger": _YtDlpLogger(),
            "progress_hooks": [progress_hook],
        }
        cookiefile = _get_ytdlp_cookiefile()
        if cookiefile:
            ydl_opts["cookiefile"] = str(cookiefile)

        path.parent.mkdir(parents=True, exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not path.exists():
            candidates = sorted(path.parent.glob(path.name + "*"))
            logger.warning(
                "download_youtube_expected_path_missing url=%s expected_path=%s candidates=%s",
                safe_url,
                path,
                [str(item) for item in candidates[:5]],
            )
        if path.exists() and path.stat().st_size > get_settings().max_upload_size_bytes:
            path.unlink(missing_ok=True)
            raise RuntimeError(f"Файл больше {get_settings().max_upload_size_mb} МБ")

        logger.info(
            "download_youtube_finished url=%s path=%s exists=%s size=%s duration_ms=%.1f",
            safe_url,
            path,
            path.exists(),
            path.stat().st_size if path.exists() else 0,
            (time.perf_counter() - started) * 1000,
        )
        return True
    except Exception:
        logger.exception(
            "download_youtube_failed url=%s path=%s exists=%s size=%s duration_ms=%.1f",
            safe_url,
            path,
            path.exists(),
            path.stat().st_size if path.exists() else 0,
            (time.perf_counter() - started) * 1000,
        )
        return False


def load_video_from_direct_url(url: str, path: Path) -> bool:
    started = time.perf_counter()
    safe_url = _safe_url(url)
    logger.info("download_direct_started url=%s path=%s", safe_url, path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, stream=True, timeout=(10, 60)) as response:
            logger.info(
                "download_direct_response url=%s status=%s content_length=%s content_type=%s",
                safe_url,
                response.status_code,
                response.headers.get("content-length", "-"),
                response.headers.get("content-type", "-"),
            )
            response.raise_for_status()
            content_length = response.headers.get("content-length")
            if (
                content_length
                and int(content_length) > get_settings().max_upload_size_bytes
            ):
                raise RuntimeError(
                    f"Файл больше {get_settings().max_upload_size_mb} МБ"
                )
            _write_stream_with_limit(
                response.iter_content(chunk_size=1024 * 1024), path, source="direct", url=url
            )
        logger.info(
            "download_direct_finished url=%s path=%s exists=%s size=%s duration_ms=%.1f",
            safe_url,
            path,
            path.exists(),
            path.stat().st_size if path.exists() else 0,
            (time.perf_counter() - started) * 1000,
        )
        return True
    except Exception:
        logger.exception(
            "download_direct_failed url=%s path=%s exists=%s size=%s duration_ms=%.1f",
            safe_url,
            path,
            path.exists(),
            path.stat().st_size if path.exists() else 0,
            (time.perf_counter() - started) * 1000,
        )
        return False


async def save_uploaded_video(file: UploadFile) -> Path:
    suffix = _safe_suffix(file.filename)
    settings = get_settings()
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_hash = hashlib.sha256((file.filename or now).encode("utf-8")).hexdigest()[
        :12
    ]
    path = settings.uploads_dir / f"upload_{now}_{filename_hash}{suffix}"
    total = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("upload_save_started filename=%s content_type=%s path=%s", file.filename, file.content_type, path)
    with open(path, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > settings.max_upload_size_bytes:
                path.unlink(missing_ok=True)
                logger.warning(
                    "upload_save_size_limit_exceeded filename=%s path=%s downloaded_bytes=%s max_bytes=%s",
                    file.filename,
                    path,
                    total,
                    settings.max_upload_size_bytes,
                )
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"Файл больше {settings.max_upload_size_mb} МБ",
                )
            out.write(chunk)
    if total == 0:
        path.unlink(missing_ok=True)
        logger.warning("upload_save_empty_file filename=%s path=%s", file.filename, path)
        raise HTTPException(status_code=400, detail="Пустой файл")
    logger.info("upload_save_finished filename=%s path=%s bytes=%s", file.filename, path, total)
    return path


def cleanup_old_uploads() -> int:
    settings = get_settings()
    cutoff = (
        datetime.datetime.now().timestamp()
        - settings.cleanup_uploads_after_hours * 3600
    )
    removed = 0
    for folder in (settings.uploads_dir, settings.outputs_dir):
        for path in folder.glob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
                removed += 1
    if removed:
        logger.info("cleanup_old_uploads_finished removed=%s", removed)
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
    logger.info(
        "download_dispatch url=%s source_type=%s path=%s",
        _safe_url(url),
        actual_source,
        path,
    )
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
    logger.info("download_target_path_prepared source_type=%s path=%s", source_type, full_path)
    return full_path


def _get_yandex_disk_download_url(public_url: str) -> str:
    YANDEX_DISK_API = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    logger.info("yandex_download_url_request_started url=%s", _safe_url(public_url))
    response = requests.get(
        YANDEX_DISK_API, params={"public_key": public_url}, timeout=(10, 30)
    )
    logger.info(
        "yandex_download_url_response status=%s url=%s",
        response.status_code,
        _safe_url(public_url),
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
    logger.info("srt_file_written job_id=%s path=%s segments=%s", job_id, path, len(segments))
    return path
