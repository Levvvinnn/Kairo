"""Logging utilities for Kairo."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application-wide logging."""
    # TODO: Add structured logging and file handlers for production usage.
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
