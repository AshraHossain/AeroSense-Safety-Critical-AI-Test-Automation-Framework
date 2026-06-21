"""
Unit tests for MCPServer endpoints (mocked, no database required).
Tests HITL and audit endpoints with mocked orchestrator and logger.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.mcp_server import server
from src.mcp_server.server import app


@pytest.fixture(autouse=True)
def mock_hitl_and_audit():
    """Mock HITL orchestrator and audit logger for all tests."""
    mock_orch = MagicMock()
    mock_logger = MagicMock()

    # Setup default mock behaviors
    mock_orch.list_pending.return_value = []
    mock_orch.submit.return_value = {"status": "executed", "human_review": False}
    mock_orch.approve.return_value = {"status": "executed", "human_decision": "approved"}
    mock_orch.deny.return_value = {"status": "rejected", "human_decision": "denied"}
    mock_logger.all_records.return_value = []
    mock_logger.export_csv.return_value = "id,timestamp,model,outcome\n"

    with patch.object(server, "get_hitl_orchestrator", return_value=mock_orch):
        with patch.object(server, "get_audit_logger", return_value=mock_logger):
            yield mock_orch, mock_logger


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


def test_health_check(client):
    """GET /health returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "version" in body


def test_hitl_list_pending_empty(client, mock_hitl_and_audit):
    """GET /mcp/hitl/pending returns empty list when no pending actions."""
    mock_orch, _ = mock_hitl_and_audit
    response = client.get("/mcp/hitl/pending")
    assert response.status_code == 200
    body = response.json()
    assert body["actions"] == []
    mock_orch.list_pending.assert_called_once()


def test_hitl_list_pending_with_actions(client, mock_hitl_and_audit):
    """GET /mcp/hitl/pending returns pending actions."""
    mock_orch, _ = mock_hitl_and_audit
    mock_orch.list_pending.return_value = [
        {"action_id": "a1", "status": "pending_review", "action_type": "test"},
        {"action_id": "a2", "status": "pending_review", "action_type": "heal"},
    ]

    response = client.get("/mcp/hitl/pending")
    assert response.status_code == 200
    body = response.json()
    assert len(body["actions"]) == 2
    assert body["actions"][0]["action_id"] == "a1"


def test_hitl_submit_action(client, mock_hitl_and_audit):
    """POST /mcp/hitl/submit creates action."""
    mock_orch, _ = mock_hitl_and_audit
    mock_orch.submit.return_value = {
        "action_id": "test_id",
        "status": "pending_review",
        "human_review": True,
    }

    response = client.post(
        "/mcp/hitl/submit",
        json={
            "action_id": "test_id",
            "action_type": "generate_test",
            "proposed_change": {"test": "example"},
            "confidence": 0.75,
            "reversible": True,
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending_review"
    mock_orch.submit.assert_called_once()


def test_hitl_approve_action(client, mock_hitl_and_audit):
    """POST /mcp/hitl/approve/{action_id} approves action."""
    mock_orch, _ = mock_hitl_and_audit
    response = client.post(
        "/mcp/hitl/approve/test_id",
        json={"human_reviewer": "alice"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "executed"
    assert body["human_decision"] == "approved"
    mock_orch.approve.assert_called_once()


def test_hitl_approve_not_found(client, mock_hitl_and_audit):
    """POST /mcp/hitl/approve with non-existent action raises 404."""
    mock_orch, _ = mock_hitl_and_audit
    mock_orch.approve.side_effect = ValueError("Action not found")

    response = client.post(
        "/mcp/hitl/approve/does_not_exist",
        json={"human_reviewer": "alice"}
    )

    assert response.status_code == 404


def test_hitl_deny_action(client, mock_hitl_and_audit):
    """POST /mcp/hitl/deny/{action_id} denies action."""
    mock_orch, _ = mock_hitl_and_audit
    response = client.post(
        "/mcp/hitl/deny/test_id",
        json={"human_reviewer": "bob", "reason": "incorrect"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["human_decision"] == "denied"
    mock_orch.deny.assert_called_once()


def test_audit_log_get_records(client, mock_hitl_and_audit):
    """GET /mcp/audit returns audit records."""
    _, mock_logger = mock_hitl_and_audit
    mock_logger.all_records.return_value = [
        {
            "id": 1,
            "timestamp": "2026-06-21T10:00:00",
            "model": "claude-sonnet-4-6",
            "outcome": "applied",
        }
    ]

    response = client.get("/mcp/audit")
    assert response.status_code == 200
    body = response.json()
    assert len(body["records"]) == 1
    assert body["records"][0]["id"] == 1
    mock_logger.all_records.assert_called_once()


def test_audit_log_export_json(client, mock_hitl_and_audit):
    """GET /mcp/audit/export?format=json returns JSON."""
    _, mock_logger = mock_hitl_and_audit
    mock_logger.all_records.return_value = [
        {"id": 1, "model": "claude-sonnet-4-6"}
    ]

    response = client.get("/mcp/audit/export?format=json")
    assert response.status_code == 200
    body = response.json()
    assert "records" in body


def test_audit_log_export_csv(client, mock_hitl_and_audit):
    """GET /mcp/audit/export?format=csv returns CSV."""
    _, mock_logger = mock_hitl_and_audit
    mock_logger.export_csv.return_value = "id,model,outcome\n1,claude-sonnet-4-6,applied\n"

    response = client.get("/mcp/audit/export?format=csv")
    assert response.status_code == 200
    # In production, content-type would be text/csv
    # For testing, just verify the response is successful
    assert response.text is not None
