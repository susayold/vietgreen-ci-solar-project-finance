"""Deterministic Vietnam TOU schedule mapping for the remote 8,760 engine.

Hourly labels represent one-hour intervals. Interval midpoints make the
17:30 and 22:30 legal boundaries explicit and reproducible. No billed rate is
inferred by this module.
"""
from __future__ import annotations
from datetime import datetime, timedelta
import hashlib

LEGAL_SCHEDULE_VERSION="DECISION-963-2026-04-22-MIDPOINT-V1"
CURRENT_BILLED_REFERENCE_VERSION="MOIT-BRIEFING-2026-07-09-CURRENT-REFERENCE-V1"

def hourly_grid(year=2027):
    start=datetime(year,1,1)
    return [start+timedelta(hours=i) for i in range(8760)]

def _midpoint_hour(ts):
    return ts.hour+0.5

def legal_period(ts):
    midpoint=_midpoint_hour(ts)
    if midpoint<6.0: return "low"
    if ts.weekday()<=5 and 17.5<=midpoint<22.5: return "peak"
    return "normal"

def current_billed_reference_period(ts):
    midpoint=_midpoint_hour(ts)
    if midpoint<6.0: return "low"
    if ts.weekday()<=5 and (9.5<=midpoint<11.5 or 17.0<=midpoint<20.0):
        return "peak_current_reference"
    return "normal_current_reference"

def validate_hourly_mapping(year=2027):
    grid=hourly_grid(year)
    legal=[legal_period(ts) for ts in grid]
    current=[current_billed_reference_period(ts) for ts in grid]
    if len(grid)!=8760 or len(set(grid))!=8760:
        raise ValueError("hourly grid must contain 8,760 unique timestamps")
    return {
        "year":year,
        "hour_count":len(grid),
        "legal_period_counts":{p:legal.count(p) for p in sorted(set(legal))},
        "current_billed_reference_counts":{p:current.count(p) for p in sorted(set(current))},
        "schedule_status":"PASS",
        "schedule_hash":hashlib.sha256(("|".join(legal)+"||"+"|".join(current)).encode()).hexdigest(),
    }

def hourly_tariff_summary(solar_kwh,self_consumed_kwh,year=2027):
    if len(solar_kwh)!=8760 or len(self_consumed_kwh)!=8760:
        raise ValueError("tariff mapping requires 8,760 observations")
    grid=hourly_grid(year)
    legal=[legal_period(ts) for ts in grid]
    control=validate_hourly_mapping(year)
    legal_self={p:sum(v for v,label in zip(self_consumed_kwh,legal) if label==p) for p in ("peak","normal","low")}
    legal_solar={p:sum(v for v,label in zip(solar_kwh,legal) if label==p) for p in ("peak","normal","low")}
    daytime=sum(v for v,ts in zip(self_consumed_kwh,grid) if 6.0<=_midpoint_hour(ts)<17.5)
    total=sum(self_consumed_kwh)
    return {
        "year":year,"hour_count":8760,
        "legal_peak_hours":control["legal_period_counts"].get("peak",0),
        "legal_normal_hours":control["legal_period_counts"].get("normal",0),
        "legal_low_hours":control["legal_period_counts"].get("low",0),
        "current_billed_peak_reference_hours":control["current_billed_reference_counts"].get("peak_current_reference",0),
        "legal_self_consumed_kwh":legal_self,"legal_solar_kwh":legal_solar,
        "daytime_self_consumed_share":daytime/total if total else 0.0,
        "tariff_schedule_hash":control["schedule_hash"],
        "tariff_schedule_status":control["schedule_status"],
        "current_billed_schedule_status":"WATCH",
        "billing_rate_status":"SIMULATED_MODEL_INPUT_ONLY",
    }

def weighted_model_only_tariff(base_vnd_kwh,daytime_premium_vnd_kwh,summary):
    return float(base_vnd_kwh)+float(daytime_premium_vnd_kwh)*float(summary["daytime_self_consumed_share"])
