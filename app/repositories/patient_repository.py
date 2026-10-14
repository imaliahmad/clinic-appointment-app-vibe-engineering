"""SQL for patients."""

from __future__ import annotations

from typing import Any

from app.db import get_db


def get_patient_by_phone(phone: str) -> dict[str, Any] | None:
    row = (
        get_db().execute("SELECT * FROM patients WHERE phone = ?", (phone,)).fetchone()
    )
    return dict(row) if row else None


def insert_patient(
    name: str, phone: str, date_of_birth: str | None, created_at: str
) -> int:
    cursor = get_db().execute(
        "INSERT INTO patients (name, phone, date_of_birth, created_at) VALUES (?, ?, ?, ?)",
        (name, phone, date_of_birth, created_at),
    )
    return cursor.lastrowid
