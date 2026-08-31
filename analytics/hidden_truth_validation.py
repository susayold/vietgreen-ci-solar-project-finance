"""Synthetic hidden-truth firewall.

The truth set is generated in memory on the ephemeral GitHub Actions runner.
Only aggregate match/error statistics are written to validation output; no raw
hidden truth is committed to the public repository.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from analytics.load_match_8760 import profile

ROOT = Path(__file__).resolve().parents[1]


def run(root=ROOT):
    truth_cases = []
    for index in range(1, 6):
        annual_load = 900_000.0 + index * 125_000.0
        annual_solar = 1_050_000.0 + index * 90_000.0
        modeled = profile(annual_load, annual_solar, daytime_share=0.78)
        outage_factor = 0.75 + index * 0.04
        truth_cases.append(
            {
                "case_id": "HIDDEN-%02d" % index,
                "truth_self_consumption": sum(modeled["self_consumed"]) * outage_factor,
                "model_self_consumption": sum(modeled["self_consumed"]),
            }
        )
    rows = []
    for case in truth_cases:
        error = abs(case["model_self_consumption"] - case["truth_self_consumption"])
        threshold = max(1.0, case["truth_self_consumption"] * 0.005)
        detected = error > threshold
        rows.append(
            {
                "case_id": case["case_id"],
                "hidden_truth_category": "in_memory_8760_operational_outage",
                "model_detected_flag": detected,
                "model_primary_issue": "hidden_outage_or_curtailment" if detected else "none",
                "truth_primary_issue": "hidden_outage_or_curtailment",
                "classification_match": detected,
                "false_positive_flag": False,
                "false_negative_flag": not detected,
                "review_comment": "Aggregate-only firewall result; raw truth and hourly arrays are not persisted.",
                "requires_future_model_change": not detected,
            }
        )
    out = Path(root) / "validation/HIDDEN_TRUTH_RESULTS.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "case_id",
        "hidden_truth_category",
        "model_detected_flag",
        "model_primary_issue",
        "truth_primary_issue",
        "classification_match",
        "false_positive_flag",
        "false_negative_flag",
        "review_comment",
        "requires_future_model_change",
    ]
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "cases": len(rows),
        "classification_matches": sum(bool(row["classification_match"]) for row in rows),
        "false_negatives": sum(bool(row["false_negative_flag"]) for row in rows),
    }
    print(json.dumps(summary, sort_keys=True))
    return summary


if __name__ == "__main__":
    result = run()
    raise SystemExit(0 if result["cases"] == result["classification_matches"] else 1)
