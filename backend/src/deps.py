from typing import Annotated
import sqlite3

from fastapi import Depends, Header, HTTPException, status

from .database import get_db, row_to_dict
from .security import decode_access_token


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def optional_current_user(
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> dict | None:
    token = _extract_bearer_token(authorization)
    if not token:
        return None
    payload = decode_access_token(token)
    user = db.execute(
        "SELECT id, name, login, role, created_at FROM users WHERE id = ?",
        (int(payload["sub"]),),
    ).fetchone()
    return row_to_dict(user)


def current_user(
    user: Annotated[dict | None, Depends(optional_current_user)],
) -> dict:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нет токена",
        )
    return user


def admin_user(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )
    return user
