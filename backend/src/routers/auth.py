from typing import Annotated
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from ..database import get_db, row_to_dict, utc_now
from ..deps import admin_user, current_user
from ..pydantic_models import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    RoleUpdateRequest,
    UserPublic,
)
from ..security import create_access_token, hash_password, verify_password
from ..serializers import serialize_user


router = APIRouter(prefix="/api/auth", tags=["auth"])


def _auth_response(user: dict) -> AuthResponse:
    return AuthResponse(
        token=create_access_token(user["id"], user["role"]),
        user=serialize_user(user),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> AuthResponse:
    existing = db.execute(
        "SELECT id FROM users WHERE login = ?",
        (payload.login,),
    ).fetchone()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует",
        )

    now = utc_now()
    cursor = db.execute(
        """
        INSERT INTO users (name, login, password_hash, role, created_at, updated_at)
        VALUES (?, ?, ?, 'user', ?, ?)
        """,
        (payload.name, payload.login, hash_password(payload.password), now, now),
    )
    user = row_to_dict(
        db.execute(
            "SELECT id, name, login, role, created_at FROM users WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    )
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> AuthResponse:
    user = row_to_dict(
        db.execute(
            "SELECT id, name, login, password_hash, role, created_at FROM users WHERE login = ?",
            (payload.login,),
        ).fetchone()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль",
        )
    return _auth_response(user)


@router.get("/me")
def me(user: Annotated[dict, Depends(current_user)]) -> dict:
    return {"user": serialize_user(user)}


@router.get("/users", response_model=list[UserPublic])
def list_users(
    _: Annotated[dict, Depends(admin_user)],
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> list[UserPublic]:
    rows = db.execute(
        "SELECT id, name, login, role, created_at FROM users ORDER BY id"
    ).fetchall()
    return [serialize_user(dict(row)) for row in rows]


@router.patch("/users/{user_id}/role", response_model=UserPublic)
def update_user_role(
    user_id: int,
    payload: RoleUpdateRequest,
    admin: Annotated[dict, Depends(admin_user)],
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> UserPublic:
    if user_id == admin["id"] and payload.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя снять роль администратора с самого себя",
        )

    now = utc_now()
    db.execute(
        "UPDATE users SET role = ?, updated_at = ? WHERE id = ?",
        (payload.role, now, user_id),
    )
    user = row_to_dict(
        db.execute(
            "SELECT id, name, login, role, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return serialize_user(user)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: Annotated[dict, Depends(admin_user)],
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> dict:
    if user_id == admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить самого себя",
        )

    cursor = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return {"message": "Пользователь удалён"}
