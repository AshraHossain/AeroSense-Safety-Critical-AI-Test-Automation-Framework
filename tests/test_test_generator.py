from src.requirements_parser.parser import Requirement
from src.test_generator.generator import generate_test_stub


def test_stub_contains_requirement_marker():
    req = Requirement(id="REQ-001", text="System shall log AI decisions")
    stub = generate_test_stub(req, model="claude-sonnet-4-6", confidence=0.92)
    assert '@pytest.mark.requirement("REQ-001")' in stub


def test_stub_contains_ai_generated_header():
    req = Requirement(id="REQ-002", text="System shall escalate low confidence")
    stub = generate_test_stub(req, model="claude-sonnet-4-6", confidence=0.77)
    assert "# AI-GENERATED: confidence=0.77, model=claude-sonnet-4-6, timestamp=" in stub


def test_stub_function_name_derived_from_requirement_id():
    req = Requirement(id="REQ-003", text="Anything")
    stub = generate_test_stub(req, model="m", confidence=0.5)
    assert "def test_req_003(" in stub
