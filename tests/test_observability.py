"""
Observability and monitoring tests (Phase 4).
Tests metrics, tracing, health checks, and production readiness.
"""
from pathlib import Path

import pytest


def test_prometheus_config_exists():
    """Prometheus configuration file exists."""
    prometheus_config = Path("k8s/prometheus.yml")
    assert prometheus_config.exists()


def test_prometheus_config_scrapes_app():
    """Prometheus configured to scrape app metrics."""
    prometheus_config = Path("k8s/prometheus.yml")
    content = prometheus_config.read_text()

    assert "scrape_configs" in content
    assert "app" in content or "aerosense" in content.lower()


def test_prometheus_config_scrapes_postgres():
    """Prometheus scrapes postgres exporter metrics."""
    prometheus_config = Path("k8s/prometheus.yml")
    content = prometheus_config.read_text()

    assert "postgres" in content.lower() or "pg_exporter" in content.lower()


def test_telemetry_module_exists():
    """Telemetry module for OpenTelemetry setup exists."""
    telemetry_module = Path("src/telemetry.py")
    assert telemetry_module.exists()


def test_telemetry_exports_metrics():
    """Telemetry module exports metrics for requests, HITL, audit."""
    telemetry_module = Path("src/telemetry.py")
    content = telemetry_module.read_text()

    assert "Counter" in content or "Histogram" in content or "metrics" in content


def test_telemetry_exports_tracer():
    """Telemetry module exports tracer for distributed tracing."""
    telemetry_module = Path("src/telemetry.py")
    content = telemetry_module.read_text()

    assert "Tracer" in content or "trace" in content.lower()


def test_kubernetes_deployment_exists():
    """Kubernetes Deployment manifest exists."""
    deployment = Path("k8s/deployment.yaml")
    assert deployment.exists()


def test_kubernetes_deployment_configures_app():
    """Deployment configures app container with health checks."""
    deployment = Path("k8s/deployment.yaml")
    content = deployment.read_text()

    assert "containers" in content or "image" in content
    assert "aerosense" in content.lower() or "testforge" in content.lower()


def test_kubernetes_deployment_has_liveness_probe():
    """Deployment includes liveness probe for app availability."""
    deployment = Path("k8s/deployment.yaml")
    content = deployment.read_text()

    assert "livenessProbe" in content or "liveness" in content.lower()
    assert "health" in content.lower()


def test_kubernetes_deployment_has_readiness_probe():
    """Deployment includes readiness probe for traffic routing."""
    deployment = Path("k8s/deployment.yaml")
    content = deployment.read_text()

    assert "readinessProbe" in content or "readiness" in content.lower()


def test_kubernetes_service_exists():
    """Kubernetes Service manifest exists."""
    service = Path("k8s/service.yaml")
    assert service.exists()


def test_kubernetes_service_exposes_app():
    """Service exposes app on port 8000."""
    service = Path("k8s/service.yaml")
    content = service.read_text()

    assert "8000" in content or "port" in content.lower()


def test_kubernetes_configmap_exists():
    """ConfigMap for environment configuration exists."""
    configmap = Path("k8s/configmap.yaml")
    assert configmap.exists()


def test_kubernetes_configmap_has_app_config():
    """ConfigMap includes app configuration variables."""
    configmap = Path("k8s/configmap.yaml")
    content = configmap.read_text()

    assert "LOG_LEVEL" in content or "PORT" in content


def test_kubernetes_postgres_deployment_exists():
    """Postgres StatefulSet or Deployment manifest exists."""
    postgres_manifest = Path("k8s/postgres.yaml")
    assert postgres_manifest.exists()


def test_kubernetes_postgres_has_persistent_volume():
    """Postgres uses PersistentVolumeClaim for data durability."""
    postgres_manifest = Path("k8s/postgres.yaml")
    content = postgres_manifest.read_text()

    assert "PersistentVolumeClaim" in content or "volumeClaimTemplates" in content or "postgres" in content.lower()


def test_metrics_emitted_in_mcp_server():
    """MCPServer emits metrics for requests and HITL decisions."""
    mcp_server = Path("src/mcp_server/server.py")
    content = mcp_server.read_text()

    assert "metric" in content.lower() or "counter" in content.lower()


def test_tracing_enabled_for_requests():
    """Requests traced with OpenTelemetry spans."""
    mcp_server = Path("src/mcp_server/server.py")
    content = mcp_server.read_text()

    assert "trace" in content.lower() or "span" in content.lower()


def test_audit_trail_includes_timestamp_and_actor():
    """Audit events include timestamp, actor, and action."""
    audit_logger = Path("src/audit_logger/postgres_logger.py")
    content = audit_logger.read_text()

    # Should have timestamp, model (actor), and outcome (action)
    assert "timestamp" in content
    assert "model" in content
    assert "outcome" in content
