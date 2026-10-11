"""Structured logging setup for FastAPI application."""

import logging
import sys
from typing import Any, Dict


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure unified application logger with structured formatting."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    logger = logging.getLogger("forest_fire_api")
    logger.setLevel(numeric_level)

    # Avoid duplicate handlers if reconfigured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(numeric_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
