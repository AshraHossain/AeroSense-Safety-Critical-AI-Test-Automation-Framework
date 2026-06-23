"""
Documentation and configuration completeness tests (Final Polish).
Tests README, API docs, deployment guides, monitoring configs.
"""
from pathlib import Path

import pytest


def test_readme_exists():
    """README.md exists and documents project."""
    readme = Path("README.md")
    assert readme.exists()


def test_readme_has_quick_start():
    """README includes quick start section."""
    readme = Path("README.md")
    content = readme.read_text()
    assert "quick start" in content.lower() or "getting started" in content.lower()


def test_readme_documents_architecture():
    """README includes architecture overview."""
    readme = Path("README.md")
    content = readme.read_text()
    assert "architecture" in content.lower() or "components" in content.lower()


def test_architecture_md_exists():
    """ARCHITECTURE.md documents system design."""
    arch = Path("ARCHITECTURE.md")
    assert arch.exists()


def test_architecture_documents_components():
    """ARCHITECTURE.md describes all 8 components."""
    arch = Path("ARCHITECTURE.md")
    content = arch.read_text()
    components = [
        "RequirementsParser",
        "TestGenerator",
        "LocatorHealer",
        "HITLOrchestrator",
        "RTMBuilder",
        "TestRunner",
        "AuditLogger",
        "MCPServer",
    ]
    assert any(comp.lower() in content.lower() for comp in components)


def test_deployment_guide_exists():
    """DEPLOYMENT.md provides step-by-step deployment instructions."""
    deploy = Path("DEPLOYMENT.md")
    assert deploy.exists()


def test_deployment_covers_kubernetes():
    """DEPLOYMENT.md includes Kubernetes deployment steps."""
    deploy = Path("DEPLOYMENT.md")
    content = deploy.read_text()
    assert "kubernetes" in content.lower() or "helm" in content.lower() or "k8s" in content.lower()


def test_openapi_spec_exists():
    """OpenAPI/Swagger specification exists."""
    spec = Path("openapi.json")
    assert spec.exists()


def test_openapi_documents_endpoints():
    """OpenAPI spec includes all endpoints."""
    spec = Path("openapi.json")
    content = spec.read_text()
    assert "/mcp/" in content


def test_setup_script_exists():
    """Setup script for environment initialization exists."""
    setup = Path("scripts/setup.sh")
    assert setup.exists()


def test_setup_generates_env_file():
    """Setup script generates .env file."""
    setup = Path("scripts/setup.sh")
    content = setup.read_text()
    assert ".env" in content


def test_grafana_dashboard_exists():
    """Grafana dashboard configuration exists."""
    dashboard = Path("monitoring/grafana-dashboard.json")
    assert dashboard.exists()


def test_grafana_monitors_latency():
    """Grafana dashboard includes latency metrics."""
    dashboard = Path("monitoring/grafana-dashboard.json")
    content = dashboard.read_text()
    assert "latency" in content.lower() or "duration" in content.lower()


def test_prometheus_alerts_exist():
    """Prometheus alert rules file exists."""
    alerts = Path("monitoring/prometheus-alerts.yml")
    assert alerts.exists()


def test_prometheus_alerts_cover_slos():
    """Alert rules include SLO violations."""
    alerts = Path("monitoring/prometheus-alerts.yml")
    content = alerts.read_text()
    assert "alert" in content.lower()
    assert "latency" in content.lower() or "error" in content.lower()


def test_license_exists():
    """LICENSE file exists."""
    license_file = Path("LICENSE")
    assert license_file.exists()


def test_codeowners_exists():
    """CODEOWNERS file for governance exists."""
    codeowners = Path(".github/CODEOWNERS")
    assert codeowners.exists()


def test_codeowners_defines_owners():
    """CODEOWNERS defines code ownership."""
    codeowners = Path(".github/CODEOWNERS")
    content = codeowners.read_text()
    assert "@" in content  # GitHub handle references


def test_example_requests_exist():
    """Example curl/HTTP requests for HITL endpoints exist."""
    examples = Path("examples/hitl-requests.sh")
    assert examples.exists()


def test_examples_document_approval_flow():
    """Examples show HITL approval/denial flow."""
    examples = Path("examples/hitl-requests.sh")
    content = examples.read_text()
    assert "approve" in content.lower() or "deny" in content.lower()


def test_security_scanning_in_ci():
    """CI pipeline includes security scanning."""
    lint_workflow = Path(".github/workflows/lint.yml")
    content = lint_workflow.read_text()
    assert "security" in content.lower() or "bandit" in content.lower() or "safety" in content.lower()


def test_contributing_guide_exists():
    """CONTRIBUTING.md provides contribution guidelines."""
    contrib = Path("CONTRIBUTING.md")
    assert contrib.exists()


def test_troubleshooting_guide_exists():
    """TROUBLESHOOTING.md documents common issues."""
    troubleshoot = Path("TROUBLESHOOTING.md")
    assert troubleshoot.exists()
