# Contributing to AeroSense-TestForge

## Workflow

1. **Plan:** Issues describe what to implement
2. **Test:** Write tests FIRST (RED phase)
3. **Implement:** Code to pass tests (GREEN phase)
4. **Review:** Code review via PR
5. **Commit:** Conventional format with Co-Author attribution

## TDD (Mandatory)

All code changes require tests first:

```bash
# RED: Write failing test
pytest tests/test_foo.py -v  # should fail

# GREEN: Implement minimal code to pass
pytest tests/test_foo.py -v  # should pass

# REFACTOR: Clean up, maintain tests passing
pytest --cov=src --cov-report=term-missing
```

## Code Style

- Python: PEP 8 via black + ruff
- Coverage: 80% minimum (90% for DO-178C modules)
- Commits: `type(scope): description`
  - Types: `feat`, `fix`, `test`, `docs`, `chore`, `refactor`

## DO-178C Changes

Changes to compliance-critical modules require:

1. `@pytest.mark.requirement("REQ-XXX")` tags
2. `# AI-GENERATED: confidence=X.XX` headers for LLM output
3. RTM auto-update before commit
4. Coverage >= 90%

## Security

- No hardcoded secrets
- All user input validated
- Request signatures verified
- Audit trail immutable

## Before Submitting PR

```bash
# Format
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Test
pytest --cov=src --cov-report=term-missing

# Build
docker build -t aerosense:test .
```

## Questions?

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.
