"""Standalone-first portfolio allocation with explicit decision labels."""
def allocate(projects,equity_budget=float("inf"),max_country_share=1.0):
    total=len(projects);counts={};out=[];spent=0.0
    for p in sorted(projects,key=lambda x:float(x.get("equity_npv_local_at_reference",0)),reverse=True):
        c=p.get("country","");share=(counts.get(c,0)+1)/max(total,1)
        if share>float(max_country_share): continue
        out.append(p);counts[c]=counts.get(c,0)+1;spent+=float(p.get("equity_local",0))
    return out,spent
