"""Singapore: EMA regulated tariff reference only."""
from .common import base_cost,curve
def customer_energy_cost(project,market_data):
    return base_cost(project,market_data,project.get("annual_load_kwh",0))|{"tariff_status":"REFERENCE_AVOIDED_COST","includes_gst":False}
def build_avoided_cost_curve(project,market_data,annual_load_kwh,years=5): return curve(project,market_data,annual_load_kwh,years)
def apply_network_charges(project,market_data,energy_kwh): return 0.0
def apply_open_access_charges(project,market_data,energy_kwh): return 0.0
def tax_schedule(project,market_data,taxable_income): return max(0,float(taxable_income))*float(market_data.get("tax_rate",.17))
def debt_benchmark(project,market_data): return dict(market_data.get("debt_pack",{}),base_index_type="REFERENCE")
def fx_context(project,market_data): return dict(market_data.get("fx_pack",{}),rate_type="REFERENCE")
