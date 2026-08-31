"""Validate the public website data contract against the V4 release."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "website" / "data"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


manifest = json.loads((ROOT / "release/MODEL_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
shared = json.loads((DATA / "shared-summary.json").read_text(encoding="utf-8"))
required = ["shared-summary.json", "overview.json", "case.json", "economics.json", "debt.json", "portfolio.json", "risk.json", "model.json", "evidence.json", "metadata.json"]
errors: list[str] = []

for filename in required:
    path = DATA / filename
    if not path.exists():
        errors.append(f"missing {filename}")
    else:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {filename}: {exc}")

if shared.get("releaseId") != manifest["release_id"]:
    errors.append("release id mismatch")
if shared.get("selectedProjectIds") != manifest["selected_ids"]:
    errors.append("selected project IDs mismatch")
for key, manifest_key in [("selectedProjects", "selected_count"), ("currentPositiveEquityNPV", "current_terms_positive_equity_npv_rows"), ("negotiatedPositiveEquityNPV", "negotiated_positive_equity_npv_rows")]:
    if shared.get(key) != manifest[manifest_key]:
        errors.append(f"{key} mismatch")
if shared.get("currentDecision") != "NO_DEPLOYMENT":
    errors.append("current decision must be NO_DEPLOYMENT")
if shared.get("transactionEvidenceStatus") != "OPEN" or shared.get("bankableTransactionReady") is not False:
    errors.append("evidence boundary mismatch")

exposure = read_csv(ROOT / "outputs/portfolio_exposure_v4.csv")
selected = [row for row in exposure if row.get("selected_flag", "").lower() == "true"]
if {row["project_id"] for row in selected} != set(manifest["selected_ids"]):
    errors.append("exposure selected rows mismatch")
if len(selected) != manifest["selected_count"]:
    errors.append("selected count mismatch")

def total(field: str) -> float:
    return sum(float(row[field]) for row in selected)

if not math.isclose(total("equity_required_vnd") / 1e9, manifest["selected_equity_bvnd"], rel_tol=0, abs_tol=1e-6):
    errors.append("selected equity total mismatch")
if not math.isclose(total("debt_vnd") / 1e9, manifest["selected_debt_bvnd"], rel_tol=0, abs_tol=1e-6):
    errors.append("selected debt total mismatch")
if not math.isclose(total("cfads_y1_vnd") / 1e9, manifest["selected_cfads_y1_bvnd"], rel_tol=0, abs_tol=1e-6):
    errors.append("selected CFADS total mismatch")

phase2 = read_csv(ROOT / "outputs/scenario_summary_v4_phase2.csv")
if not any(row["scenario"] == "BASE_SPONSOR" and row["status"] == "PASS" for row in phase2):
    errors.append("base scenario missing or not PASS")
if not any(row["scenario"] == "COMBINED_DOWNSIDE" and row["status"] == "FAIL_DSCR" for row in phase2):
    errors.append("combined downside status not visible")

for path in DATA.glob("*.json"):
    text = path.read_text(encoding="utf-8").lower()
    for token in ("hidden_truth", "password", "localhost", "private_validation"):
        if token in text:
            errors.append(f"forbidden token {token} in {path.name}")
    try:
        parsed = json.loads(text)
        stack = [parsed]
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

if errors:
    print("Website data validation FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print(f"Website data validation PASS: {len(required)} JSON contracts; {len(selected)} selected projects; release {manifest['release_id']}")
