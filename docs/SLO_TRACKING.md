# SLO Tracking Guide

How to verify we're meeting Service Level Objectives.

## Service Level Objectives (SLOs)

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Availability | 99.5% | < 99% |
| Latency (p95) | < 500ms | > 500ms for 5m |
| Error rate | < 0.1% | > 0.1% for 5m |
| RTM coverage | ≥ 90% | < 90% |

## Checking SLO Compliance

### Availability (uptime)

```bash
# Prometheus query
curl 'http://localhost:9090/api/v1/query?query=up{job="aerosense"}'

# If result is 1 → up, 0 → down
# Calculate: uptime_seconds / total_seconds * 100
```

### Latency (p95)

```bash
# Prometheus query
curl 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, http_request_duration_seconds)'

# Result in seconds. Should be < 0.5
```

### Error Rate

```bash
# Prometheus query
curl 'http://localhost:9090/api/v1/query?query=rate(http_request_failed[5m])'

# Result as decimal (0.001 = 0.1%). Should be < 0.001
```

### RTM Coverage

```bash
# Run tests with coverage report
pytest --cov=src --cov-report=term-missing

# Check: "TOTAL ... 90%"
# Should be >= 90%
```

## Grafana Dashboard

Open http://localhost:3000 (admin/admin) and create dashboard with panels:

```json
{
  "panels": [
    {
      "title": "Availability",
      "targets": [{"expr": "up{job=\"aerosense\"}"}]
    },
    {
      "title": "Latency p95",
      "targets": [{"expr": "histogram_quantile(0.95, http_request_duration_seconds)"}]
    },
    {
      "title": "Error Rate",
      "targets": [{"expr": "rate(http_request_failed[5m])"}]
    }
  ]
}
```

## Weekly SLO Review

Every Monday, check:

1. **Availability:** Did we hit 99.5%?
2. **Latency:** Was p95 consistently < 500ms?
3. **Error rate:** Did we stay < 0.1%?
4. **RTM coverage:** Maintained >= 90%?

Document in Slack: `#slo-tracking` channel

## SLO Violations

If an SLO is violated:

1. **Declare incident** (RUNBOOKS.md)
2. **Root cause analysis** (POSTMORTEM_TEMPLATE.md)
3. **Remediation plan** (timeline and owner)
4. **Prevention** (how to prevent recurrence)

## SLO Budgets

Monthly "error budget" = (100% - SLO%) × minutes in month

Example: 99.5% SLO = 0.5% budget = 216 minutes/month

If we've used our budget, go to "SLO preservation mode":
- Pause feature development
- Focus on reliability
- Reduce deployment frequency
- Increase testing rigor
