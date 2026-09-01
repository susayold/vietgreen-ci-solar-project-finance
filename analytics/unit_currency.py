"""Explicit, testable unit and currency contracts."""
from __future__ import annotations
from typing import Mapping, Any

_POWER={"W":1.0,"kW":1000.0,"MW":1000000.0,"Wp":1.0,"kWp":1000.0,"MWp":1000000.0}
_ENERGY={"Wh":1.0,"kWh":1000.0,"MWh":1000000.0,"GWh":1000000000.0}
_CURRENCIES={"USD","EUR","VND","INR","THB","SGD","AUD","PLN"}

def convert_power(value, from_unit, to_unit):
    if from_unit not in _POWER or to_unit not in _POWER: raise ValueError("unsupported power unit")
    return float(value)*_POWER[from_unit]/_POWER[to_unit]

def convert_energy(value, from_unit, to_unit):
    if from_unit not in _ENERGY or to_unit not in _ENERGY: raise ValueError("unsupported energy unit")
    return float(value)*_ENERGY[from_unit]/_ENERGY[to_unit]

def _factor(registry, base, quote):
    if base==quote: return 1.0
    if (base,quote) in registry: return float(registry[(base,quote)])
    if (quote,base) in registry: return 1.0/float(registry[(quote,base)])
    if base=="USD" and ("USD",quote) in registry: return float(registry[("USD",quote)])
    if quote=="USD" and ("USD",base) in registry: return 1.0/float(registry[("USD",base)])
    raise ValueError(f"missing FX pair {base}/{quote}")

def convert_currency(value, from_currency, to_currency, fx_registry, value_date=None):
    return float(value)*_factor(fx_registry,from_currency,to_currency)

def convert_capex_intensity(value, source_unit, target_unit, fx_registry, value_date=None, capacity_kwp=None, source_currency=None, target_currency=None):
    if source_unit not in {"USD_per_kWp","USD_per_Wdc","EUR_per_kWp","local_currency_per_kWp"}: raise ValueError("unsupported CAPEX source unit")
    if target_unit not in {"USD_total","EUR_total","local_currency_total","USD_per_kWp","local_currency_per_kWp"}: raise ValueError("unsupported CAPEX target unit")
    intensity=float(value)*1000.0 if source_unit.endswith("_per_Wdc") else float(value)
    if target_unit.endswith("_per_kWp"): return intensity
    if capacity_kwp is None: raise ValueError("capacity_kwp required for total CAPEX")
    src=source_currency or ("USD" if source_unit.startswith("USD") else "EUR")
    dst=target_currency or ("USD" if target_unit.startswith("USD") else "EUR")
    total=intensity*float(capacity_kwp)
    return convert_currency(total,src,dst,fx_registry,value_date) if src!=dst else total

def normalize_percent(value):
    value=float(value)
    return value/100.0 if abs(value)>1.0 else value

def validate_currency_unit_pair(value, currency, unit):
    if value in (None,""): return True
    if currency not in _CURRENCIES: raise ValueError("unsupported currency")
    if not unit: raise ValueError("monetary value requires unit")
    return True

def ledger_currency(rows, fields=("capex_local","revenue_local","cfads_local")):
    currencies={r.get("currency") for r in rows for f in fields if r.get(f) not in (None,"")}
    if len(currencies)>1: raise ValueError(f"mixed ledger currencies: {currencies}")
    return next(iter(currencies),None)
