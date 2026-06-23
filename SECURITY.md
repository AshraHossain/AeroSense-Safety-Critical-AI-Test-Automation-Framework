# Security Policy

## Reporting Security Vulnerabilities

**Do not open a public GitHub issue for security vulnerabilities.**

Email: security@aerosense.ai

Include:
- Vulnerability description
- Affected components/versions
- Proof of concept (no real data)
- Suggested fix (optional)

**Expected Response Time:** Within 48 hours

## Bug Bounty

Currently no formal bug bounty program. Security researchers are encouraged to disclose privately.

## Security Scanning

All commits trigger:
- **bandit:** Python security linting (high/medium severity)
- **safety:** Dependency vulnerability check
- **mypy:** Type checking (catches unsafe patterns)

## Secure by Default

- No hardcoded secrets (all checked via pre-commit)
- All user input validated at system boundaries
- HMAC-SHA256 request signing for audit integrity
- Rate limiting prevents API exhaustion
- CSP headers prevent XSS
- Postgres append-only audit trail (immutable)
- Request signatures verified for authenticity

## Compliance

- **DO-178C:** Traceability, audit trail, confidence gating, deterministic execution
- **OWASP Top 10:** Mitigated via input validation, rate limiting, CSRF tokens, secure headers

## Third-Party Dependencies

Reviewed quarterly via `safety check`. See `pyproject.toml` for version pins.

## Incident Response

1. Verify vulnerability (reproduce independently)
2. Notify maintainer (security@aerosense.ai)
3. Coordinate fix and disclosure timeline
4. Release patch with credit to reporter
