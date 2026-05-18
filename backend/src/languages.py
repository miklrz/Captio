"""Поддерживаемые языки распознавания и перевода видео."""

SUPPORTED_LANGUAGES = [
    {"code": "ru", "label": "Русский"},
    {"code": "en", "label": "English"},
    {"code": "es", "label": "Español"},
    {"code": "de", "label": "Deutsch"},
    {"code": "fr", "label": "Français"},
    {"code": "it", "label": "Italiano"},
    {"code": "pt", "label": "Português"},
    {"code": "pl", "label": "Polski"},
    {"code": "tr", "label": "Türkçe"},
    {"code": "uk", "label": "Українська"},
    {"code": "kk", "label": "Қазақша"},
    {"code": "zh-CN", "label": "中文"},
    {"code": "ja", "label": "日本語"},
    {"code": "ko", "label": "한국어"},
    {"code": "ar", "label": "العربية"},
]

LANGUAGE_CODES = {item["code"] for item in SUPPORTED_LANGUAGES}
LANGUAGE_LABELS = {item["code"]: item["label"] for item in SUPPORTED_LANGUAGES}


def normalize_language_code(value: str | None) -> str | None:
    if value is None:
        return None
    code = value.strip()
    return code or None


def ensure_supported_language(value: str | None, *, field_name: str) -> str | None:
    code = normalize_language_code(value)
    if code is None:
        return None
    if code not in LANGUAGE_CODES:
        allowed = ", ".join(sorted(LANGUAGE_CODES))
        raise ValueError(f"Неподдерживаемый язык в поле {field_name}: {code}. Доступные языки: {allowed}")
    return code


def get_language_label(code: str | None) -> str:
    if not code:
        return "авто"
    return LANGUAGE_LABELS.get(code, code)
