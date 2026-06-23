# AeroSense-TestForge: AI-Powered Test Automation for Safety-Critical Software

Production-grade test automation framework for aviation/defense software governed by FAA DO-178C standards. AI agents generate, self-heal, and trace tests while maintaining auditability and human oversight.

**Status:** MVP + Production Hardening Complete (170 tests, 79% coverage)

## Quick Start

```bash
# 1. Clone and setup environment
git clone https://github.com/AshraHossain/aerosense-testforge.git
cd aerosense-testforge
bash scripts/setup.sh

# 2. Local development (Docker)
docker-compose up

# 3. Run tests
pytest --cov=src --cov-report=term-missing

# 4. Load testing
k6 run load-tests/endpoints.js

# 5. Production deployment
helm install aerosense ./helm
```

## Architecture

8 core components working together:

```
┌─ Requirements Parser ─────────────────────────────────┐
│  SRS (PDF/Markdown/JIRA) → Structured requirements   │
│  Output: REQ-001, REQ-002, ... with descriptions      │
└────────────────────────────────────────────────────────┘
                            ↓
┌─ Test Generator (LLM) ────────────────────────────────┐
│  Requirements → AI generates pytest stubs             │
│  Confidence scoring, RTM tagging, traceability        │
└────────────────────────────────────────────────────────┘
                            ↓
┌─ HITL Orchestrator ───────────────────────────────────┐
│  AI proposes → Human reviews → System executes        │
│  Confidence-gated autonomy: ≥0.85 auto-exec, <0.85    │
│  requires HITL approval                               │
└────────────────────────────────────────────────────────┘
                            ↓
┌─ Test Runner + RTM Builder ───────────────────────────┐
│  Execute pytest suite, track requirement coverage     │
│  Maintain 90%+ coverage for safety-critical targets   │
└────────────────────────────────────────────────────────┘
                            ↓
┌─ Audit Logger (PostgreSQL, Append-Only) ──────────────┐
│  Immutable record: timestamp, model, confidence,      │
│  human decision, outcome. Triggers prevent UPDATE/DELETE│
└────────────────────────────────────────────────────────┘
```

## Features

- **DO-178C Compliance:** Traceability tags, immutable audit trail, confidence gating, deterministic execution
- **Self-Healing Tests:** Playwright locator healing with confidence scoring
- **Append-Only Audit Log:** PostgreSQL with UPDATE/DELETE triggers for regulatory compliance
- **Rate Limiting:** Per-endpoint rate limits (10-100 req/min)
- **Request Signing:** HMAC-SHA256 for audit trail integrity
- **Kubernetes Ready:** Helm charts, auto-scaling (2-10 replicas), Prometheus metrics
- **Load Testing:** K6 scripts with SLO validation (500ms p95, 100 RPS target)
- **Chaos Engineering:** Pod disruption budgets, network latency injection

## Deployment

### Docker (Development)
```bash
docker-compose up
# Starts: app (port 8000) + postgres (5432) + redis (6379)
```

### Kubernetes (Production)
```bash
helm install aerosense ./helm \
  --set postgres.password=<secret> \
  --set secrets.anthropicApiKey=<key>
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## API

All endpoints require authentication via request signing. See [openapi.json](openapi.json) for full spec.

### Core Endpoints
- `POST /mcp/generate_tests` — Generate test stubs from SRS
- `GET /mcp/rtm` — Requirements Traceability Matrix
- `POST /mcp/hitl/submit` — Submit action for approval
- `POST /mcp/hitl/approve/{action_id}` — Approve pending action
- `GET /mcp/audit` — Audit log with CSV export
- `GET /health` — Service health check

See [examples/hitl-requests.sh](examples/hitl-requests.sh) for curl examples.

## Testing

```bash
# Unit tests (fast, no postgres required)
pytest tests/ -k "not integration" --cov=src

# Integration tests (require postgres)
pytest tests/ -m integration

# Load testing
k6 run load-tests/endpoints.js

# Chaos engineering
kubectl apply -f k8s/chaos/network-chaos.yaml
```

## Monitoring

- **Prometheus:** Metrics endpoint at `/metrics`
- **Grafana:** Dashboard config at [monitoring/grafana-dashboard.json](monitoring/grafana-dashboard.json)
- **Alerts:** Rules at [monitoring/prometheus-alerts.yml](monitoring/prometheus-alerts.yml)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — See [LICENSE](LICENSE)

## Architecture Deep Dive

See [ARCHITECTURE.md](ARCHITECTURE.md) for component interactions, design decisions, and DO-178C compliance patterns.

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

---

**Built for safety-critical software with confidence.**
