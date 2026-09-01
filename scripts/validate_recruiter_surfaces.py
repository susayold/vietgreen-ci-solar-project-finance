"""Fail-closed cross-artifact reconciliation for V4.1.3 recruiter surfaces."""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "release" / "MODEL_RELEASE_MANIFEST.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
SHARED_PATH = ROOT / "website" / "data" / "shared-summary.json"
RECONCILIATION_PATH = ROOT / "validation" / "RECRUITER_SURFACE_RECONCILIATION.csv"

SURFACES = [
    ROOT / "README.md",
    ROOT / "EXECUTIVE_SUMMARY.md",
    ROOT / "BUSINESS_CASE.md",
    ROOT / "reports" / "RECRUITER_PACKAGE.md",
    ROOT / "reports" / "CV_BULLETS_V4.md",
    ROOT / "reports" / "INVESTMENT_COMMITTEE_MEMO.md",
    ROOT / "reports" / "LENDER_CREDIT_MEMO.md",
    ROOT / "reports" / "WEBSITE_CONTENT_MAP.md",
    ROOT / "reports" / "WEBSITE_QA_REPORT.md",
    ROOT / "reports" / "WEBSITE_RELEASE_MANIFEST.json",
    ROOT / "release" / "MODEL_RELEASE_MANIFEST.json",
    ROOT / "validation" / "OPEN_EXTERNAL_GATES.csv",
    ROOT / "validation" / "V4_READINESS_STATE.csv",
    SHARED_PATH,
]
SURFACES.extend(path for path in (ROOT / "website").rglob("*") if path.is_file())
OLD_CLAIMS = (
    "11 selected",
    "13.10 mwp",
    "138.143294",
    "152.457008",
    "-66.202345",
    "model/vietgreen_core_model.xlsx",
    "fixedVsResized",
    '"resized"',
)
DOC_STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "EXECUTIVE_SUMMARY.md",
    ROOT / "BUSINESS_CASE.md",
    ROOT / "reports" / "RECRUITER_PACKAGE.md",
    ROOT / "reports" / "CV_BULLETS_V4.md",
    ROOT / "reports" / "INVESTMENT_COMMITTEE_MEMO.md",
    ROOT / "reports" / "LENDER_CREDIT_MEMO.md",
    ROOT / "reports" / "RECRUITER_SURFACE_RECONCILIATION.md",
]
COMMON_STATUS = (
    "CURRENT_TERMS_DECISION=NO_DEPLOYMENT",
    "SELECTED_COUNT=4",
    "SELECTED_IDS=VG-005|VG-010|VG-011|VG-012",
    "RECRUITER_READY=TRUE",
    "TRANSACTION_EVIDENCE_STATUS=OPEN",
    "BANKABLE_TRANSACTION_READY=FALSE",
    "EXTERNAL_GATE_COUNT_OPEN=8",
)
NUMERIC_METRICS = {
    "selected_equity_bvnd": 0.000001,
    "selected_debt_bvnd": 0.000001,
    "selected_cfads_bvnd": 0.000001,
    "base_equity_npv_bvnd": 0.000001,
    "p90_equity_npv_bvnd": 0.000001,
    "pooled_min_dscr": 0.001,
}
def normalise(value: object) -> str:
    return str(value).strip().upper().replace(" ", "")
def parse_assignment(text: str, key: str) -> str | None:
    match = re.search(rf"(?mi)^\s*{re.escape(key)}\s*=\s*([^\r\n]+)", text)
    return match.group(1).strip() if match else None
def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")
def expected_values() -> dict[str, str]:
    scenario = MANIFEST["scenario_summary"]
    return {
        "current_terms_decision": str(MANIFEST["current_terms_decision"]),
        "selected_count": str(MANIFEST["selected_count"]),
        "selected_ids": "|".join(MANIFEST["selected_ids"]),
        "recruiter_ready": str(MANIFEST["recruiter_ready"]).upper(),
        "transaction_evidence_status": str(MANIFEST["transaction_evidence_status"]),
        "bankable_transaction_ready": str(MANIFEST["bankable_transaction_ready"]).upper(),
        "negotiated_case_type": "HYPOTHETICAL",
        "selected_equity_bvnd": "30.124825",
        "selected_debt_bvnd": "55.946104",
        "selected_cfads_bvnd": "12.003384",
        "pooled_min_dscr": "1.300",
        "base_equity_npv_bvnd": f"{float(scenario['base_equity_npv_bvnd']):.6f}",
        "p90_equity_npv_bvnd": f"{float(scenario['p90_equity_npv_bvnd']):.6f}",
    }
KEYS = {
    "current_terms_decision": "CURRENT_TERMS_DECISION",
    "selected_count": "SELECTED_COUNT",
    "selected_ids": "SELECTED_IDS",
    "recruiter_ready": "RECRUITER_READY",
    "transaction_evidence_status": "TRANSACTION_EVIDENCE_STATUS",
    "bankable_transaction_ready": "BANKABLE_TRANSACTION_READY",
    "negotiated_case_type": "NEGOTIATED_CASE_TYPE",
    "selected_equity_bvnd": "SELECTED_EQUITY_BVND",
    "selected_debt_bvnd": "SELECTED_DEBT_BVND",
    "selected_cfads_bvnd": "SELECTED_CFADS_Y1_BVND",
    "pooled_min_dscr": "POOLED_MIN_DSCR",
    "base_equity_npv_bvnd": "BASE_EQUITY_NPV_BVND",
    "p90_equity_npv_bvnd": "P90_EQUITY_NPV_BVND",
}
def extract_surface_value(surface: str, metric_id: str) -> str | None:
    path = ROOT / surface
    if surface == "website/data/shared-summary.json":
        shared = json.loads(load_text(path))
        shared_map = {
            "selected_count": shared.get("selectedProjects"),
            "selected_ids": "|".join(shared.get("selectedProjectIds", [])),
            "current_terms_decision": shared.get("currentDecision"),
        }
        value = shared_map.get(metric_id)
        return None if value is None else str(value).upper() if isinstance(value, bool) else str(value)
    key = KEYS.get(metric_id)
    if key is None or not path.exists():
        return None
    return parse_assignment(load_text(path), key)
