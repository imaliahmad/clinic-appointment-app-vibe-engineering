"""Shared API test fixtures: app with a temporary database, test client, CLI runner."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from app import clock, create_app
from app.db import init_db


@pytest.fixture
def app(tmp_path: Path) -> Iterator[Flask]:
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    with app.app_context():
        init_db()
    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


FIXED_NOW = datetime(2026, 1, 5, 9, 0)  # a Monday, clinic-local


@pytest.fixture
def fixed_now(monkeypatch: pytest.MonkeyPatch) -> datetime:
    """Fix `app.clock.now()` to FIXED_NOW and return it."""
    monkeypatch.setattr(clock, "now", lambda: FIXED_NOW)
    return FIXED_NOW
