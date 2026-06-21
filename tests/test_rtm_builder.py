import csv

from src.requirements_parser.parser import Requirement
from src.rtm_builder.builder import build_rtm, export_csv, scan_test_tags


def test_scan_test_tags_finds_requirement_markers(tmp_path):
    test_file = tmp_path / "test_sample.py"
    test_file.write_text(
        '@pytest.mark.requirement("REQ-001")\n'
        "def test_req_001():\n    pass\n\n"
        '@pytest.mark.requirement("REQ-002")\n'
        "def test_req_002():\n    pass\n"
    )
    tags = scan_test_tags(tmp_path)
    assert tags == {"REQ-001": ["test_req_001"], "REQ-002": ["test_req_002"]}


def test_build_rtm_marks_covered_requirement():
    reqs = [Requirement(id="REQ-001", text="Log decisions")]
    tags = {"REQ-001": ["test_req_001"]}
    rows = build_rtm(reqs, tags)
    assert rows == [
        {"requirement_id": "REQ-001", "requirement_text": "Log decisions",
         "tests": ["test_req_001"], "coverage": "covered"}
    ]


def test_build_rtm_marks_uncovered_requirement():
    reqs = [Requirement(id="REQ-002", text="Escalate low confidence")]
    rows = build_rtm(reqs, {})
    assert rows[0]["coverage"] == "uncovered"
    assert rows[0]["tests"] == []


def test_export_csv_writes_header_and_rows(tmp_path):
    rows = [{"requirement_id": "REQ-001", "requirement_text": "x",
             "tests": ["test_req_001"], "coverage": "covered"}]
    out = tmp_path / "rtm.csv"
    export_csv(rows, out)
    with open(out, newline="") as f:
        reader = list(csv.DictReader(f))
    assert reader[0]["requirement_id"] == "REQ-001"
    assert reader[0]["coverage"] == "covered"
