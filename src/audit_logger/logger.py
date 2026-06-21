import sqlite3
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    model TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,
    response_hash TEXT NOT NULL,
    confidence REAL NOT NULL,
    human_decision TEXT NOT NULL,
    outcome TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS audit_log_no_update
BEFORE UPDATE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log is append-only: UPDATE forbidden');
END;

CREATE TRIGGER IF NOT EXISTS audit_log_no_delete
BEFORE DELETE ON audit_log
BEGIN
    SELECT RAISE(ABORT, 'audit_log is append-only: DELETE forbidden');
END;
"""


class AuditLogger:
    """ponytail: sqlite append-only log. Swap to Postgres when multi-process
    writers need real concurrency — schema/triggers port directly."""

    def __init__(self, db_path: Path):
        self.db_path = str(db_path)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(_SCHEMA)

    def record(self, *, model, prompt_hash, response_hash, confidence, human_decision, outcome):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO audit_log (model, prompt_hash, response_hash, confidence, "
                "human_decision, outcome) VALUES (?, ?, ?, ?, ?, ?)",
                (model, prompt_hash, response_hash, confidence, human_decision, outcome),
            )

    def all_records(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM audit_log ORDER BY id").fetchall()
            return [dict(r) for r in rows]
