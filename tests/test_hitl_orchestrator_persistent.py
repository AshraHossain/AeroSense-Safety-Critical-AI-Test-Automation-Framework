"""
HITLOrchestrator with LangGraph persistence (Phase 2).
Tests state checkpointing, cross-session continuity, HITL decision gating.
"""
import os
from dataclasses import dataclass

import pytest
import psycopg2

from src.hitl_orchestrator.orchestrator import HITLOrchestrator


@pytest.fixture
def postgres_url():
    """PostgreSQL connection URL."""
    url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/aerosense_test"
    )
    return url


@pytest.fixture
def orchestrator(postgres_url):
    """Create HITLOrchestrator with Postgres + LangGraph checkpointing."""
    orch = HITLOrchestrator(postgres_url)
    orch.init_schema()
    yield orch
    # Cleanup
    with psycopg2.connect(postgres_url) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE orchestrator_state CASCADE")
            conn.commit()


@pytest.mark.integration
def test_hitl_submit_auto_action_confidence_high_and_reversible(orchestrator):
    """Action with confidence >= 0.85 and reversible=True auto-executes."""
    result = orchestrator.submit(
        action_id="heal_locator_001",
        action_type="heal_locator",
        proposed_change={"selector": "button.submit", "new_selector": "button[type=submit]"},
        confidence=0.88,
        reversible=True
    )

    assert result["status"] == "executed"
    assert result["human_review"] is False


@pytest.mark.integration
def test_hitl_submit_hitl_action_confidence_mid_range(orchestrator):
    """Action with 0.60 <= confidence < 0.85 escalates to HITL review."""
    result = orchestrator.submit(
        action_id="test_gen_002",
        action_type="generate_test",
        proposed_change={"test_name": "test_auth_flow", "body": "..."},
        confidence=0.70,
        reversible=True
    )

    assert result["status"] == "pending_review"
    assert result["human_review"] is True


@pytest.mark.integration
def test_hitl_submit_reject_action_confidence_too_low(orchestrator):
    """Action with confidence < 0.60 auto-rejected."""
    result = orchestrator.submit(
        action_id="rtm_edit_003",
        action_type="edit_rtm",
        proposed_change={"requirement_id": "REQ-001", "new_coverage": "test_foo"},
        confidence=0.45,
        reversible=False
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "confidence_too_low"


@pytest.mark.integration
def test_hitl_submit_hitl_action_irreversible(orchestrator):
    """Action with confidence >= 0.85 but irreversible=True escalates to HITL."""
    result = orchestrator.submit(
        action_id="commit_004",
        action_type="commit_tests",
        proposed_change={"tests": ["test_new_1", "test_new_2"], "message": "add tests"},
        confidence=0.90,
        reversible=False
    )

    assert result["status"] == "pending_review"
    assert result["human_review"] is True
    assert result["reason"] == "irreversible_action"


@pytest.mark.integration
def test_hitl_approve_action_changes_status(orchestrator):
    """Human approval transitions pending action to executed."""
    # Submit auto-HITL action
    submitted = orchestrator.submit(
        action_id="test_approve",
        action_type="generate_test",
        proposed_change={"test": "example"},
        confidence=0.72,
        reversible=True
    )
    assert submitted["status"] == "pending_review"

    # Approve it
    result = orchestrator.approve(action_id="test_approve")
    assert result["status"] == "executed"
    assert result["human_decision"] == "approved"


@pytest.mark.integration
def test_hitl_deny_action_changes_status(orchestrator):
    """Human denial transitions pending action to rejected."""
    submitted = orchestrator.submit(
        action_id="test_deny",
        action_type="generate_test",
        proposed_change={"test": "example"},
        confidence=0.75,
        reversible=True
    )
    assert submitted["status"] == "pending_review"

    result = orchestrator.deny(action_id="test_deny", reason="incorrect_logic")
    assert result["status"] == "rejected"
    assert result["human_decision"] == "denied"


@pytest.mark.integration
def test_hitl_state_persists_across_sessions(orchestrator, postgres_url):
    """Action state checkpointed to PostgreSQL; survives orchestrator restart."""
    # Session 1: Submit action
    orch1 = HITLOrchestrator(postgres_url)
    result1 = orch1.submit(
        action_id="persist_test",
        action_type="generate_test",
        proposed_change={"test": "persists"},
        confidence=0.70,
        reversible=True
    )
    assert result1["status"] == "pending_review"

    # Session 2: New orchestrator instance, load state
    orch2 = HITLOrchestrator(postgres_url)
    loaded = orch2.get_action("persist_test")
    assert loaded["status"] == "pending_review"
    assert loaded["action_type"] == "generate_test"

    # Session 2: Approve the action
    approved = orch2.approve(action_id="persist_test")
    assert approved["status"] == "executed"

    # Session 3: Verify state persisted
    orch3 = HITLOrchestrator(postgres_url)
    final = orch3.get_action("persist_test")
    assert final["status"] == "executed"


@pytest.mark.integration
def test_hitl_list_pending_actions(orchestrator):
    """List all pending_review actions."""
    # Submit 3 actions: 2 pending, 1 auto-executed
    orchestrator.submit(
        action_id="p1",
        action_type="generate_test",
        proposed_change={"test": "1"},
        confidence=0.70,
        reversible=True
    )
    orchestrator.submit(
        action_id="p2",
        action_type="generate_test",
        proposed_change={"test": "2"},
        confidence=0.65,
        reversible=True
    )
    orchestrator.submit(
        action_id="a1",
        action_type="heal_locator",
        proposed_change={"selector": "old"},
        confidence=0.90,
        reversible=True
    )

    pending = orchestrator.list_pending()
    assert len(pending) == 2
    assert all(a["status"] == "pending_review" for a in pending)
    assert set(a["action_id"] for a in pending) == {"p1", "p2"}


@pytest.mark.integration
def test_hitl_approve_unknown_action_raises(orchestrator):
    """Approving non-existent action raises error."""
    with pytest.raises(ValueError, match="Action.*not found"):
        orchestrator.approve(action_id="does_not_exist")


@pytest.mark.integration
def test_hitl_cannot_approve_already_executed(orchestrator):
    """Cannot approve an already-executed action."""
    orchestrator.submit(
        action_id="auto_exec",
        action_type="heal_locator",
        proposed_change={"selector": "old"},
        confidence=0.90,
        reversible=True
    )

    with pytest.raises(ValueError, match="already executed"):
        orchestrator.approve(action_id="auto_exec")


@pytest.mark.integration
def test_hitl_records_audit_trail(orchestrator):
    """Each HITL decision logged to audit trail with timestamp and user."""
    orchestrator.submit(
        action_id="audit_test",
        action_type="generate_test",
        proposed_change={"test": "audit"},
        confidence=0.75,
        reversible=True
    )

    orchestrator.approve(
        action_id="audit_test",
        human_reviewer="alice@example.com"
    )

    audit = orchestrator.get_audit_trail(action_id="audit_test")
    assert len(audit) >= 2  # submit + approve
    assert audit[-1]["event"] == "approved"
    assert audit[-1]["human_reviewer"] == "alice@example.com"
