"""HTML pages served from frontend/."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, Response, send_from_directory

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

page_bp = Blueprint("pages", __name__)


@page_bp.get("/")
def login_page() -> Response:
    return send_from_directory(FRONTEND_DIR, "login.html")
