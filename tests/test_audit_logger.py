import sqlite3

import pytest

from src.audit_logger.logger import AuditLogger


@pytest.fixture
def logger(tmp_path):
    return AuditLogger(tmp_path / "audit.db")


def test_record_writes_row(logger):
    logger.record(
        model="claude-sonnet-4-6",
        prompt_hash="abc",
        response_hash="def",
        confidence=0.9,
        human_decision="approved",
        outcome="applied",
    )
    rows = logger.all_records()
    assert len(rows) == 1
    assert rows[0]["model"] == "claude-sonnet-4-6"
    assert rows[0]["confidence"] == 0.9


def test_records_are_append_only_no_update_method(logger):
    assert not hasattr(logger, "update")
    assert not hasattr(logger, "delete")


def test_direct_update_on_audit_table_is_rejected(logger):
    logger.record(
        model="m", prompt_hash="p", response_hash="r",
        confidence=1.0, human_decision="approved", outcome="applied",
    )
    with sqlite3.connect(logger.db_path) as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE audit_log SET outcome = 'tampered'")


def test_multiple_records_preserve_order(logger):
    for i in range(3):
        logger.record(
            model="m", prompt_hash=f"p{i}", response_hash="r",
            confidence=0.5, human_decision="pending", outcome="queued",
        )
    rows = logger.all_records()
    assert [r["prompt_hash"] for r in rows] == ["p0", "p1", "p2"]
