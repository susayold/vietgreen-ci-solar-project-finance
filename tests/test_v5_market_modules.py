from analytics.markets.tariff_india import customer_energy_cost
from analytics.markets.tariff_eu import band_for_load
from analytics.markets.tariff_singapore import customer_energy_cost as sg_cost
def test_india_requires_context(): assert customer_energy_cost({"project_id":"x","annual_load_kwh":100},{"energy_rate":7,"currency":"INR","state":"Tamil Nadu"})["currency"]=="INR"
def test_europe_band(): assert band_for_load(2500000)=="ID"
def test_singapore_reference(): assert sg_cost({"project_id":"x","annual_load_kwh":100},{"energy_rate":.3191,"currency":"SGD"})["tariff_status"]=="REFERENCE_AVOIDED_COST"
