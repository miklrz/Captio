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
        _seed_demo_users(db)


def _seed_demo_users(db: sqlite3.Connection) -> None:
    users = [
        ("Администратор", "admin", "admin123", "admin"),
        ("Paimon", "paimon", "123456", "user"),
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
