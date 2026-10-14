"""Login decorators for API routes."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import redirect, session

from app.responses import failure
from app.rules.auth_rules import can_access_page, home_path_for_role
from app.services import auth_service


def current_user() -> dict[str, Any] | None:
    """Return the logged-in, active user; clear a stale session."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    user = auth_service.get_active_user(user_id)
    if user is None:
        session.clear()
    return user


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if current_user() is None:
            return failure("Login required", status_code=401)
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """API decorator: 401 if not logged in, 403 if the role is not allowed."""

    def decorator(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            user = current_user()
            if user is None:
                return failure("Login required", status_code=401)
            if user["role"] not in roles:
                return failure("You are not allowed to do this", status_code=403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def page_role_required(
    page_role: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Page decorator: redirect to `/` if not logged in, to the user's own page if the role differs."""

    def decorator(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            user = current_user()
            if user is None:
                return redirect("/")
            if not can_access_page(user["role"], page_role):
                return redirect(home_path_for_role(user["role"]))
            return view(*args, **kwargs)

        return wrapped

    return decorator
