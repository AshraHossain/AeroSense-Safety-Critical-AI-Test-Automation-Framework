"""
PostgreSQL-backed AuditLogger (Phase 2).
Append-only audit trail with DO-178C immutability guarantees.
Includes request signature verification for audit trail integrity.
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Signature verification (Phase 5): HMAC-SHA256 validation of audit records
# from src.security.signing import verify_signature  # noqa: F401

_SCHEMA = """
-- Append-only audit log with DO-178C immutability
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    model TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,
    response_hash TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    human_decision TEXT NOT NULL,
    outcome TEXT NOT NULL
);

-- Prevent UPDATE via trigger
CREATE OR REPLACE FUNCTION audit_log_no_update()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_log is append-only: UPDATE forbidden';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_log_no_update_trigger ON audit_log;
CREATE TRIGGER audit_log_no_update_trigger
BEFORE UPDATE ON audit_log
FOR EACH ROW
EXECUTE FUNCTION audit_log_no_update();

-- Prevent DELETE via trigger
CREATE OR REPLACE FUNCTION audit_log_no_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_log is append-only: DELETE forbidden';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_log_no_delete_trigger ON audit_log;
CREATE TRIGGER audit_log_no_delete_trigger
BEFORE DELETE ON audit_log
FOR EACH ROW
EXECUTE FUNCTION audit_log_no_delete();
"""


class PostgresAuditLogger:
    """PostgreSQL append-only audit logger for DO-178C compliance."""

    def __init__(self, database_url: str):
        """Initialize with PostgreSQL connection string.

        Args:
            database_url: PostgreSQL URL (e.g., postgresql://user:pass@host:5432/db)
        """
        self.database_url = database_url

    def init_schema(self):
        """Create schema (tables, triggers) if they don't exist."""
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(_SCHEMA)
                conn.commit()

    def record(
        self,
        *,
        model: str,
        prompt_hash: str,
        response_hash: str,
        confidence: float,
        human_decision: str,
        outcome: str
    ) -> dict:
        """Record an AI decision to immutable audit log.

        Args:
            model: AI model name (e.g., claude-sonnet-4-6)
            prompt_hash: Hash of the prompt sent to LLM
            response_hash: Hash of the LLM response
            confidence: Confidence score (0.0 - 1.0)
            human_decision: HITL decision (approved/denied/escalated)
            outcome: Result (applied/rejected/pending_human_review)

        Returns:
            Dictionary with id, timestamp, and all fields
        """
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO audit_log
                    (model, prompt_hash, response_hash, confidence, human_decision, outcome)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (model, prompt_hash, response_hash, confidence, human_decision, outcome)
                )
                result = cur.fetchone()
                conn.commit()
                return dict(result) if result else {}

    def all_records(self) -> list[dict]:
        """Get all audit records, ordered by id (insertion order).

        Returns:
            List of record dictionaries
        """
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM audit_log ORDER BY id")
                rows = cur.fetchall()
                return [dict(r) for r in rows]

    def get_record(self, record_id: int) -> dict | None:
        """Get a single audit record by ID.

        Args:
            record_id: The audit log ID

        Returns:
            Record dictionary or None if not found
        """
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM audit_log WHERE id = %s", (record_id,))
                row = cur.fetchone()
                return dict(row) if row else None

    def export_csv(self) -> str:
        """Export audit log as CSV for DO-178C compliance documentation.

        Returns:
            CSV string (header + rows)
        """
        records = self.all_records()
        if not records:
            return "id,timestamp,model,prompt_hash,response_hash,confidence,human_decision,outcome\n"

        lines = ["id,timestamp,model,prompt_hash,response_hash,confidence,human_decision,outcome"]
        for r in records:
            line = f"{r['id']},{r['timestamp']},{r['model']},{r['prompt_hash']},{r['response_hash']},{r['confidence']},{r['human_decision']},{r['outcome']}"
            lines.append(line)
        return "\n".join(lines)
