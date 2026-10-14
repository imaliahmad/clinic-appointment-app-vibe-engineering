"""Login, logout and me."""

from __future__ import annotations

from flask import Flask
from flask.testing import FlaskClient

from app.db import get_db
from app.seed import seed_doctors, seed_users


def _seed(app: Flask) -> None:
    with app.app_context():
        seed_doctors()
        seed_users("2026-01-05T09:00")
        get_db().commit()


def _login(client: FlaskClient, username: str, password: str):  # noqa: ANN202
    return client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )


def test_A1_login_success(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    response = _login(client, "reception", "reception123")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["role"] == "receptionist"
    assert "password_hash" not in data


def test_A3_wrong_password_returns_401(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    response = _login(client, "reception", "nope")
    assert response.status_code == 401
    assert response.get_json()["status"] is False


def test_A6_missing_password_returns_400(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    response = client.post("/api/auth/login", json={"username": "reception"})
    assert response.status_code == 400


def test_A7_me_without_login_returns_401(client: FlaskClient) -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_A8_logout_clears_session(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    _login(client, "admin", "admin123")
    assert client.get("/api/auth/me").status_code == 200
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").status_code == 401


def test_A11_wrong_role_returns_403(app: Flask, client: FlaskClient) -> None:
    from app.auth import role_required

    @app.get("/api/_only_admin")
    @role_required("admin")
    def only_admin() -> str:
        return "ok"

    _seed(app)
    assert client.get("/api/_only_admin").status_code == 401
    _login(client, "reception", "reception123")
    response = client.get("/api/_only_admin")
    assert response.status_code == 403
    assert response.get_json()["status"] is False


def test_A13_page_without_login_redirects_to_login(client: FlaskClient) -> None:
    response = client.get("/reception")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_A14_other_role_page_redirects_to_own_page(
    app: Flask, client: FlaskClient
) -> None:
    _seed(app)
    _login(client, "reception", "reception123")
    response = client.get("/doctor")
    assert response.status_code == 302
    assert response.headers["Location"] == "/reception"
    assert client.get("/reception").status_code == 200


def test_A16_login_page_redirects_signed_in_user(
    app: Flask, client: FlaskClient
) -> None:
    _seed(app)
    _login(client, "drali", "doctor123")
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/doctor"


def _set_active(app: Flask, username: str, active: int) -> None:
    with app.app_context():
        db = get_db()
        db.execute("UPDATE users SET active = ? WHERE username = ?", (active, username))
        db.commit()


def _add_admin_route(app: Flask) -> None:
    from app.auth import role_required

    @app.get("/api/_only_admin2")
    @role_required("admin")
    def only_admin2() -> str:
        return "ok"


def test_A1_login_sets_cookie_and_returns_user_fields(
    app: Flask, client: FlaskClient
) -> None:
    _seed(app)
    response = _login(client, "reception", "reception123")
    body = response.get_json()
    assert body["status"] is True
    assert body["message"]
    assert body["data"]["username"] == "reception"
    assert isinstance(body["data"]["id"], int)
    assert "password" not in response.get_data(as_text=True).lower()
    assert "session=" in response.headers.get("Set-Cookie", "")


def test_A2_doctor_login_me_has_doctor_id(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    with app.app_context():
        row = (
            get_db()
            .execute("SELECT id FROM doctors WHERE name = ?", ("Dr Ali Khan",))
            .fetchone()
        )
        doctor_id = row["id"]
    response = _login(client, "drali", "doctor123")
    assert response.status_code == 200
    assert response.get_json()["data"]["role"] == "doctor"
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    data = me.get_json()["data"]
    assert data["doctor_id"] == doctor_id
    assert data["username"] == "drali"
    assert "password" not in me.get_data(as_text=True).lower()


def test_A4_unknown_username_returns_401_same_message(
    app: Flask, client: FlaskClient
) -> None:
    _seed(app)
    wrong_pw = _login(client, "reception", "nope").get_json()
    unknown = _login(client, "nobody", "whatever")
    assert unknown.status_code == 401
    assert unknown.get_json()["status"] is False
    assert unknown.get_json()["message"] == wrong_pw["message"]
    assert unknown.get_json()["message"] == "Invalid username or password"


def test_A5_inactive_user_login_returns_401(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    _set_active(app, "reception", 0)
    response = _login(client, "reception", "reception123")
    assert response.status_code == 401
    assert response.get_json()["status"] is False
    assert response.get_json()["message"] == "Invalid username or password"


def test_A6_blank_username_returns_400(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    for username in ("", "   "):
        response = _login(client, username, "reception123")
        assert response.status_code == 400
        assert response.get_json()["status"] is False


def test_A6_blank_password_returns_400(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    assert _login(client, "reception", "").status_code == 400


def test_A6_missing_username_returns_400(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    response = client.post("/api/auth/login", json={"password": "x"})
    assert response.status_code == 400
    assert response.get_json()["status"] is False


def test_A6_missing_password_has_message(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    response = client.post("/api/auth/login", json={"username": "reception"})
    assert response.get_json()["status"] is False
    assert response.get_json()["message"]


def test_A6_no_json_body_returns_400(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    response = client.post("/api/auth/login")
    assert response.status_code == 400
    assert response.get_json()["status"] is False


def test_A6_non_json_body_returns_400(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    response = client.post(
        "/api/auth/login", data="username=reception", content_type="text/plain"
    )
    assert response.status_code == 400
    assert response.get_json()["status"] is False


def test_A7_me_without_login_has_json_envelope(client: FlaskClient) -> None:
    body = client.get("/api/auth/me").get_json()
    assert body["status"] is False
    assert body["message"]


def test_A8_logout_returns_envelope(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    _login(client, "reception", "reception123")
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.get_json()["status"] is True
    assert response.get_json()["message"]


def test_A9_logout_without_login_returns_401(client: FlaskClient) -> None:
    response = client.post("/api/auth/logout")
    assert response.status_code == 401
    assert response.get_json()["status"] is False


def test_A10_deactivated_user_session_returns_401(
    app: Flask, client: FlaskClient
) -> None:
    _seed(app)
    _login(client, "reception", "reception123")
    assert client.get("/api/auth/me").status_code == 200
    _set_active(app, "reception", 0)
    assert client.get("/api/auth/me").status_code == 401
    # the session was cleared, so reactivating does not bring it back
    _set_active(app, "reception", 1)
    assert client.get("/api/auth/me").status_code == 401


def test_A10_deleted_user_session_returns_401(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    _login(client, "admin", "admin123")
    with app.app_context():
        get_db().execute("DELETE FROM users WHERE username = ?", ("admin",))
        get_db().commit()
    assert client.get("/api/auth/me").status_code == 401


def test_A11_receptionist_on_admin_route_returns_403(
    app: Flask, client: FlaskClient
) -> None:
    _add_admin_route(app)
    _seed(app)
    _login(client, "reception", "reception123")
    response = client.get("/api/_only_admin2")
    assert response.status_code == 403
    body = response.get_json()
    assert body["status"] is False
    assert body["message"]


def test_A11_admin_on_admin_route_returns_200(app: Flask, client: FlaskClient) -> None:
    _add_admin_route(app)
    _seed(app)
    _login(client, "admin", "admin123")
    assert client.get("/api/_only_admin2").status_code == 200


def test_A12_admin_route_without_login_returns_401(
    app: Flask, client: FlaskClient
) -> None:
    _add_admin_route(app)
    response = client.get("/api/_only_admin2")
    assert response.status_code == 401
    assert response.get_json()["status"] is False


def test_A13_all_role_pages_without_login_redirect(client: FlaskClient) -> None:
    for path in ("/reception", "/doctor", "/admin"):
        response = client.get(path)
        assert response.status_code == 302, path
        assert response.headers["Location"] == "/", path


def test_A14_doctor_and_admin_redirected_to_own_pages(
    app: Flask, client: FlaskClient
) -> None:
    _seed(app)
    _login(client, "drali", "doctor123")
    response = client.get("/admin")
    assert response.status_code == 302
    assert response.headers["Location"] == "/doctor"
    client.post("/api/auth/logout")
    _login(client, "admin", "admin123")
    response = client.get("/reception")
    assert response.status_code == 302
    assert response.headers["Location"] == "/admin"


def test_A15_admin_page_as_admin_returns_html(app: Flask, client: FlaskClient) -> None:
    _seed(app)
    _login(client, "admin", "admin123")
    response = client.get("/admin")
    assert response.status_code == 200
    assert "text/html" in response.content_type


def test_A16_login_page_when_not_logged_in_returns_200(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.content_type


def test_A17_session_cookie_is_httponly_and_samesite_lax(
    app: Flask, client: FlaskClient
) -> None:
    _seed(app)
    cookie = _login(client, "reception", "reception123").headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


def test_login_assets_are_served_but_pages_are_not(client: FlaskClient) -> None:
    assert client.get("/static/js/login.js").status_code == 200
    assert client.get("/static/css/style.css").status_code == 200
    assert client.get("/static/admin.html").status_code == 404
