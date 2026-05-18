import whisper
from functools import lru_cache
from pathlib import Path
import logging
import torch


logger = logging.getLogger(__name__)

WHISPER_MODEL_NAME = "large-v3"
WHISPER_CACHE_DIR = Path("models/whisper")


@lru_cache(maxsize=2)
def load_whisper_model(
    model_name: str = WHISPER_MODEL_NAME,
    device: str = "auto",
) -> whisper.Whisper:
    """
    Загружает модель Whisper. При первом запуске скачивает и кэширует.
    При повторных — загружает из кэша.
    """
    WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info(f"Загружаю Whisper '{model_name}' на устройство: {device}")

    model = whisper.load_model(
        model_name,
        device=device,
        download_root=str(WHISPER_CACHE_DIR),
    )

    logger.info("Модель загружена")
    return model


def transcribe_audio(
    model: whisper.Whisper,
    audio_path: Path,
    task: str = "transcribe",
    language: str | None = None,
) -> dict:
    """Транскрибирует аудио, возвращает текст с таймкодами"""
    options = {
        "verbose": False,
        "word_timestamps": True,
        "task": task,
    }
    if language:
        options["language"] = language
    result = model.transcribe(str(audio_path), **options)
    return result  # result["segments"] — список с таймкодами
