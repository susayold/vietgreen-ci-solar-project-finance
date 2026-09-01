import csv
from pathlib import Path

def test_sponsor_floor_is_leveraged_equity_npv_at_equity_hurdle():
    with Path("outputs/v5_1_1_project_economics.csv").open(encoding="utf-8", newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==20
    assert {r["sponsor_target_metric"] for r in rows}=={"LEVERAGED_EQUITY_NPV_AT_EQUITY_HURDLE"}
    assert all(r["sponsor_solver_status"] in {"SOLVED","SOLVED_AT_ZERO","INSUFFICIENT_DATA"} for r in rows)
    assert any(r["sponsor_floor_local_per_kwh"] not in {"","0"} for r in rows)
