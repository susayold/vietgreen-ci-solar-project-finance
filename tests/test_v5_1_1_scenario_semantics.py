from analytics.scenario_engine_v5 import apply_inputs

def test_fixed_debt_schedule_is_explicit():
    b={"debt_rate_type":"FLOATING_REFERENCE"}
    r=apply_inputs(b,{"scenario_id":"INTEREST_RATE_SHOCK"})
    assert r["debt_mode"]=="FIXED_DEBT_SCHEDULE"
    assert r["rate_delta"] > 0

def test_no_new_debt_cannot_increase():
    r=apply_inputs({},{"scenario_id":"OFFTAKER_TERMINATION"})
    assert r["debt_mode"]=="NO_NEW_DEBT"
    assert r["termination_year"]==2

def test_cod_delay_is_timing_not_energy_shock():
    r=apply_inputs({},{"scenario_id":"COD_DELAY"})
    assert r["cod_delay_years"]==1
    assert r["energy_factor"]==1.0
