import csv, json
from pathlib import Path
from analytics.physical_sanity import classify_specific_yield

ROOT=Path(__file__).resolve().parents[1]

def _rows(rel):
    with (ROOT/rel).open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def test_classifier_missing_data_fails_closed():
    assert classify_specific_yield(None)=="INSUFFICIENT_PHYSICAL_DATA"

def test_classifier_low_yield_review():
    assert classify_specific_yield(899.99)=="LOW_YIELD_REVIEW"

def test_classifier_lower_boundary_passes():
    assert classify_specific_yield(900)=="PASS_WITHIN_SCREENING_BAND"

def test_classifier_upper_boundary_passes():
    assert classify_specific_yield(1600)=="PASS_WITHIN_SCREENING_BAND"

def test_classifier_high_yield_review():
    assert classify_specific_yield(1600.01)=="HIGH_YIELD_REVIEW"

def test_classifier_extreme_threshold_is_strict():
    assert classify_specific_yield(3200)=="HIGH_YIELD_REVIEW"
    assert classify_specific_yield(3200.01)=="EXTREME_OUTLIER_BLOCK_BASE"

def test_selected_physical_count_and_status_enum():
    rows=_rows("validation/V5_1_2_PHYSICAL_QA.csv")
    assert len(rows)==20
    assert {r["physical_status"] for r in rows} <= {"PASS_WITHIN_SCREENING_BAND","LOW_YIELD_REVIEW","HIGH_YIELD_REVIEW","EXTREME_OUTLIER_BLOCK_BASE","INSUFFICIENT_PHYSICAL_DATA"}

def test_arisudhana_is_preserved_but_blocked():
    row=next(r for r in _rows("validation/V5_1_2_PHYSICAL_QA.csv") if r["project_id"]=="IN-FPEL-ARISUDHANA")
    assert row["observed_generation_kwh"]=="30500000.0"
    assert row["physical_status"]=="EXTREME_OUTLIER_BLOCK_BASE"
    assert row["base_generation_p50_kwh"]==""
    assert row["model_input_status"]=="TECHNICAL_DATA_BLOCKED"
    assert row["observed_base_case_eligible"]=="FALSE"

def test_economics_ready_count_is_nineteen():
    rows=_rows("validation/V5_1_2_PHYSICAL_QA.csv")
    assert sum(r["model_input_status"]=="READY_FOR_ECONOMICS" for r in rows)==19

def test_resolved_view_contains_provenance():
    rows=_rows("outputs/v5_1_2_model_input_view.csv")
    assert len(rows)==20
    assert {"base_generation_p50_kwh","base_generation_origin","input_ready_status"} <= set(rows[0])
    blocked=next(r for r in rows if r["project_id"]=="IN-FPEL-ARISUDHANA")
    assert blocked["input_ready_status"]=="TECHNICAL_DATA_BLOCKED"
