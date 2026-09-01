import csv
from pathlib import Path
from analytics.scenario_engine_v5 import apply_inputs

def test_fixed_no_new_and_cod_delay_semantics_are_explicit():
    fixed=apply_inputs({"debt_rate_type":"FLOATING_REFERENCE"},{"scenario_id":"INTEREST_RATE_SHOCK"})
    assert fixed["debt_mode"]=="FIXED_DEBT_SCHEDULE"
    assert fixed["rate_delta"]>0
    no_new=apply_inputs({},{"scenario_id":"OFFTAKER_TERMINATION"})
    assert no_new["debt_mode"]=="NO_NEW_DEBT"
    assert no_new["termination_year"]==2
    delay=apply_inputs({},{"scenario_id":"COD_DELAY"})
    assert delay["cod_delay_years"]==1 and delay["energy_factor"]==1.0

def test_generated_scenario_rows_preserve_the_contract():
    with Path("outputs/v5_1_1_scenarios.csv").open(encoding="utf-8", newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==180
    assert all(r["no_new_debt_increase"]=="TRUE" for r in rows if r["debt_mode"]=="NO_NEW_DEBT")
    assert all(r["base_debt_schedule_preserved"]=="TRUE" for r in rows if r["debt_mode"]=="FIXED_DEBT_SCHEDULE")
    delayed=[r for r in rows if r["scenario_id"]=="COD_DELAY"]
    assert {r["first_operating_year"] for r in delayed}=={"2"}
