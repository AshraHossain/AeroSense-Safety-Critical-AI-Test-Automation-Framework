import csv
import re
from pathlib import Path

from src.requirements_parser.parser import Requirement

_MARKER = re.compile(r'@pytest\.mark\.requirement\("(REQ-\d+)"\)')
_FUNC = re.compile(r"^def (test_\w+)\(")


def scan_test_tags(test_dir: Path) -> dict[str, list[str]]:
    tags: dict[str, list[str]] = {}
    for test_file in sorted(Path(test_dir).glob("**/*.py")):
        lines = test_file.read_text().splitlines()
        pending_req = None
        for line in lines:
            marker = _MARKER.search(line)
            if marker:
                pending_req = marker.group(1)
                continue
            func = _FUNC.match(line.strip())
            if func and pending_req:
                tags.setdefault(pending_req, []).append(func.group(1))
                pending_req = None
    return tags


def build_rtm(requirements: list[Requirement], test_tags: dict[str, list[str]]) -> list[dict]:
    rows = []
    for req in requirements:
        tests = test_tags.get(req.id, [])
        rows.append({
            "requirement_id": req.id,
            "requirement_text": req.text,
            "tests": tests,
            "coverage": "covered" if tests else "uncovered",
        })
    return rows


def export_csv(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["requirement_id", "requirement_text", "tests", "coverage"])
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "tests": ";".join(row["tests"])})
