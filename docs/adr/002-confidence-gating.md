# ADR 002: Confidence-Gated Autonomy

**Status:** Accepted

**Date:** 2026-06-22

## Context
AI decisions must balance automation (speed) with human oversight (safety). We need a way to automatically approve low-risk decisions while escalating uncertain ones.

## Decision
Implement confidence-gated autonomy:
- `confidence >= 0.85 & reversible` → Auto-execute
- `0.60 <= confidence < 0.85` → HITL escalate
- `confidence < 0.60` → Auto-reject

## Rationale
- **Safety:** Uncertain decisions always get human review
- **Efficiency:** Confident, reversible decisions proceed without delay
- **Auditability:** Every decision logged with confidence score and human outcome
- **DO-178C:** Explicit separation of autonomous and HITL flows

## Alternatives Considered
1. **All auto-execute:** Rejected (unsafe for uncertain decisions)
2. **All HITL:** Rejected (slows down safe decisions)
3. **Single threshold:** Rejected (no distinction between reversible/irreversible)

## Consequences
- Defines what "confidence" means (must be model-specific, validated)
- Irreversible actions always require HITL review
- Threshold values are tunable per action type
- Requires audit trail to track confidence at decision time
