import csv
from pathlib import Path

def _rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def test_selected_20_field_yield_and_observation_contract():
    master=_rows("data/public/project_master_real.csv")
    selected=[r for r in master if "SELECTED" in r["selection_status"]]
    assert len(master)==54
    assert len(selected)==20
    ids=[r["project_id"] for r in selected]
    assert len(ids)==len(set(ids))
    audit=_rows("validation/V5_1_1_SELECTED_PROJECT_DATA_AUDIT.csv")
    audited={r["project_id"] for r in audit}
    assert set(ids).issubset(audited)
    overlay=_rows("data/public/project_assumption_overlay.csv")
    overlay_ids={r["project_id"] for r in overlay}
    assert set(ids).issubset(overlay_ids)
    for row in selected:
        assert float(row["installed_capacity_kwp_observed"]) > 0
        assert float(row["annual_generation_kwh_observed"]) >= 0
    raw=_rows("data/public/raw_project_observations.csv")
    assert len(raw)==441

def test_arisudhana_is_preserved_but_fail_closed_for_review():
    rows=_rows("validation/V5_1_1_YIELD_SANITY_AUDIT.csv")
    ar=[r for r in rows if "ARISUDHANA" in r["project_id"].upper()]
    assert len(ar)==1
    assert ar[0]["audit_status"]=="PASS_WITH_DISCLOSED_HIGH_OUTLIER"
    assert ar[0]["engineering_review_required"]=="TRUE"
    assert ar[0]["base_case_treatment"]=="OBSERVED_SOURCE_CLAIM_WITH_ENGINEERING_REVIEW"
