import csv
from pathlib import Path

def test_lender_floor_uses_explicit_standardized_leverage_objective():
    with Path("outputs/v5_1_1_project_economics.csv").open(encoding="utf-8", newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==20
    assert {r["lender_target_metric"] for r in rows}=={"MINIMUM_TARIFF_SUPPORTING_TARGET_STANDARDIZED_LEVERAGE"}
    assert {r["lender_target_leverage"] for r in rows}=={"0.7"}
    assert all(r["lender_solver_status"] in {"SOLVED","SOLVED_AT_ZERO","INSUFFICIENT_DATA"} for r in rows)
