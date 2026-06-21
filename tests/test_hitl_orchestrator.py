import pytest

from src.hitl_orchestrator.orchestrator import HITLOrchestrator


@pytest.fixture
def orchestrator():
    return HITLOrchestrator()


def test_submit_auto_action_executes_immediately(orchestrator):
    result = orchestrator.submit(
        action_id="a1",
        action_type="heal_locator",
        proposed_change={"selector": "old"},
        confidence=0.95,
        reversible=True
    )
    assert result["status"] == "executed"
    assert result["human_review"] is False
    assert orchestrator.get_action("a1")["status"] == "executed"


def test_submit_hitl_action_queues_pending(orchestrator):
    result = orchestrator.submit(
        action_id="a2",
        action_type="generate_test",
        proposed_change={"test": "example"},
        confidence=0.7,
        reversible=True
    )
    assert result["status"] == "pending_review"
    assert result["human_review"] is True
    assert orchestrator.get_action("a2")["status"] == "pending_review"


def test_submit_reject_action_marks_rejected(orchestrator):
    result = orchestrator.submit(
        action_id="a3",
        action_type="generate_test",
        proposed_change={"test": "example"},
        confidence=0.3,
        reversible=True
    )
    assert result["status"] == "rejected"
    assert result["reason"] == "confidence_too_low"


def test_approve_pending_action_transitions_to_executed(orchestrator):
    orchestrator.submit(
        action_id="a4",
        action_type="generate_test",
        proposed_change={"test": "example"},
        confidence=0.7,
        reversible=True
    )
    result = orchestrator.approve("a4")
    assert result["status"] == "executed"
    assert orchestrator.get_action("a4")["status"] == "executed"


def test_deny_pending_action_transitions_to_rejected(orchestrator):
    orchestrator.submit(
        action_id="a5",
        action_type="generate_test",
        proposed_change={"test": "example"},
        confidence=0.7,
        reversible=True
    )
    result = orchestrator.deny("a5")
    assert result["status"] == "rejected"
    assert orchestrator.get_action("a5")["status"] == "rejected"


def test_approve_non_pending_action_raises(orchestrator):
    orchestrator.submit(
        action_id="a6",
        action_type="heal_locator",
        proposed_change={"selector": "old"},
        confidence=0.95,
        reversible=True
    )
    with pytest.raises(ValueError):
        orchestrator.approve("a6")


def test_get_action_unknown_returns_none(orchestrator):
    result = orchestrator.get_action("missing")
    assert result is None
