# CLAUDE.md — AeroSense-TestForge

## Project Overview

AeroSense-TestForge is an AI-powered test automation framework for safety-critical aviation/defense
software governed by FAA DO-178C / RTCA standards. LLMs generate, self-heal, and trace tests while
preserving the auditability, determinism, and human oversight DO-178C mandates. Built to demonstrate
production-grade AI governance for defense-software hiring managers (Lockheed, Northrop, Raytheon,
L3Harris, Boeing Defense).

**Owner**: Ash Hossain — AeroSense AI LLC / 5Y AI Holdings LLC
**Repo**: AshraHossain/aerosense-testforge

---

## Components (8)

1. **RequirementsParser** — SRS docs (PDF/Markdown/JIRA) → structured requirement objects
2. **TestGenerator** — LLM agent producing pytest stubs tagged with RTM requirement IDs
3. **LocatorHealer** — Self-healing Playwright locator engine, confidence-scored
4. **HITLOrchestrator** — LangGraph workflow: AI proposes → human reviews → system executes
5. **RTMBuilder** — Builds/updates Requirements Traceability Matrix from test metadata
6. **TestRunner** — pytest orchestrator, live result streaming via Redis pub/sub
7. **AuditLogger** — Immutable PostgreSQL audit trail for every AI + human decision
8. **MCPServer** — FastAPI-based MCP tool server exposing all framework capabilities

---

## Ponytail (token conservation)

Install once per machine:
```
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

Use ponytail mode for all implementation work in this repo — lazy-first ladder (does it need to exist? stdlib? native feature? existing dep? one line? minimum code), no speculative abstractions, shortest diff wins. DO-178C patterns above are NOT subject to ponytail simplification — traceability, audit immutability, confidence gating, and 90% coverage are hard requirements, never skip/shortcut them for brevity.

---

## Mandatory Session Workflow

1. `Skill: "graphify"` — load knowledge graph, check component state
2. `Skill: "gsd"` (`/gsd-plan`) — define phase scope, files affected, RTM impact, acceptance criteria. Wait for explicit approval.
3. Write **compliance tests first** (RTM tags + audit log verification) — RED
4. Write unit/integration tests — RED
5. Implement to GREEN
6. Run RTM coverage check — must stay ≥ 90%
7. `code-reviewer` agent — check for DO-178C pattern violations
8. Commit: `type(scope): description` + `Co-Author: Claude` (see Git Conventions)
9. `graphify update .` — refresh knowledge graph

---

## DO-178C Patterns (ENFORCED, not optional)

### 1. Traceability-First Development
- Every test function MUST carry `@pytest.mark.requirement("REQ-XXX")`
- Every AI-generated test MUST include a header comment: `# AI-GENERATED: confidence=X.XX, model=claude-sonnet-4-6, timestamp=ISO`
- RTM must be regenerated/updated before any test file is committed

### 2. Confidence-Gated Autonomy
- Auto-execute: `confidence >= 0.85` AND action reversible (e.g., suggest locator fix)
- HITL escalate: `confidence < 0.85` OR action irreversible (delete test, modify RTM, commit AI test)
- Never auto-commit AI-generated tests without a human review gate
- `final_confidence = llm_confidence × requirement_clarity_score × dom_stability_score`

| Confidence | Action |
|---|---|
| ≥ 0.85 | Auto-apply (reversible only) |
| 0.60–0.84 | HITL review required |
| < 0.60 | Reject, flag for manual authoring |

### 3. Immutable Audit Trail
- Every AI decision → PostgreSQL row: timestamp, model, prompt_hash, response_hash, confidence, human_decision, outcome
- Audit table is append-only — no UPDATE/DELETE, ever
- Export in DO-178C Table A-9 compatible CSV format

### 4. Deterministic Test Execution
- Seeded, reproducible runs (fixed seeds, pinned deps)
- All external calls (LLM, DOM) mockable for offline/CI execution
- Test results hash-verified against baseline for regression detection

### 5. Graceful Degradation
- LLM unavailable → fall back to rule-based template stubs
- DOM snapshot fails → flag for manual review, never auto-heal blind
- PostgreSQL unavailable → buffer audit events to local JSON, replay on reconnect
- Coverage drops below threshold → block CI, alert human

