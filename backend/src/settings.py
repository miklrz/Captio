from functools import lru_cache
from pathlib import Path
import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Captio"
    data_dir: Path = Path(os.getenv("CAPTIO_DATA_DIR", "data"))
    database_path: Path = Path(
        os.getenv("CAPTIO_DB_PATH", os.getenv("DATABASE_PATH", "data/captio.db"))
    )
    jwt_secret: str = os.getenv(
        "CAPTIO_JWT_SECRET",
        "change-this-secret-before-production",
    )
    jwt_expires_hours: int = int(os.getenv("CAPTIO_JWT_EXPIRES_HOURS", "24"))
    whisper_model: str = os.getenv("CAPTIO_WHISPER_MODEL", "large-v3")
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CAPTIO_CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def outputs_dir(self) -> Path:
        return self.data_dir / "outputs"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
