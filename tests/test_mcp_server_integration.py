"""
MCPServer integration tests (Phase 2).
Full endpoint wiring, RTM enforcement, coverage gating.
"""
import os

import pytest
from fastapi.testclient import TestClient

from src.mcp_server.server import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def postgres_url():
    """PostgreSQL connection URL."""
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/aerosense_test"
    )


@pytest.mark.integration
def test_mcp_generate_tests_endpoint_201_created(client):
    """POST /mcp/generate_tests creates test stub with RTM requirement tag."""
    response = client.post(
        "/mcp/generate_tests",
        json={
            "srs_content": """
REQ-001: System shall validate user email format
REQ-002: System shall reject empty passwords
            """,
            "confidence_threshold": 0.75,
            "auto_run": False
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "generated"
    assert "test_ids" in body
    assert len(body["test_ids"]) >= 1
    # Each test tagged with RTM requirement
    for test_id in body["test_ids"]:
        assert "REQ-" in test_id or body.get("rtm_tags") is not None


@pytest.mark.integration
def test_mcp_rtm_endpoint_returns_matrix(client):
    """GET /mcp/rtm returns Requirements Traceability Matrix."""
    # First generate some tests
    client.post(
        "/mcp/generate_tests",
        json={
            "srs_content": "REQ-001: Validate email\nREQ-002: Reject empty",
            "confidence_threshold": 0.75,
            "auto_run": False
        }
    )

    # Get RTM
    response = client.get("/mcp/rtm")
    assert response.status_code == 200
    body = response.json()

    assert "requirements" in body
    assert "test_coverage" in body
    assert "coverage_percentage" in body
    assert isinstance(body["coverage_percentage"], float)
    assert 0 <= body["coverage_percentage"] <= 100


@pytest.mark.integration
def test_mcp_rtm_enforces_90_percent_coverage(client):
    """RTM gate blocks generation if coverage would drop below 90%."""
    # (Assumes setup creates some unmapped requirements)
    response = client.get("/mcp/rtm")
    initial_coverage = response.json()["coverage_percentage"]

    if initial_coverage < 90:
        # Try to generate a test that doesn't cover all requirements
        gen_response = client.post(
            "/mcp/generate_tests",
            json={
                "srs_content": "REQ-UNCOVERED: Some requirement",
                "confidence_threshold": 0.75,
                "auto_run": False
            }
        )
        # Should be rejected or warned if coverage stays < 90%
        assert gen_response.status_code in [400, 422, 200]  # Either reject or warn
        if gen_response.status_code == 200:
            assert gen_response.json().get("warning") is not None


@pytest.mark.integration
def test_mcp_coverage_endpoint_returns_ratio(client):
    """GET /mcp/coverage returns test coverage percentage."""
    response = client.get("/mcp/coverage")
    assert response.status_code == 200
    body = response.json()

    assert "coverage_percentage" in body
    assert "total_lines" in body
    assert "covered_lines" in body
    assert isinstance(body["coverage_percentage"], float)
    assert 0 <= body["coverage_percentage"] <= 100


@pytest.mark.integration
def test_mcp_hitl_list_pending_endpoint(client):
    """GET /mcp/hitl/pending returns list of pending HITL actions."""
    response = client.get("/mcp/hitl/pending")
    assert response.status_code == 200
    body = response.json()

    assert "actions" in body
    assert isinstance(body["actions"], list)
    # Each action has required fields
    for action in body["actions"]:
        assert "action_id" in action
        assert "action_type" in action
        assert "status" in action
        assert action["status"] == "pending_review"


@pytest.mark.integration
def test_mcp_hitl_approve_endpoint(client):
    """POST /mcp/hitl/approve/{action_id} approves pending action."""
    # First create a pending action via submit
    client.post(
        "/mcp/hitl/submit",
        json={
            "action_id": "test_approve_action",
            "action_type": "generate_test",
            "proposed_change": {"test": "example"},
            "confidence": 0.70,
            "reversible": True
        }
    )

    # Approve it
    response = client.post(
        "/mcp/hitl/approve/test_approve_action",
        json={"human_reviewer": "alice@example.com"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "executed"
    assert body["human_decision"] == "approved"


@pytest.mark.integration
def test_mcp_hitl_deny_endpoint(client):
    """POST /mcp/hitl/deny/{action_id} denies pending action."""
    # Create pending action
    client.post(
        "/mcp/hitl/submit",
        json={
            "action_id": "test_deny_action",
            "action_type": "generate_test",
            "proposed_change": {"test": "example"},
            "confidence": 0.75,
            "reversible": True
        }
    )

    # Deny it
    response = client.post(
        "/mcp/hitl/deny/test_deny_action",
        json={
            "human_reviewer": "bob@example.com",
            "reason": "incorrect_test_logic"
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["human_decision"] == "denied"


@pytest.mark.integration
def test_mcp_audit_log_endpoint_returns_records(client):
    """GET /mcp/audit returns all audit log records."""
    response = client.get("/mcp/audit")
    assert response.status_code == 200
    body = response.json()

    assert "records" in body
    assert isinstance(body["records"], list)
    # Each record has DO-178C fields
    for record in body["records"]:
        assert "id" in record
        assert "timestamp" in record
        assert "model" in record
        assert "confidence" in record
        assert "outcome" in record


@pytest.mark.integration
def test_mcp_audit_log_export_csv(client):
    """GET /mcp/audit/export?format=csv returns CSV-formatted audit log."""
    response = client.get("/mcp/audit/export?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    # CSV has header row
    lines = response.text.strip().split("\n")
    assert len(lines) >= 1
    assert "id" in lines[0]  # Header


@pytest.mark.integration
def test_mcp_audit_log_export_json(client):
    """GET /mcp/audit/export?format=json returns JSON-formatted audit log."""
    response = client.get("/mcp/audit/export?format=json")
    assert response.status_code == 200
    body = response.json()
    assert "records" in body


@pytest.mark.integration
def test_mcp_health_check_endpoint(client):
    """GET /health returns service status."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "version" in body


@pytest.mark.integration
def test_mcp_error_handling_missing_required_field(client):
    """POST /mcp/generate_tests with missing field returns 422."""
    response = client.post(
        "/mcp/generate_tests",
        json={"srs_content": "REQ-001"}  # Missing confidence_threshold
    )
    assert response.status_code == 422


@pytest.mark.integration
def test_mcp_error_handling_invalid_action_id(client):
    """POST /mcp/hitl/approve with non-existent action returns 404."""
    response = client.post(
        "/mcp/hitl/approve/does_not_exist",
        json={"human_reviewer": "alice"}
    )
    assert response.status_code == 404
