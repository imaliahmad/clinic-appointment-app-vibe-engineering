"""SQLite connection per request and the init-db command."""

from __future__ import annotations

import logging
import sqlite3

import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext

logger = logging.getLogger(__name__)


def get_db() -> sqlite3.Connection:
    """Return this request's connection, opening it on first use."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error: BaseException | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create all tables and indexes. Keeps existing data."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    """Create the database tables (safe to run twice)."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
