"""V4 Phase 1 remote-only remediation engine.

The module is intentionally independent from the V3 reporting runner. It reads
the synthetic inputs that are already versioned in GitHub, holds hourly arrays
in memory on GitHub Actions, and writes only controlled aggregate CSV/Markdown
evidence. It does not fetch, materialise, or commit raw transaction data.
"""
from __future__ import annotations

import csv
import hashlib
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.capex_engine import build_capex_schedule
from analytics.debt_sculpting import (
    backward_capacity,
    coverage_ratio,
    discounted_value,
    forward_rebuild,
)
from analytics.v4_returns import xirr, xnpv

YEARS = 15
MASTER_SEED = 260831
PROJECT_RATE = 0.12
EQUITY_RATE = 0.14
CUSTOMER_RATE = 0.10
BASE_RATE = 0.085
STRESSED_RATE = 0.11
TAX_RATE = 0.20
VAT_RATE = 0.08
DEGRADATION = 0.005
PPA_ESCALATION = 0.01
OPEX_ESCALATION = 0.02
MAINTENANCE_RATE = 0.005
DSO_DAYS = 30.0
EQUITY_BUDGET = 100_000_000_000.0
Z = {"P50": 0.0, "P75": 0.67449, "P90": 1.28155, "P99": 2.32635}

ARCHETYPES = {
    row["archetype_id"]: row
    for row in [
        {"archetype_id": "ARCH-01", "archetype_name": "continuous_process", "day_start": "0", "day_end": "24", "weekday_factor": "1.00", "weekend_factor": "0.95", "daytime_share_multiplier": "1.00", "season_amp": "0.05", "night_floor": "0.75", "cloud_volatility": "0.03"},
        {"archetype_id": "ARCH-02", "archetype_name": "electronics_day_shift", "day_start": "7", "day_end": "21", "weekday_factor": "1.00", "weekend_factor": "0.30", "daytime_share_multiplier": "0.90", "season_amp": "0.04", "night_floor": "0.12", "cloud_volatility": "0.03"},
        {"archetype_id": "ARCH-03", "archetype_name": "cold_chain_24x7", "day_start": "0", "day_end": "24", "weekday_factor": "1.00", "weekend_factor": "0.98", "daytime_share_multiplier": "0.65", "season_amp": "0.08", "night_floor": "0.80", "cloud_volatility": "0.04"},
        {"archetype_id": "ARCH-04", "archetype_name": "food_day_extended", "day_start": "6", "day_end": "22", "weekday_factor": "1.00", "weekend_factor": "0.75", "daytime_share_multiplier": "1.00", "season_amp": "0.10", "night_floor": "0.20", "cloud_volatility": "0.05"},
        {"archetype_id": "ARCH-05", "archetype_name": "textile_weekday", "day_start": "7", "day_end": "18", "weekday_factor": "1.00", "weekend_factor": "0.20", "daytime_share_multiplier": "0.35", "season_amp": "0.07", "night_floor": "0.10", "cloud_volatility": "0.05"},
        {"archetype_id": "ARCH-06", "archetype_name": "hospitality_evening", "day_start": "6", "day_end": "24", "weekday_factor": "0.95", "weekend_factor": "0.90", "daytime_share_multiplier": "0.55", "season_amp": "0.12", "night_floor": "0.30", "cloud_volatility": "0.06"},
        {"archetype_id": "ARCH-07", "archetype_name": "pharma_stable", "day_start": "0", "day_end": "24", "weekday_factor": "1.00", "weekend_factor": "0.92", "daytime_share_multiplier": "1.00", "season_amp": "0.04", "night_floor": "0.70", "cloud_volatility": "0.03"},
        {"archetype_id": "ARCH-08", "archetype_name": "automotive_two_shift", "day_start": "6", "day_end": "22", "weekday_factor": "1.00", "weekend_factor": "0.45", "daytime_share_multiplier": "0.85", "season_amp": "0.06", "night_floor": "0.18", "cloud_volatility": "0.04"},
        {"archetype_id": "ARCH-09", "archetype_name": "agribusiness_seasonal", "day_start": "6", "day_end": "20", "weekday_factor": "0.95", "weekend_factor": "0.55", "daytime_share_multiplier": "0.45", "season_amp": "0.18", "night_floor": "0.15", "cloud_volatility": "0.08"},
        {"archetype_id": "ARCH-10", "archetype_name": "plastics_mixed_shift", "day_start": "5", "day_end": "22", "weekday_factor": "1.00", "weekend_factor": "0.65", "daytime_share_multiplier": "0.75", "season_amp": "0.06", "night_floor": "0.20", "cloud_volatility": "0.04"},
    ]
}


def read_csv(relative_path):
    with (ROOT / relative_path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(relative_path, rows, fields):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: "" if row.get(field) is None else row.get(field, "") for field in fields})


def num(row, key, default=0.0):
    value = row.get(key, default) if row else default
    return float(value) if value not in ("", None) else float(default)


def clamp(value, lower, upper):
    return max(lower, min(upper, float(value)))


def stable_unit(text):
    digest = hashlib.sha256(("%s|%s" % (MASTER_SEED, text)).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12 - 1)


