import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def _rows(rel):
    with (ROOT/rel).open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def _scenario(sid):
    return [r for r in _rows("outputs/v5_1_2_scenarios.csv") if r["scenario_id"]==sid]

def test_scenario_row_count():
    assert len(_rows("outputs/v5_1_2_scenarios.csv"))==19*9

def test_policy_debt_modes_are_explicit():
    modes={r["scenario_id"]:r["debt_mode"] for r in _rows("config/v5_1_2_scenario_policy.csv")}
    assert modes=={"BASE":"RESIZED_DEBT","P90_ENERGY":"FIXED_CONTRACTUAL_SCHEDULE","CAPEX_OVERRUN":"NO_NEW_DEBT","INTEREST_RATE_SHOCK":"FIXED_CONTRACTUAL_SCHEDULE","COD_DELAY":"FIXED_CONTRACTUAL_SCHEDULE","OPEX_INFLATION":"FIXED_CONTRACTUAL_SCHEDULE","OFFTAKER_NONPAYMENT":"FIXED_CONTRACTUAL_SCHEDULE","OFFTAKER_TERMINATION":"NO_NEW_DEBT","COMBINED_DOWNSIDE":"NO_NEW_DEBT"}

def test_p90_does_not_resize_debt():
    for r in _scenario("P90_ENERGY"):
        assert r["debt_mode"]=="FIXED_CONTRACTUAL_SCHEDULE"
        assert abs(float(r["debt_capacity_change_local"]))<1e-7
        assert r["principal_schedule_preserved"]=="TRUE"

def test_capex_overrun_has_no_additional_debt():
    for r in _scenario("CAPEX_OVERRUN"):
        assert r["debt_mode"]=="NO_NEW_DEBT"
        assert abs(float(r["additional_debt_local"]))<1e-7
        assert float(r["equity_funded_incremental_capex_local"])>0
        assert r["no_new_debt_increase"]=="TRUE"

def test_termination_has_no_additional_debt():
    for r in _scenario("OFFTAKER_TERMINATION"):
        assert r["debt_mode"]=="NO_NEW_DEBT"
        assert abs(float(r["additional_debt_local"]))<1e-7

def test_combined_downside_has_no_additional_debt():
    for r in _scenario("COMBINED_DOWNSIDE"):
        assert r["debt_mode"]=="NO_NEW_DEBT"
        assert abs(float(r["additional_debt_local"]))<1e-7

def test_floating_rate_reprices_interest_only():
    for r in _scenario("INTEREST_RATE_SHOCK"):
        assert r["debt_mode"]=="FIXED_CONTRACTUAL_SCHEDULE"
        assert r["principal_schedule_preserved"]=="TRUE"
        assert r["interest_schedule_changed"]=="TRUE"

def test_cod_delay_shifts_first_operating_year():
    for r in _scenario("COD_DELAY"):
        assert r["debt_mode"]=="FIXED_CONTRACTUAL_SCHEDULE"
        assert r["first_operating_year"]=="2"
        assert float(r["year_1_revenue_local"])==0
        assert float(r["year_1_depreciation_local"])==0

def test_opex_inflation_keeps_contractual_schedule():
    for r in _scenario("OPEX_INFLATION"):
        assert r["debt_mode"]=="FIXED_CONTRACTUAL_SCHEDULE"
        assert r["principal_schedule_preserved"]=="TRUE"

def test_nonpayment_keeps_contractual_schedule():
    for r in _scenario("OFFTAKER_NONPAYMENT"):
        assert r["debt_mode"]=="FIXED_CONTRACTUAL_SCHEDULE"
        assert r["principal_schedule_preserved"]=="TRUE"

def test_all_scenarios_have_reference_boundary():
    assert all(r["reference_case"]=="SCENARIO_REFERENCE_NOT_ACTUAL_PPA" for r in _rows("outputs/v5_1_2_scenarios.csv"))
