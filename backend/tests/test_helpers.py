import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.helpers import _get_ytdlp_cookiefile
from src.settings import get_settings


def test_get_ytdlp_cookiefile_copies_configured_file_to_data_dir(monkeypatch, tmp_path):
    cookiefile = tmp_path / "cookies.txt"
    cookiefile.write_text(
        "# Netscape HTTP Cookie File\r\n"
        ".youtube.com\tTRUE\t/\tTRUE\t0\tSID\tsecret",
        encoding="utf-8",
    )

    monkeypatch.setenv("CAPTIO_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("CAPTIO_YTDLP_COOKIES_FILE", str(cookiefile))
    monkeypatch.delenv("CAPTIO_YTDLP_COOKIES_CONTENT", raising=False)
    get_settings.cache_clear()

    try:
        runtime_cookiefile = _get_ytdlp_cookiefile()
        assert runtime_cookiefile == tmp_path / "data" / "youtube_cookies.txt"
        assert runtime_cookiefile.read_text(encoding="utf-8") == (
            "# Netscape HTTP Cookie File\n"
            ".youtube.com\tTRUE\t/\tTRUE\t0\tSID\tsecret\n"
        )
    finally:
        get_settings.cache_clear()


def test_get_ytdlp_cookiefile_writes_env_content(monkeypatch, tmp_path):
    cookie_content = (
        "# Netscape HTTP Cookie File\\n"
        ".youtube.com\tTRUE\t/\tTRUE\t0\tSID\tsecret"
    )

    monkeypatch.setenv("CAPTIO_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.delenv("CAPTIO_YTDLP_COOKIES_FILE", raising=False)
    monkeypatch.setenv("CAPTIO_YTDLP_COOKIES_CONTENT", cookie_content)
    get_settings.cache_clear()

    try:
        cookiefile = _get_ytdlp_cookiefile()
        assert cookiefile == tmp_path / "data" / "youtube_cookies.txt"
        assert cookiefile.read_text(encoding="utf-8") == (
            "# Netscape HTTP Cookie File\n"
            ".youtube.com\tTRUE\t/\tTRUE\t0\tSID\tsecret\n"
        )
    finally:
        get_settings.cache_clear()
