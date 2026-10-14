"""SQL for users."""

from __future__ import annotations

from typing import Any

from app.db import get_db


def get_user_by_username(username: str) -> dict[str, Any] | None:
    row = (
        get_db()
        .execute("SELECT * FROM users WHERE username = ?", (username,))
        .fetchone()
    )
    return dict(row) if row else None


def insert_user(
    username: str,
    password_hash: str,
    role: str,
    doctor_id: int | None,
    created_at: str,
) -> int:
    cursor = get_db().execute(
        "INSERT INTO users (username, password_hash, role, doctor_id, created_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (username, password_hash, role, doctor_id, created_at),
    )
    return cursor.lastrowid
