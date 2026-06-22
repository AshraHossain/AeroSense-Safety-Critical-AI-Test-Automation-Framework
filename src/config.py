"""
Configuration management (Phase 3A).
Loads and validates environment variables at startup.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Application configuration from environment variables."""

    database_url: str
    claude_model: str
    port: int
    log_level: str
    anthropic_api_key: str = None

    def __post_init__(self):
        """Validate configuration after init."""
        if not self.database_url:
            raise ValueError("DATABASE_URL is required")
        if not self.database_url.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must be a valid postgresql:// URL")

        if not self.claude_model:
            raise ValueError("CLAUDE_MODEL is required")
        if "latest" in self.claude_model or "next" in self.claude_model:
            raise ValueError("CLAUDE_MODEL must be pinned to a specific version (not 'latest')")

        valid_levels = {"debug", "info", "warning", "error"}
        if self.log_level not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")

        if self.port < 1 or self.port > 65535:
            raise ValueError(f"PORT must be between 1 and 65535, got {self.port}")

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        database_url = os.environ.get("DATABASE_URL")
        claude_model = os.environ.get("CLAUDE_MODEL")
        port = int(os.environ.get("PORT", "8000"))
        log_level = os.environ.get("LOG_LEVEL", "info")
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")

        return cls(
            database_url=database_url,
            claude_model=claude_model,
            port=port,
            log_level=log_level,
            anthropic_api_key=anthropic_api_key,
        )


def get_config() -> Config:
    """Get global config instance (lazy load)."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


_config: Config = None
