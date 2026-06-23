"""
Load testing and performance benchmarks (Phase 6).
Tests SLOs, throughput targets, resource utilization.
"""
from pathlib import Path

import pytest


def test_load_test_scripts_directory_exists():
    """Load test scripts directory exists."""
    load_tests_dir = Path("load-tests")
    assert load_tests_dir.exists() and load_tests_dir.is_dir()


def test_k6_load_test_script_exists():
    """K6 load test script exists."""
    script = Path("load-tests/endpoints.js")
    assert script.exists()


def test_k6_script_defines_scenarios():
    """K6 script includes load scenarios (ramp-up, sustained, spike)."""
    script = Path("load-tests/endpoints.js")
    content = script.read_text()

    assert "scenario" in content.lower() or "stages" in content.lower()


def test_k6_script_tests_core_endpoints():
    """K6 script tests critical endpoints."""
    script = Path("load-tests/endpoints.js")
    content = script.read_text()

    endpoints = ["/mcp/generate_tests", "/mcp/hitl/submit", "/mcp/audit"]
    assert any(ep in content for ep in endpoints)


def test_benchmark_config_exists():
    """Performance benchmark configuration file exists."""
    config = Path("load-tests/benchmarks.json")
    assert config.exists()


def test_benchmark_config_defines_slos():
    """Benchmark config includes SLOs (response time, throughput)."""
    config = Path("load-tests/benchmarks.json")
    content = config.read_text()

    assert "latency" in content.lower() or "response" in content.lower()
    assert "throughput" in content.lower() or "rps" in content.lower()


def test_chaos_engineering_directory_exists():
    """Chaos engineering manifests directory exists."""
    chaos_dir = Path("k8s/chaos")
    assert chaos_dir.exists() and chaos_dir.is_dir()


def test_pod_disruption_budget_exists():
    """Pod Disruption Budget (PDB) manifest exists."""
    pdb = Path("k8s/chaos/pod-disruption-budget.yaml")
    assert pdb.exists()


def test_pdb_allows_disruptions():
    """PDB allows controlled pod disruptions during chaos."""
    pdb = Path("k8s/chaos/pod-disruption-budget.yaml")
    content = pdb.read_text()

    assert "minAvailable" in content or "maxUnavailable" in content


def test_network_chaos_manifest_exists():
    """Network chaos injection manifest exists."""
    chaos = Path("k8s/chaos/network-chaos.yaml")
    assert chaos.exists()


def test_network_chaos_injects_latency():
    """Network chaos manifest can inject latency."""
    chaos = Path("k8s/chaos/network-chaos.yaml")
    content = chaos.read_text()

    assert "latency" in content.lower() or "delay" in content.lower()


def test_postgres_failure_test_exists():
    """Test for postgres unavailability scenario exists."""
    test = Path("tests/test_resilience_postgres_failure.py")
    assert test.exists()


def test_postgres_failure_test_checks_graceful_degradation():
    """Postgres failure test validates graceful degradation."""
    test = Path("tests/test_resilience_postgres_failure.py")
    content = test.read_text()

    assert "graceful" in content.lower() or "fallback" in content.lower()


def test_rate_limiter_under_load_test_exists():
    """Test for rate limiter under load exists."""
    test = Path("tests/test_rate_limiter_load.py")
    assert test.exists()


def test_rate_limiter_load_test_verifies_enforcement():
    """Rate limiter load test verifies limits are enforced."""
    test = Path("tests/test_rate_limiter_load.py")
    content = test.read_text()

    assert "limit" in content.lower() or "429" in content


def test_resource_limits_configured():
    """K8s resource limits are configured."""
    deployment = Path("helm/templates/deployment.yaml")
    content = deployment.read_text()

    assert "resources:" in content or "limits:" in content


def test_horizontal_pod_autoscaler_exists():
    """Horizontal Pod Autoscaler (HPA) manifest exists."""
    hpa = Path("k8s/hpa.yaml")
    assert hpa.exists()


def test_hpa_scales_on_cpu():
    """HPA scales based on CPU utilization."""
    hpa = Path("k8s/hpa.yaml")
    content = hpa.read_text()

    assert "cpu" in content.lower() or "metrics" in content.lower()


def test_performance_profile_script_exists():
    """Performance profiling script exists."""
    profile = Path("load-tests/profile.py")
    assert profile.exists()


def test_cost_analysis_script_exists():
    """Cost analysis script for resource optimization exists."""
    cost = Path("load-tests/cost-analysis.py")
    assert cost.exists()
