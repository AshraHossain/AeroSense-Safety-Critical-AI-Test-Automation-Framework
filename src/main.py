"""
Application entrypoint (Phase 3A).
Runs startup checks, initializes app, and serves requests.
"""
import sys

import uvicorn

from src.config import get_config
from src.logging_config import get_logger
from src.startup import startup_checks


def main():
    """Start the application."""
    logger = get_logger(__name__)
    config = get_config()

    try:
        logger.info("Starting AeroSense-TestForge", extra={"action": "startup"})
        logger.info(f"Configuration loaded: port={config.port}, log_level={config.log_level}")

        # Run startup checks
        logger.info("Running startup checks...", extra={"action": "health_check"})
        startup_checks()
        logger.info("Startup checks passed", extra={"action": "health_check"})

        # Start server
        logger.info(f"Starting server on port {config.port}", extra={"action": "server_start"})
        uvicorn.run(
            "src.mcp_server.server:app",
            host="0.0.0.0",
            port=config.port,
            log_level=config.log_level.lower(),
            access_log=False,  # Use custom JSON logging instead
        )
    except Exception as e:
        logger.error(f"Startup failed: {e}", extra={"action": "startup_error"})
        sys.exit(1)


if __name__ == "__main__":
    main()
