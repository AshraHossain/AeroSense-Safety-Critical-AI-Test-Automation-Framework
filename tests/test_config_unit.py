"""
Unit tests for config module (no database required).
"""
import os
from unittest.mock import patch

import pytest

from src.config import Config


def test_config_stores_all_fields():
    """Config stores all environment fields."""
    config = Config(
        database_url="postgresql://test",
        claude_model="claude-sonnet-4-6",
        port=8000,
        log_level="info",
        anthropic_api_key="key",
    )

    assert config.database_url == "postgresql://test"
    assert config.claude_model == "claude-sonnet-4-6"
    assert config.port == 8000
    assert config.log_level == "info"
    assert config.anthropic_api_key == "key"


def test_config_is_frozen():
    """Config is immutable (frozen dataclass)."""
    config = Config(
        database_url="postgresql://test",
        claude_model="claude-sonnet-4-6",
        port=8000,
        log_level="info",
    )

    with pytest.raises(Exception):  # FrozenInstanceError
        config.port = 9000


def test_config_port_validation_too_low():
    """Port validation rejects values < 1."""
    with pytest.raises(ValueError, match="PORT.*1 and 65535"):
        Config(
            database_url="postgresql://test",
            claude_model="claude-sonnet-4-6",
            port=0,
            log_level="info",
        )


def test_config_port_validation_too_high():
    """Port validation rejects values > 65535."""
    with pytest.raises(ValueError, match="PORT.*1 and 65535"):
        Config(
            database_url="postgresql://test",
            claude_model="claude-sonnet-4-6",
            port=65536,
            log_level="info",
        )


def test_config_log_level_validation():
    """Log level validation checks against allowed values."""
    with pytest.raises(ValueError, match="LOG_LEVEL"):
        Config(
            database_url="postgresql://test",
            claude_model="claude-sonnet-4-6",
            port=8000,
            log_level="invalid",
        )


def test_config_log_level_all_valid():
    """All standard log levels are valid."""
    for level in ["debug", "info", "warning", "error"]:
        config = Config(
            database_url="postgresql://test",
            claude_model="claude-sonnet-4-6",
            port=8000,
            log_level=level,
        )
        assert config.log_level == level
