from functools import lru_cache
from pathlib import Path
import os
from urllib.parse import unquote
from pydantic import BaseModel, Field


def _load_env_file() -> None:
    env_paths = [
        Path.cwd() / ".env",
        Path.cwd() / "backend" / ".env",
        Path(__file__).resolve().parents[1] / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    ]
    seen: set[Path] = set()

    for env_path in env_paths:
        env_path = env_path.resolve()
        if env_path in seen or not env_path.is_file():
            continue
        seen.add(env_path)

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            if not key or key in os.environ:
                continue

            value = value.strip()
            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in {"'", '"'}
            ):
                value = value[1:-1]
            os.environ[key] = value


_load_env_file()


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _database_path() -> Path:
    explicit_path = os.getenv("CAPTIO_DB_PATH") or os.getenv("DATABASE_PATH")
    if explicit_path:
        return Path(explicit_path)

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("sqlite:///"):
            return Path(unquote(database_url.removeprefix("sqlite:///")))
        raise ValueError(
            "Captio uses sqlite3 in this coursework build. "
            "Set DATABASE_URL as sqlite:///data/captio.db or use CAPTIO_DB_PATH."
        )

    return Path("data/captio.db")


class Settings(BaseModel):
    app_name: str = "Captio"
    environment: str = Field(default_factory=lambda: os.getenv("CAPTIO_ENV", "development"))
    data_dir: Path = Field(default_factory=lambda: Path(os.getenv("CAPTIO_DATA_DIR", "data")))
    database_path: Path = Field(default_factory=_database_path)
    jwt_secret: str = Field(default_factory=lambda: os.getenv("CAPTIO_JWT_SECRET", "change-this-secret-before-production"))
    jwt_expires_hours: int = Field(default_factory=lambda: int(os.getenv("CAPTIO_JWT_EXPIRES_HOURS", "24")))
    whisper_model: str = Field(default_factory=lambda: os.getenv("CAPTIO_WHISPER_MODEL", "large"))
    max_upload_size_mb: int = Field(default_factory=lambda: int(os.getenv("CAPTIO_MAX_UPLOAD_SIZE_MB", "512")))
    cleanup_uploads_after_hours: int = Field(default_factory=lambda: int(os.getenv("CAPTIO_CLEANUP_UPLOADS_AFTER_HOURS", "24")))
    allowed_video_extensions: list[str] = Field(default_factory=lambda: _csv(os.getenv("CAPTIO_ALLOWED_VIDEO_EXTENSIONS", ".mp4,.mov,.mkv,.webm,.avi,.mp3,.wav,.m4a")))
    cors_origins: list[str] = Field(default_factory=lambda: _csv(os.getenv("CAPTIO_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")))
    cors_origin_regex: str | None = Field(default_factory=lambda: os.getenv("CAPTIO_CORS_ORIGIN_REGEX", r"https://.*\.(onrender\.com|vercel\.app|netlify\.app)"))
    seed_demo_users: bool = Field(default_factory=lambda: _bool(os.getenv("CAPTIO_SEED_DEMO_USERS"), True))
    demo_admin_name: str = Field(default_factory=lambda: os.getenv("CAPTIO_DEMO_ADMIN_NAME", "Администратор"))
    demo_admin_login: str = Field(default_factory=lambda: os.getenv("CAPTIO_DEMO_ADMIN_LOGIN", "admin"))
    demo_admin_password: str = Field(default_factory=lambda: os.getenv("CAPTIO_DEMO_ADMIN_PASSWORD", "admin123"))
    demo_user_name: str = Field(default_factory=lambda: os.getenv("CAPTIO_DEMO_USER_NAME", "Paimon"))
    demo_user_login: str = Field(default_factory=lambda: os.getenv("CAPTIO_DEMO_USER_LOGIN", "paimon"))
    demo_user_password: str = Field(default_factory=lambda: os.getenv("CAPTIO_DEMO_USER_PASSWORD", "123456"))

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
    if (
        settings.environment.lower() == "production"
        and settings.jwt_secret == "change-this-secret-before-production"
    ):
        raise ValueError("CAPTIO_JWT_SECRET must be set explicitly in production")
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    print(settings)
    return settings
