from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from src.requirements_parser.parser import parse_srs
from src.rtm_builder.builder import build_rtm, scan_test_tags
from src.test_generator.generator import generate_test_stub

app = FastAPI(title="AeroSense-TestForge MCP Server")


class GenerateTestsRequest(BaseModel):
    srs_markdown: str
    model: str
    confidence: float


class RTMRequest(BaseModel):
    srs_markdown: str
    test_dir: str


@app.post("/generate-tests")
def generate_tests(req: GenerateTestsRequest):
    requirements = parse_srs(req.srs_markdown)
    stubs = [generate_test_stub(r, model=req.model, confidence=req.confidence) for r in requirements]
    return {"stubs": stubs}


@app.post("/rtm")
def rtm(req: RTMRequest):
    requirements = parse_srs(req.srs_markdown)
    tags = scan_test_tags(Path(req.test_dir))
    return {"rtm": build_rtm(requirements, tags)}


@app.post("/coverage")
def coverage(req: RTMRequest):
    requirements = parse_srs(req.srs_markdown)
    tags = scan_test_tags(Path(req.test_dir))
    rows = build_rtm(requirements, tags)
    covered = sum(1 for r in rows if r["coverage"] == "covered")
    ratio = covered / len(rows) if rows else 0.0
    return {"coverage_ratio": ratio, "covered": covered, "total": len(rows)}
