"""JSON response helpers. Every API response uses this envelope:
{"status": true|false, "message": "...", "data": ..., "errors": []}
"""

from __future__ import annotations

from typing import Any

from flask import Response, jsonify


def success(
    data: Any = None, message: str = "OK", status_code: int = 200
) -> tuple[Response, int]:
    body = {"status": True, "message": message, "data": data, "errors": []}
    return jsonify(body), status_code


def failure(
    message: str, errors: list[str] | None = None, status_code: int = 400
) -> tuple[Response, int]:
    body = {"status": False, "message": message, "data": None, "errors": errors or []}
    return jsonify(body), status_code
