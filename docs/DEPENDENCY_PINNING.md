# Dependency Pinning Rationale

Why we pin specific versions and when to update.

## Pinned Dependencies

| Package | Version | Reason | Risk if updated |
|---------|---------|--------|-----------------|
| anthropic | 0.25.1 | API compatibility | Breaking API changes, auth failures |
| fastapi | 0.104.1 | Security + stability | Async behavior changes, route conflicts |
| sqlalchemy | 2.0.23 | ORM compatibility | Query syntax, migration breakage |
| pydantic | 2.5.0 | Validation schema | Type validation changes, config errors |
| alembic | 1.12.1 | Migration compatibility | Migration failures, schema corruption |
| pytest | 7.4.3 | Test runner | Test discovery changes, fixture conflicts |
| psycopg2 | 2.9.9 | Database driver | Connection failures, query issues |

## Policy

- **Security patches:** Apply within 48 hours (e.g., 0.25.1 → 0.25.2)
- **Minor updates:** Apply after testing on staging (e.g., 0.25.0 → 0.26.0)
- **Major updates:** Require approval + full test suite (e.g., 0.25.0 → 1.0.0)

## Critical Dependencies

These should **NEVER** be updated without testing:

- `anthropic` — API breaking changes common
- `sqlalchemy` — ORM query syntax changes
- `alembic` — migration compatibility
- `fastapi` — async/routing changes

## Safe to Update

These can be updated more liberally:

- `pytest` — backward compatible across minor versions
- `black` — formatter, same output
- `ruff` — linter, no runtime impact

## Updating a Dependency

```bash
# 1. Check what changed
pip index versions anthropic | head -20

# 2. Read changelog
# Go to: https://github.com/anthropics/anthropic-sdk-python/blob/main/CHANGELOG.md

# 3. Update locally
pip install anthropic==0.26.0

# 4. Run full test suite
pytest --cov=src

# 5. Test specific functionality
# For anthropic: run /mcp/generate_tests endpoint
# For sqlalchemy: run /mcp/audit endpoint
# For alembic: run `alembic upgrade head`

# 6. Commit
git add pyproject.toml
git commit -m "chore: update anthropic to 0.26.0"

# 7. Push to feature branch, create PR
# Let CI/CD verify in full environment

# 8. Merge and deploy to staging first
```

## Security Vulnerabilities

If a security vulnerability is found in a pinned dependency:

1. **Assess risk** — does it affect our code path?
2. **Update immediately** — security > stability
3. **Test thoroughly** — full test suite + load test
4. **Deploy ASAP** — don't delay patching

Example: If `sqlalchemy` has SQL injection vulnerability:
```bash
# Immediate action
pip install sqlalchemy==2.0.24  # patched version
pytest --cov=src
# Deploy within 24 hours
```

## Dependency Audit

Weekly check for updates and vulnerabilities:

```bash
# Check for outdated packages
pip list --outdated

# Check for security issues
pip install safety
safety check

# Check for dependency conflicts
pip check
```

## Future Updates

Plan quarterly dependency review:
- 1st Monday of quarter: audit dependencies
- Prioritize security patches
- Schedule updates during low-traffic periods
- Test in staging before prod

## Troubleshooting Update Failures

**Test fails after update:**
1. Run with old version → confirm test was passing
2. Read changelog for breaking changes
3. Adapt code to new API
4. Rerun tests
5. Commit code + version bump together

**Production issue after update:**
1. Rollback to previous version immediately
2. Investigate root cause (not just "new version bad")
3. Test fix locally before redeploying
4. Document in postmortem
