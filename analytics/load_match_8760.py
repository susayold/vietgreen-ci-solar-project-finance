from datetime import datetime,timedelta
from math import pi,sin

def profile(annual_load_kwh,annual_solar_kwh,daytime_share=0.75,year=2027):
    """Create deterministic local-standard 8,760 load and solar profiles."""
    start=datetime(year,1,1)
    raw_load,raw_solar,timestamps=[],[],[]
    daytime_share=max(0.0,min(1.0,float(daytime_share)))
    daytime_multiplier=0.75+0.50*daytime_share
    non_daytime_multiplier=1.25-0.50*daytime_share
    for h in range(8760):
        ts=start+timedelta(hours=h)
        timestamps.append(ts.isoformat())
        solar_shape=max(0.0,sin(pi*(ts.hour-6)/12.0)) if 6<=ts.hour<18 else 0.0
        operating=ts.weekday()<5 and 6<=ts.hour<22
        base_shape=(1.0 if operating else 0.35)*(1.25 if 8<=ts.hour<18 else 0.75)
        load_shape=base_shape*(daytime_multiplier if 6<=ts.hour<18 else non_daytime_multiplier)
        raw_load.append(load_shape)
        raw_solar.append(solar_shape*(0.95+0.05*sin(2*pi*ts.timetuple().tm_yday/365)))
    ls=annual_load_kwh/sum(raw_load); ss=annual_solar_kwh/sum(raw_solar)
    load=[x*ls for x in raw_load]; solar=[x*ss for x in raw_solar]
    self_consumed=[min(a,b) for a,b in zip(load,solar)]
    excess=[max(b-a,0.0) for a,b in zip(load,solar)]
    return {"load":load,"solar":solar,"self_consumed":self_consumed,"excess":excess,
            "load_sum":sum(load),"solar_sum":sum(solar),"timestamps":timestamps,
            "profile_year":year,"hour_count":len(timestamps)}
