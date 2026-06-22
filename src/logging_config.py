"""
Structured logging configuration (Phase 3A).
JSON-formatted logs for observability and audit trail.
"""
import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "user"):
            log_entry["user"] = record.user
        if hasattr(record, "action"):
            log_entry["action"] = record.action

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def get_logger(name: str) -> logging.Logger:
    """Get logger with JSON formatting.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    from src.config import get_config

    config = get_config()
    logger = logging.getLogger(name)

    # Set log level
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Create handler (stdout)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Set formatter
    formatter = JsonFormatter()
    handler.setFormatter(formatter)

    # Add handler to logger (avoid duplicates)
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
