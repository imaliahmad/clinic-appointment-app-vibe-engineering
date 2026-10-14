"""Auth routes."""

from __future__ import annotations

from flask import Blueprint, Response

from app.auth import login_required
from app.handlers import auth_handler

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login() -> tuple[Response, int]:
    return auth_handler.login()


@auth_bp.post("/logout")
@login_required
def logout() -> tuple[Response, int]:
    return auth_handler.logout()


@auth_bp.get("/me")
@login_required
def me() -> tuple[Response, int]:
    return auth_handler.me()
