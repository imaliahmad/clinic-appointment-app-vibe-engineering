"""`seed` command: sample doctors, hours, users and patients."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from click.testing import Result
from flask import Flask
from flask.testing import FlaskCliRunner
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db


def count_rows(app: Flask, table: str) -> int:
    with app.app_context():
        return get_db().execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_seed_adds_doctors_and_hours(app: Flask, runner: FlaskCliRunner) -> None:
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0
    assert "Doctors: 3 added, 0 already there" in result.output
    assert "Doctor hours: 15 added, 0 already there" in result.output
    assert count_rows(app, "doctors") == 3
    assert count_rows(app, "doctor_hours") == 15


def test_seed_adds_users_with_hashed_passwords_and_doctor_links(
    app: Flask, runner: FlaskCliRunner
) -> None:
    result = runner.invoke(args=["seed"])
    assert "Users: 4 added, 0 already there" in result.output
    with app.app_context():
        rows = get_db().execute(
            "SELECT u.username, u.password_hash, u.role, d.name AS doctor_name"
            " FROM users u LEFT JOIN doctors d ON d.id = u.doctor_id"
        )
        users = {row["username"]: dict(row) for row in rows}
    assert users["drali"]["doctor_name"] == "Dr Ali Khan"
    assert users["drsara"]["role"] == "doctor"
    assert users["admin"]["doctor_name"] is None
    assert check_password_hash(users["reception"]["password_hash"], "reception123")


def test_seed_adds_patients(app: Flask, runner: FlaskCliRunner) -> None:
    result = runner.invoke(args=["seed"])
    assert "Patients: 5 added, 0 already there" in result.output
    assert count_rows(app, "patients") == 5


def test_seed_twice_adds_nothing_the_second_time(
    app: Flask, runner: FlaskCliRunner
) -> None:
    runner.invoke(args=["seed"])
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0
    assert "Doctors: 0 added, 3 already there" in result.output
    assert "Doctor hours: 0 added, 0 already there" in result.output
    assert "Users: 0 added, 4 already there" in result.output
    assert "Patients: 0 added, 5 already there" in result.output
    assert count_rows(app, "doctor_hours") == 15


# Spec cases A1-A11


def query(app: Flask, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with app.app_context():
        return [dict(r) for r in get_db().execute(sql, params).fetchall()]


def seed_once(app: Flask, runner: FlaskCliRunner) -> Result:
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0, result.output
    return result


def test_A1_seed_on_empty_db_creates_all_rows(
    app: Flask, runner: FlaskCliRunner
) -> None:
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0
    assert count_rows(app, "doctors") == 3
    assert count_rows(app, "doctor_hours") == 15
    assert count_rows(app, "users") == 4
    assert count_rows(app, "patients") == 5


def test_A2_seed_twice_keeps_counts_and_reports_zero_added(
    app: Flask, runner: FlaskCliRunner
) -> None:
    first = runner.invoke(args=["seed"])
    second = runner.invoke(args=["seed"])
    assert first.exit_code == 0
    assert second.exit_code == 0
    lines = [ln for ln in second.output.splitlines() if ln.strip()]
    assert len(lines) == 4
    assert all(": 0 added" in ln for ln in lines)
    assert count_rows(app, "doctors") == 3
    assert count_rows(app, "doctor_hours") == 15
    assert count_rows(app, "users") == 4
    assert count_rows(app, "patients") == 5


def test_A3_doctors_have_three_different_valid_slot_minutes(
    app: Flask, runner: FlaskCliRunner
) -> None:
    seed_once(app, runner)
    slots = [r["slot_minutes"] for r in query(app, "SELECT slot_minutes FROM doctors")]
    assert len(slots) == 3
    assert len(set(slots)) == 3
    assert all(s in (10, 15, 20, 30, 45, 60) for s in slots)


def test_A4_at_least_one_doctor_works_all_seven_weekdays(
    app: Flask, runner: FlaskCliRunner
) -> None:
    seed_once(app, runner)
    rows = query(app, "SELECT doctor_id, weekday FROM doctor_hours")
    by_doctor: dict[int, set[int]] = {}
    for r in rows:
        by_doctor.setdefault(r["doctor_id"], set()).add(r["weekday"])
    assert any(days == set(range(7)) for days in by_doctor.values())


def test_A5_doctors_have_different_weekly_hours(
    app: Flask, runner: FlaskCliRunner
) -> None:
    seed_once(app, runner)
    rows = query(
        app, "SELECT doctor_id, weekday, start_time, end_time FROM doctor_hours"
    )
    schedules: dict[int, set[tuple]] = {}
    for r in rows:
        schedules.setdefault(r["doctor_id"], set()).add(
            (r["weekday"], r["start_time"], r["end_time"])
        )
    assert len(schedules) == 3
    assert len({frozenset(s) for s in schedules.values()}) == 3


def test_A6_every_hours_row_is_valid_and_fits_one_slot(
    app: Flask, runner: FlaskCliRunner
) -> None:
    seed_once(app, runner)
    rows = query(
        app,
        "SELECT h.start_time, h.end_time, d.slot_minutes FROM doctor_hours h"
        " JOIN doctors d ON d.id = h.doctor_id",
    )
    assert len(rows) == 15
    for r in rows:
        assert re.fullmatch(r"\d{2}:\d{2}", r["start_time"])
        assert re.fullmatch(r"\d{2}:\d{2}", r["end_time"])
        assert r["start_time"] < r["end_time"]
        start = datetime.strptime(r["start_time"], "%H:%M")
        end = datetime.strptime(r["end_time"], "%H:%M")
        assert (end - start).total_seconds() / 60 >= r["slot_minutes"]


def test_A7_users_have_right_roles_links_and_are_active(
    app: Flask, runner: FlaskCliRunner
) -> None:
    seed_once(app, runner)
    rows = query(
        app,
        "SELECT u.username, u.role, u.active, u.doctor_id, d.name AS doctor_name"
        " FROM users u LEFT JOIN doctors d ON d.id = u.doctor_id",
    )
    users = {r["username"]: r for r in rows}
    assert set(users) == {"admin", "reception", "drali", "drsara"}
    assert users["admin"]["role"] == "admin"
    assert users["reception"]["role"] == "receptionist"
    assert users["drali"]["role"] == "doctor"
    assert users["drsara"]["role"] == "doctor"
    assert users["drali"]["doctor_name"] == "Dr Ali Khan"
    assert users["drsara"]["doctor_name"] == "Dr Sara Ahmed"
    assert users["admin"]["doctor_id"] is None
    assert users["reception"]["doctor_id"] is None
    assert all(u["active"] == 1 for u in users.values())


def test_A8_passwords_are_hashed_and_verify(app: Flask, runner: FlaskCliRunner) -> None:
    seed_once(app, runner)
    passwords = {
        "admin": "admin123",
        "reception": "reception123",
        "drali": "doctor123",
        "drsara": "doctor123",
    }
    rows = query(app, "SELECT username, password_hash FROM users")
    hashes = {r["username"]: r["password_hash"] for r in rows}
    assert set(hashes) == set(passwords)
    for username, plain in passwords.items():
        assert hashes[username] != plain
        assert check_password_hash(hashes[username], plain)


def test_A9_patients_have_valid_unique_phones_and_birth_dates(
    app: Flask, runner: FlaskCliRunner, fixed_now: datetime
) -> None:
    seed_once(app, runner)
    rows = query(app, "SELECT phone, date_of_birth FROM patients")
    assert len(rows) == 5
    phones = [r["phone"] for r in rows]
    assert len(set(phones)) == 5
    for phone in phones:
        assert phone.isdigit()
        assert 10 <= len(phone) <= 15
    for r in rows:
        dob = r["date_of_birth"]
        if dob is None:
            continue
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", dob)
        assert date.fromisoformat(dob) < fixed_now.date()


def test_A10_partly_seeded_db_keeps_existing_user_and_adds_rest(
    app: Flask, runner: FlaskCliRunner
) -> None:
    original_hash = generate_password_hash("other-password")
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO users (username, password_hash, role, doctor_id, created_at)"
            " VALUES (?, ?, 'admin', NULL, '2025-01-01T00:00')",
            ("admin", original_hash),
        )
        db.commit()
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0
    assert "Users: 3 added, 1 already there" in result.output
    rows = query(app, "SELECT username, password_hash FROM users")
    hashes = {r["username"]: r["password_hash"] for r in rows}
    assert set(hashes) == {"admin", "reception", "drali", "drsara"}
    assert hashes["admin"] == original_hash
    assert not check_password_hash(hashes["admin"], "admin123")


def test_A11_created_at_equals_fixed_clock(
    app: Flask, runner: FlaskCliRunner, fixed_now: datetime
) -> None:
    seed_once(app, runner)
    users = query(app, "SELECT created_at FROM users")
    patients = query(app, "SELECT created_at FROM patients")
    assert len(users) == 4
    assert len(patients) == 5
    assert {r["created_at"] for r in users} == {"2026-01-05T09:00"}
    assert {r["created_at"] for r in patients} == {"2026-01-05T09:00"}
