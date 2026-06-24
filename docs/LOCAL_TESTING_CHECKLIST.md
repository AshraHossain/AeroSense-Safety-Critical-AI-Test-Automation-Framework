# Local Testing Checklist (Pre-Push)

Run through this before pushing to remote.

## Code Quality

- [ ] `black src tests` — Code formatted
- [ ] `ruff check src tests` — No linting issues
- [ ] `mypy src --ignore-missing-imports` — No type errors
- [ ] `bandit -r src/ -ll` — No security issues

## Testing

- [ ] `pytest -k "not integration" --cov=src` — Tests pass, coverage ≥80%
- [ ] Coverage report reviewed (critical modules ≥90%)
- [ ] No new warnings or flaky tests

## Git Hygiene

- [ ] `git status` — No untracked files (except .env.local)
- [ ] `git diff` — Changes match what you intended
- [ ] Commit message follows conventional format (`type(scope): description`)
- [ ] No hardcoded secrets or `.env` files

## Integration (If touching DB/HITL/RTM)

- [ ] `docker-compose up postgres` — DB running
- [ ] `pytest -m integration` — Integration tests pass
- [ ] `alembic current` — DB schema matches latest migration
- [ ] RTM coverage ≥90% (if touching requirements)

## Load Testing (If touching API endpoints)

- [ ] `make load-test` — Performance baseline not regressed
- [ ] p95 latency < 500ms
- [ ] Error rate < 0.1%

## Compliance (If DO-178C critical module)

- [ ] `@pytest.mark.requirement("REQ-XXX")` tags added
- [ ] Audit trail tested (if touching AuditLogger)
- [ ] Confidence gating tested (if touching HITLOrchestrator)
- [ ] Coverage ≥90%

## Documentation

- [ ] README updated (if API changes)
- [ ] CHANGELOG entry added (if user-facing change)
- [ ] Code comments added (if WHY is non-obvious)

## Final Check

- [ ] `make clean` — Cleanup build artifacts
- [ ] `git status` — Ready to push
- [ ] Branch is rebased/merged to latest main (if needed)

## Push Command

```bash
git push -u origin feature-branch
```

---

**Tip:** Use `make` for shortcuts:
```bash
make lint       # format + lint + typecheck
make test       # run tests with coverage
make coverage   # open HTML coverage report
```
