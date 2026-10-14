"""Schema, double-booking index and init-db command."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskCliRunner

from app.db import get_db

NOW = "2026-01-05T09:00"


def insert_doctor(db: sqlite3.Connection, name: str = "Dr Test") -> int:
    cursor = db.execute(
        "INSERT INTO doctors (name, specialty, slot_minutes) VALUES (?, ?, ?)",
        (name, "General", 15),
    )
    return cursor.lastrowid


def insert_appointment(
    db: sqlite3.Connection, doctor_id: int, status: str = "booked"
) -> None:
    db.execute(
        "INSERT INTO appointments (doctor_id, patient_id, start_at, end_at, status,"
        " created_by, created_at, updated_at) VALUES (?, 1, ?, ?, ?, 1, ?, ?)",
        (doctor_id, "2026-01-06T09:00", "2026-01-06T09:15", status, NOW, NOW),
    )


@pytest.fixture
def db(app: Flask) -> Iterator[sqlite3.Connection]:
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO users (username, password_hash, role, created_at)"
            " VALUES ('reception', 'x', 'receptionist', ?)",
            (NOW,),
        )
        db.execute(
            "INSERT INTO patients (name, phone, created_at) VALUES ('Pat', '03001234567', ?)",
            (NOW,),
        )
        yield db


def test_A7_init_db_creates_tables_and_index(db: sqlite3.Connection) -> None:
    names = {
        row["name"]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'index')"
        )
    }
    for table in ("users", "doctors", "doctor_hours", "patients", "appointments"):
        assert table in names
    assert "idx_appointments_doctor_start_active" in names


def test_A8_init_db_twice_keeps_data(app: Flask, runner: FlaskCliRunner) -> None:
    with app.app_context():
        db = get_db()
        insert_doctor(db, "Dr Keep")
        db.commit()

    for _ in range(2):
        result = runner.invoke(args=["init-db"])
        assert result.exit_code == 0
        assert "Initialized the database." in result.output

    with app.app_context():
        row = get_db().execute("SELECT name FROM doctors").fetchone()
    assert row["name"] == "Dr Keep"


def test_A19_seed_command_runs(runner: FlaskCliRunner) -> None:
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0


def test_A9_double_booking_same_doctor_and_start_is_rejected(
    db: sqlite3.Connection,
) -> None:
    doctor_id = insert_doctor(db)
    insert_appointment(db, doctor_id)
    with pytest.raises(sqlite3.IntegrityError):
        insert_appointment(db, doctor_id)


def test_A11_same_start_for_two_doctors_both_saved(db: sqlite3.Connection) -> None:
    first = insert_doctor(db, "Dr One")
    second = insert_doctor(db, "Dr Two")
    insert_appointment(db, first)
    insert_appointment(db, second)
    count = db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    assert count == 2


def test_A12_foreign_key_unknown_doctor_is_rejected(db: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        insert_appointment(db, 9999)


def test_A13_check_slot_minutes_25_is_rejected(db: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO doctors (name, specialty, slot_minutes) VALUES ('D', 'G', 25)"
        )


def test_A13_check_weekday_7_is_rejected(db: sqlite3.Connection) -> None:
    doctor_id = insert_doctor(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO doctor_hours (doctor_id, weekday, start_time, end_time)"
            " VALUES (?, 7, '09:00', '17:00')",
            (doctor_id,),
        )


def test_A13_check_weekday_0_and_6_are_accepted(db: sqlite3.Connection) -> None:
    doctor_id = insert_doctor(db)
    for weekday in (0, 6):
        db.execute(
            "INSERT INTO doctor_hours (doctor_id, weekday, start_time, end_time)"
            " VALUES (?, ?, '09:00', '17:00')",
            (doctor_id, weekday),
        )
    count = db.execute("SELECT COUNT(*) FROM doctor_hours").fetchone()[0]
    assert count == 2


def test_A13_check_status_pending_is_rejected(db: sqlite3.Connection) -> None:
    doctor_id = insert_doctor(db)
    with pytest.raises(sqlite3.IntegrityError):
        insert_appointment(db, doctor_id, status="pending")


def test_A13_check_role_nurse_is_rejected(db: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO users (username, password_hash, role, created_at)"
            " VALUES ('nina', 'x', 'nurse', ?)",
            (NOW,),
        )


def test_A14_duplicate_patient_phone_is_rejected(db: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO patients (name, phone, created_at)"
            " VALUES ('Other', '03001234567', ?)",
            (NOW,),
        )


def test_A14_duplicate_username_is_rejected(db: sqlite3.Connection) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO users (username, password_hash, role, created_at)"
            " VALUES ('reception', 'y', 'admin', ?)",
            (NOW,),
        )


def test_A14_duplicate_doctor_hours_same_weekday_is_rejected(
    db: sqlite3.Connection,
) -> None:
    doctor_id = insert_doctor(db)
    sql = (
        "INSERT INTO doctor_hours (doctor_id, weekday, start_time, end_time)"
        " VALUES (?, 2, '09:00', '17:00')"
    )
    db.execute(sql, (doctor_id,))
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(sql, (doctor_id,))


def test_A10_cancelled_slot_can_be_booked_again(db: sqlite3.Connection) -> None:
    doctor_id = insert_doctor(db)
    insert_appointment(db, doctor_id, status="cancelled")
    insert_appointment(db, doctor_id)
    count = db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    assert count == 2
