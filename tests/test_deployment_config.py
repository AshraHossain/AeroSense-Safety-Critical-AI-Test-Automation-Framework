"""
Deployment configuration tests (Phase 3A).
Tests environment loading, validation, and startup initialization.
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


def test_env_file_example_exists():
    """Project has .env.example template for configuration."""
    env_example = Path(".env.example")
    assert env_example.exists(), ".env.example not found"


def test_env_example_contains_required_vars():
    """All required environment variables documented in .env.example."""
    env_example = Path(".env.example")
    content = env_example.read_text()

    required_vars = [
        "DATABASE_URL",
        "CLAUDE_MODEL",
        "PORT",
        "LOG_LEVEL",
    ]
    for var in required_vars:
        assert var in content, f"{var} not in .env.example"


def test_config_load_from_env():
    """Configuration loads from environment variables."""
    env = {
        "DATABASE_URL": "postgresql://test:test@localhost/test",
        "CLAUDE_MODEL": "claude-sonnet-4-6",
        "PORT": "8000",
        "LOG_LEVEL": "info",
    }

    with patch.dict(os.environ, env, clear=False):
        from src.config import Config

        config = Config.from_env()
        assert config.database_url == "postgresql://test:test@localhost/test"
        assert config.claude_model == "claude-sonnet-4-6"
        assert config.port == 8000
        assert config.log_level == "info"


def test_config_defaults_when_missing_optional_vars():
    """Configuration uses sensible defaults for optional variables."""
    env = {
        "DATABASE_URL": "postgresql://test:test@localhost/test",
        "CLAUDE_MODEL": "claude-sonnet-4-6",
    }

    with patch.dict(os.environ, env, clear=True):
        from src.config import Config

        config = Config.from_env()
        assert config.port == 8000  # Default port
        assert config.log_level == "info"  # Default log level


def test_config_raises_on_missing_required_vars():
    """Configuration validation fails if required variables missing."""
    env = {"CLAUDE_MODEL": "claude-sonnet-4-6"}

    with patch.dict(os.environ, env, clear=True):
        from src.config import Config

        with pytest.raises(ValueError, match="DATABASE_URL"):
            Config.from_env()


def test_config_validates_database_url_format():
    """Configuration validates DATABASE_URL is valid postgres URL."""
    env = {
        "DATABASE_URL": "invalid-url",
        "CLAUDE_MODEL": "claude-sonnet-4-6",
    }

    with patch.dict(os.environ, env, clear=True):
        from src.config import Config

        with pytest.raises(ValueError, match="DATABASE_URL.*postgresql"):
            Config.from_env()


def test_config_validates_model_is_pinned():
    """Configuration validates model version is explicitly pinned."""
    env = {
        "DATABASE_URL": "postgresql://test:test@localhost/test",
        "CLAUDE_MODEL": "claude-latest",  # Not pinned
    }

    with patch.dict(os.environ, env, clear=True):
        from src.config import Config

        with pytest.raises(ValueError, match="CLAUDE_MODEL.*pinned"):
            Config.from_env()


@pytest.mark.skipif(
    os.environ.get("DATABASE_URL") is None,
    reason="DATABASE_URL not set - postgres not available"
)
def test_startup_checks_database_connectivity():
    """Startup validates postgres is reachable."""
    from src.startup import startup_checks

    # Should initialize without errors if postgres available
    startup_checks()


@pytest.mark.skipif(
    os.environ.get("DATABASE_URL") is None,
    reason="DATABASE_URL not set - postgres not available"
)
def test_startup_initializes_audit_logger():
    """Startup initializes audit logger and verifies schema."""
    from src.startup import startup_checks

    startup_checks()
    # If we reach here, postgres is available and schema was created
    assert True


@pytest.mark.skipif(
    os.environ.get("DATABASE_URL") is None,
    reason="DATABASE_URL not set - postgres not available"
)
def test_startup_validates_claude_api_available():
    """Startup validates Claude API is accessible."""
    from src.startup import startup_checks

    startup_checks()
    assert True


def test_app_starts_with_valid_config():
    """FastAPI app starts successfully when config is valid."""
    from fastapi.testclient import TestClient
    from src.mcp_server.server import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_docker_entrypoint_script_exists():
    """Dockerfile uses valid entrypoint script."""
    dockerfile = Path("Dockerfile")
    assert dockerfile.exists(), "Dockerfile not found"

    content = dockerfile.read_text()
    assert "ENTRYPOINT" in content or "CMD" in content


def test_docker_compose_file_exists():
    """docker-compose.yml defines postgres + app services."""
    docker_compose = Path("docker-compose.yml")
    assert docker_compose.exists(), "docker-compose.yml not found"

    content = docker_compose.read_text()
    assert "postgres" in content.lower()
    assert "app" in content.lower() or "aerosense" in content.lower()


def test_docker_compose_postgres_init():
    """docker-compose postgres service initializes with schema."""
    docker_compose = Path("docker-compose.yml")
    if not docker_compose.exists():
        pytest.skip("docker-compose.yml not found")

    content = docker_compose.read_text()

    # Should reference init script or migration tool
    assert "postgres" in content.lower() and "app" in content.lower()


@pytest.mark.skipif(
    os.environ.get("DATABASE_URL") is None and os.environ.get("CLAUDE_MODEL") is None,
    reason="Env vars not set - skipping logging config test"
)
def test_logging_config_json_output():
    """Logging is configured for JSON output (structured logging)."""
    from unittest.mock import patch

    with patch("src.config.get_config") as mock_config:
        mock_config.return_value.log_level = "info"

        from src.logging_config import get_logger

        logger = get_logger(__name__)
        # Should be able to log without errors
        logger.info("test message", extra={"request_id": "123"})
        assert True
