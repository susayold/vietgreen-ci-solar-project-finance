def fx_path(base_fx, depreciation, periods):
    values=[]; fx=base_fx
    for _ in range(periods):
        fx *= 1.0 + depreciation; values.append(fx)
    return values

def translate_usd_debt_service(usd_service, base_fx, depreciation):
    return [s*fx for s,fx in zip(usd_service, fx_path(base_fx,depreciation,len(usd_service)))]

def break_even_depreciation(npv_vnd, usd_service, cfads, base_fx, low=0.0, high=0.20, iterations=60):
    def value(d):
        fx=fx_path(base_fx,d,len(usd_service)); return sum((c-s*f)/(1.14**(i+1)) for i,(c,s,f) in enumerate(zip(cfads,usd_service,fx)))
    for _ in range(iterations):
        mid=(low+high)/2
        if value(mid)>npv_vnd: low=mid
        else: high=mid
    return (low+high)/2
