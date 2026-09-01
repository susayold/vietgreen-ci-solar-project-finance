"""Australia: AER/state/network reference."""
from .common import base_cost,curve
def customer_energy_cost(project,market_data):
    if market_data.get("tariff_scope")=="DMO" and market_data.get("customer_segment")!="LARGE_CI": raise ValueError("DMO cannot silently represent large C&I")
    return base_cost(project,market_data,project.get("annual_load_kwh",0))|{"tariff_scope":market_data.get("tariff_scope","STATE_RETAILER_REFERENCE")}
def build_avoided_cost_curve(project,market_data,annual_load_kwh,years=5): return curve(project,market_data,annual_load_kwh,years)
def apply_network_charges(project,market_data,energy_kwh): return float(market_data.get("network_charge",0) or 0)*float(energy_kwh)
def apply_open_access_charges(project,market_data,energy_kwh): return 0.0
def tax_schedule(project,market_data,taxable_income): return max(0,float(taxable_income))*float(market_data.get("tax_rate",.30))
def debt_benchmark(project,market_data): return dict(market_data.get("debt_pack",{}),base_index_type="RBA_REFERENCE")
def fx_context(project,market_data): return dict(market_data.get("fx_pack",{}),rate_type="REFERENCE")
