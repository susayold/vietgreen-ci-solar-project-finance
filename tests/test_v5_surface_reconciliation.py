import csv
from pathlib import Path

def test_current_surface_reconciliation_has_plan_schema_and_all_pass():
    path=Path("validation/V5_1_1_CURRENT_SURFACE_RECONCILIATION.csv")
    with path.open(encoding="utf-8", newline="") as f:
        reader=csv.DictReader(f); rows=list(reader)
    assert reader.fieldnames==["surface","metric_or_claim","authoritative_source","expected_value","actual_value","status"]
    assert len(rows)==10
    assert {r["status"] for r in rows}=={"PASS"}
    text="\n".join(Path(p).read_text(encoding="utf-8", errors="ignore") for p in [
        "README.md","EXECUTIVE_SUMMARY.md","BUSINESS_CASE.md",
        "reports/INVESTMENT_COMMITTEE_MEMO.md","reports/LENDER_CREDIT_MEMO.md",
        "reports/RECRUITER_PACKAGE.md","website/index.html"
    ])
    assert "V5.1.1" in text and "FRONTIER_ONLY" in text
    with Path("outputs/v5_1_1_energy.csv").open(encoding="utf-8", newline="") as f:
        energy=list(csv.DictReader(f))
    assert len(energy)==20
    for row in energy:
        p50=float(row["generation_p50_kwh_modeled"])
        p90=float(row["generation_p90_kwh"])
        p99=float(row["generation_p99_kwh"])
        assert p50 >= p90 >= p99 >= 0
        assert row["specific_yield_observed"] != "BLOCK"
