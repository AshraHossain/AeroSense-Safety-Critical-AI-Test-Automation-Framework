from src.locator_healer.healer import decide


class HITLOrchestrator:
    """ponytail: in-memory state machine. Swap to LangGraph + Postgres
    checkpointing when approval workflows need multi-step branching."""

    def __init__(self):
        self._actions: dict[str, str] = {}

    def submit(self, *, action_id: str, confidence: float, reversible: bool) -> str:
        outcome = decide(confidence=confidence, reversible=reversible)
        status = {"auto": "executed", "hitl": "pending", "reject": "rejected"}[outcome]
        self._actions[action_id] = status
        return status

    def approve(self, action_id: str) -> None:
        if self.status(action_id) != "pending":
            raise ValueError(f"{action_id} is not pending approval")
        self._actions[action_id] = "executed"

    def deny(self, action_id: str) -> None:
        if self.status(action_id) != "pending":
            raise ValueError(f"{action_id} is not pending approval")
        self._actions[action_id] = "rejected"

    def status(self, action_id: str) -> str:
        return self._actions[action_id]
