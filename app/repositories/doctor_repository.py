"""SQL for doctors and their weekly hours."""

from __future__ import annotations

from app.db import get_db


def get_doctor_id_by_name(name: str) -> int | None:
    row = get_db().execute("SELECT id FROM doctors WHERE name = ?", (name,)).fetchone()
    return row["id"] if row else None


def insert_doctor(name: str, specialty: str, slot_minutes: int) -> int:
    cursor = get_db().execute(
        "INSERT INTO doctors (name, specialty, slot_minutes) VALUES (?, ?, ?)",
        (name, specialty, slot_minutes),
    )
    return cursor.lastrowid


def insert_doctor_hours(
    doctor_id: int, weekday: int, start_time: str, end_time: str
) -> bool:
    """Add hours for one weekday. Returns False if that weekday already has hours."""
    cursor = get_db().execute(
        "INSERT OR IGNORE INTO doctor_hours (doctor_id, weekday, start_time, end_time)"
        " VALUES (?, ?, ?, ?)",
        (doctor_id, weekday, start_time, end_time),
    )
    return cursor.rowcount == 1
