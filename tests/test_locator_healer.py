from src.locator_healer.healer import compute_confidence, decide


def test_compute_confidence_multiplies_three_scores():
    assert compute_confidence(0.9, 0.9, 0.9) == round(0.9 * 0.9 * 0.9, 4)


def test_decide_auto_when_confidence_high_and_reversible():
    assert decide(confidence=0.9, reversible=True) == "auto"


def test_decide_hitl_when_confidence_high_but_irreversible():
    assert decide(confidence=0.95, reversible=False) == "hitl"


def test_decide_hitl_when_confidence_mid():
    assert decide(confidence=0.7, reversible=True) == "hitl"


def test_decide_reject_when_confidence_low():
    assert decide(confidence=0.4, reversible=True) == "reject"


def test_decide_boundary_at_0_85_is_auto():
    assert decide(confidence=0.85, reversible=True) == "auto"


def test_decide_boundary_at_0_60_is_hitl_not_reject():
    assert decide(confidence=0.60, reversible=True) == "hitl"
