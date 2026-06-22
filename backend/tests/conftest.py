import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database import init_db
from src.main import app
from src.settings import get_settings


class DummyModel:
    def transcribe(self, *_args, **_kwargs):
        return {
            "text": "hello world",
            "segments": [{"start": 0.0, "end": 1.0, "text": "hello world"}],
        }


@pytest.fixture()
def test_client(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    monkeypatch.setenv("CAPTIO_ENV", "testing")
    monkeypatch.setenv("CAPTIO_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CAPTIO_DB_PATH", str(data_dir / "test.db"))
    monkeypatch.setenv("CAPTIO_JWT_SECRET", "test-secret")
    monkeypatch.setenv("CAPTIO_WHISPER_MODEL", "base")
    monkeypatch.setenv("CAPTIO_SEED_DEMO_USERS", "true")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("CAPTIO_MAX_UPLOAD_SIZE_MB", raising=False)
    monkeypatch.setattr(
        "src.routers.videos.load_whisper_model",
        lambda **_kwargs: DummyModel(),
    )
    get_settings.cache_clear()
    init_db()

    with TestClient(app) as client:
        yield client

    get_settings.cache_clear()


def auth_headers(client: TestClient, login: str = "admin", password: str = "admin123") -> dict:
    response = client.post(
        "/api/auth/login",
        json={"login": login, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}
