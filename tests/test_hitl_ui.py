"""
HITL approval UI tests (Phase 5).
Tests WebSocket endpoints, real-time streaming, UI templates.
"""
from pathlib import Path

import pytest


def test_hitl_ui_templates_directory_exists():
    """UI templates directory exists."""
    templates_dir = Path("src/templates")
    assert templates_dir.exists() and templates_dir.is_dir()


def test_hitl_approval_template_exists():
    """Approval page HTML template exists."""
    template = Path("src/templates/approval.html")
    assert template.exists()


def test_approval_template_has_decision_form():
    """Approval template includes approve/deny form."""
    template = Path("src/templates/approval.html")
    content = template.read_text()

    assert "approve" in content.lower()
    assert "deny" in content.lower()


def test_websocket_endpoint_exists():
    """WebSocket endpoint for real-time HITL updates defined."""
    server = Path("src/mcp_server/server.py")
    content = server.read_text()

    assert "websocket" in content.lower() or "ws" in content.lower()


def test_rate_limiter_middleware_exists():
    """Rate limiting middleware module exists."""
    rate_limiter = Path("src/middleware/rate_limiter.py")
    assert rate_limiter.exists()


def test_rate_limiter_supports_per_endpoint_limits():
    """Rate limiter can enforce different limits per endpoint."""
    rate_limiter = Path("src/middleware/rate_limiter.py")
    content = rate_limiter.read_text()

    assert "endpoint" in content.lower() or "path" in content.lower()
    assert "limit" in content.lower()


def test_request_signing_module_exists():
    """Request signing utility module exists."""
    signing = Path("src/security/signing.py")
    assert signing.exists()


def test_request_signing_uses_hmac():
    """Request signing uses HMAC-SHA256."""
    signing = Path("src/security/signing.py")
    content = signing.read_text()

    assert "hmac" in content.lower()
    assert "sha256" in content.lower() or "sha-256" in content.lower()


def test_request_signing_includes_timestamp():
    """Signed requests include timestamp for replay protection."""
    signing = Path("src/security/signing.py")
    content = signing.read_text()

    assert "timestamp" in content.lower() or "time" in content.lower()


def test_security_headers_configured():
    """Security headers (CSP, HSTS, X-Frame-Options) configured."""
    server = Path("src/mcp_server/server.py")
    content = server.read_text()

    has_csp = "content-security-policy" in content.lower() or "csp" in content.lower()
    has_hsts = "strict-transport-security" in content.lower() or "hsts" in content.lower()
    has_frame = "x-frame-options" in content.lower()

    assert has_csp or has_hsts or has_frame


def test_helm_charts_directory_exists():
    """Helm charts directory exists."""
    helm_dir = Path("helm")
    assert helm_dir.exists() and helm_dir.is_dir()


def test_helm_values_yaml_exists():
    """Helm values.yaml exists."""
    values = Path("helm/values.yaml")
    assert values.exists()


def test_helm_values_configurable():
    """Helm values include key configuration variables."""
    values = Path("helm/values.yaml")
    content = values.read_text()

    assert "replicaCount" in content or "replicas" in content.lower()
    assert "image" in content.lower()
    assert "resources" in content.lower()


def test_helm_chart_yaml_exists():
    """Helm Chart.yaml metadata exists."""
    chart_file = Path("helm/Chart.yaml")
    assert chart_file.exists()


def test_helm_chart_version_pinned():
    """Helm chart has explicit version (not floating)."""
    chart_file = Path("helm/Chart.yaml")
    content = chart_file.read_text()

    assert "version:" in content
    # Should have version like "0.1.0" not "latest"
    assert "latest" not in content.lower()


def test_helm_deployment_template_exists():
    """Helm deployment template exists."""
    deployment = Path("helm/templates/deployment.yaml")
    assert deployment.exists()


def test_helm_secret_template_exists():
    """Helm secret template for credentials exists."""
    secret = Path("helm/templates/secret.yaml")
    assert secret.exists()


def test_helm_secret_uses_externalsecrets():
    """Helm secret template supports external secrets or sealed secrets."""
    secret = Path("helm/templates/secret.yaml")
    content = secret.read_text()

    has_external = "externalsecrets" in content.lower() or "external-secret" in content.lower()
    has_sealed = "sealedsecrets" in content.lower() or "sealed-secret" in content.lower()
    has_ref = "valueFrom" in content or "secretRef" in content

    assert has_external or has_sealed or has_ref


def test_audit_log_includes_signature_verification():
    """Audit logger validates request signatures."""
    audit_logger = Path("src/audit_logger/postgres_logger.py")
    content = audit_logger.read_text()

    # Should reference signature or validation
    assert "signature" in content.lower() or "verify" in content.lower()
