"""Unit tests for app/rules/auth_rules.py."""

from __future__ import annotations

import pytest

from app.rules.auth_rules import can_access_page, home_path_for_role


@pytest.mark.parametrize(
    ("role", "path"),
    [("receptionist", "/reception"), ("doctor", "/doctor"), ("admin", "/admin")],
)
def test_U1_U3_home_path_for_role(role: str, path: str) -> None:
    assert home_path_for_role(role) == path


def test_U4_unknown_role_raises() -> None:
    with pytest.raises(ValueError):
        home_path_for_role("nurse")


def test_U4_empty_role_raises() -> None:
    with pytest.raises(ValueError):
        home_path_for_role("")


@pytest.mark.parametrize("role", ["receptionist", "doctor", "admin"])
def test_U5_every_role_can_access_its_own_page(role: str) -> None:
    assert can_access_page(role, role) is True


@pytest.mark.parametrize(
    ("role", "page_role"),
    [
        ("receptionist", "doctor"),
        ("receptionist", "admin"),
        ("doctor", "receptionist"),
        ("admin", "doctor"),
        ("admin", "receptionist"),
    ],
)
def test_U6_U7_every_other_page_is_denied(role: str, page_role: str) -> None:
    assert can_access_page(role, page_role) is False


def test_U5_own_page_allowed() -> None:
    assert can_access_page("doctor", "doctor") is True


def test_U6_other_page_denied() -> None:
    assert can_access_page("doctor", "admin") is False


def test_U7_admin_has_no_access_to_other_roles_pages() -> None:
    assert can_access_page("admin", "receptionist") is False
