"""Deterministic 8,760 load/solar matching with invariant checks."""
from datetime import datetime,timedelta
from math import pi,sin
def profile(annual_load_kwh,annual_solar_kwh,daytime_share=.75,year=2027):
    start=datetime(year,1,1); raw_load=[];raw_solar=[];timestamps=[]
    daytime_share=max(0,min(1,float(daytime_share)))
    for h in range(8760):
        ts=start+timedelta(hours=h); timestamps.append(ts.isoformat())
        solar=max(0,sin(pi*(ts.hour-6)/12)) if 6<=ts.hour<18 else 0
        operating=ts.weekday()<5 and 6<=ts.hour<22
        load_shape=(1 if operating else .35)*(1.25 if 8<=ts.hour<18 else .75)*(1.0 if 6<=ts.hour<18 else .7)
        raw_load.append(load_shape);raw_solar.append(solar*(.95+.05*sin(2*pi*ts.timetuple().tm_yday/365)))
    load_scale=float(annual_load_kwh)/sum(raw_load);solar_scale=float(annual_solar_kwh)/sum(raw_solar)
    load=[x*load_scale for x in raw_load];solar=[x*solar_scale for x in raw_solar]
    self_consumed=[min(a,b) for a,b in zip(load,solar)]
    export=[max(b-a,0) for a,b in zip(load,solar)]
    grid_purchase=[max(a-b,0) for a,b in zip(load,solar)]
    assert len(load)==len(solar)==8760
    return {"load":load,"solar":solar,"self_consumed":self_consumed,"export":export,"grid_purchase":grid_purchase,"load_sum":sum(load),"solar_sum":sum(solar),"self_consumed_sum":sum(self_consumed),"export_sum":sum(export),"profile_year":year,"hour_count":8760,"timestamps":timestamps}
