import re
from dataclasses import dataclass

_REQ_LINE = re.compile(r"^-\s*(REQ-\d+):\s*(.+)$")


@dataclass(frozen=True)
class Requirement:
    id: str
    text: str


def parse_srs(markdown: str) -> list[Requirement]:
    requirements = []
    for line in markdown.splitlines():
        match = _REQ_LINE.match(line.strip())
        if match:
            requirements.append(Requirement(id=match.group(1), text=match.group(2).strip()))
    return requirements
