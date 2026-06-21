from fastapi.testclient import TestClient

from src.mcp_server.server import app

client = TestClient(app)


def test_generate_tests_endpoint_returns_stub():
    resp = client.post("/generate-tests", json={
        "srs_markdown": "- REQ-001: System shall log decisions",
        "model": "claude-sonnet-4-6",
        "confidence": 0.9,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["stubs"]) == 1
    assert '@pytest.mark.requirement("REQ-001")' in body["stubs"][0]


def test_rtm_endpoint_builds_matrix():
    resp = client.post("/rtm", json={
        "srs_markdown": "- REQ-001: a\n- REQ-002: b",
        "test_dir": "tests",
    })
    assert resp.status_code == 200
    rows = resp.json()["rtm"]
    assert {r["requirement_id"] for r in rows} == {"REQ-001", "REQ-002"}


def test_coverage_endpoint_returns_ratio():
    resp = client.post("/coverage", json={
        "srs_markdown": "- REQ-001: a",
        "test_dir": "tests",
    })
    assert resp.status_code == 200
    assert "coverage_ratio" in resp.json()
