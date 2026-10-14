"""`seed` command. Placeholder until feature 2 adds sample data."""

from __future__ import annotations

import logging

import click
from flask import Flask
from flask.cli import with_appcontext

logger = logging.getLogger(__name__)


@click.command("seed")
@with_appcontext
def seed_command() -> None:
    """Insert sample data (nothing yet)."""
    logger.info("Seed: nothing to seed yet.")


def init_app(app: Flask) -> None:
    app.cli.add_command(seed_command)
