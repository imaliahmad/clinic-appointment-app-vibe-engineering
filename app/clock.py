"""The ONLY place that reads the real clock. Tests replace `now()` to fix the time."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import get_clinic_tz


def now() -> datetime:
    """Current clinic-local time as a naive datetime (no tzinfo), like stored times."""
    return datetime.now(ZoneInfo(get_clinic_tz())).replace(tzinfo=None)
