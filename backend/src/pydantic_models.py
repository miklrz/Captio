from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .languages import ensure_supported_language, SUPPORTED_LANGUAGES


Role = Literal["user", "admin"]
TaskMode = Literal["transcribe", "translate"]
VideoStatus = Literal["pending", "processing", "done", "failed"]
SourceType = Literal["auto", "yandex", "youtube", "direct", "upload"]


class UserPublic(BaseModel):
    id: int
    name: str
    login: str
    role: Role
    roles: list[str] = Field(default_factory=list)
    rights: list[str] = Field(default_factory=list)
    created_at: str | None = None


class AuthResponse(BaseModel):
    token: str
    user: UserPublic


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    login: str = Field(..., min_length=1, max_length=80)
    password: str = Field(..., min_length=4, max_length=200)


class LoginRequest(BaseModel):
    login: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RoleUpdateRequest(BaseModel):
    role: Role


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class TaskUpdateRequest(BaseModel):
    done: bool


class TaskPublic(BaseModel):
    id: int
    title: str
    done: bool
    user_id: int
    created_at: str | None = None
    updated_at: str | None = None
    owner_name: str | None = None
    owner_login: str | None = None


class SubtitleSegment(BaseModel):
    start: float
    end: float
    text: str


class VideoRequest(BaseModel):
    """Запрос на обработку видео по ссылке."""

    video_url: str = Field(..., description="Ссылка на видео")
    source_type: SourceType = "auto"
    task: TaskMode = Field(
        "transcribe",
        description="transcribe - распознать речь, translate - перевести",
    )
    language: str | None = Field(None, description="Исходный язык, например ru/en")
    target_language: str | None = Field("en", description="Целевой язык перевода")

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str | None) -> str | None:
        return ensure_supported_language(value, field_name="language")

    @field_validator("target_language")
    @classmethod
    def validate_target_language(cls, value: str | None) -> str | None:
        return ensure_supported_language(value or "en", field_name="target_language")


class VideoResponse(BaseModel):
    """Ответ сервиса с идентификатором фоновой обработки."""

    job_id: int | None = None
    status: VideoStatus = "pending"
    stage: str = "queued"
    progress: int = Field(0, ge=0, le=100)
    status_message: str = "Задача поставлена в очередь"
    text: str = Field("", description="Текст субтитров")
    segments: list[SubtitleSegment] = Field(default_factory=list)
    srt: str | None = Field(None, description="Содержимое SRT-файла")
    srt_url: str | None = None


class LanguagePublic(BaseModel):
    code: str
    label: str


class VideoJobPublic(BaseModel):
    id: int
    user_id: int | None = None
    source_url: str
    source_type: str
    status: VideoStatus
    stage: str = "queued"
    progress: int = Field(0, ge=0, le=100)
    status_message: str = "Задача поставлена в очередь"
    task_mode: TaskMode
    language: str | None = None
    target_language: str | None = None
    text: str | None = None
    segments: list[SubtitleSegment] = Field(default_factory=list)
    srt_url: str | None = None
    error_message: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    finished_at: str | None = None


class LanguagesResponse(BaseModel):
    languages: list[LanguagePublic] = Field(default_factory=lambda: SUPPORTED_LANGUAGES)
