"""
Cost analysis and resource optimization (Phase 6).
Analyzes K8s resource utilization for cost optimization.
"""
import json
from pathlib import Path


def analyze_costs():
    """Analyze and optimize resource utilization costs."""
    benchmarks = json.loads(Path("load-tests/benchmarks.json").read_text())
    limits = benchmarks["resource_limits"]
    scaling = benchmarks["scaling"]

    # AWS pricing (example)
    cpu_hour_cost = 0.02  # $/vCPU-hour
    memory_gb_hour_cost = 0.002  # $/GB-hour
    db_connection_cost = 0.001  # $/connection-hour

    # Current allocation
    min_replicas = scaling["min_replicas"]
    max_replicas = scaling["max_replicas"]
    cpu_per_pod = limits["cpu_cores"]
    memory_per_pod = limits["memory_mb"] / 1024  # Convert to GB

    # Monthly cost (30 days, 24 hours)
    hours_per_month = 30 * 24
    min_replicas_cost = (
        min_replicas * cpu_per_pod * cpu_hour_cost * hours_per_month
        + min_replicas * memory_per_pod * memory_gb_hour_cost * hours_per_month
    )

    avg_replicas = (min_replicas + max_replicas) / 2
    avg_cost = (
        avg_replicas * cpu_per_pod * cpu_hour_cost * hours_per_month
        + avg_replicas * memory_per_pod * memory_gb_hour_cost * hours_per_month
    )

    # DB connections
    db_cost = limits["postgres_connections"] * db_connection_cost * hours_per_month

    analysis = {
        "current_allocation": {
            "min_replicas": min_replicas,
            "max_replicas": max_replicas,
            "cpu_per_pod": cpu_per_pod,
            "memory_per_pod_gb": memory_per_pod,
        },
        "cost_estimates": {
            "min_monthly_cost_usd": round(min_replicas_cost, 2),
            "avg_monthly_cost_usd": round(avg_cost + db_cost, 2),
            "db_monthly_cost_usd": round(db_cost, 2),
        },
        "optimization_suggestions": [
            "Monitor actual CPU/memory utilization over 1 week",
            "Reduce max_replicas if peak utilization < 80%",
            "Use spot instances for non-critical workloads (save 70%)",
            "Right-size requests/limits based on observed usage",
        ],
    }

    return analysis


if __name__ == "__main__":
    analysis = analyze_costs()
    print("Cost Analysis:")
    print(json.dumps(analysis, indent=2))
