"""
PostgreSQL AuditLogger compliance tests (Phase 2).
Tests append-only immutability, DO-178C audit trail integrity.
"""
import os
from datetime import datetime

import pytest

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

from src.audit_logger.postgres_logger import PostgresAuditLogger

pytestmark = pytest.mark.skipif(
    not HAS_POSTGRES,
    reason="psycopg2 not installed"
)


@pytest.fixture
def postgres_url():
    """PostgreSQL connection URL from environment."""
    url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/aerosense_test"
    )
    return url


@pytest.fixture
def postgres_logger(postgres_url):
    """Create and initialize PostgreSQL logger, clean up after test."""
    logger = PostgresAuditLogger(postgres_url)
    logger.init_schema()
    yield logger
    # Cleanup: truncate audit table
    with psycopg2.connect(postgres_url) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE audit_log CASCADE")
            conn.commit()


@pytest.mark.integration
def test_postgres_record_writes_row(postgres_logger):
    """Record writes immutable row to PostgreSQL."""
    postgres_logger.record(
        model="claude-sonnet-4-6",
        prompt_hash="abc123",
        response_hash="def456",
        confidence=0.95,
        human_decision="approved",
        outcome="applied"
    )

    rows = postgres_logger.all_records()
    assert len(rows) == 1
    assert rows[0]["model"] == "claude-sonnet-4-6"
    assert rows[0]["confidence"] == 0.95
    assert rows[0]["outcome"] == "applied"


@pytest.mark.integration
def test_postgres_append_only_no_update_method(postgres_logger):
    """AuditLogger has no update() or delete() methods."""
    assert not hasattr(postgres_logger, "update")
    assert not hasattr(postgres_logger, "delete")


@pytest.mark.integration
def test_postgres_direct_update_rejected_by_trigger(postgres_url, postgres_logger):
    """Direct UPDATE on audit_log rejected by PostgreSQL trigger."""
    postgres_logger.record(
        model="claude-sonnet-4-6",
        prompt_hash="p1",
        response_hash="r1",
        confidence=0.85,
        human_decision="pending",
        outcome="queued"
    )

    # Attempt direct UPDATE via raw connection
    with psycopg2.connect(postgres_url) as conn:
        with conn.cursor() as cur:
            with pytest.raises(psycopg2.IntegrityError):
                cur.execute(
                    "UPDATE audit_log SET outcome = 'tampered' WHERE prompt_hash = %s",
                    ("p1",)
                )
                conn.commit()


@pytest.mark.integration
def test_postgres_direct_delete_rejected_by_trigger(postgres_url, postgres_logger):
    """Direct DELETE on audit_log rejected by PostgreSQL trigger."""
    postgres_logger.record(
        model="claude-sonnet-4-6",
        prompt_hash="p2",
        response_hash="r2",
        confidence=0.9,
        human_decision="approved",
        outcome="applied"
    )

    with psycopg2.connect(postgres_url) as conn:
        with conn.cursor() as cur:
            with pytest.raises(psycopg2.IntegrityError):
                cur.execute("DELETE FROM audit_log WHERE prompt_hash = %s", ("p2",))
                conn.commit()


@pytest.mark.integration
def test_postgres_multiple_records_preserve_order(postgres_logger):
    """Multiple records maintain insertion order via sequence ID."""
    for i in range(5):
        postgres_logger.record(
            model="claude-sonnet-4-6",
            prompt_hash=f"p{i}",
            response_hash=f"r{i}",
            confidence=0.8 + (0.01 * i),
            human_decision="approved",
            outcome="applied"
        )

    rows = postgres_logger.all_records()
    assert len(rows) == 5
    assert [r["prompt_hash"] for r in rows] == ["p0", "p1", "p2", "p3", "p4"]
    assert [r["id"] for r in rows] == [1, 2, 3, 4, 5]


@pytest.mark.integration
def test_postgres_timestamp_automatically_set(postgres_logger):
    """Timestamp field set by PostgreSQL DEFAULT, not application."""
    before = datetime.utcnow()
    postgres_logger.record(
        model="claude-sonnet-4-6",
        prompt_hash="ts_test",
        response_hash="ts_resp",
        confidence=0.75,
        human_decision="approved",
        outcome="applied"
    )
    after = datetime.utcnow()

    rows = postgres_logger.all_records()
    assert len(rows) == 1
    ts = datetime.fromisoformat(rows[0]["timestamp"])
    assert before <= ts <= after


@pytest.mark.integration
def test_postgres_all_fields_present_in_export(postgres_logger):
    """Record includes all required DO-178C fields for export."""
    postgres_logger.record(
        model="claude-opus-4-1",
        prompt_hash="export_prompt",
        response_hash="export_response",
        confidence=0.92,
        human_decision="escalated",
        outcome="pending_human_review"
    )

    rows = postgres_logger.all_records()
    assert len(rows) == 1
    record = rows[0]

    required_fields = {
        "id", "timestamp", "model", "prompt_hash", "response_hash",
        "confidence", "human_decision", "outcome"
    }
    assert set(record.keys()) >= required_fields
