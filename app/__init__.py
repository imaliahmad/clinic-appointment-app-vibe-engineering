"""Clinic Booking: Flask app factory."""

from __future__ import annotations

import logging
import os
from typing import Any

from flask import Flask, request
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import NotFound

from app.config import load_config
from app.responses import failure


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure the Flask app. `test_config` overrides the environment."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(load_config(app.instance_path))
    if test_config is not None:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    logging.basicConfig(level=logging.INFO)

    from app import db, seed
    from app.endpoints.page_endpoints import page_bp

    db.init_app(app)
    seed.init_app(app)
    app.register_blueprint(page_bp)

    @app.errorhandler(404)
    def not_found(error: NotFound) -> ResponseReturnValue:
        if request.path.startswith("/api/"):
            return failure("Not found", status_code=404)
        return error

    return app
