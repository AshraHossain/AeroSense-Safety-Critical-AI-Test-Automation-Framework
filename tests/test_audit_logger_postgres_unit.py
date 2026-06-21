"""
Unit tests for PostgresAuditLogger (mocked, no database required).
"""
from unittest.mock import MagicMock, patch

import pytest

from src.audit_logger.postgres_logger import PostgresAuditLogger


@pytest.fixture
def mock_postgres_logger():
    """Create PostgresAuditLogger with mocked postgres connection."""
    with patch("src.audit_logger.postgres_logger.psycopg2.connect"):
        logger = PostgresAuditLogger("postgresql://mock:mock@localhost/test")
        return logger


def test_postgres_logger_init_calls_connect():
    """__init__ stores database URL."""
    logger = PostgresAuditLogger("postgresql://user:pass@host:5432/db")
    assert logger.database_url == "postgresql://user:pass@host:5432/db"


def test_postgres_logger_record_returns_dict(mock_postgres_logger):
    """record() returns dictionary with inserted data."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    with patch("src.audit_logger.postgres_logger.psycopg2.connect", return_value=mock_conn):
        logger = PostgresAuditLogger("postgresql://test")
        mock_cur.fetchone.return_value = {
            "id": 1,
            "timestamp": "2026-06-21T10:00:00",
            "model": "claude-sonnet-4-6",
            "prompt_hash": "abc",
            "response_hash": "def",
            "confidence": 0.95,
            "human_decision": "approved",
            "outcome": "applied"
        }

        result = logger.record(
            model="claude-sonnet-4-6",
            prompt_hash="abc",
            response_hash="def",
            confidence=0.95,
            human_decision="approved",
            outcome="applied"
        )

        assert result["model"] == "claude-sonnet-4-6"
        assert result["confidence"] == 0.95
        mock_cur.execute.assert_called_once()


def test_postgres_logger_all_records_returns_list(mock_postgres_logger):
    """all_records() returns list of dicts."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mock_records = [
        {"id": 1, "model": "m1", "confidence": 0.9},
        {"id": 2, "model": "m2", "confidence": 0.8},
    ]
    mock_cur.fetchall.return_value = mock_records

    with patch("src.audit_logger.postgres_logger.psycopg2.connect", return_value=mock_conn):
        logger = PostgresAuditLogger("postgresql://test")
        result = logger.all_records()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["model"] == "m1"


def test_postgres_logger_get_record_returns_dict(mock_postgres_logger):
    """get_record() returns single record or None."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mock_cur.fetchone.return_value = {"id": 1, "model": "test"}

    with patch("src.audit_logger.postgres_logger.psycopg2.connect", return_value=mock_conn):
        logger = PostgresAuditLogger("postgresql://test")
        result = logger.get_record(1)

        assert result["id"] == 1
        mock_cur.execute.assert_called_once()


def test_postgres_logger_get_record_returns_none_if_not_found(mock_postgres_logger):
    """get_record() returns None if record doesn't exist."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mock_cur.fetchone.return_value = None

    with patch("src.audit_logger.postgres_logger.psycopg2.connect", return_value=mock_conn):
        logger = PostgresAuditLogger("postgresql://test")
        result = logger.get_record(999)

        assert result is None


def test_postgres_logger_export_csv_returns_string(mock_postgres_logger):
    """export_csv() returns CSV formatted string."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mock_records = [
        {
            "id": 1,
            "timestamp": "2026-06-21T10:00:00",
            "model": "claude-sonnet-4-6",
            "prompt_hash": "p1",
            "response_hash": "r1",
            "confidence": 0.9,
            "human_decision": "approved",
            "outcome": "applied"
        }
    ]
    mock_cur.fetchall.return_value = mock_records

    with patch("src.audit_logger.postgres_logger.psycopg2.connect", return_value=mock_conn):
        logger = PostgresAuditLogger("postgresql://test")
        result = logger.export_csv()

        assert isinstance(result, str)
        assert "id,timestamp,model" in result
        assert "1,2026-06-21T10:00:00" in result


def test_postgres_logger_export_csv_empty_returns_header():
    """export_csv() with no records returns header only."""
    with patch("src.audit_logger.postgres_logger.psycopg2.connect"):
        logger = PostgresAuditLogger("postgresql://test")
        with patch.object(logger, "all_records", return_value=[]):
            result = logger.export_csv()

            assert "id,timestamp,model" in result
            lines = result.strip().split("\n")
            assert len(lines) == 1  # Header only


def test_postgres_logger_init_schema_calls_execute(mock_postgres_logger):
    """init_schema() executes schema SQL."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    with patch("src.audit_logger.postgres_logger.psycopg2.connect", return_value=mock_conn):
        logger = PostgresAuditLogger("postgresql://test")
        logger.init_schema()

        mock_cur.execute.assert_called_once()
        # Verify that the schema call includes CREATE TABLE
        call_args = mock_cur.execute.call_args[0][0]
        assert "CREATE TABLE" in call_args
        assert "CREATE TRIGGER" in call_args
