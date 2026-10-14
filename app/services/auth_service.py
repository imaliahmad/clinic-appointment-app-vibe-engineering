"""Login logic."""

from __future__ import annotations

from typing import Any

from werkzeug.security import check_password_hash

from app.repositories import user_repository

INVALID_LOGIN = "Invalid username or password"


def authenticate(
    username: str, password: str
) -> tuple[dict[str, Any] | None, str | None]:
    """Return (user, None) on success or (None, error message)."""
    user = user_repository.get_user_by_username(username)
    if (
        user is None
        or not user["active"]
        or not check_password_hash(user["password_hash"], password)
    ):
        return None, INVALID_LOGIN
    return user, None


def get_active_user(user_id: int) -> dict[str, Any] | None:
    """Return the user if it exists and is active."""
    user = user_repository.get_user_by_id(user_id)
    if user is None or not user["active"]:
        return None
    return user
