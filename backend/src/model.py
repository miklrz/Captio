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
) -> object:
    """
    Загружает модель Whisper. При первом запуске скачивает и кэширует.
    При повторных — загружает из кэша.
    """
    import whisper

    WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info("Загружаю Whisper '%s' на устройство: %s", model_name, device)

    model = whisper.load_model(
        model_name,
        device=device,
        download_root=str(WHISPER_CACHE_DIR),
    )

    logger.info("Модель загружена")
    return model


def transcribe_audio(
    model: object,
    audio_path: Path,
    task: str = "transcribe",
    language: str | None = None,
) -> dict:
    """Транскрибирует аудио, возвращает текст с таймкодами."""
    options = {
        "verbose": False,
        "word_timestamps": True,
        "task": task,
    }
    if language:
        options["language"] = language
    return model.transcribe(str(audio_path), **options)


def _translate_text(text: str, target_language: str) -> str:
    if not text.strip():
        return text
    try:
        from deep_translator import GoogleTranslator
    except ImportError as exc:
        raise RuntimeError(
            "Для перевода на языки кроме английского установите зависимость deep-translator"
        ) from exc
    return GoogleTranslator(source="auto", target=target_language).translate(text)


def translate_segments(
    text: str,
    segments: list[dict],
    target_language: str,
) -> tuple[str, list[dict]]:
    """Переводит общий текст и тексты сегментов, сохраняя таймкоды."""
    translated_segments: list[dict] = []
    for segment in segments:
        translated_segments.append(
            {
                **segment,
                "text": _translate_text(str(segment.get("text", "")), target_language),
            }
        )
    translated_text = _translate_text(text, target_language) if text else " ".join(
        item["text"] for item in translated_segments
    )
    return translated_text, translated_segments
