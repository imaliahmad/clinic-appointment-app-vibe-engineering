"""Request handling for login, logout and me."""

from __future__ import annotations

from typing import Any

from flask import Response, request, session

from app.auth import current_user
from app.responses import failure, success
from app.services import auth_service


def login() -> tuple[Response, int]:
    body: Any = request.get_json(silent=True)
    if not isinstance(body, dict):
        return failure("Request body must be JSON", status_code=400)
    username = body.get("username")
    password = body.get("password")
    errors = []
    if not isinstance(username, str) or not username.strip():
        errors.append("username is required")
    if not isinstance(password, str) or not password:
        errors.append("password is required")
    if errors:
        return failure("Invalid input", errors, 400)

    user, error = auth_service.authenticate(username.strip(), password)
    if user is None:
        return failure(error or auth_service.INVALID_LOGIN, status_code=401)

    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["doctor_id"] = user["doctor_id"]
    data = {"id": user["id"], "username": user["username"], "role": user["role"]}
    return success(data, "Logged in")


def logout() -> tuple[Response, int]:
    session.clear()
    return success(None, "Logged out")


def me() -> tuple[Response, int]:
    user = current_user()
    assert user is not None  # guaranteed by login_required
    data = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "doctor_id": user["doctor_id"],
    }
    return success(data)
