"""Configuration from environment variables, with dev-only fallbacks."""

from __future__ import annotations

import os
from typing import Any

DEFAULT_SECRET_KEY = "dev"
DEFAULT_CLINIC_TZ = "Asia/Karachi"
DEFAULT_DATABASE_NAME = "clinic.db"


def get_clinic_tz() -> str:
    """Return the clinic time zone name (e.g. 'Asia/Karachi')."""
    return os.environ.get("CLINIC_TZ") or DEFAULT_CLINIC_TZ


def load_config(instance_path: str) -> dict[str, Any]:
    """Build the Flask config dict. The default database lives in the instance folder."""
    return {
        "SECRET_KEY": os.environ.get("SECRET_KEY") or DEFAULT_SECRET_KEY,
        "CLINIC_TZ": get_clinic_tz(),
        "DATABASE": os.environ.get("CLINIC_DATABASE")
        or os.path.join(instance_path, DEFAULT_DATABASE_NAME),
    }
