from datetime import datetime, timedelta
from math import pi, sin

def profile(annual_load_kwh, annual_solar_kwh, daytime_share=0.75, year=2027):
    start = datetime(year, 1, 1)
    raw_load, raw_solar = [], []
    for h in range(8760):
        ts = start + timedelta(hours=h)
        solar_shape = max(0.0, sin(pi * (ts.hour - 6) / 12.0)) if 6 <= ts.hour < 18 else 0.0
        operating = ts.weekday() < 5 and (6 <= ts.hour < 22)
        load_shape = (1.0 if operating else 0.35) * (1.25 if 8 <= ts.hour < 18 else 0.75)
        raw_load.append(load_shape)
        raw_solar.append(solar_shape * (0.95 + 0.05 * sin(2*pi*ts.timetuple().tm_yday/365)))
    ls = annual_load_kwh / sum(raw_load)
    ss = annual_solar_kwh / sum(raw_solar)
    load = [x*ls for x in raw_load]; solar = [x*ss for x in raw_solar]
    self_consumed = [min(a,b) for a,b in zip(load,solar)]
    excess = [max(b-a,0.0) for a,b in zip(load,solar)]
    return {'load':load,'solar':solar,'self_consumed':self_consumed,'excess':excess,'load_sum':sum(load),'solar_sum':sum(solar)}
