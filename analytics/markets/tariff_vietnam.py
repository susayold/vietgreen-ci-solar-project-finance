"""Vietnam: MOIT/EVN legal reference, with project billing status separated."""
from .common import base_cost,curve
def customer_energy_cost(project,market_data):
    if not market_data.get("customer_class"): raise ValueError("Vietnam customer class required")
    return base_cost(project,market_data,project.get("annual_load_kwh",0))|{"tariff_status":market_data.get("tariff_status","LEGAL_EFFECTIVE")}
def build_avoided_cost_curve(project,market_data,annual_load_kwh,years=5): return curve(project,market_data,annual_load_kwh,years)
def apply_network_charges(project,market_data,energy_kwh): return float(market_data.get("network_charge",0) or 0)*float(energy_kwh)
def apply_open_access_charges(project,market_data,energy_kwh): return 0.0
def tax_schedule(project,market_data,taxable_income): return max(0,float(taxable_income))*float(market_data.get("tax_rate",.2))
def debt_benchmark(project,market_data): return dict(market_data.get("debt_pack",{}),base_index_type="SBV_REFERENCE")
def fx_context(project,market_data): return dict(market_data.get("fx_pack",{}),rate_type="SBV_REFERENCE")
