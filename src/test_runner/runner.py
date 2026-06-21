import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_junit_xml(path: Path) -> dict[str, str]:
    tree = ET.parse(path)
    results = {}
    for case in tree.getroot().iter("testcase"):
        name = case.get("name")
        results[name] = "failed" if case.find("failure") is not None else "passed"
    return results


def run_suite(*, target_dir: Path, junit_path: Path) -> dict[str, str]:
    subprocess.run(
        [sys.executable, "-m", "pytest", str(target_dir), f"--junitxml={junit_path}", "-q"],
        capture_output=True,
    )
    return parse_junit_xml(junit_path)
