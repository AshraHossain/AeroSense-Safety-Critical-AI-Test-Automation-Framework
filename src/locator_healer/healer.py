from typing import Literal

Decision = Literal["auto", "hitl", "reject"]

AUTO_THRESHOLD = 0.85
REJECT_THRESHOLD = 0.60


def compute_confidence(llm_confidence: float, requirement_clarity_score: float, dom_stability_score: float) -> float:
    return round(llm_confidence * requirement_clarity_score * dom_stability_score, 4)


def decide(*, confidence: float, reversible: bool) -> Decision:
    if confidence < REJECT_THRESHOLD:
        return "reject"
    if confidence >= AUTO_THRESHOLD and reversible:
        return "auto"
    return "hitl"
