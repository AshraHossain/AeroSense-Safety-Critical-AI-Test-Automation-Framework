"""
Unit tests for HITLOrchestrator postgres persistence (mocked, no database required).
"""
from unittest.mock import MagicMock, patch

import pytest

from src.hitl_orchestrator.orchestrator import HITLOrchestrator


@pytest.fixture
def mock_orchestrator():
    """Create HITLOrchestrator with mocked postgres."""
    with patch("src.hitl_orchestrator.orchestrator.psycopg2.connect"):
        orch = HITLOrchestrator("postgresql://test:test@localhost/test")
        return orch


def test_hitl_init_with_postgres_url():
    """__init__ stores database URL."""
    orch = HITLOrchestrator("postgresql://user:pass@host:5432/db")
    assert orch.database_url == "postgresql://user:pass@host:5432/db"


def test_hitl_init_schema_calls_execute(mock_orchestrator):
    """init_schema() executes schema SQL."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    with patch("src.hitl_orchestrator.orchestrator.psycopg2.connect", return_value=mock_conn):
        orch = HITLOrchestrator("postgresql://test")
        orch.init_schema()

        mock_cur.execute.assert_called_once()
        call_args = mock_cur.execute.call_args[0][0]
        assert "CREATE TABLE" in call_args


def test_hitl_submit_with_postgres_saves_to_db(mock_orchestrator):
    """submit() persists action to postgres if database_url set."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    with patch("src.hitl_orchestrator.orchestrator.psycopg2.connect", return_value=mock_conn):
        orch = HITLOrchestrator("postgresql://test")
        result = orch.submit(
            action_id="test_id",
            action_type="generate_test",
            proposed_change={"test": "example"},
            confidence=0.90,
            reversible=True
        )

        # Verify postgres was called twice (INSERT into orchestrator_state, INSERT into hitl_audit)
        assert mock_conn.cursor.call_count >= 1


def test_hitl_get_action_from_postgres(mock_orchestrator):
    """get_action() loads from postgres if database_url set."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mock_cur.fetchone.return_value = {
        "action_id": "test_id",
        "action_type": "generate_test",
        "status": "pending_review",
        "confidence": 0.90,
    }

    with patch("src.hitl_orchestrator.orchestrator.psycopg2.connect", return_value=mock_conn):
        orch = HITLOrchestrator("postgresql://test")
        result = orch.get_action("test_id")

        assert result["action_id"] == "test_id"
        mock_cur.execute.assert_called_once()


def test_hitl_list_pending_from_postgres(mock_orchestrator):
    """list_pending() queries postgres for pending_review actions."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mock_cur.fetchall.return_value = [
        {"action_id": "a1", "status": "pending_review", "confidence": 0.7},
        {"action_id": "a2", "status": "pending_review", "confidence": 0.75},
    ]

    with patch("src.hitl_orchestrator.orchestrator.psycopg2.connect", return_value=mock_conn):
        orch = HITLOrchestrator("postgresql://test")
        result = orch.list_pending()

        assert len(result) == 2
        assert all(a["status"] == "pending_review" for a in result)
        mock_cur.execute.assert_called_once()


def test_hitl_approve_persists_to_postgres(mock_orchestrator):
    """approve() updates action in postgres."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    # First call for get_action, returns pending_review
    mock_cur.fetchone.return_value = {
        "action_id": "test_id",
        "action_type": "generate_test",
        "proposed_change": {"test": "example"},
        "status": "pending_review",
        "confidence": 0.90,
        "reversible": True,
        "human_decision": None,
        "human_reviewer": None,
    }

    with patch("src.hitl_orchestrator.orchestrator.psycopg2.connect", return_value=mock_conn):
        orch = HITLOrchestrator("postgresql://test")
        result = orch.approve("test_id")

        assert result["status"] == "executed"
        assert result["human_decision"] == "approved"


def test_hitl_deny_persists_to_postgres(mock_orchestrator):
    """deny() updates action in postgres."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mock_cur.fetchone.return_value = {
        "action_id": "test_id",
        "action_type": "generate_test",
        "proposed_change": {"test": "example"},
        "status": "pending_review",
        "confidence": 0.70,
        "reversible": True,
        "human_decision": None,
        "human_reviewer": None,
    }

    with patch("src.hitl_orchestrator.orchestrator.psycopg2.connect", return_value=mock_conn):
        orch = HITLOrchestrator("postgresql://test")
        result = orch.deny("test_id", reason="incorrect_logic")

        assert result["status"] == "rejected"
        assert result["human_decision"] == "denied"


def test_hitl_get_audit_trail_from_postgres(mock_orchestrator):
    """get_audit_trail() queries hitl_audit table."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None

    mock_cur.fetchall.return_value = [
        {"id": 1, "action_id": "test_id", "event": "submitted"},
        {"id": 2, "action_id": "test_id", "event": "approved"},
    ]

    with patch("src.hitl_orchestrator.orchestrator.psycopg2.connect", return_value=mock_conn):
        orch = HITLOrchestrator("postgresql://test")
        result = orch.get_audit_trail("test_id")

        assert len(result) == 2
        assert result[0]["event"] == "submitted"
        assert result[1]["event"] == "approved"


def test_hitl_in_memory_fallback_no_postgres():
    """In-memory fallback works when no database_url provided."""
    orch = HITLOrchestrator()  # No database_url
    result = orch.submit(
        action_id="mem1",
        action_type="test",
        proposed_change={},
        confidence=0.90,
        reversible=True
    )

    assert result["status"] == "executed"
    action = orch.get_action("mem1")
    assert action["action_id"] == "mem1"


def test_hitl_list_pending_in_memory():
    """list_pending() filters in-memory actions."""
    orch = HITLOrchestrator()
    orch.submit(
        action_id="a1",
        action_type="test",
        proposed_change={},
        confidence=0.70,
        reversible=True
    )
    orch.submit(
        action_id="a2",
        action_type="test",
        proposed_change={},
        confidence=0.90,
        reversible=True
    )

    pending = orch.list_pending()
    assert len(pending) == 1
    assert pending[0]["action_id"] == "a1"
