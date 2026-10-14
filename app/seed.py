"""`seed` command: sample doctors, weekly hours, users and patients. Local development only.

Safe to run twice: rows that already exist (doctor by name, user by username, patient by phone)
are left alone, and only missing ones are added.
"""

from __future__ import annotations

import logging
from typing import Any

import click
from flask import Flask
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from app import clock
from app.db import get_db
from app.repositories import doctor_repository, patient_repository, user_repository

logger = logging.getLogger(__name__)

TIME_FORMAT = "%Y-%m-%dT%H:%M"

ALL_WEEK = (0, 1, 2, 3, 4, 5, 6)
MON_TO_FRI = (0, 1, 2, 3, 4)

DOCTORS: list[dict[str, Any]] = [
    {
        "name": "Dr Ali Khan",
        "specialty": "General Physician",
        "slot_minutes": 15,
        "weekdays": ALL_WEEK,
        "start_time": "09:00",
        "end_time": "17:00",
    },
    {
        "name": "Dr Sara Ahmed",
        "specialty": "Pediatrics",
        "slot_minutes": 20,
        "weekdays": MON_TO_FRI,
        "start_time": "10:00",
        "end_time": "14:00",
    },
    {
        "name": "Dr Bilal Hussain",
        "specialty": "Dermatology",
        "slot_minutes": 30,
        "weekdays": (0, 2, 5),
        "start_time": "16:00",
        "end_time": "20:00",
    },
]

# Dr Bilal Hussain has no login on purpose: bookable, but no doctor page.
USERS: list[dict[str, Any]] = [
    {"username": "admin", "password": "admin123", "role": "admin", "doctor": None},
    {
        "username": "reception",
        "password": "reception123",
        "role": "receptionist",
        "doctor": None,
    },
    {
        "username": "drali",
        "password": "doctor123",
        "role": "doctor",
        "doctor": "Dr Ali Khan",
    },
    {
        "username": "drsara",
        "password": "doctor123",
        "role": "doctor",
        "doctor": "Dr Sara Ahmed",
    },
]

PATIENTS: list[dict[str, Any]] = [
    {"name": "Ahmed Raza", "phone": "03001234567", "date_of_birth": "1985-03-12"},
    {"name": "Fatima Noor", "phone": "03111234567", "date_of_birth": "1992-07-25"},
    {"name": "Usman Tariq", "phone": "03211234567", "date_of_birth": None},
    {"name": "Ayesha Siddiqui", "phone": "03331234567", "date_of_birth": "2015-11-02"},
    {"name": "Hamza Iqbal", "phone": "03451234567", "date_of_birth": "1970-01-30"},
]


def seed_doctors() -> tuple[tuple[int, int], tuple[int, int]]:
    """Add missing doctors and their hours. Returns ((added, skipped) doctors, (added, skipped) hours)."""
    doctors_added = doctors_skipped = hours_added = hours_skipped = 0
    for doctor in DOCTORS:
        if doctor_repository.get_doctor_id_by_name(doctor["name"]) is not None:
            doctors_skipped += 1
            continue
        doctor_id = doctor_repository.insert_doctor(
            doctor["name"], doctor["specialty"], doctor["slot_minutes"]
        )
        doctors_added += 1
        for weekday in doctor["weekdays"]:
            if doctor_repository.insert_doctor_hours(
                doctor_id, weekday, doctor["start_time"], doctor["end_time"]
            ):
                hours_added += 1
            else:
                hours_skipped += 1
    return (doctors_added, doctors_skipped), (hours_added, hours_skipped)


def seed_users(created_at: str) -> tuple[int, int]:
    """Add missing users (password hashed, doctors linked by name). Existing users are not changed."""
    added = skipped = 0
    for user in USERS:
        if user_repository.get_user_by_username(user["username"]) is not None:
            skipped += 1
            continue
        doctor_id = (
            doctor_repository.get_doctor_id_by_name(user["doctor"])
            if user["doctor"]
            else None
        )
        user_repository.insert_user(
            user["username"],
            generate_password_hash(user["password"]),
            user["role"],
            doctor_id,
            created_at,
        )
        added += 1
    return added, skipped


def seed_patients(created_at: str) -> tuple[int, int]:
    """Add missing patients (found by phone)."""
    added = skipped = 0
    for patient in PATIENTS:
        if patient_repository.get_patient_by_phone(patient["phone"]) is not None:
            skipped += 1
            continue
        patient_repository.insert_patient(
            patient["name"], patient["phone"], patient["date_of_birth"], created_at
        )
        added += 1
    return added, skipped


def echo_counts(label: str, counts: tuple[int, int]) -> None:
    added, skipped = counts
    click.echo(f"{label}: {added} added, {skipped} already there")


@click.command("seed")
@with_appcontext
def seed_command() -> None:
    """Insert sample data that is missing (safe to run twice)."""
    created_at = clock.now().strftime(TIME_FORMAT)
    doctors, hours = seed_doctors()
    users = seed_users(created_at)
    patients = seed_patients(created_at)
    get_db().commit()
    echo_counts("Doctors", doctors)
    echo_counts("Doctor hours", hours)
    echo_counts("Users", users)
    echo_counts("Patients", patients)


def init_app(app: Flask) -> None:
    app.cli.add_command(seed_command)
