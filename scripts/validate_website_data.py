"""Fail-closed validation of the V4.1 recruiter website data contract."""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "website" / "data"
MANIFEST = json.loads((ROOT / "release/MODEL_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
REQUIRED = [
    "shared-summary.json", "overview.json", "case.json", "economics.json",
    "debt.json", "portfolio.json", "risk.json", "model.json", "evidence.json",
    "metadata.json", "release-meta.json",
]
errors: list[str] = []
payloads = {}

for filename in REQUIRED:
    path = DATA / filename
    if not path.exists():
        errors.append(f"missing {filename}")
        continue
    try:
        payloads[filename] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {filename}: {exc}")

shared = payloads.get("shared-summary.json", {})
expected_shared = {
    "releaseId": MANIFEST["release_id"],
    "selectedProjectIds": MANIFEST["selected_ids"],
    "selectedProjects": MANIFEST["selected_count"],
    "currentPositiveEquityNPV": MANIFEST["current_terms_positive_equity_npv_rows"],
    "negotiatedPositiveEquityNPV": MANIFEST["negotiated_positive_equity_npv_rows"],
    "currentDecision": "NO_DEPLOYMENT",
    "transactionEvidenceStatus": "OPEN",
    "bankableTransactionReady": False,
    "dataContractVersion": "V4.1-RECRUITER-CLOSURE",
}
for key, expected in expected_shared.items():
    if shared.get(key) != expected:
        errors.append(f"shared {key} mismatch: {shared.get(key)!r} != {expected!r}")
if len(shared.get("metricIds", [])) != len(set(shared.get("metricIds", []))):
    errors.append("shared metricIds are not unique")

meta = payloads.get("release-meta.json", {})
if meta.get("dataContractVersion") != "V4.1-RECRUITER-CLOSURE":
    errors.append("release metadata contract version mismatch")
expected_sha = os.environ.get("GITHUB_SHA")
if expected_sha and meta.get("gitSha") not in {expected_sha, "pending-ci"}:
    errors.append("release metadata gitSha does not match GITHUB_SHA")

risk = payloads.get("risk.json", {})
if "fixedVsResized" in risk:
    errors.append("risk contract still exposes fixedVsResized")
for row in risk.get("scenarios", []):
    required = {"economicStatus", "creditStatus", "readinessImpact", "sourceScenarioId"}
    missing = required - set(row)
    if missing:
        errors.append(f"scenario {row.get('scenario')} missing {sorted(missing)}")
    economic = "PASS" if float(row.get("equityNPVBVND", -1)) >= 0 else "NEGATIVE"
    credit = "PASS" if float(row.get("minDSCR", 0)) >= float(MANIFEST["pooled_min_dscr"]) else "FAIL_DSCR"
    if row.get("economicStatus") != economic:
        errors.append(f"scenario {row.get('scenario')} economicStatus is not derived from Equity NPV")
    if row.get("creditStatus") != credit:
        errors.append(f"scenario {row.get('scenario')} creditStatus is not derived from DSCR")
    if "status" in row:
        errors.append(f"scenario {row.get('scenario')} has ambiguous legacy status")

for path in DATA.glob("*.json"):
    text = path.read_text(encoding="utf-8").lower()
    for token in ("hidden_truth", "private_validation", "localhost", "password", "secret"):
        if token in text:
            errors.append(f"forbidden token {token} in {path.name}")
    try:
        value = json.loads(text)
        stack = [value]
        while stack:
            item = stack.pop()
            if isinstance(item, float) and not math.isfinite(item):
                errors.append(f"non-finite numeric value in {path.name}")
            elif isinstance(item, dict):
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
    except json.JSONDecodeError:
        pass
    if path.name != "release-meta.json":
        for date_value in re.findall(r"20\\d{2}-\\d{2}-\\d{2}", text):
            if date_value != MANIFEST["release_date"]:
                errors.append(f"unapproved date {date_value} in {path.name}")

if errors:
    print("Website data validation FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)
print(f"Website data validation PASS: {len(payloads)} JSON contracts; contract V4.1-RECRUITER-CLOSURE")
