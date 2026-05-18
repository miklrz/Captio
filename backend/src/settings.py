from functools import lru_cache
from pathlib import Path
import os

from pydantic import BaseModel, Field


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseModel):
    app_name: str = "Captio"
    data_dir: Path = Field(default_factory=lambda: Path(os.getenv("CAPTIO_DATA_DIR", "data")))
    database_path: Path = Field(default_factory=lambda: Path(os.getenv("CAPTIO_DB_PATH", os.getenv("DATABASE_PATH", "data/captio.db"))))
    jwt_secret: str = Field(default_factory=lambda: os.getenv("CAPTIO_JWT_SECRET", "change-this-secret-before-production"))
    jwt_expires_hours: int = Field(default_factory=lambda: int(os.getenv("CAPTIO_JWT_EXPIRES_HOURS", "24")))
    whisper_model: str = Field(default_factory=lambda: os.getenv("CAPTIO_WHISPER_MODEL", "large-v3"))
    max_upload_size_mb: int = Field(default_factory=lambda: int(os.getenv("CAPTIO_MAX_UPLOAD_SIZE_MB", "512")))
    cleanup_uploads_after_hours: int = Field(default_factory=lambda: int(os.getenv("CAPTIO_CLEANUP_UPLOADS_AFTER_HOURS", "24")))
    allowed_video_extensions: list[str] = Field(default_factory=lambda: _csv(os.getenv("CAPTIO_ALLOWED_VIDEO_EXTENSIONS", ".mp4,.mov,.mkv,.webm,.avi,.mp3,.wav,.m4a")))
    cors_origins: list[str] = Field(default_factory=lambda: _csv(os.getenv("CAPTIO_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")))

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def outputs_dir(self) -> Path:
        return self.data_dir / "outputs"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
