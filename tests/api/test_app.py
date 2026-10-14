"""App factory, pages, JSON envelope and API 404."""

from __future__ import annotations

from flask import Flask
from flask.testing import FlaskClient

from app.responses import failure, success


def test_A1_login_page_is_served(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"Clinic Booking" in response.data


def test_A2_success_envelope(app: Flask) -> None:
    with app.test_request_context():
        response, code = success({"x": 1}, "Done")
    assert code == 200
    assert response.get_json() == {
        "status": True,
        "message": "Done",
        "data": {"x": 1},
        "errors": [],
    }


def test_A3_success_with_status_code_201(app: Flask) -> None:
    with app.test_request_context():
        response, code = success({"id": 5}, "Created", status_code=201)
    assert code == 201
    assert response.get_json()["status"] is True
    assert response.get_json()["data"] == {"id": 5}


def test_A4_failure_without_errors_gives_empty_list(app: Flask) -> None:
    with app.test_request_context():
        response, code = failure("Bad")
    assert code == 400
    assert response.get_json() == {
        "status": False,
        "message": "Bad",
        "data": None,
        "errors": [],
    }


def test_A4_failure_envelope(app: Flask) -> None:
    with app.test_request_context():
        response, code = failure("Bad input", ["phone is required"], 400)
    assert code == 400
    assert response.get_json() == {
        "status": False,
        "message": "Bad input",
        "data": None,
        "errors": ["phone is required"],
    }


def test_A5_unknown_api_path_returns_json_404(client: FlaskClient) -> None:
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json() == {
        "status": False,
        "message": "Not found",
        "data": None,
        "errors": [],
    }


def test_A6_unknown_page_returns_html_404(client: FlaskClient) -> None:
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert not response.is_json
