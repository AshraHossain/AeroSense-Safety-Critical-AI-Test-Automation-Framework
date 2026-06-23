# Architecture: AeroSense-TestForge

## System Overview

8-component pipeline with DO-178C compliance gates:

1. **RequirementsParser** — Extracts requirements from SRS (PDF/Markdown/JIRA)
2. **TestGenerator** — Claude LLM generates pytest stubs tagged with REQ-IDs
3. **LocatorHealer** — Self-healing Playwright locators with confidence scoring
4. **HITLOrchestrator** — Human-in-loop approval with confidence gating
5. **RTMBuilder** — Maintains Requirements Traceability Matrix from test tags
6. **TestRunner** — Pytest orchestrator with Redis pub/sub streaming
7. **AuditLogger** — PostgreSQL append-only audit trail (immutable via triggers)
8. **MCPServer** — FastAPI MCP tool server exposing all operations

## DO-178C Patterns (Enforced)

### 1. Traceability-First Development
Every test function carries `@pytest.mark.requirement("REQ-XXX")` tag. RTM auto-updates before commit.

### 2. Confidence-Gated Autonomy
```
confidence >= 0.85 & reversible → auto-execute
0.60 - 0.84 → HITL escalate
< 0.60 → auto-reject
```

### 3. Immutable Audit Trail
PostgreSQL append-only with BEFORE UPDATE/DELETE triggers that raise exceptions. Exported as DO-178C Table A-9 CSV.

### 4. Deterministic Execution
Seeded RNG, pinned deps, mockable external calls (LLM, DOM). Reproducible across runs.

### 5. Graceful Degradation
- LLM unavailable → rule-based template stubs
- DOM snapshot fails → flag for manual review
- PostgreSQL unavailable → buffer to JSON, replay on reconnect
- Coverage < 90% → block CI with alert

## Deployment Architecture

### Local (docker-compose)
```
┌─ PostgreSQL ─────────────────────┐
├─ FastAPI + MCPServer (port 8000)─┤
├─ Redis (pub/sub for test streams)│
└─────────────────────────────────┘
```

### Kubernetes (Helm)
```
┌─ Deployment (2-10 replicas) ──────────────┐
│  Health/readiness probes → /health        │
│  Rate limiting middleware (10-100 req/min)│
│  Security headers (CSP, HSTS, X-Frame)    │
├─ StatefulSet (postgres) ─────────────────┤
│  10Gi PersistentVolumeClaim               │
│  External secrets integration (AWS/Vault) │
├─ HPA (CPU/memory based scaling) ─────────┤
│  Target: 70% CPU, 80% memory              │
│  Scale up: 100% per 15s, Scale down: 50% │
└───────────────────────────────────────────┘
```

## Data Flow

### Test Generation
```
SRS (PDF) → RequirementsParser → [REQ-001, REQ-002, ...]
          ↓
       TestGenerator (Claude)
          ↓
       [test_req_001, test_req_002] with @pytest.mark.requirement tags
          ↓
       HITLOrchestrator (confidence-gated approval)
          ↓
       AuditLogger (record: model, confidence, human_decision, outcome)
```

### Test Execution + RTM
```
pytest --cov=src
          ↓
       RTMBuilder scans @pytest.mark.requirement tags
          ↓
       Builds RTM: REQ-001 ← test_req_001 (✓ covered)
          ↓
       Exports: RTM.csv + coverage_percent
          ↓
       CI gate: coverage >= 90% or block merge
```

## Security Architecture

- **Request Signing:** HMAC-SHA256(secret, timestamp:payload) for audit integrity
- **Rate Limiting:** Per-endpoint, per-client sliding window (10-100 req/min)
- **Headers:** CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- **Secrets:** Kubernetes Secret + external-secrets (AWS Secrets Manager)
- **Audit Trail:** Immutable PostgreSQL, no UPDATE/DELETE allowed

## Performance Characteristics

| Metric | Target | Achieved |
|--------|--------|----------|
| Latency (p95) | 500ms | 350ms* |
| Latency (p99) | 1000ms | 850ms* |
| Throughput | 100 RPS | 85-120 RPS* |
| Error rate | <0.1% | 0.05%* |
| Test coverage | 90%+ | 79%* |

*Measured under load-tests/endpoints.js k6 scenarios

## Cost Optimization

- Kubernetes: 2-10 replicas, ~$500-600/month on AWS (estimate)
- Auto-scaling prevents over-provisioning
- Spot instances reduce cost by 70% for non-critical workloads
- PostgreSQL pooling: 20 connection limit

## Testing Coverage

- Unit tests: 170 tests, 79% coverage
- Integration tests: 11 postgres-backed tests (skipped in CI without DB)
- E2E tests: K6 load test scenarios (ramp-up, sustained, spike)
- Chaos tests: Network latency, packet loss, pod disruption

## Known Limitations

- **In-memory rate limiter:** Doesn't persist across pod restarts. Use Redis for distributed environments.
- **Telemetry fallback:** If OpenTelemetry unavailable, metrics not emitted (graceful degradation).
- **Self-healing:** Confidence < 0.6 auto-rejected, requires manual healing.

## Future Enhancements

- WebSocket real-time HITL updates (currently polling)
- Distributed caching layer (Redis)
- Multi-tenant support with RBAC
- Advanced HITL UI with visual diff
