# ADR 001: PostgreSQL Append-Only Audit Trail

**Status:** Accepted

**Date:** 2026-06-22

## Context
DO-178C requires an immutable audit trail of all AI and human decisions. We need to ensure that no record can be modified or deleted once created.

## Decision
Use PostgreSQL with BEFORE UPDATE/DELETE triggers that raise exceptions, preventing any modification or deletion of audit records.

## Rationale
- **Immutability:** Triggers enforce immutability at the database layer, not just application logic
- **Compliance:** Satisfies DO-178C audit trail requirements
- **Simplicity:** No external audit log service required
- **Performance:** Triggers are fast and have minimal overhead

## Alternatives Considered
1. **Application-level checks:** Rejected (can be bypassed if DB accessed directly)
2. **AWS QLDB:** Rejected (adds external dependency, higher cost)
3. **Blockchain:** Rejected (unnecessary complexity for compliance requirement)

## Consequences
- All audit queries are read-only (no UPDATE/DELETE)
- Schema changes require ALTER TABLE statements
- Disk usage grows monotonically (no compaction)
- Recommended: Backup and archive old records periodically
