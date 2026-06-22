"""
Startup initialization and validation (Phase 3A).
Performs health checks and initializes infrastructure on app start.
"""
import psycopg2

from src.config import get_config


def startup_checks():
    """Run startup validation checks.

    Raises:
        Exception: If any critical check fails
    """
    config = get_config()

    # Check database connectivity
    try:
        with psycopg2.connect(config.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception as e:
        raise Exception(f"Database connectivity check failed: {e}")

    # Initialize audit logger schema
    from src.audit_logger.postgres_logger import PostgresAuditLogger
    try:
        logger = PostgresAuditLogger(config.database_url)
        logger.init_schema()
    except Exception as e:
        raise Exception(f"Failed to initialize audit logger schema: {e}")

    # Initialize HITL orchestrator schema
    from src.hitl_orchestrator.orchestrator import HITLOrchestrator
    try:
        orchestrator = HITLOrchestrator(config.database_url)
        orchestrator.init_schema()
    except Exception as e:
        raise Exception(f"Failed to initialize HITL orchestrator schema: {e}")
