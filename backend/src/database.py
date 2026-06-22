from collections.abc import Iterator
from datetime import datetime, timezone
import json
import sqlite3

from .security import hash_password
from .settings import get_settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    connection = sqlite3.connect(
        settings.database_path,
        check_same_thread=False,
        isolation_level=None,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db() -> Iterator[sqlite3.Connection]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


def init_db() -> None:
    with get_connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                login TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS video_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                source_url TEXT NOT NULL,
                source_type TEXT NOT NULL,
                stored_path TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                stage TEXT NOT NULL DEFAULT 'queued',
                progress INTEGER NOT NULL DEFAULT 0,
                status_message TEXT NOT NULL DEFAULT 'Задача поставлена в очередь',
                task_mode TEXT NOT NULL DEFAULT 'transcribe',
                language TEXT,
                target_language TEXT,
                transcript_text TEXT,
                segments_json TEXT,
                srt_path TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                finished_at TEXT
            );
            """
        )
        _ensure_video_job_status_columns(db)
        _seed_demo_users(db)


def _ensure_video_job_status_columns(db: sqlite3.Connection) -> None:
    """Добавляет новые поля статуса в уже существующую SQLite-БД."""
    columns = {row["name"] for row in db.execute("PRAGMA table_info(video_jobs)").fetchall()}
    migrations = {
        "stage": "ALTER TABLE video_jobs ADD COLUMN stage TEXT NOT NULL DEFAULT 'queued'",
        "progress": "ALTER TABLE video_jobs ADD COLUMN progress INTEGER NOT NULL DEFAULT 0",
        "status_message": "ALTER TABLE video_jobs ADD COLUMN status_message TEXT NOT NULL DEFAULT 'Задача поставлена в очередь'",
        "task_mode": "ALTER TABLE video_jobs ADD COLUMN task_mode TEXT NOT NULL DEFAULT 'transcribe'",
        "language": "ALTER TABLE video_jobs ADD COLUMN language TEXT",
        "target_language": "ALTER TABLE video_jobs ADD COLUMN target_language TEXT",
        "transcript_text": "ALTER TABLE video_jobs ADD COLUMN transcript_text TEXT",
        "segments_json": "ALTER TABLE video_jobs ADD COLUMN segments_json TEXT",
        "srt_path": "ALTER TABLE video_jobs ADD COLUMN srt_path TEXT",
        "error_message": "ALTER TABLE video_jobs ADD COLUMN error_message TEXT",
        "finished_at": "ALTER TABLE video_jobs ADD COLUMN finished_at TEXT",
    }
    for name, statement in migrations.items():
        if name not in columns:
            db.execute(statement)


def _seed_demo_users(db: sqlite3.Connection) -> None:
    settings = get_settings()
    if not settings.seed_demo_users:
        return

    users = [
        (
            settings.demo_admin_name,
            settings.demo_admin_login,
            settings.demo_admin_password,
            "admin",
        ),
        (
            settings.demo_user_name,
            settings.demo_user_login,
            settings.demo_user_password,
            "user",
        ),
    ]
    for name, login, password, role in users:
        exists = db.execute("SELECT id FROM users WHERE login = ?", (login,)).fetchone()
        if exists:
            continue
        now = utc_now()
        db.execute(
            """
            INSERT INTO users (name, login, password_hash, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, login, hash_password(password), role, now, now),
        )


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def bool_from_db(value: int | bool) -> bool:
    return bool(value)


def segments_from_db(value: str | None) -> list[dict]:
    if not value:
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []
