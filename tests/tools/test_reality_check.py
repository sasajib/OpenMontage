"""Contract tests for tools.analysis.reality_check (no models needed for the pure helpers)."""
from tools.analysis.reality_check import RealityCheck


def test_verdict_levels():
    v = RealityCheck._verdict
    assert v([]) == "PASS"
    assert v([{"severity": "minor"}]) == "PASS"
    assert v([{"severity": "major"}]) == "REVIEW"
    assert v([{"severity": "minor"}, {"severity": "critical"}]) == "REJECT"


def test_markdown_report_lists_findings():
    md = RealityCheck._markdown({"input": "x.mp4", "frames": 3, "verdict": "REJECT", "seconds": 1.0,
                                 "findings": [{"frame": 1, "category": "continuity", "severity": "critical", "note": "face drifts"}],
                                 "anatomy": {}, "identity": {}, "continuity": {}, "camera": {}, "vlm": {"skipped": True}})
    assert "REJECT" in md and "face drifts" in md


def test_schema_and_cost():
    t = RealityCheck()
    assert "input_path" in t.input_schema["required"]
    assert t.estimate_cost({"vlm": False}) == 0.0
    assert t.estimate_cost({"vlm": True}) > 0
