"""Validate the machine-readable lineage spine for public metrics."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINEAGE = ROOT / "reports" / "WEBSITE_METRIC_LINEAGE.csv"
shared = json.loads((ROOT / "website" / "data" / "shared-summary.json").read_text(encoding="utf-8"))
required = {"metric_id", "public_label", "source_path", "source_field", "source_sha256", "source_git_sha", "unit", "precision", "transform", "consumers", "claim_class", "tolerance"}
with LINEAGE.open(encoding="utf-8", newline="") as fh:
    reader = csv.DictReader(fh)
    rows = list(reader)
    fields = set(reader.fieldnames or [])
errors = []
if fields != required:
    errors.append(f"lineage columns mismatch: {sorted(fields)}")
ids = [row.get("metric_id", "") for row in rows]
if len(ids) != len(set(ids)):
    errors.append("duplicate metric_id")
for row in rows:
    if not row.get("public_label") or not row.get("source_field") or not row.get("consumers"):
        errors.append(f"incomplete lineage row {row.get('metric_id')}")
    if row.get("source_git_sha") != "current_commit":
        errors.append(f"{row.get('metric_id')} must use current_commit marker")
    if row.get("source_sha256") != "computed_at_validation":
        errors.append(f"{row.get('metric_id')} must use computed_at_validation marker")
    if not (ROOT / row.get("source_path", "")).exists():
        errors.append(f"{row.get('metric_id')} source path missing: {row.get('source_path')}")
shared_ids = set(shared.get("metricIds", []))
if not shared_ids.issubset(set(ids)):
    errors.append(f"shared metrics missing lineage: {sorted(shared_ids - set(ids))}")
if errors:
    print("Metric lineage validation FAILED")
    print("\n".join(f"- {item}" for item in errors))
    raise SystemExit(1)
print(f"Metric lineage validation PASS: {len(rows)} metrics; sources resolve in repository")
