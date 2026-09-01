"""Common arithmetic shared by explicit country market modules."""
def base_cost(project, market_data, annual_load_kwh):
    rate=float(market_data["energy_rate"])
    return {"project_id":project["project_id"],"currency":market_data["currency"],"annual_load_kwh":float(annual_load_kwh),"reference_rate_local_per_kwh":rate,"annual_reference_cost_local":float(annual_load_kwh)*rate,"tariff_status":market_data.get("tariff_status","REFERENCE_ONLY")}
def curve(project, market_data, annual_load_kwh, years=5):
    rate=float(market_data["energy_rate"]); growth=float(market_data.get("escalation",.02))
    return [{"year":i,"rate_local_per_kwh":rate*(1+growth)**(i-1),"currency":market_data["currency"]} for i in range(1,years+1)]
