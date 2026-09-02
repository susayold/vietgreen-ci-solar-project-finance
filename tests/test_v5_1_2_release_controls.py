import json
from pathlib import Path
from analytics.scan_v5_1_2_stale_content import scan

ROOT=Path(__file__).resolve().parents[1]

def test_static_manifest_has_no_runtime_identity():
    d=json.loads((ROOT/"release/MODEL_RELEASE_MANIFEST.json").read_text())
    flat=json.dumps(d)
    for marker in ("source_sha","workflow_run_id","artifact_id","artifact_digest","timestamp"):
        assert marker not in flat

def test_static_contract_is_remote_only_and_frontier_only():
    d=json.loads((ROOT/"release/V5_1_2_STATIC_RELEASE_CONTRACT.json").read_text())
    assert d["remote_only"] is True
    assert d["ppa_mode"]=="FRONTIER_ONLY"
    assert d["decision_boundary"]=="INDETERMINATE_MISSING_COMMERCIAL_DATA"

def test_current_content_has_truthful_boundary():
    assert "BANKABLE_TRANSACTION_READY=FALSE" in (ROOT/"reports/LENDER_CREDIT_MEMO.md").read_text()
    memo=(ROOT/"reports/INVESTMENT_COMMITTEE_MEMO.md").read_text().upper()
    assert "INVESTMENT APPROVAL" not in memo
    assert "INVEST=" not in memo

def test_stale_current_surface_scan_passes():
    assert scan(ROOT)==[]

def test_remote_only_is_explicit_in_data_contract():
    d=json.loads((ROOT/"artifacts/v5_1_2_surfaces/content_contract.json").read_text())
    assert d["remote_only"] is True

def test_red_team_report_has_evidence_lines():
    text=(ROOT/"validation/V5_1_2_RED_TEAM_REPORT.md").read_text()
    assert all(f"RT-{i:02d}" in text for i in range(1,21))
