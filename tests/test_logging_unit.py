"""
Unit tests for logging configuration (no database required).
"""
import json
import logging
from io import StringIO
from unittest.mock import patch

from src.logging_config import JsonFormatter, get_logger


def test_json_formatter_formats_log_as_json():
    """JsonFormatter produces valid JSON output."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="test message",
        args=(),
        exc_info=None,
    )

    output = formatter.format(record)
    data = json.loads(output)

    assert data["level"] == "INFO"
    assert data["logger"] == "test.logger"
    assert data["message"] == "test message"
    assert "timestamp" in data


def test_json_formatter_includes_extra_fields():
    """JsonFormatter includes extra attributes in JSON."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="test",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-123"
    record.user = "alice"

    output = formatter.format(record)
    data = json.loads(output)

    assert data["request_id"] == "req-123"
    assert data["user"] == "alice"


def test_get_logger_returns_logger():
    """get_logger returns a logging.Logger instance."""
    with patch("src.config.get_config") as mock_get_config:
        mock_get_config.return_value.log_level = "info"
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"


def test_get_logger_uses_json_formatter():
    """Logger returned by get_logger uses JsonFormatter."""
    with patch("src.config.get_config") as mock_get_config:
        mock_get_config.return_value.log_level = "info"
        logger = get_logger("test.json")

        # Logger should have a handler with JsonFormatter
        has_json_formatter = any(
            isinstance(h.formatter, JsonFormatter)
            for h in logger.handlers
        )
        assert has_json_formatter


def test_get_logger_with_mock_config():
    """get_logger respects log level from config."""
    with patch("src.config.get_config") as mock_get_config:
        mock_get_config.return_value.log_level = "debug"

        logger = get_logger("test.debug")
        # Logger should be set to DEBUG level
        assert any(h.level == logging.DEBUG for h in logger.handlers)
