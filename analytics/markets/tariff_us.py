"""US: EIA state/sector tariff fallback with explicit scope."""
from .common import base_cost,curve
def customer_energy_cost(project,market_data):
    if not market_data.get("state") and market_data.get("fallback_level")!="NATIONAL_CONTEXT": raise ValueError("US state/utility or explicit fallback required")
    return base_cost(project,market_data,project.get("annual_load_kwh",0))|{"fallback_level":market_data.get("fallback_level","STATE_SECTOR")}
def build_avoided_cost_curve(project,market_data,annual_load_kwh,years=5): return curve(project,market_data,annual_load_kwh,years)
def apply_network_charges(project,market_data,energy_kwh): return float(market_data.get("network_charge",0) or 0)*float(energy_kwh)
def apply_open_access_charges(project,market_data,energy_kwh): return 0.0
def tax_schedule(project,market_data,taxable_income): return max(0,float(taxable_income))*float(market_data.get("tax_rate",.26))
def debt_benchmark(project,market_data): return dict(market_data.get("debt_pack",{}),base_index_type="US_TREASURY_PLUS_SPREAD")
def fx_context(project,market_data): return dict(market_data.get("fx_pack",{}),rate_type="USD_REPORTING")
