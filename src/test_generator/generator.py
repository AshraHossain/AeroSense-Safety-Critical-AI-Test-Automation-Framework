from datetime import datetime, timezone

from src.requirements_parser.parser import Requirement

_TEMPLATE = '''# AI-GENERATED: confidence={confidence}, model={model}, timestamp={timestamp}
import pytest


@pytest.mark.requirement("{req_id}")
def {func_name}():
    """{req_text}"""
    raise NotImplementedError("fill in assertions for {req_id}")
'''


def generate_test_stub(req: Requirement, *, model: str, confidence: float) -> str:
    func_name = "test_" + req.id.lower().replace("-", "_")
    return _TEMPLATE.format(
        confidence=confidence,
        model=model,
        timestamp=datetime.now(timezone.utc).isoformat(),
        req_id=req.id,
        func_name=func_name,
        req_text=req.text,
    )
