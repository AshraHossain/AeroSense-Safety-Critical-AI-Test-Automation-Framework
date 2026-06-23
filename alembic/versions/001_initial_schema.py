"""Initial schema: audit_log and orchestrator_state tables

Revision ID: 001
Revises:
Create Date: 2026-06-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial audit_log and orchestrator_state tables."""
    # Audit log table (append-only)
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True, server_default=sa.text("nextval('audit_log_id_seq'::regclass)")),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("model", sa.String, nullable=False),
        sa.Column("prompt_hash", sa.String, nullable=False),
        sa.Column("response_hash", sa.String, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("human_decision", sa.String),
        sa.Column("outcome", sa.String, nullable=False),
    )

    # Prevent UPDATE and DELETE on audit_log
    op.execute("""
        CREATE TRIGGER audit_log_no_update
        BEFORE UPDATE ON audit_log
        FOR EACH ROW
        EXECUTE FUNCTION raise_immutable_error();
    """)

    op.execute("""
        CREATE TRIGGER audit_log_no_delete
        BEFORE DELETE ON audit_log
        FOR EACH ROW
        EXECUTE FUNCTION raise_immutable_error();
    """)

    # HITL orchestrator state table
    op.create_table(
        "orchestrator_state",
        sa.Column("action_id", sa.String, primary_key=True),
        sa.Column("action_type", sa.String, nullable=False),
        sa.Column("proposed_change", sa.String, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("reversible", sa.Boolean, nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("human_decision", sa.String),
        sa.Column("human_reviewer", sa.String),
    )

    # HITL audit trail
    op.create_table(
        "hitl_audit",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("action_id", sa.String, sa.ForeignKey("orchestrator_state.action_id"), nullable=False),
        sa.Column("event", sa.String, nullable=False),
        sa.Column("details", sa.String),
        sa.Column("human_reviewer", sa.String),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("hitl_audit")
    op.drop_table("orchestrator_state")
    op.drop_table("audit_log")
