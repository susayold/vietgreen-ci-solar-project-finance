"""V5.1.1 scenario semantics: schedules are explicit and auditable."""
from __future__ import annotations
from copy import deepcopy
from typing import Dict, Any

SCENARIO_RULES = {
    "BASE": {"debt_mode":"RESIZED_DEBT","energy_response":"NONE","capex_response":"NONE","rate_response":"NONE","timing_response":"NONE"},
    "P90_ENERGY": {"debt_mode":"FIXED_CONTRACTUAL_SCHEDULE","energy_response":"P90_ENERGY","capex_response":"NONE","rate_response":"NONE","timing_response":"NONE"},
    "CAPEX_OVERRUN": {"debt_mode":"NO_NEW_DEBT","energy_response":"NONE","capex_response":"CAPEX_UP","rate_response":"NONE","timing_response":"NONE"},
    "INTEREST_RATE_SHOCK": {"debt_mode":"FIXED_CONTRACTUAL_SCHEDULE","energy_response":"NONE","capex_response":"NONE","rate_response":"RATE_UP_IF_FLOATING","timing_response":"NONE"},
    "COD_DELAY": {"debt_mode":"FIXED_CONTRACTUAL_SCHEDULE","energy_response":"NONE","capex_response":"NONE","rate_response":"NONE","timing_response":"COD_DELAY"},
    "OPEX_INFLATION": {"debt_mode":"FIXED_CONTRACTUAL_SCHEDULE","energy_response":"NONE","capex_response":"NONE","rate_response":"NONE","timing_response":"NONE"},
    "OFFTAKER_NONPAYMENT": {"debt_mode":"FIXED_CONTRACTUAL_SCHEDULE","energy_response":"NONE","capex_response":"NONE","rate_response":"NONE","timing_response":"NONE"},
    "OFFTAKER_TERMINATION": {"debt_mode":"NO_NEW_DEBT","energy_response":"NONE","capex_response":"NONE","rate_response":"NONE","timing_response":"TERMINATION"},
    "COMBINED_DOWNSIDE": {"debt_mode":"NO_NEW_DEBT","energy_response":"P90_ENERGY","capex_response":"CAPEX_UP","rate_response":"RATE_UP_IF_FLOATING","timing_response":"COD_DELAY"},
}

def semantics(scenario_id: str, row: Dict[str, Any]|None=None) -> Dict[str, Any]:
    out=dict(SCENARIO_RULES.get(scenario_id, {})); out.update(row or {}); out["scenario_id"]=scenario_id
    out.setdefault("debt_mode","FIXED_CONTRACTUAL_SCHEDULE")
    return out

def apply_inputs(base: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    s=semantics(str(scenario.get("scenario_id",scenario.get("id","BASE"))), scenario)
    out=deepcopy(base)
    out["scenario_id"]=s["scenario_id"]; out["debt_mode"]=s["debt_mode"]
    out["energy_factor"]=float(s.get("energy_factor", 0.90 if s["energy_response"]=="P90_ENERGY" else 1.0))
    out["capex_factor"]=float(s.get("capex_factor", 1.15 if s["capex_response"]=="CAPEX_UP" else 1.0))
    out["rate_delta"]=float(s.get("rate_delta", 0.02 if s["rate_response"]=="RATE_UP_IF_FLOATING" else 0.0))
    out["cod_delay_years"]=int(s.get("cod_delay_years", 1 if s["timing_response"]=="COD_DELAY" else 0))
    out["opex_factor"]=float(s.get("opex_factor", 1.15 if s["scenario_id"]=="OPEX_INFLATION" else 1.0))
    out["collection_haircut"]=float(s.get("collection_haircut", 0.75 if s["scenario_id"]=="OFFTAKER_NONPAYMENT" else 1.0))
    out["termination_year"]=s.get("termination_year", 2 if s["timing_response"]=="TERMINATION" else None)
    return out
