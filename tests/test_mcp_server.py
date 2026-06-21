from fastapi.testclient import TestClient

from src.mcp_server.server import app

client = TestClient(app)


def test_generate_tests_endpoint_returns_stub():
    """Test /mcp/generate_tests returns test stubs with RTM tags."""
    resp = client.post(
        "/mcp/generate_tests",
        json={
            "srs_content": "- REQ-001: System shall log decisions",
            "confidence_threshold": 0.9,
            "auto_run": False,
        }
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "generated"
    assert len(body["test_ids"]) >= 1
    assert "rtm_tags" in body


def test_rtm_endpoint_builds_matrix():
    """Test /mcp/rtm returns traceability matrix."""
    resp = client.get("/mcp/rtm")
    assert resp.status_code == 200
    body = resp.json()
    assert "requirements" in body
    assert "test_coverage" in body
    assert "coverage_percentage" in body


def test_coverage_endpoint_returns_ratio():
    """Test /mcp/coverage returns coverage percentage."""
    resp = client.get("/mcp/coverage")
    assert resp.status_code == 200
    body = resp.json()
    assert "coverage_percentage" in body
    assert "total_lines" in body
    assert "covered_lines" in body
