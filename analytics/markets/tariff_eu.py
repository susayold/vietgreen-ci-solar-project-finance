"""EU: Eurostat non-household consumption-band tariff selection."""
BANDS=[(0,20000,"IA"),(20000,500000,"IB"),(500000,2000000,"IC"),(2000000,20000000,"ID"),(20000000,70000000,"IE"),(70000000,150000000,"IF"),(150000000,float("inf"),"IG")]
from .common import base_cost,curve
def band_for_load(load_kwh):
    for low,high,band in BANDS:
        if low<=float(load_kwh)<high:return band
    return "IG"
def customer_energy_cost(project,market_data):
    out=base_cost(project,market_data,project.get("annual_load_kwh",0));out["eurostat_band"]=band_for_load(project.get("annual_load_kwh",0));out["tax_treatment"]=market_data.get("tax_treatment","EXCLUDING_RECOVERABLE_TAXES");return out
def build_avoided_cost_curve(project,market_data,annual_load_kwh,years=5): return curve(project,market_data,annual_load_kwh,years)
def apply_network_charges(project,market_data,energy_kwh): return float(market_data.get("network_charge",0) or 0)*float(energy_kwh)
def apply_open_access_charges(project,market_data,energy_kwh): return 0.0
def tax_schedule(project,market_data,taxable_income): return max(0,float(taxable_income))*float(market_data.get("tax_rate",.25))
def debt_benchmark(project,market_data): return dict(market_data.get("debt_pack",{}),base_index_type="ECB_MRO")
def fx_context(project,market_data): return dict(market_data.get("fx_pack",{}),rate_type="ECB_REFERENCE")
