import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "website" / "public" / "data"

def read(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

def test_cv_summary_is_frozen_and_governed():
    summary = read("summary.json")
    assert summary["modelSha"] == "ff69e15d211ff1abc88200574242ed2f1db49074"
    assert summary["modelFrozen"] is True
    assert summary["remoteOnly"] is True
    assert summary["decision"] == "INDETERMINATE_MISSING_COMMERCIAL_DATA"

def test_cv_universe_and_scenarios():
    projects = read("projects.json")["projects"]
    assert len(projects) == 20
    assert sum(p["economicsStatus"] == "READY_FOR_ECONOMICS" for p in projects) == 19
    assert len(read("risk.json")["scenarios"]) == 171

def test_featured_case_claim_boundary():
    economics = read("economics.json")
    frontier = economics["featuredFrontier"]
    assert economics["featured"]["projectId"] == "VN-GY-GOMALL"
    assert frontier["status"] == "EMPTY_NEGOTIATION_ZONE"
    assert economics["featured"]["referenceCase"] == "REFERENCE_CASE_NOT_ACTUAL_PPA"
