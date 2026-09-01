"""Capacity-constrained debt sizing and forward sculpting."""
def backward_capacity(cfads,rate,sculpting_dscr):
    closing=0.0; services=[]; opening=0.0
    for cash in reversed([max(0,float(x)) for x in cfads]):
        service=cash/float(sculpting_dscr) if sculpting_dscr else 0
        opening=(closing+service)/(1+float(rate));services.append(service);closing=opening
    return (closing,list(reversed(services))) if services else (0.0,[])
def forward_rebuild(initial_debt,cfads,rate,sculpting_dscr):
    debt=max(0,float(initial_debt));rows=[]
    for cash in cfads:
        cash=max(0,float(cash)); opening=debt
        if debt<=1e-8:
            rows.append({"opening":0.0,"interest":0.0,"principal":0.0,"debt_service":0.0,"closing":0.0,"dscr":None});continue
        interest=debt*float(rate); target=cash/float(sculpting_dscr) if sculpting_dscr else 0
        service=min(target,debt+interest); principal=max(0,min(debt,service-interest)); closing=max(0,debt-principal)
        rows.append({"opening":opening,"interest":interest,"principal":principal,"debt_service":interest+principal,"closing":closing,"dscr":cash/(interest+principal) if interest+principal else None});debt=closing
    return rows
def discounted_value(values,rate): return sum(float(v)/(1+float(rate))**i for i,v in enumerate(values,1))
def coverage_ratio(cfads,debt_service): return min((float(c)/float(s) for c,s in zip(cfads,debt_service) if float(s)>0),default=0.0)
def capacity_constraints(cfads,rate,dscr,llcr,plcr,leverage_cap,capex):
    dscr_capacity,_=backward_capacity(cfads,rate,dscr);pv_llcr=discounted_value(cfads,rate)/float(llcr) if llcr else float("inf");pv_plcr=discounted_value(cfads,rate)/float(plcr) if plcr else float("inf");lev=float(capex)*float(leverage_cap)
    choices={"DSCR":dscr_capacity,"LLCR":pv_llcr,"PLCR":pv_plcr,"LEVERAGE":lev};binding=min(choices,key=choices.get)
    return choices[binding],binding,choices
