import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from src.database import init_db
from src.main import app
from src.settings import get_settings


class DummyModel:
    def transcribe(self, *_args, **_kwargs):
        return {
            "text": "hello world",
            "segments": [{"start": 0.0, "end": 1.0, "text": "hello world"}],
        }


def test_video_upload_creates_job_and_finishes(monkeypatch, tmp_path):
    monkeypatch.setenv("CAPTIO_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("CAPTIO_DB_PATH", str(tmp_path / "data" / "test.db"))
    get_settings.cache_clear()
    init_db()

    monkeypatch.setattr("src.routers.videos.load_whisper_model", lambda **_kwargs: DummyModel())

    client = TestClient(app)
    response = client.post(
        "/api/videos/upload",
        files={"file": ("sample.mp4", b"fake-video", "video/mp4")},
        data={"task": "transcribe", "language": "ru"},
    )

    assert response.status_code == 202
    job_id = response.json()["job_id"]

    status_response = client.get(f"/api/videos/{job_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["status"] == "done"
    assert data["text"] == "hello world"
    assert data["segments"][0]["start"] == 0.0


def test_rejects_too_large_upload(monkeypatch, tmp_path):
    monkeypatch.setenv("CAPTIO_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("CAPTIO_DB_PATH", str(tmp_path / "data" / "test.db"))
    monkeypatch.setenv("CAPTIO_MAX_UPLOAD_SIZE_MB", "0")
    get_settings.cache_clear()
    init_db()

    client = TestClient(app)
    response = client.post(
        "/api/videos/upload",
        files={"file": ("sample.mp4", b"x", "video/mp4")},
    )

    assert response.status_code == 413