---

## Testing Standards

- **Coverage target: 90% minimum** (safety-critical justification — higher than OmniCompute's 80%)
- Required test types: unit, integration, E2E, **compliance** (RTM completeness, audit log integrity, traceability tag presence), **adversarial** (LLM returns low-confidence/malformed output — system must degrade gracefully)
- TDD mandatory — write compliance tests BEFORE implementing any DO-178C pattern
- Never mock AuditLogger in integration tests — must verify real DB writes
- Agent: `tdd-guide` for all new features/fixes

---

## Documentation Guides

Base (OmniCompute 23-guide template): README, ARCHITECTURE.md, COMPONENTS.md, QUICK_REFERENCE.md,
DEPLOYMENT.md, DEVELOPMENT.md, TESTING.md, FAQ.md, TROUBLESHOOTING.md, OPERATIONS.md, GLOSSARY.md,
COST_ANALYSIS.md (+ remaining OmniCompute guides), all cross-linked via a "Documentation Map" section.

Safety-critical additions (required):
- `DO178C_COMPLIANCE.md` — maps framework to DO-178C objectives/tables
- `RTM_GUIDE.md` — how to read/generate/export the Requirements Traceability Matrix
- `HITL_WORKFLOW.md` — decision points, escalation criteria, approval UI
- `AUDIT_LOG.md` — schema, query patterns, compliance export procedures
- `SELF_HEALING.md` — locator healing algorithm, confidence scoring, when NOT to auto-heal
- `AI_GOVERNANCE.md` — model selection, prompt versioning, AI decision boundaries
- `PORTFOLIO.md` — interview positioning (see below)

---

## GitHub Setup Checklist

OmniCompute base:
- [ ] CI/CD pipeline (pytest + coverage + mypy + ruff)
- [ ] Issue templates (bug, feature)
- [ ] PR template with checklist
- [ ] Discussion templates
- [ ] Status badges on README
- [ ] Branch protection on master

Safety-critical additions:
- [ ] Branch protection requires DO-178C compliance check (RTM coverage gate)
- [ ] Issue label `do-178c-impact` for changes touching traceability/audit
- [ ] PR template fields: "RTM Impact", "Audit Log Impact", "Coverage Delta"
- [ ] Secret scanning enabled
- [ ] CODEOWNERS — Ash owns all compliance-critical modules

---

## Git Conventions

- Format: `type(scope): description` — types: feat, fix, test, docs, chore, refactor, perf, ci
- Body explains why, not what
- Co-Author attribution in commit message
- Atomic commits — one logical change per commit
- Any commit touching RTM/audit logic MUST be labeled `do-178c-impact` on its PR

---

## AI Governance

- **Model pinning**: `claude-sonnet-4-6` for all test generation and locator healing. Pin explicitly in prompt headers and audit records — never silently float to a newer model without a version bump + re-validation pass.
- **Prompt versioning**: every prompt template lives in `prompts/` with a semver header (`# prompt_version: 1.2.0`). Bumping a prompt requires re-running the adversarial test suite.
- **Confidence thresholds**: see table in Pattern 2 above.

---

## What Claude Should NEVER Do

- Auto-commit AI-generated tests without HITL approval
- Modify, delete, or backfill audit log records (append-only, no exceptions)
- Skip RTM update before a test file commit
- Mark a requirement "covered" without an explicit `@pytest.mark.requirement` tag on a passing test
- Auto-heal a broken locator when DOM snapshot capture failed
- Let CI pass with RTM coverage < 90%

---

## Quick Demo Script (interview-ready, <3 min)

1. `docker compose up -d` — boots PostgreSQL + Redis + FastAPI + MCP server
2. `python scripts/generate_tests.py --srs examples/sample_srs.md` — AI generates pytest suite tagged with `REQ-*` IDs
3. Open HITL approval UI (`http://localhost:8000/hitl`) — review one AI-generated test, approve
4. `pytest --cov` — run suite, show RTM auto-update + coverage ≥ 90%
5. `python scripts/export_rtm.py --format pdf` — export DO-178C-style traceability matrix for audit
