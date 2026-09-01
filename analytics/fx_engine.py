"""Reporting FX and explicit foreign-debt exposure helpers."""
def fx_path(base_fx,depreciation,periods):
    fx=float(base_fx);out=[]
    for _ in range(periods): fx*=1+float(depreciation);out.append(fx)
    return out
def local_to_usd(value,local_per_usd): return float(value)/float(local_per_usd)
def translate_foreign_debt_service(foreign_service,local_per_usd,depreciation=0):
    return [float(x)*fx for x,fx in zip(foreign_service,fx_path(local_per_usd,depreciation,len(foreign_service)))]
