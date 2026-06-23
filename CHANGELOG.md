# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2026-06-23

### Added
- 8-component MVP: RequirementsParser, TestGenerator, LocatorHealer, HITLOrchestrator, RTMBuilder, TestRunner, AuditLogger, MCPServer
- PostgreSQL append-only audit logger with DO-178C immutability
- HITL orchestrator with confidence-gated autonomy (≥0.85 auto-exec, <0.85 HITL)
- 10 MCP endpoints (test generation, RTM, HITL approval, audit export)
- Docker compose for local development
- Kubernetes deployment (Helm charts with dev/staging/prod configs)
- GitHub Actions CI/CD (lint, type-check, test, coverage gate, security scan)
- OpenTelemetry metrics + Prometheus scraping + Grafana dashboards
- Prometheus alert rules (latency, error rate, rate limits, DB failures)
- Rate limiting middleware (10-100 req/min per endpoint)
- HMAC-SHA256 request signing for audit integrity
- Security headers (CSP, HSTS, X-Frame-Options)
- K6 load testing scripts (ramp-up, sustained, spike scenarios)
- Chaos engineering manifests (network latency, packet loss, PDB)
- Horizontal Pod Autoscaling (2-10 replicas on CPU/memory)
- Alembic database migrations with schema versioning
- 193 unit + integration + load tests (79% coverage)
- Complete documentation (README, ARCHITECTURE, DEPLOYMENT, CONTRIBUTING, TROUBLESHOOTING)
- Setup automation (bash scripts)
- Example HITL workflow requests

### Security
- Request signing via HMAC-SHA256
- Rate limiting prevents API exhaustion
- Security headers prevent XSS, clickjacking
- Audit trail immutable (PostgreSQL triggers)
- Dependency vulnerability scanning (bandit, safety)

### Performance
- SLO targets: p95 < 500ms, p99 < 1000ms, error rate < 0.1%
- Load tested to 40 concurrent users
- Auto-scaling 2-10 replicas
- Graceful degradation on postgres failure

---

## Guidelines

### Format
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Group changes by type (Added, Changed, Deprecated, Removed, Fixed, Security)
- Link PRs: `[#123](https://github.com/AshraHossain/aerosense-testforge/pull/123)`
- Date format: YYYY-MM-DD

### Categories
- **Added** — new features, endpoints, tests
- **Changed** — modifications to existing functionality
- **Deprecated** — features marked for removal
- **Removed** — deleted features or endpoints
- **Fixed** — bug fixes
- **Security** — security improvements or vulnerability patches
