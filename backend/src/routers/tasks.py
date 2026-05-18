from typing import Annotated
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import get_db, row_to_dict, utc_now
from ..deps import current_user
from ..pydantic_models import TaskCreateRequest, TaskPublic, TaskUpdateRequest
from ..serializers import serialize_task


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _get_task_or_404(db: sqlite3.Connection, task_id: int) -> dict:
    task = row_to_dict(
        db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
    return task


def _ensure_can_modify_task(user: dict, task: dict) -> None:
    if user["role"] != "admin" and task["user_id"] != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на изменение этой задачи",
        )


@router.get("/", response_model=list[TaskPublic])
def list_tasks(
    user: Annotated[dict, Depends(current_user)],
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> list[TaskPublic]:
    if user["role"] == "admin":
        rows = db.execute(
            """
            SELECT t.*, u.name AS owner_name, u.login AS owner_login
            FROM tasks t
            LEFT JOIN users u ON t.user_id = u.id
            ORDER BY t.created_at DESC, t.id DESC
            """
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT * FROM tasks
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user["id"],),
        ).fetchall()
    return [serialize_task(dict(row)) for row in rows]


@router.post("/", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreateRequest,
    user: Annotated[dict, Depends(current_user)],
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> TaskPublic:
    now = utc_now()
    cursor = db.execute(
        """
        INSERT INTO tasks (title, done, user_id, created_at, updated_at)
        VALUES (?, 0, ?, ?, ?)
        """,
        (payload.title.strip(), user["id"], now, now),
    )
    task = row_to_dict(
        db.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    )
    return serialize_task(task)


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    user: Annotated[dict, Depends(current_user)],
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> TaskPublic:
    task = _get_task_or_404(db, task_id)
    _ensure_can_modify_task(user, task)

    db.execute(
        "UPDATE tasks SET done = ?, updated_at = ? WHERE id = ?",
        (1 if payload.done else 0, utc_now(), task_id),
    )
    updated = row_to_dict(
        db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    )
    return serialize_task(updated)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    user: Annotated[dict, Depends(current_user)],
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> dict:
    task = _get_task_or_404(db, task_id)
    _ensure_can_modify_task(user, task)
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return {"message": "Задача удалена"}
