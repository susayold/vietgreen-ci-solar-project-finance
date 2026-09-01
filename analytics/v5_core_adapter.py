"""V5 public-data adapter into universal local-currency project inputs."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping
from .unit_currency import normalize_percent

@dataclass(frozen=True)
class MarketContext:
    country: str
    subnational_market: str
    currency: str
    tariff_scheme: str
    tax_pack: Mapping[str, Any]
    debt_pack: Mapping[str, Any]
    fx_pack: Mapping[str, Any]
    inflation_pack: Mapping[str, Any]
    regulatory_archetype: str

def _value(assumptions, name, default=None):
    row=assumptions.get(name,{})
    value=row.get("value",default)
    return default if value in (None,"") else value

def adapt_project(project, assumptions, market):
    capacity=float(project["installed_capacity_kwp"])
    generation=float(_value(assumptions,"annual_generation_kwh",project.get("annual_generation_kwh") or 0))
    ratio=float(_value(assumptions,"self_consumption_ratio",.85))
    return {
        "project_id":project["project_id"],"country":project["country"],"currency":market.currency,
        "capacity_kwp":capacity,"generation_p50_kwh":generation,"generation_p90_kwh":generation*.90,"generation_p99_kwh":generation*.85,
        "annual_load_kwh":float(_value(assumptions,"annual_customer_load_kwh",generation/max(ratio,.01))),
        "self_consumption_ratio":ratio,"capex_local":float(_value(assumptions,"project_cost_local",0)),
        "operating_horizon_years":int(float(_value(assumptions,"operating_horizon_years",25))),
        "ppa_tenor_years":int(float(_value(assumptions,"ppa_tenor_years",20))),
        "debt_tenor_years":int(float(_value(assumptions,"debt_tenor_years",15))),
        "tax_rate":normalize_percent(_value(assumptions,"tax_rate",.2)),
        "debt_rate":normalize_percent(_value(assumptions,"debt_all_in_rate",.08)),
        "opex_rate":normalize_percent(_value(assumptions,"opex_percent_of_capex",.015)),
        "customer_ceiling_local_per_kwh":float(_value(assumptions,"customer_ceiling_local_per_kwh",0)),
        "ppa_mode":str(_value(assumptions,"ppa_mode","FRONTIER_ONLY")),
        "load_evidence_level":str(_value(assumptions,"load_evidence_level","LEVEL_4_NOT_DISCLOSED")),
        "fx_to_usd":float(_value(assumptions,"fx_to_usd",1)),
        "project_discount_rate":normalize_percent(_value(assumptions,"project_discount_rate",.10)),
        "equity_hurdle_rate":normalize_percent(_value(assumptions,"equity_hurdle_rate",.14)),
        "customer_discount_rate":normalize_percent(_value(assumptions,"customer_discount_rate",.08)),
        "inflation_rate":normalize_percent(_value(assumptions,"inflation_rate",.02)),
        "ppa_escalation_rate":normalize_percent(_value(assumptions,"ppa_escalation_rate",.01)),
        "degradation_rate":normalize_percent(_value(assumptions,"degradation",.005)),
    }