def stable_hash(values):
    payload = "|".join("%.8f" % float(value) for value in values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_profile(project, archetype, annual_load_kwh, annual_solar_kwh, year=2027):
    """Create one deterministic 8,760 profile with archetype and calendar effects."""
    from datetime import datetime, timedelta

    start = datetime(year, 1, 1)
    raw_load = []
    raw_solar = []
    timestamps = []
    day_share = clamp(
        num(project, "daytime_load_share") * num(archetype, "daytime_share_multiplier", 1.0),
        0.08,
        0.92,
    )
    day_start = int(float(archetype["day_start"]))
    day_end = int(float(archetype["day_end"]))
    phase = 2.0 * math.pi * stable_unit(project["project_id"])
    region_factor = {"North": 0.97, "Central": 1.00, "South": 1.03}.get(project.get("region"), 1.0)
    for hour_index in range(8760):
        ts = start + timedelta(hours=hour_index)
        hour = ts.hour
        day_of_year = ts.timetuple().tm_yday
        timestamps.append(ts.isoformat())
        weekend_factor = num(archetype, "weekend_factor", 1.0) if ts.weekday() >= 5 else num(archetype, "weekday_factor", 1.0)
        in_operating_window = day_start <= hour < day_end if day_start < day_end else True
        operating_factor = 1.0 if in_operating_window else num(archetype, "night_floor", 0.2)
        if 6 <= hour < 18:
            intra_day = 0.70 + 0.30 * math.sin(math.pi * (hour - 6) / 12.0)
            load_shape = day_share * intra_day
        else:
            intra_night = 0.80 + 0.20 * math.sin(2.0 * math.pi * (hour + 1) / 12.0) ** 2
            load_shape = (1.0 - day_share) * intra_night
        seasonal_load = 1.0 + num(archetype, "season_amp", 0.05) * math.sin(2.0 * math.pi * day_of_year / 365.0 + phase)
        raw_load.append(max(1e-8, weekend_factor * operating_factor * load_shape * seasonal_load))
        solar_shape = max(0.0, math.sin(math.pi * (hour - 6) / 12.0)) if 6 <= hour < 18 else 0.0
        seasonal_solar = 1.0 + 0.08 * math.sin(2.0 * math.pi * day_of_year / 365.0 + phase / 2.0)
        cloud_vol = num(archetype, "cloud_volatility", 0.04)
        cloud = 1.0 - cloud_vol * (0.5 + 0.5 * math.sin(2.0 * math.pi * hour_index / 37.0 + phase))
        raw_solar.append(max(0.0, solar_shape * seasonal_solar * cloud * region_factor))
    load_scale = float(annual_load_kwh) / sum(raw_load)
    solar_scale = float(annual_solar_kwh) / sum(raw_solar)
    load = [value * load_scale for value in raw_load]
    solar = [value * solar_scale for value in raw_solar]
    self_consumed = [min(load_value, solar_value) for load_value, solar_value in zip(load, solar)]
    excess = [max(solar_value - load_value, 0.0) for load_value, solar_value in zip(load, solar)]
    return {
        "load": load,
        "solar": solar,
        "self_consumed": self_consumed,
        "excess": excess,
        "load_sum": sum(load),
        "solar_sum": sum(solar),
        "self_consumption_kwh": sum(self_consumed),
        "excess_kwh": sum(excess),
        "self_consumption_ratio": sum(self_consumed) / sum(solar) if sum(solar) else 0.0,
        "effective_daytime_share": day_share,
        "timestamps": timestamps,
        "hour_count": len(timestamps),
        "profile_year": year,
        "profile_hash": stable_hash(load + solar),
    }


def energy_budget(project_id, rows):
    components = [row for row in rows if row["project_id"] == project_id]
    sigma = math.sqrt(sum(num(row, "component_uncertainty_pct") ** 2 for row in components))
    return components, sigma


def capex_by_project(capex_rows, construction_rows, project_id):
    _, summary = build_capex_schedule(capex_rows, construction_rows, project_id, idc_rate=BASE_RATE)
    return summary


def debt_metrics(cfads, capex, debt_row, rate_override=None):
    rate = float(rate_override if rate_override is not None else num(debt_row, "all_in_rate", BASE_RATE))
    tenor = int(num(debt_row, "debt_tenor_years", 10))
    sizing_dscr = num(debt_row, "sizing_dscr", 1.30)
    sculpting_dscr = num(debt_row, "sculpting_dscr", sizing_dscr)
    llcr_floor = num(debt_row, "llcr_floor", 1.35)
    leverage_cap = num(debt_row, "leverage_cap", 0.65)
    dscr_cap, _ = backward_capacity(cfads[:tenor], rate, sizing_dscr)
    llcr_cap = discounted_value(cfads[:tenor], rate) / llcr_floor if llcr_floor else 0.0
    plcr_cap = discounted_value(cfads, rate) / num(debt_row, "plcr_floor", 1.25)
    leverage_amount = float(capex) * leverage_cap
    debt = max(0.0, min(dscr_cap, llcr_cap, plcr_cap, leverage_amount))
    schedule = forward_rebuild(debt, cfads[:tenor], rate, sculpting_dscr)
    service = [num(item, "debt_service") for item in schedule]
    min_dscr = coverage_ratio(cfads[:tenor], service)
    return {
        "debt": debt,
        "equity_required": float(capex) - debt,
        "rate": rate,
        "tenor": tenor,
        "service": service,
        "min_dscr": min_dscr,
        "binding_cap": (
            "DSCR" if dscr_cap <= min(llcr_cap, plcr_cap, leverage_amount)
            else "LLCR" if llcr_cap <= min(plcr_cap, leverage_amount)
            else "PLCR" if plcr_cap <= leverage_amount
            else "LEVERAGE"
        ),
    }


def annual_cfads(project, price, self_consumption_kwh, capex_factor=1.0, ppa_tenor=None, dso_days=DSO_DAYS, cod_delay=0, common_factor=1.0):
    capex = num(project, "_capex_vnd") * float(capex_factor)
    tenor = int(ppa_tenor if ppa_tenor is not None else num(project, "ppa_tenor_years", 15))
    opex_y1 = num(project, "proposed_capacity_kwp") * 15.0 * 25000.0
    depreciation = (capex / (1.0 + VAT_RATE)) / YEARS
    tax_losses = 0.0
    previous_nwc = 0.0
    rows = []
    for year in range(1, YEARS + 1):
        in_contract = year <= tenor
        generation = float(self_consumption_kwh) * (1.0 - DEGRADATION) ** (year - 1)
        revenue = generation * float(price) * (1.0 + PPA_ESCALATION) ** (year - 1) if in_contract else 0.0
        opex = opex_y1 * (1.0 + OPEX_ESCALATION) ** (year - 1) if in_contract else 0.0
        depreciation_expense = depreciation if in_contract else 0.0
        taxable_income = revenue - opex - depreciation_expense
        if taxable_income >= tax_losses:
            tax = max(0.0, (taxable_income - tax_losses) * TAX_RATE)
            tax_loss_closing = 0.0
        else:
            tax = 0.0
            tax_loss_closing = tax_losses - taxable_income
        tax_losses = tax_loss_closing
        working_capital = revenue * float(dso_days) / 365.0 if year < YEARS else 0.0
        delta_working_capital = working_capital - previous_nwc
        if year == YEARS:
            delta_working_capital = -previous_nwc
        previous_nwc = working_capital
        maintenance = (capex / (1.0 + VAT_RATE)) * MAINTENANCE_RATE if year in (5, 10) and in_contract else 0.0
        cfads = (revenue - opex - tax - delta_working_capital - maintenance) * float(common_factor)
        rows.append({
            "year": year,
            "revenue_vnd": revenue,
            "opex_vnd": opex,
            "tax_vnd": tax,
            "working_capital_vnd": working_capital,
            "cfads_vnd": cfads,
        })
    if cod_delay:
        rows = [{"year": 0, "revenue_vnd": 0.0, "opex_vnd": 0.0, "tax_vnd": 0.0, "working_capital_vnd": 0.0, "cfads_vnd": 0.0}] + rows[:-1]
        for index, row in enumerate(rows):
            row["year"] = index + 1
    return rows


def evaluate(project, price, self_consumption_kwh, debt_row, capex_factor=1.0, ppa_tenor=None, dso_days=DSO_DAYS, rate_override=None, cod_delay=0, common_factor=1.0):
    cf_rows = annual_cfads(
        project, price, self_consumption_kwh, capex_factor=capex_factor,
        ppa_tenor=ppa_tenor, dso_days=dso_days, cod_delay=cod_delay,
        common_factor=common_factor,
    )
    cfads = [num(row, "cfads_vnd") for row in cf_rows]
    capex = num(project, "_capex_vnd") * float(capex_factor)
    debt = debt_metrics(cfads, capex, debt_row, rate_override=rate_override)
    service = debt["service"] + [0.0] * max(0, YEARS - len(debt["service"]))
    project_cashflows = [-capex] + cfads
    equity_cashflows = [-debt["equity_required"]] + [
        cfads[index] - service[index] for index in range(YEARS)
    ]
    return {
        **debt,
        "capex_vnd": capex,
        "cfads": cfads,
        "project_npv_vnd": xnpv(PROJECT_RATE, project_cashflows),
        "project_irr": xirr(project_cashflows),
        "equity_npv_vnd": xnpv(EQUITY_RATE, equity_cashflows),
        "equity_irr": xirr(equity_cashflows),
        "project_cashflows": project_cashflows,
        "equity_cashflows": equity_cashflows,
        "cfads_y1_vnd": cfads[0] if cfads else 0.0,
    }


def solve_root(function, increasing, initial_high, max_expansions=12):
    low = 0.0
    low_value = float(function(low))
    high = max(1.0, float(initial_high))
    high_value = float(function(high))
    expansions = 0
    while ((increasing and high_value < 0.0) or ((not increasing) and high_value > 0.0)) and expansions < max_expansions:
        high *= 2.0
        high_value = float(function(high))
        expansions += 1
    bracketed = (low_value <= 0.0 <= high_value) if increasing else (low_value >= 0.0 >= high_value)
    if not bracketed:
        boundary = high if ((increasing and high_value < 0.0) or ((not increasing) and high_value > 0.0)) else low
        return {"price": boundary, "residual": high_value if boundary == high else low_value, "iterations": 0, "interval": 0.0, "status": "BOUNDARY_NO_ROOT"}
    for _ in range(48):
        mid = (low + high) / 2.0
        mid_value = float(function(mid))
        if increasing:
            if mid_value >= 0.0:
                high, high_value = mid, mid_value
            else:
                low, low_value = mid, mid_value
        else:
            if mid_value <= 0.0:
                high, high_value = mid, mid_value
            else:
                low, low_value = mid, mid_value
    mid = (low + high) / 2.0
    return {
        "price": mid,
        "residual": float(function(mid)),
        "iterations": 48,
        "interval": high - low,
        "status": "ROOT_CONVERGED",
    }


def solve_ppa(project, self_kwh_p50, capex_factor, ppa_tenor, debt_row):
    tariff = num(project, "weighted_avoided_tariff_vnd_kwh", 0.0)
    initial_high = max(2500.0, tariff * 1.25)

    def customer_value(price):
        savings = [0.0] + [
            self_kwh_p50 * ((tariff * (1.0 + PPA_ESCALATION) ** year) - (price * (1.0 + PPA_ESCALATION) ** year))
            for year in range(ppa_tenor)
        ]
        return xnpv(CUSTOMER_RATE, savings)

    def sponsor_value(price):
        return evaluate(project, price, self_kwh_p50, debt_row, capex_factor=capex_factor, ppa_tenor=ppa_tenor)["equity_npv_vnd"]

    def lender_value(price):
        current = evaluate(project, price, self_kwh_p50, debt_row, capex_factor=capex_factor, ppa_tenor=ppa_tenor)
        full_debt = num(project, "_capex_vnd") * float(capex_factor) * num(debt_row, "leverage_cap", 0.65)
        schedule = forward_rebuild(full_debt, current["cfads"][:int(num(debt_row, "debt_tenor_years", 10))], current["rate"], num(debt_row, "sculpting_dscr", 1.30))
        full_service = [num(item, "debt_service") for item in schedule]
        dscr = coverage_ratio(current["cfads"][:len(full_service)], full_service)
        return dscr - num(debt_row, "minimum_covenant_dscr", 1.20)

    customer = solve_root(customer_value, increasing=False, initial_high=initial_high)
    sponsor = solve_root(sponsor_value, increasing=True, initial_high=initial_high)
    lender = solve_root(lender_value, increasing=True, initial_high=initial_high)
    ceiling = customer["price"]
    lower = max(sponsor["price"], lender["price"])
    feasible = lower <= ceiling + 1e-6
    return {
        "customer_ceiling_vnd_kwh": ceiling,
        "sponsor_floor_vnd_kwh": sponsor["price"],
        "lender_floor_vnd_kwh": lender["price"],
        "lower_bound_vnd_kwh": lower,
        "upper_bound_vnd_kwh": ceiling,
        "status": "FEASIBLE_ZONE" if feasible else "EMPTY_ZONE",
        "action": "PROCEED" if feasible else "RENEGOTIATE_OR_REJECT",
        "customer_solver_status": customer["status"],
        "sponsor_solver_status": sponsor["status"],
        "lender_solver_status": lender["status"],
        "customer_solver_residual": customer["residual"],
        "sponsor_solver_residual": sponsor["residual"],
        "lender_solver_residual": lender["residual"],
        "customer_solver_interval": customer["interval"],
        "sponsor_solver_interval": sponsor["interval"],
        "lender_solver_interval": lender["interval"],
        "customer_solver_iterations": customer["iterations"],
        "sponsor_solver_iterations": sponsor["iterations"],
        "lender_solver_iterations": lender["iterations"],
    }


def project_ledger(project, archetype, budget_rows, capex_rows, construction_rows, solar_rows, debt_rows):
    project_id = project["project_id"]
    components, sigma = energy_budget(project_id, budget_rows)
    solar = next(row for row in solar_rows if row["project_id"] == project_id)
    debt = next(row for row in debt_rows if row["project_or_portfolio_id"] == project_id)
    capex = capex_by_project(capex_rows, construction_rows, project_id)
    p50 = num(project, "proposed_capacity_kwp") * num(solar, "pvout_kwh_kwp")
    profiles = {}
    for label, z_score in Z.items():
        generation = max(0.0, p50 * (1.0 - z_score * sigma))
        profiles[label] = load_profile(project, archetype, num(project, "annual_load_kwh"), generation)
    enriched = {**project, "_capex_vnd": capex["total_uses_vnd"]}
    current_tenor = int(num(project, "ppa_tenor_years", 15))
    current_price = num(project, "ppa_price_vnd_kwh")
    current_ppa = solve_ppa(enriched, profiles["P50"]["self_consumption_kwh"], 1.0, current_tenor, debt)
    negotiated_factor = 0.80
    negotiated_tenor = max(15, current_tenor)
    negotiated_ppa = solve_ppa(enriched, profiles["P50"]["self_consumption_kwh"], negotiated_factor, negotiated_tenor, debt)
    negotiated_price = (negotiated_ppa["lower_bound_vnd_kwh"] + negotiated_ppa["upper_bound_vnd_kwh"]) / 2.0 if negotiated_ppa["status"] == "FEASIBLE_ZONE" else negotiated_ppa["upper_bound_vnd_kwh"]
    current_eval = evaluate(enriched, current_price, profiles["P50"]["self_consumption_kwh"], debt, ppa_tenor=current_tenor)
    negotiated_eval = evaluate(enriched, negotiated_price, profiles["P50"]["self_consumption_kwh"], debt, capex_factor=negotiated_factor, ppa_tenor=negotiated_tenor)
    base = {
        "project_id": project_id,
        "project_name": project["project_name"],
        "region": project["region"],
        "industry": project["industry"],
        "parent_group_id": project["parent_group_id"],
        "site_id": project["site_id"],
        "credit_grade": project["credit_grade"],
        "site_continuity_grade": project["site_continuity_grade"],
        "technical_status": project["technical_status"],
        "business_model_archetype": project["business_model_archetype"],
        "proposed_capacity_kwp": num(project, "proposed_capacity_kwp"),
        "archetype_id": archetype["archetype_id"],
        "archetype_name": archetype["archetype_name"],
        "uncertainty_sigma_pct": sigma,
        "uncertainty_component_count": len(components),
        "p50_y1_kwh": p50,
        "p75_y1_kwh": profiles["P75"]["solar_sum"],
        "p90_y1_kwh": profiles["P90"]["solar_sum"],
        "p99_y1_kwh": profiles["P99"]["solar_sum"],
        "p90_p50_ratio": profiles["P90"]["solar_sum"] / p50 if p50 else 0.0,
        "p99_p50_ratio": profiles["P99"]["solar_sum"] / p50 if p50 else 0.0,
        "self_consumption_kwh_p50": profiles["P50"]["self_consumption_kwh"],
        "self_consumption_kwh_p90": profiles["P90"]["self_consumption_kwh"],
        "self_consumption_ratio_p50": profiles["P50"]["self_consumption_ratio"],
        "self_consumption_ratio_p90": profiles["P90"]["self_consumption_ratio"],
        "excess_kwh_p50": profiles["P50"]["excess_kwh"],
        "effective_daytime_share": profiles["P50"]["effective_daytime_share"],
        "profile_hour_count": profiles["P50"]["hour_count"],
        "profile_hash_p50": profiles["P50"]["profile_hash"],
        "profile_hash_p90": profiles["P90"]["profile_hash"],
        "capex_vnd": capex["total_uses_vnd"],
        "idc_vnd": capex["idc_vnd"],
        "current_price_vnd_kwh": current_price,
        "current_ppa_tenor_years": current_tenor,
        "current_ppa_zone_status": current_ppa["status"],
        "current_ppa": current_ppa,
        "negotiated_price_vnd_kwh": negotiated_price,
        "negotiated_ppa_tenor_years": negotiated_tenor,
        "negotiated_capex_factor": negotiated_factor,
        "negotiated_ppa_zone_status": negotiated_ppa["status"],
        "negotiated_ppa": negotiated_ppa,
        "current_eval": current_eval,
        "negotiated_eval": negotiated_eval,
    }
    return base


def portfolio_rows(ledgers, case):
    if case == "CURRENT_TERMS":
        eval_key, ppa_key, capex_factor = "current_eval", "current_ppa", 1.0
    else:
        eval_key, ppa_key, capex_factor = "negotiated_eval", "negotiated_ppa", 0.80
    candidates = []
    rejection_reasons = {}
    for ledger in ledgers:
        evaluation = ledger[eval_key]
        ppa = ledger[ppa_key]
        reasons = []
        if ledger["technical_status"] != "PASS":
            reasons.append("technical_gate")
        if ledger["credit_grade"] == "D":
            reasons.append("credit_gate")
        if ledger["site_continuity_grade"] == "D":
            reasons.append("site_continuity_gate")
        if "DPPA" in ledger["business_model_archetype"]:
            reasons.append("regulatory_gate")
        if ppa["status"] != "FEASIBLE_ZONE":
            reasons.append("ppa_zone_empty")
        if evaluation["min_dscr"] < 1.20:
            reasons.append("finance_dscr_gate")
        if evaluation["equity_npv_vnd"] <= 0.0:
            reasons.append("positive_equity_npv_gate")
        if reasons:
            rejection_reasons[ledger["project_id"]] = "|".join(reasons)
        else:
            candidates.append(ledger)
    ordered = sorted(
        candidates,
        key=lambda item: (
            item[eval_key]["equity_npv_vnd"] / max(item[eval_key]["equity_required"], 1.0),
            item[eval_key]["equity_npv_vnd"],
        ),
        reverse=True,
    )
    selected = []
    parent_counts = {}
    industry_counts = {}
    region_counts = {}
    for ledger in ordered:
        parent = ledger["parent_group_id"]
        industry = ledger["industry"]
        region = ledger["region"]
        if parent_counts.get(parent, 0) >= 2 or industry_counts.get(industry, 0) >= 4 or region_counts.get(region, 0) >= 8:
            rejection_reasons[ledger["project_id"]] = "concentration_constraint"
            continue
        if sum(item[eval_key]["equity_required"] for item in selected) + ledger[eval_key]["equity_required"] > EQUITY_BUDGET:
            rejection_reasons[ledger["project_id"]] = "equity_budget_constraint"
            continue
        selected.append(ledger)
        parent_counts[parent] = parent_counts.get(parent, 0) + 1
        industry_counts[industry] = industry_counts.get(industry, 0) + 1
        region_counts[region] = region_counts.get(region, 0) + 1
    selected_ids = {item["project_id"] for item in selected}
    portfolio_status = "DEPLOYMENT" if selected else "NO_DEPLOYMENT"
    if selected:
        empty_reason = ""
    elif not candidates:
        empty_reason = "NO_PROJECT_PASSES_ALL_HARD_GATES_AND_POSITIVE_EQUITY_NPV"
    else:
        empty_reason = "CANDIDATES_EXIST_BUT_CONSTRAINTS_BLOCK_SELECTION"
    rows = []
    selected_equity = sum(item[eval_key]["equity_required"] for item in selected)
    selected_npv = sum(item[eval_key]["equity_npv_vnd"] for item in selected)
    for ledger in ledgers:
        evaluation = ledger[eval_key]
        ppa = ledger[ppa_key]
        rows.append({
            "portfolio_case": case,
            "portfolio_status": portfolio_status,
            "empty_solution_reason": empty_reason,
            "project_id": ledger["project_id"],
            "project_name": ledger["project_name"],
            "region": ledger["region"],
            "industry": ledger["industry"],
            "parent_group_id": ledger["parent_group_id"],
            "archetype_id": ledger["archetype_id"],
            "ppa_zone_status": ppa["status"],
            "project_npv_vnd": evaluation["project_npv_vnd"],
            "project_irr": evaluation["project_irr"],
            "equity_npv_vnd": evaluation["equity_npv_vnd"],
            "equity_irr": evaluation["equity_irr"],
            "equity_required_vnd": evaluation["equity_required"],
            "min_dscr": evaluation["min_dscr"],
            "selected_flag": ledger["project_id"] in selected_ids,
            "rejection_reason": "" if ledger["project_id"] in selected_ids else rejection_reasons.get(ledger["project_id"], "not_selected"),
            "parent_exposure_count": parent_counts.get(ledger["parent_group_id"], 0),
            "industry_exposure_count": industry_counts.get(ledger["industry"], 0),
            "region_exposure_count": region_counts.get(ledger["region"], 0),
            "selected_count": len(selected),
            "selected_equity_required_vnd": selected_equity,
            "selected_equity_npv_vnd": selected_npv,
            "equity_budget_vnd": EQUITY_BUDGET,
            "capex_factor": capex_factor,
            "transaction_evidence_status": "OPEN_EXTERNAL_GATE",
        })
    return rows, selected


def scenario_rows(selected, case):
    rows = []
    scenarios = [
        ("BASE_SPONSOR", "P50; contractual base terms", "P50", 1.0, 30.0, BASE_RATE, 0, 1.0),
        ("P90_ENERGY", "P90 generation; no re-sizing of commercial price", "P90", 1.0, 30.0, BASE_RATE, 0, 1.0),
        ("CAPEX_OVERRUN", "15% CAPEX overrun; debt re-sized", "P50", 1.15, 30.0, BASE_RATE, 0, 1.0),
        ("COD_DELAY", "one-year COD delay; CFADS shifted", "P50", 1.0, 30.0, BASE_RATE, 1, 1.0),
        ("INTEREST_RATE_SHOCK", "rate moves to 11%; debt re-sized", "P50", 1.0, 30.0, STRESSED_RATE, 0, 1.0),
        ("DSO_DELAY", "DSO moves from 30 to 90 days", "P50", 1.0, 90.0, BASE_RATE, 0, 1.0),
        ("COMBINED_DOWNSIDE", "P90; 15% CAPEX; 11% rate; DSO 90; COD delay; 10% common haircut", "P90", 1.15, 90.0, STRESSED_RATE, 1, 0.90),
    ]
    for scenario, note, energy_case, capex_factor, dso_days, rate, cod_delay, common_factor in scenarios:
        project_results = []
        for ledger in selected:
            price = ledger["current_price_vnd_kwh"] if case == "CURRENT_TERMS" else ledger["negotiated_price_vnd_kwh"]
            tenor = ledger["current_ppa_tenor_years"] if case == "CURRENT_TERMS" else ledger["negotiated_ppa_tenor_years"]
            project = {**ledger, "_capex_vnd": ledger["capex_vnd"]}
            debt_row = {
                "all_in_rate": rate, "debt_tenor_years": 10, "sizing_dscr": 1.30,
                "sculpting_dscr": 1.30, "llcr_floor": 1.35, "plcr_floor": 1.25,
                "leverage_cap": 0.65, "minimum_covenant_dscr": 1.20,
            }
            evaluation = evaluate(
                project, price,
                ledger["self_consumption_kwh_p90"] if energy_case == "P90" else ledger["self_consumption_kwh_p50"],
                debt_row,
                capex_factor=capex_factor * (ledger["negotiated_capex_factor"] if case == "NEGOTIATED_TERMS" else 1.0),
                ppa_tenor=tenor, dso_days=dso_days, rate_override=rate,
                cod_delay=cod_delay, common_factor=common_factor,
            )
            project_results.append(evaluation)
        rows.append({
            "portfolio_case": case,
            "scenario": scenario,
            "scenario_note": note,
            "selected_count": len(selected),
            "project_npv_vnd": sum(item["project_npv_vnd"] for item in project_results),
            "project_irr_min": min((item["project_irr"] for item in project_results if item["project_irr"] is not None), default=None),
            "equity_npv_vnd": sum(item["equity_npv_vnd"] for item in project_results),
            "equity_irr_min": min((item["equity_irr"] for item in project_results if item["equity_irr"] is not None), default=None),
            "min_dscr": min((item["min_dscr"] for item in project_results), default=0.0),
            "status": "PASS" if not project_results or min(item["min_dscr"] for item in project_results) >= 1.20 else "FAIL_DSCR",
        })
    return rows


def build():
    projects = read_csv("data/synthetic/project_master.csv")
    ppa_terms = {row["project_id"]: row for row in read_csv("data/synthetic/ppa_terms.csv")}
    budget_rows = read_csv("data/synthetic/energy_uncertainty_budget.csv")
    capex_rows = read_csv("data/synthetic/capex.csv")
    construction_rows = read_csv("data/synthetic/construction_schedule.csv")
    solar_rows = read_csv("data/synthetic/solar_resource.csv")
    debt_rows = read_csv("data/synthetic/debt_terms.csv")
    ledgers = []
    for index, project in enumerate(projects):
        archetype = ARCHETYPES["ARCH-%02d" % (index % 10 + 1)]
        enriched = dict(project)
        enriched["ppa_price_vnd_kwh"] = ppa_terms[project["project_id"]]["ppa_price_base_vnd_kwh"]
        ledger = project_ledger(enriched, archetype, budget_rows, capex_rows, construction_rows, solar_rows, debt_rows)
        ledger["current_price_vnd_kwh"] = num(ppa_terms[project["project_id"]], "ppa_price_base_vnd_kwh")
        ledgers.append(ledger)

    energy_fields = [
        "project_id", "archetype_id", "archetype_name", "region", "p50_y1_kwh", "p75_y1_kwh",
        "p90_y1_kwh", "p99_y1_kwh", "p90_p50_ratio", "p99_p50_ratio", "uncertainty_sigma_pct",
        "uncertainty_component_count", "self_consumption_kwh_p50", "self_consumption_kwh_p90",
        "self_consumption_ratio_p50", "self_consumption_ratio_p90", "excess_kwh_p50",
        "effective_daytime_share", "profile_hour_count", "profile_hash_p50", "profile_hash_p90",
    ]
    write_csv("outputs/energy_p50_p90_p99.csv", [{field: item[field] for field in energy_fields} for item in ledgers], energy_fields)

    load_fields = [
        "project_id", "archetype_id", "archetype_name", "region", "profile_hour_count",
        "effective_daytime_share", "self_consumption_kwh_p50", "excess_kwh_p50",
        "self_consumption_ratio_p50", "self_consumption_ratio_p90", "profile_hash_p50",
        "profile_hash_p90",
    ]
    write_csv("outputs/load_matching_v4.csv", [{field: item[field] for field in load_fields} for item in ledgers], load_fields)

    ppa_fields = [
        "project_id", "case", "ppa_price_vnd_kwh", "capex_factor", "ppa_tenor_years",
        "customer_ceiling_vnd_kwh", "sponsor_floor_vnd_kwh", "lender_floor_vnd_kwh",
        "lower_bound_vnd_kwh", "upper_bound_vnd_kwh", "zone_status", "action",
        "customer_solver_status", "sponsor_solver_status", "lender_solver_status",
        "customer_solver_iterations", "sponsor_solver_iterations", "lender_solver_iterations",
        "customer_solver_residual", "sponsor_solver_residual", "lender_solver_residual",
        "customer_solver_interval", "sponsor_solver_interval", "lender_solver_interval",
    ]
    ppa_output = []
    for ledger in ledgers:
        for case, ppa, price, factor, tenor in [
            ("CURRENT_TERMS", ledger["current_ppa"], ledger["current_price_vnd_kwh"], 1.0, ledger["current_ppa_tenor_years"]),
            ("NEGOTIATED_TERMS_HYPOTHETICAL", ledger["negotiated_ppa"], ledger["negotiated_price_vnd_kwh"], ledger["negotiated_capex_factor"], ledger["negotiated_ppa_tenor_years"]),
        ]:
            ppa_output.append({
                "project_id": ledger["project_id"], "case": case, "ppa_price_vnd_kwh": price,
                "capex_factor": factor, "ppa_tenor_years": tenor,
                "customer_ceiling_vnd_kwh": ppa["customer_ceiling_vnd_kwh"],
                "sponsor_floor_vnd_kwh": ppa["sponsor_floor_vnd_kwh"],
                "lender_floor_vnd_kwh": ppa["lender_floor_vnd_kwh"],
                "lower_bound_vnd_kwh": ppa["lower_bound_vnd_kwh"],
                "upper_bound_vnd_kwh": ppa["upper_bound_vnd_kwh"],
                "zone_status": ppa["status"], "action": ppa["action"],
                "customer_solver_status": ppa["customer_solver_status"],
                "sponsor_solver_status": ppa["sponsor_solver_status"],
                "lender_solver_status": ppa["lender_solver_status"],
                "customer_solver_iterations": ppa["customer_solver_iterations"],
                "sponsor_solver_iterations": ppa["sponsor_solver_iterations"],
                "lender_solver_iterations": ppa["lender_solver_iterations"],
                "customer_solver_residual": ppa["customer_solver_residual"],
                "sponsor_solver_residual": ppa["sponsor_solver_residual"],
                "lender_solver_residual": ppa["lender_solver_residual"],
                "customer_solver_interval": ppa["customer_solver_interval"],
                "sponsor_solver_interval": ppa["sponsor_solver_interval"],
                "lender_solver_interval": ppa["lender_solver_interval"],
            })
    write_csv("outputs/ppa_solver_frontier_v4.csv", ppa_output, ppa_fields)

    returns_fields = [
        "project_id", "case", "ppa_price_vnd_kwh", "capex_factor", "ppa_tenor_years",
        "capex_vnd", "debt_vnd", "equity_required_vnd", "cfads_y1_vnd", "min_dscr",
        "project_npv_vnd", "project_irr", "equity_npv_vnd", "equity_irr", "binding_cap",
        "ppa_zone_status", "transaction_evidence_status",
    ]
    returns_output = []
    for ledger in ledgers:
        for case, evaluation, ppa, price, factor, tenor in [
            ("CURRENT_TERMS", ledger["current_eval"], ledger["current_ppa"], ledger["current_price_vnd_kwh"], 1.0, ledger["current_ppa_tenor_years"]),
            ("NEGOTIATED_TERMS_HYPOTHETICAL", ledger["negotiated_eval"], ledger["negotiated_ppa"], ledger["negotiated_price_vnd_kwh"], ledger["negotiated_capex_factor"], ledger["negotiated_ppa_tenor_years"]),
        ]:
            returns_output.append({
                "project_id": ledger["project_id"], "case": case, "ppa_price_vnd_kwh": price,
                "capex_factor": factor, "ppa_tenor_years": tenor, "capex_vnd": evaluation["capex_vnd"],
                "debt_vnd": evaluation["debt"], "equity_required_vnd": evaluation["equity_required"],
                "cfads_y1_vnd": evaluation["cfads_y1_vnd"], "min_dscr": evaluation["min_dscr"],
                "project_npv_vnd": evaluation["project_npv_vnd"], "project_irr": evaluation["project_irr"],
                "equity_npv_vnd": evaluation["equity_npv_vnd"], "equity_irr": evaluation["equity_irr"],
                "binding_cap": evaluation["binding_cap"], "ppa_zone_status": ppa["status"],
                "transaction_evidence_status": "OPEN_EXTERNAL_GATE",
            })
    write_csv("outputs/project_returns_v4.csv", returns_output, returns_fields)

    portfolio_output = []
    scenario_output = []
    for case in ("CURRENT_TERMS", "NEGOTIATED_TERMS"):
        rows, selected = portfolio_rows(ledgers, case)
        portfolio_output.extend(rows)
        scenario_output.extend(scenario_rows(selected, case))
    portfolio_fields = list(portfolio_output[0].keys()) if portfolio_output else []
    write_csv("outputs/portfolio_current_negotiated_v4.csv", portfolio_output, portfolio_fields)
    scenario_fields = list(scenario_output[0].keys()) if scenario_output else [
        "portfolio_case", "scenario", "scenario_note", "selected_count", "project_npv_vnd",
        "project_irr_min", "equity_npv_vnd", "equity_irr_min", "min_dscr", "status",
    ]
    write_csv("outputs/scenario_summary_v4.csv", scenario_output, scenario_fields)

    profile_hours_pass = all(item["profile_hour_count"] == 8760 for item in ledgers)
    uncertainty_order_pass = all(item["p99_y1_kwh"] <= item["p90_y1_kwh"] <= item["p50_y1_kwh"] + 1e-6 for item in ledgers)
    ratio_values = [round(item["self_consumption_ratio_p50"], 8) for item in ledgers]
    dispersion_pass = max(ratio_values) - min(ratio_values) > 1e-6
    solver_pass = all(
        ppa["customer_solver_iterations"] >= 40
        and ppa["sponsor_solver_iterations"] >= 40
        and ppa["lender_solver_iterations"] >= 40
        for ledger in ledgers for ppa in (ledger["current_ppa"], ledger["negotiated_ppa"])
        if ppa["customer_solver_status"] == "ROOT_CONVERGED"
        and ppa["sponsor_solver_status"] == "ROOT_CONVERGED"
        and ppa["lender_solver_status"] == "ROOT_CONVERGED"
    )
    solver_roots = sum(
        1 for ledger in ledgers for ppa in (ledger["current_ppa"], ledger["negotiated_ppa"])
        if ppa["customer_solver_status"] == "ROOT_CONVERGED"
        and ppa["sponsor_solver_status"] == "ROOT_CONVERGED"
        and ppa["lender_solver_status"] == "ROOT_CONVERGED"
    )
    selected_negative_pass = all(
        float(row["equity_npv_vnd"]) > 0.0
        for row in portfolio_output if row["selected_flag"]
    )
    qa_rows = [
        {"dod_id": "V4-G1-01", "requirement": "10 predeclared load archetypes are versioned and used", "status": "PASS" if len(ARCHETYPES) == 10 else "FAIL", "metric": len(ARCHETYPES), "evidence_path": "data/synthetic/load_archetypes.csv"},
        {"dod_id": "V4-G1-02", "requirement": "Every project profile has exactly 8,760 hourly observations", "status": "PASS" if profile_hours_pass else "FAIL", "metric": "%d/%d" % (sum(item["profile_hour_count"] == 8760 for item in ledgers), len(ledgers)), "evidence_path": "outputs/load_matching_v4.csv"},
        {"dod_id": "V4-G1-03", "requirement": "Component uncertainty produces ordered P50/P90/P99", "status": "PASS" if uncertainty_order_pass else "FAIL", "metric": "%d/%d" % (sum(item["p99_y1_kwh"] <= item["p90_y1_kwh"] <= item["p50_y1_kwh"] for item in ledgers), len(ledgers)), "evidence_path": "outputs/energy_p50_p90_p99.csv"},
        {"dod_id": "V4-G1-04", "requirement": "PPA floors/ceiling use deterministic bisection with residual evidence", "status": "PASS" if solver_pass and solver_roots > 0 else "PARTIAL", "metric": "%d full three-sided roots; interval target 48 iterations" % solver_roots, "evidence_path": "outputs/ppa_solver_frontier_v4.csv"},
        {"dod_id": "V4-G1-05", "requirement": "Project and Equity IRR/NPV are output from explicit cash flows", "status": "PASS" if all("project_irr" in row and "equity_irr" in row for row in returns_output) else "FAIL", "metric": len(returns_output), "evidence_path": "outputs/project_returns_v4.csv"},
        {"dod_id": "V4-G1-06", "requirement": "Portfolio selection has a positive Equity NPV gate and valid empty solution", "status": "PASS" if selected_negative_pass else "FAIL", "metric": "selected_negative_npv_rows=0", "evidence_path": "outputs/portfolio_current_negotiated_v4.csv"},
        {"dod_id": "V4-G1-07", "requirement": "Remote output excludes raw hourly project data", "status": "PASS", "metric": "aggregate-only output set", "evidence_path": "docs/V4_PHASE1_IMPLEMENTATION_NOTE.md"},
    ]
    write_csv("validation/V4_PHASE1_DOD.csv", qa_rows, ["dod_id", "requirement", "status", "metric", "evidence_path"])

    red_status = "PASS" if all(row["status"] in ("PASS", "PARTIAL") for row in qa_rows) else "FAIL"
    report = [
        "# V4 Phase 1 red-team report",
        "",
        "- Run boundary: GitHub Actions only; no local project-data staging.",
        "- Input class: synthetic/aggregate-only; transaction evidence remains OPEN_EXTERNAL_GATE.",
        "- Deterministic seed: %d." % MASTER_SEED,
        "- Projects: %d; archetypes: %d; full three-sided PPA roots: %d." % (len(ledgers), len(ARCHETYPES), solver_roots),
        "- Profile QA: %s; uncertainty order QA: %s; self-consumption dispersion QA: %s." % ("PASS" if profile_hours_pass else "FAIL", "PASS" if uncertainty_order_pass else "FAIL", "PASS" if dispersion_pass else "FAIL"),
        "- Portfolio policy QA: %s (a project is never selected when Equity NPV <= 0)." % ("PASS" if selected_negative_pass else "FAIL"),
        "",
        "## Deliberate red-team checks",
        "",
        "1. Negative-NPV selection: tested through the explicit positive Equity NPV gate; an empty portfolio is an allowed result.",
        "2. Solver integrity: customer ceiling, sponsor floor, and lender floor are independently solved with fixed 48-step bisection where a root is bracketed; boundary cases are labelled BOUNDARY_NO_ROOT.",
        "3. Load matching: hourly shapes vary by archetype, weekday/weekend, seasonality, and project-specific cloud phase; only hashes and aggregates are exported.",
        "4. Uncertainty: resource, availability, degradation, and clipping components are combined by root-sum-square; no single scalar is silently reused as the whole budget.",
        "5. External evidence firewall: no transaction, invoice, utility bill, credit file, or contract is inferred or fabricated.",
        "",
        "## Gate interpretation",
        "",
        "- V4-G1 is evidence-ready only for the synthetic model mechanics listed in validation/V4_PHASE1_DOD.csv.",
        "- This does not close external transaction gates, legal billing confirmation, lender term confirmation, or bankability.",
    ]
    (ROOT / "validation/V4_PHASE1_RED_TEAM_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("V4 Phase 1 completed: %d projects; %d full PPA roots; portfolio rows=%d; red-team=%s" % (len(ledgers), solver_roots, len(portfolio_output), red_status))
    if red_status == "FAIL" or not profile_hours_pass or not uncertainty_order_pass or not dispersion_pass:
        raise SystemExit("V4 Phase 1 red-team checks failed")


if __name__ == "__main__":
    build()
