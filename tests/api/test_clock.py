"""Clock and configuration."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from app import clock, create_app

TOLERANCE = timedelta(seconds=5)


def test_A15_fixed_now_fixes_the_clock(fixed_now: datetime) -> None:
    assert clock.now() == datetime(2026, 1, 5, 9, 0)
    assert clock.now().tzinfo is None


def test_A16_real_clock_is_naive_clinic_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLINIC_TZ", raising=False)
    expected = datetime.now(ZoneInfo("Asia/Karachi")).replace(tzinfo=None)
    actual = clock.now()
    assert actual.tzinfo is None
    assert abs(actual - expected) < TOLERANCE


def test_A16_real_clock_follows_clinic_tz(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLINIC_TZ", "UTC")
    expected = datetime.now(ZoneInfo("UTC")).replace(tzinfo=None)
    assert abs(clock.now() - expected) < TOLERANCE


def test_A17_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("SECRET_KEY", "CLINIC_TZ", "CLINIC_DATABASE"):
        monkeypatch.delenv(name, raising=False)
    app = create_app()
    assert app.config["SECRET_KEY"] == "dev"
    assert app.config["CLINIC_TZ"] == "Asia/Karachi"
    assert Path(app.config["DATABASE"]).parts[-2:] == ("instance", "clinic.db")


def test_A18_test_config_overrides_env_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("CLINIC_DATABASE", str(tmp_path / "env.db"))
    given = str(tmp_path / "given.db")
    app = create_app({"DATABASE": given, "TESTING": True})
    assert app.config["DATABASE"] == given
    assert app.config["TESTING"] is True


def test_A17_config_database_from_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    db_path = str(tmp_path / "env.db")
    monkeypatch.setenv("CLINIC_DATABASE", db_path)
    assert create_app().config["DATABASE"] == db_path
