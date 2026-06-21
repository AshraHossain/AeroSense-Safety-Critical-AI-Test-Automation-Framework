import pytest

from src.hitl_orchestrator.orchestrator import HITLOrchestrator


@pytest.fixture
def orchestrator():
    return HITLOrchestrator()


def test_submit_auto_action_executes_immediately(orchestrator):
    result = orchestrator.submit(action_id="a1", confidence=0.95, reversible=True)
    assert result == "executed"
    assert orchestrator.status("a1") == "executed"


def test_submit_hitl_action_queues_pending(orchestrator):
    result = orchestrator.submit(action_id="a2", confidence=0.7, reversible=True)
    assert result == "pending"
    assert orchestrator.status("a2") == "pending"


def test_submit_reject_action_marks_rejected(orchestrator):
    result = orchestrator.submit(action_id="a3", confidence=0.3, reversible=True)
    assert result == "rejected"


def test_approve_pending_action_transitions_to_executed(orchestrator):
    orchestrator.submit(action_id="a4", confidence=0.7, reversible=True)
    orchestrator.approve("a4")
    assert orchestrator.status("a4") == "executed"


def test_deny_pending_action_transitions_to_rejected(orchestrator):
    orchestrator.submit(action_id="a5", confidence=0.7, reversible=True)
    orchestrator.deny("a5")
    assert orchestrator.status("a5") == "rejected"


def test_approve_non_pending_action_raises(orchestrator):
    orchestrator.submit(action_id="a6", confidence=0.95, reversible=True)
    with pytest.raises(ValueError):
        orchestrator.approve("a6")


def test_status_unknown_action_raises(orchestrator):
    with pytest.raises(KeyError):
        orchestrator.status("missing")