EXPECTED_ROWS = [
    ("README.md", "current_terms_decision"),
    ("README.md", "selected_count"),
    ("README.md", "selected_ids"),
    ("README.md", "recruiter_ready"),
    ("README.md", "transaction_evidence_status"),
    ("README.md", "bankable_transaction_ready"),
    ("README.md", "selected_equity_bvnd"),
    ("EXECUTIVE_SUMMARY.md", "current_terms_decision"),
    ("EXECUTIVE_SUMMARY.md", "selected_count"),
    ("EXECUTIVE_SUMMARY.md", "selected_equity_bvnd"),
    ("EXECUTIVE_SUMMARY.md", "selected_debt_bvnd"),
    ("BUSINESS_CASE.md", "current_terms_decision"),
    ("BUSINESS_CASE.md", "negotiated_case_type"),
    ("BUSINESS_CASE.md", "selected_count"),
    ("reports/CV_BULLETS_V4.md", "selected_count"),
    ("reports/CV_BULLETS_V4.md", "base_equity_npv_bvnd"),
    ("reports/CV_BULLETS_V4.md", "p90_equity_npv_bvnd"),
    ("reports/INVESTMENT_COMMITTEE_MEMO.md", "selected_debt_bvnd"),
    ("reports/INVESTMENT_COMMITTEE_MEMO.md", "selected_cfads_bvnd"),
    ("reports/INVESTMENT_COMMITTEE_MEMO.md", "pooled_min_dscr"),
    ("reports/LENDER_CREDIT_MEMO.md", "selected_debt_bvnd"),
    ("reports/LENDER_CREDIT_MEMO.md", "pooled_min_dscr"),
    ("reports/LENDER_CREDIT_MEMO.md", "bankable_transaction_ready"),
    ("website/data/shared-summary.json", "selected_count"),
    ("website/data/shared-summary.json", "selected_ids"),
    ("website/data/shared-summary.json", "current_terms_decision"),
]
errors: list[str] = []
missing_surfaces = 0
for path in SURFACES:
    if not path.exists():
        errors.append(f"missing surface: {path.relative_to(ROOT)}")
        missing_surfaces += 1
    else:
        text = load_text(path).lower()
        for claim in OLD_CLAIMS:
            if claim.lower() in text:
                errors.append(f"stale claim {claim}: {path.relative_to(ROOT)}")
for path in DOC_STATUS_SURFACES:
    text = load_text(path)
    for token in COMMON_STATUS:
        if token not in text:
            errors.append(f"{path.relative_to(ROOT)} missing status invariant {token}")
if not RECONCILIATION_PATH.exists():
    errors.append("missing validation/RECRUITER_SURFACE_RECONCILIATION.csv")
    rows = []
else:
    with RECONCILIATION_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
expected = expected_values()
expected_keys = set(EXPECTED_ROWS)
actual_keys = {(row.get("surface", ""), row.get("metric_id", "")) for row in rows}
missing_metrics = len(expected_keys - actual_keys)
if missing_metrics:
    errors.append(f"reconciliation missing {missing_metrics} required metric rows")
if len(actual_keys) != len(rows):
    errors.append("reconciliation contains duplicate surface/metric rows")
for row in rows:
    key = (row.get("surface", ""), row.get("metric_id", ""))
    if key not in expected_keys:
        errors.append(f"unexpected reconciliation row: {key}")
        continue
    metric_id = row["metric_id"]
    authoritative = expected[metric_id]
    surface_value = row.get("surface_value", "")
    actual = extract_surface_value(row["surface"], metric_id)
    tolerance = float(row.get("tolerance", "0")) if metric_id in NUMERIC_METRICS else 0.0
    try:
        if metric_id in NUMERIC_METRICS:
            matches = math.isfinite(float(authoritative)) and math.isfinite(float(surface_value)) and math.isfinite(float(actual or "nan")) and abs(float(surface_value) - float(authoritative)) <= tolerance and abs(float(actual or "nan") - float(authoritative)) <= tolerance
        else:
            matches = normalise(authoritative) == normalise(surface_value) == normalise(actual)
    except (TypeError, ValueError):
        matches = False
    if row.get("authoritative_value") != authoritative:
        matches = False
    if row.get("status", "").upper() != "PASS":
        matches = False
    if not matches:
        errors.append(f"reconciliation mismatch: {row['surface']} / {metric_id} (actual={actual!r}, row={surface_value!r}, authoritative={authoritative!r})")
claim_boundary_conflicts = 0
for path in DOC_STATUS_SURFACES + [MANIFEST_PATH, SHARED_PATH]:
    text = load_text(path).upper()
    if "BANKABLE_TRANSACTION_READY=TRUE" in text or '"BANKABLE_TRANSACTION_READY": TRUE' in text or '"BANKABLETRANSACTIONREADY": TRUE' in text:
        claim_boundary_conflicts += 1
        errors.append(f"claim boundary conflict: {path.relative_to(ROOT)}")
if errors:
    print("Recruiter surface reconciliation FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)
print(f"Recruiter surface reconciliation PASS: rows_failed=0; missing_surfaces={missing_surfaces}; missing_metrics={missing_metrics}; claim_boundary_conflicts={claim_boundary_conflicts}; rows={len(rows)}")
