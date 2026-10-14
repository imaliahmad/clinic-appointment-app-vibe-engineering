"""Pure rules for roles and pages. No Flask, no DB."""

from __future__ import annotations

HOME_PATHS: dict[str, str] = {
    "receptionist": "/reception",
    "doctor": "/doctor",
    "admin": "/admin",
}


def home_path_for_role(role: str) -> str:
    """Return the page path a user with this role lands on."""
    if role not in HOME_PATHS:
        raise ValueError(f"Unknown role: {role}")
    return HOME_PATHS[role]


def can_access_page(role: str, page_role: str) -> bool:
    """A page is only for the role it belongs to."""
    return role == page_role
