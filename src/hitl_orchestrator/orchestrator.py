"""
HITLOrchestrator with LangGraph + Postgres persistence (Phase 2).
Manages AI action proposals, HITL approval workflows, state checkpointing.
"""
from datetime import datetime, timezone
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from src.locator_healer.healer import decide

_SCHEMA = """
-- HITL action state, persisted across restarts
CREATE TABLE IF NOT EXISTS orchestrator_state (
    action_id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    proposed_change JSONB NOT NULL,
    confidence FLOAT NOT NULL,
    reversible BOOLEAN NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    human_decision TEXT,
    human_reviewer TEXT
);

-- Audit trail for HITL decisions
CREATE TABLE IF NOT EXISTS hitl_audit (
    id SERIAL PRIMARY KEY,
    action_id TEXT NOT NULL REFERENCES orchestrator_state(action_id),
    event TEXT NOT NULL,
    details JSONB,
    human_reviewer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class HITLOrchestrator:
    """HITL orchestrator with LangGraph + Postgres checkpointing.
    Persists state across restarts, enforces confidence-gated autonomy."""

    def __init__(self, database_url: str = None):
        """Initialize with optional postgres for persistence.

        Args:
            database_url: PostgreSQL connection URL. If None, uses in-memory only.
        """
        self.database_url = database_url
        self._in_memory: dict[str, dict] = {}

    def init_schema(self):
        """Create schema (tables, triggers) if they don't exist."""
        if not self.database_url:
            return
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(_SCHEMA)
                conn.commit()

    def submit(
        self,
        *,
        action_id: str,
        action_type: str,
        proposed_change: dict,
        confidence: float,
        reversible: bool
    ) -> dict:
        """Submit an AI-proposed action for HITL gating.

        Applies confidence + reversibility rules:
        - confidence >= 0.85 & reversible=True → auto-execute
        - confidence < 0.60 → auto-reject
        - else → escalate to HITL review

        Args:
            action_id: Unique action identifier
            action_type: Type of action (generate_test, heal_locator, etc.)
            proposed_change: The proposed modification (dict)
            confidence: AI confidence score (0.0 - 1.0)
            reversible: Can the action be undone?

        Returns:
            Dictionary with status, human_review flag, optional reason
        """
        outcome = decide(confidence=confidence, reversible=reversible)

        status_map = {"auto": "executed", "hitl": "pending_review", "reject": "rejected"}
        status = status_map[outcome]
        reason = None
        human_review = status == "pending_review"

        if outcome == "reject":
            reason = "confidence_too_low"
        elif outcome == "hitl" and not reversible:
            reason = "irreversible_action"

        action = {
            "action_id": action_id,
            "action_type": action_type,
            "proposed_change": proposed_change,
            "confidence": confidence,
            "reversible": reversible,
            "status": status,
            "human_decision": None,
            "human_reviewer": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Persist to postgres if available
        if self.database_url:
            self._save_action_to_db(action)
            self._log_audit(action_id, "submitted", {"outcome": outcome})
        else:
            self._in_memory[action_id] = action

        result = {
            "action_id": action_id,
            "status": status,
            "human_review": human_review,
        }
        if reason:
            result["reason"] = reason
        return result

    def approve(self, action_id: str, human_reviewer: str = "system") -> dict:
        """Approve a pending HITL action.

        Args:
            action_id: Action to approve
            human_reviewer: Identifier of approving human

        Returns:
            Updated action dictionary

        Raises:
            ValueError: If action not found or not pending
        """
        action = self.get_action(action_id)
        if not action:
            raise ValueError(f"Action {action_id} not found")
        if action["status"] == "executed":
            raise ValueError(f"Action {action_id} already executed")
        if action["status"] != "pending_review":
            raise ValueError(f"Action {action_id} cannot be approved (status: {action['status']})")

        action["status"] = "executed"
        action["human_decision"] = "approved"
        action["human_reviewer"] = human_reviewer
        action["updated_at"] = datetime.now(timezone.utc).isoformat()

        if self.database_url:
            self._save_action_to_db(action)
            self._log_audit(action_id, "approved", {"human_reviewer": human_reviewer})
        else:
            self._in_memory[action_id] = action

        return action

    def deny(self, action_id: str, reason: str = None, human_reviewer: str = "system") -> dict:
        """Deny a pending HITL action.

        Args:
            action_id: Action to deny
            reason: Reason for denial
            human_reviewer: Identifier of reviewer

        Returns:
            Updated action dictionary

        Raises:
            ValueError: If action not found or not pending
        """
        action = self.get_action(action_id)
        if not action:
            raise ValueError(f"Action {action_id} not found")
        if action["status"] != "pending_review":
            raise ValueError(f"Action {action_id} cannot be denied (status: {action['status']})")

        action["status"] = "rejected"
        action["human_decision"] = "denied"
        action["human_reviewer"] = human_reviewer
        action["updated_at"] = datetime.now(timezone.utc).isoformat()

        if self.database_url:
            self._save_action_to_db(action)
            self._log_audit(action_id, "denied", {"reason": reason, "human_reviewer": human_reviewer})
        else:
            self._in_memory[action_id] = action

        return action

    def get_action(self, action_id: str) -> dict | None:
        """Get action state by ID.

        Args:
            action_id: Action identifier

        Returns:
            Action dictionary or None if not found
        """
        if self.database_url:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT * FROM orchestrator_state WHERE action_id = %s",
                        (action_id,)
                    )
                    row = cur.fetchone()
                    return dict(row) if row else None
        return self._in_memory.get(action_id)

    def list_pending(self) -> list[dict]:
        """Get all pending_review actions.

        Returns:
            List of action dictionaries with status == 'pending_review'
        """
        if self.database_url:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT * FROM orchestrator_state WHERE status = %s ORDER BY created_at",
                        ("pending_review",)
                    )
                    return [dict(r) for r in cur.fetchall()]
        return [a for a in self._in_memory.values() if a["status"] == "pending_review"]

    def get_audit_trail(self, action_id: str) -> list[dict]:
        """Get audit trail for an action.

        Args:
            action_id: Action identifier

        Returns:
            List of audit events
        """
        if self.database_url:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT * FROM hitl_audit WHERE action_id = %s ORDER BY created_at",
                        (action_id,)
                    )
                    return [dict(r) for r in cur.fetchall()]
        return []  # In-memory doesn't track audit

    def _save_action_to_db(self, action: dict):
        """Persist action to postgres."""
        if not self.database_url:
            return
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO orchestrator_state
                    (action_id, action_type, proposed_change, confidence, reversible,
                     status, human_decision, human_reviewer, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (action_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        human_decision = EXCLUDED.human_decision,
                        human_reviewer = EXCLUDED.human_reviewer,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        action["action_id"],
                        action["action_type"],
                        str(action["proposed_change"]),
                        action["confidence"],
                        action["reversible"],
                        action["status"],
                        action["human_decision"],
                        action["human_reviewer"],
                        action["updated_at"]
                    )
                )
                conn.commit()

    def _log_audit(self, action_id: str, event: str, details: dict = None):
        """Log HITL decision to audit trail."""
        if not self.database_url:
            return
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO hitl_audit (action_id, event, details)
                    VALUES (%s, %s, %s)
                    """,
                    (action_id, event, str(details or {}))
                )
                conn.commit()
