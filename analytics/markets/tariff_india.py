"""India: state/DISCOM/open-access tariff module."""
from .common import base_cost,curve
def _validate(market_data):
    if not market_data.get("state") and not market_data.get("regulatory_archetype"): raise ValueError("India state/regulatory context required")
def customer_energy_cost(project,market_data):
    _validate(market_data); return base_cost(project,market_data,project.get("annual_load_kwh",0))|{"open_access_charges_required":bool(market_data.get("open_access",False))}
def build_avoided_cost_curve(project,market_data,annual_load_kwh,years=5): _validate(market_data); return curve(project,market_data,annual_load_kwh,years)
def apply_network_charges(project,market_data,energy_kwh): return sum(float(market_data.get(k,0) or 0)*float(energy_kwh) for k in ("wheeling_charge","transmission_charge","banking_charge"))
def apply_open_access_charges(project,market_data,energy_kwh): return sum(float(market_data.get(k,0) or 0)*float(energy_kwh) for k in ("cross_subsidy_surcharge","additional_surcharge"))
def tax_schedule(project,market_data,taxable_income): return max(0,float(taxable_income))*float(market_data.get("tax_rate",.25))
def debt_benchmark(project,market_data): return dict(market_data.get("debt_pack",{}),base_index_type="RBI_REPO")
def fx_context(project,market_data): return dict(market_data.get("fx_pack",{}),rate_type="ECB_REFERENCE_CROSS_RATE")
