"""
Structured logging setup.

Supports two formats:
  - json: Single-line JSON per log entry (for CI/production)
  - text: Human-readable format (for local development)

Usage:
    from core.logger import setup_logging
    setup_logging()  # Call once at startup (conftest.py)
"""

import json
import logging
import sys
from datetime import datetime, timezone

from core.config import settings


class JsonFormatter(logging.Formatter):
    """Outputs log records as single-line JSON for structured log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])
            log_entry["exception_type"] = type(record.exc_info[1]).__name__
        return json.dumps(log_entry)


def setup_logging() -> None:
    """Configure root logger based on settings."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    handler = logging.StreamHandler(sys.stdout)

    if settings.LOG_FORMAT == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
            )
        )

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
