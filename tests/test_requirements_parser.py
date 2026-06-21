from src.requirements_parser.parser import Requirement, parse_srs


def test_parses_single_requirement():
    text = "- REQ-001: System shall log all AI decisions"
    reqs = parse_srs(text)
    assert reqs == [Requirement(id="REQ-001", text="System shall log all AI decisions")]


def test_parses_multiple_requirements():
    text = (
        "# SRS\n"
        "- REQ-001: First requirement\n"
        "- REQ-002: Second requirement\n"
    )
    reqs = parse_srs(text)
    assert [r.id for r in reqs] == ["REQ-001", "REQ-002"]


def test_ignores_non_requirement_lines():
    text = "# Title\nSome prose.\n- REQ-001: Valid one\n- Not a requirement line\n"
    reqs = parse_srs(text)
    assert len(reqs) == 1
    assert reqs[0].id == "REQ-001"


def test_empty_input_returns_empty_list():
    assert parse_srs("") == []


def test_strips_whitespace_from_text():
    text = "- REQ-003:   padded text   "
    reqs = parse_srs(text)
    assert reqs[0].text == "padded text"
