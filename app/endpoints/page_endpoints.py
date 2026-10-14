"""HTML pages served from frontend/."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, Response, redirect, send_from_directory

from app.auth import current_user, page_role_required
from app.rules.auth_rules import home_path_for_role

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

page_bp = Blueprint("pages", __name__)


@page_bp.get("/")
def login_page() -> Response:
    user = current_user()
    if user is not None:
        return redirect(home_path_for_role(user["role"]))
    return send_from_directory(FRONTEND_DIR, "login.html")


@page_bp.get("/reception")
@page_role_required("receptionist")
def reception_page() -> Response:
    return send_from_directory(FRONTEND_DIR, "reception.html")


@page_bp.get("/doctor")
@page_role_required("doctor")
def doctor_page() -> Response:
    return send_from_directory(FRONTEND_DIR, "doctor.html")


@page_bp.get("/admin")
@page_role_required("admin")
def admin_page() -> Response:
    return send_from_directory(FRONTEND_DIR, "admin.html")


@page_bp.get("/static/<any(css, js):folder>/<path:filename>")
def static_asset(folder: str, filename: str) -> Response:
    """Serve only frontend/css and frontend/js, never the HTML pages."""
    return send_from_directory(FRONTEND_DIR / folder, filename)
