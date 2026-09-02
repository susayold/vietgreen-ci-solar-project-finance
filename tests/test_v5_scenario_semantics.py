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
    fixed_rows=[r for r in rows if r["debt_mode"]=="FIXED_DEBT_SCHEDULE"]
    assert all(r["base_debt_schedule_preserved"]=="TRUE" for r in fixed_rows)
    assert all(r["principal_schedule_preserved"]=="TRUE" for r in fixed_rows)
    p90=[r for r in rows if r["scenario_id"]=="P90_ENERGY"]
    assert all(float(r["year_1_generation_kwh"]) < float(r["base_year_1_generation_kwh"]) for r in p90)
    capex=[r for r in rows if r["scenario_id"]=="CAPEX_OVERRUN"]
    assert all(float(r["incremental_capex_local"]) > 0 for r in capex)
    combined=[r for r in rows if r["scenario_id"]=="COMBINED_DOWNSIDE"]
    assert all(float(r["equity_funded_incremental_capex_local"])==float(r["incremental_capex_local"]) for r in combined)
    rate=[r for r in rows if r["scenario_id"]=="INTEREST_RATE_SHOCK"]
    assert all(float(r["scenario_debt_interest_y1_local"]) >= float(r["base_debt_interest_y1_local"]) for r in rate)
    delayed=[r for r in rows if r["scenario_id"]=="COD_DELAY"]
    assert {r["first_operating_year"] for r in delayed}=={"2"}
    assert all(float(r["year_1_revenue_local"])==0 and float(r["year_2_revenue_local"])>0 for r in delayed)
    assert all(float(r["year_1_depreciation_local"])==0 and float(r["year_2_depreciation_local"])>0 for r in delayed)
    terminated=[r for r in rows if r["scenario_id"]=="OFFTAKER_TERMINATION"]
    assert all(float(r["year_2_revenue_local"])==0 for r in terminated)
    assert all(float(r["energy_factor"])==0.90 for r in combined)
    assert all(float(r["capex_factor"])>1 and float(r["rate_response"])>0 and int(r["cod_delay_years"])==1 for r in combined)
