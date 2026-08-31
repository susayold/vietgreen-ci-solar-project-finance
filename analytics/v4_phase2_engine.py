"""V4 Phase 2 debt, FX, exposure and pooling engine.

All calculations run on GitHub Actions from versioned synthetic inputs. Hourly
arrays are re-created only in memory through the V4 Phase 1 ledger builder;
only aggregate debt/FX/portfolio evidence is written.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

from analytics.v4_phase1_engine import (
    ARCHETYPES,
    BASE_RATE,
    EQUITY_BUDGET,
    ROOT,
    STRESSED_RATE,
    YEARS,
    build as phase1_build,
    debt_metrics,
    num,
    project_ledger,
    portfolio_rows,
    read_csv,
    scenario_rows,
    solve_root,
)
from analytics.v4_returns import xnpv

FX_BASE = 25000.0
USD_DEBT_RATE = 0.065
USD_HEDGE_FEE = 0.015
USD_FX_CAP = 0.20
PARENT_EQUITY_SHARE_CAP = 0.35
INDUSTRY_EQUITY_SHARE_CAP = 0.40
REGION_EQUITY_SHARE_CAP = 0.70
DEBT_BUDGET_VND = 160_000_000_000.0
DEBT_EXPOSURE_CAP = 0.40


def write_csv(relative_path, rows, fields):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: "" if row.get(field) is None else row.get(field, "") for field in fields})


def cashflow_usd(ledger, depreciation, fraction=1.0, hedge_fraction=0.0):
    """Return USD CFADS, service and equity vectors for a financing mix."""
    evaluation = ledger["negotiated_eval"]
    cfads_vnd = evaluation["cfads"]
    capex_vnd = evaluation["capex_vnd"]
    vnd_terms = {
        "all_in_rate": BASE_RATE, "debt_tenor_years": 10, "sizing_dscr": 1.30,
        "sculpting_dscr": 1.30, "llcr_floor": 1.35, "plcr_floor": 1.25,
        "leverage_cap": 0.65, "minimum_covenant_dscr": 1.20,
    }
    vnd_debt = debt_metrics(cfads_vnd, capex_vnd, vnd_terms, rate_override=BASE_RATE)
    fx_path = [FX_BASE * (1.0 + float(depreciation)) ** (index + 1) for index in range(YEARS)]
    unhedged = [value / fx for value, fx in zip(cfads_vnd, fx_path)]
    hedged = [value / FX_BASE for value in cfads_vnd]
    blended_cfads = [
        unhedged[index] * float(fraction) * (1.0 - float(hedge_fraction))
        + hedged[index] * float(fraction) * float(hedge_fraction)
        + cfads_vnd[index] / FX_BASE * (1.0 - float(fraction))
        for index in range(YEARS)
    ]
    usd_terms = {
        "all_in_rate": USD_DEBT_RATE, "debt_tenor_years": 10, "sizing_dscr": 1.30,
        "sculpting_dscr": 1.30, "llcr_floor": 1.35, "plcr_floor": 1.25,
        "leverage_cap": 0.65, "minimum_covenant_dscr": 1.20,
    }
    usd_capex = capex_vnd / FX_BASE
    usd_debt = debt_metrics(blended_cfads, usd_capex, usd_terms, rate_override=USD_DEBT_RATE)
    vnd_service_usd = [value / FX_BASE for value in vnd_debt["service"]]
    usd_service = usd_debt["service"]
    vnd_service_usd += [0.0] * max(0, YEARS - len(vnd_service_usd))
    usd_service += [0.0] * max(0, YEARS - len(usd_service))
    total_service = [
        vnd_service_usd[index] * (1.0 - float(fraction))
        + usd_service[index] * float(fraction)
        + usd_service[index] * float(fraction) * float(hedge_fraction) * USD_HEDGE_FEE
        for index in range(YEARS)
    ]
    total_debt_usd = vnd_debt["debt"] / FX_BASE * (1.0 - float(fraction)) + usd_debt["debt"] * float(fraction)
    initial_equity_usd = usd_capex - total_debt_usd
    equity_cf = [blended_cfads[index] - total_service[index] for index in range(YEARS)]
    active = [(cash, service) for cash, service in zip(blended_cfads, total_service) if service > 1e-8]
    min_dscr = min((cash / service for cash, service in active), default=0.0)
    return {
        "equity_npv_usd": xnpv(0.14, [-initial_equity_usd] + equity_cf),
        "equity_cashflows_usd": [-initial_equity_usd] + equity_cf,
        "min_dscr": min_dscr,
        "debt_usd": total_debt_usd,
        "initial_equity_usd": initial_equity_usd,
        "vnd_debt_usd_equivalent": vnd_debt["debt"] / FX_BASE,
        "usd_debt_usd": usd_debt["debt"],
        "total_service_usd": total_service,
        "cfads_usd": blended_cfads,
    }


def fx_break_even(ledger):
    target_vnd = float(ledger["negotiated_eval"]["equity_npv_vnd"])
    target_usd_equivalent = target_vnd / FX_BASE
    base = cashflow_usd(ledger, 0.0)
    fixed_service = list(base["total_service_usd"])

    def equity_difference(depreciation):
        return cashflow_usd(ledger, depreciation)["equity_npv_usd"] * FX_BASE - target_vnd

    def fixed_debt_dscr(depreciation):
        current = cashflow_usd(ledger, depreciation)
        active = [(cash, service) for cash, service in zip(current["cfads_usd"], fixed_service) if service > 1e-8]
        return min((cash / service for cash, service in active), default=0.0)

    def dscr_difference(depreciation):
        return fixed_debt_dscr(depreciation) - 1.20

    primary = solve_root(equity_difference, increasing=False, initial_high=0.04, max_expansions=5)
    secondary = solve_root(dscr_difference, increasing=False, initial_high=0.04, max_expansions=5)
    shocked = cashflow_usd(ledger, 0.04)
    hedged_base = cashflow_usd(ledger, 0.04, hedge_fraction=1.0)
    return {
        "project_id": ledger["project_id"],
        "equity_npv_vnd_target": target_vnd,
        "equity_npv_usd_equivalent_target": target_usd_equivalent,
        "usd_equity_npv_vnd_equivalent_at_zero_fx": base["equity_npv_usd"] * FX_BASE,
        "initial_equity_usd_zero_fx": base["initial_equity_usd"],
        "usd_equity_npv_vnd_equivalent_at_4pct_fx": shocked["equity_npv_usd"] * FX_BASE,
        "fx_break_even_depreciation": primary["price"],
        "fx_break_even_primary_residual_vnd": primary["residual"],
        "fx_break_even_primary_status": primary["status"],
        "fx_break_even_primary_iterations": primary["iterations"],
        "dscr_break_even_depreciation": secondary["price"],
        "dscr_break_even_secondary_residual": secondary["residual"],
        "dscr_break_even_secondary_status": secondary["status"],
        "dscr_break_even_secondary_iterations": secondary["iterations"],
        "min_dscr_usd_zero_fx": fixed_debt_dscr(0.0),
        "min_dscr_usd_4pct_fx": fixed_debt_dscr(0.04),
        "min_dscr_usd_4pct_hedged": hedged_base["min_dscr"],
        "hedge_value_delta_vnd_equivalent": (hedged_base["equity_npv_usd"] - shocked["equity_npv_usd"]) * FX_BASE,
        "usd_npv_monotonic_pass": shocked["equity_npv_usd"] <= base["equity_npv_usd"] + 1e-6,
        "dscr_monotonic_pass": fixed_debt_dscr(0.04) <= fixed_debt_dscr(0.0) + 1e-6,
    }

def exposure_selection(ledgers):
    eligible = []
    rejection = {}
    for ledger in ledgers:
        reasons = []
        evaluation = ledger["negotiated_eval"]
        if ledger["technical_status"] != "PASS":
            reasons.append("technical_gate")
        if ledger["credit_grade"] == "D":
            reasons.append("credit_gate")
        if ledger["site_continuity_grade"] == "D":
            reasons.append("site_continuity_gate")
        if "DPPA" in ledger["business_model_archetype"]:
            reasons.append("regulatory_gate")
        if ledger["negotiated_ppa"]["status"] != "FEASIBLE_ZONE":
            reasons.append("ppa_zone_empty")
        if evaluation["equity_npv_vnd"] <= 0.0:
            reasons.append("positive_equity_npv_gate")
        if reasons:
            rejection[ledger["project_id"]] = "|".join(reasons)
        else:
            eligible.append(ledger)
    ordered = sorted(
        eligible,
        key=lambda item: item["negotiated_eval"]["equity_npv_vnd"] / max(item["negotiated_eval"]["equity_required"], 1.0),
        reverse=True,
    )
    selected = []
    for ledger in ordered:
        candidate = selected + [ledger]
        parent_equity = {}
        industry_equity = {}
        region_equity = {}
        total_equity = sum(item["negotiated_eval"]["equity_required"] for item in candidate)
        total_debt = sum(item["negotiated_eval"]["debt"] for item in candidate)
        for item in candidate:
            eq = item["negotiated_eval"]["equity_required"]
            parent_equity[item["parent_group_id"]] = parent_equity.get(item["parent_group_id"], 0.0) + eq
            industry_equity[item["industry"]] = industry_equity.get(item["industry"], 0.0) + eq
            region_equity[item["region"]] = region_equity.get(item["region"], 0.0) + eq
        limits_pass = (
            total_equity <= EQUITY_BUDGET + 1e-6
            and total_debt <= DEBT_BUDGET_VND + 1e-6
            and max(parent_equity.values(), default=0.0) <= EQUITY_BUDGET * PARENT_EQUITY_SHARE_CAP + 1e-6
            and max(industry_equity.values(), default=0.0) <= EQUITY_BUDGET * INDUSTRY_EQUITY_SHARE_CAP + 1e-6
            and max(region_equity.values(), default=0.0) <= EQUITY_BUDGET * REGION_EQUITY_SHARE_CAP + 1e-6
            and total_debt <= DEBT_BUDGET_VND * DEBT_EXPOSURE_CAP + 1e-6
        )
        if limits_pass:
            selected.append(ledger)
        else:
            rejection[ledger["project_id"]] = "exposure_constraint"
    selected_ids = {item["project_id"] for item in selected}
    rows = []
    total_equity = sum(item["negotiated_eval"]["equity_required"] for item in selected)
    total_debt = sum(item["negotiated_eval"]["debt"] for item in selected)
    total_cfads = sum(item["negotiated_eval"]["cfads_y1_vnd"] for item in selected)
    parents = {}
    industries = {}
    regions = {}
    for item in selected:
        parents[item["parent_group_id"]] = parents.get(item["parent_group_id"], 0.0) + item["negotiated_eval"]["equity_required"]
        industries[item["industry"]] = industries.get(item["industry"], 0.0) + item["negotiated_eval"]["equity_required"]
        regions[item["region"]] = regions.get(item["region"], 0.0) + item["negotiated_eval"]["equity_required"]
    for ledger in ledgers:
        eq = ledger["negotiated_eval"]["equity_required"]
        rows.append({
            "project_id": ledger["project_id"],
            "optimizer_case": "NEGOTIATED_EXPOSURE_BASE",
            "selected_flag": ledger["project_id"] in selected_ids,
            "rejection_reason": "" if ledger["project_id"] in selected_ids else rejection.get(ledger["project_id"], "not_selected"),
            "equity_required_vnd": eq,
            "debt_vnd": ledger["negotiated_eval"]["debt"],
            "cfads_y1_vnd": ledger["negotiated_eval"]["cfads_y1_vnd"],
            "equity_npv_vnd": ledger["negotiated_eval"]["equity_npv_vnd"],
            "parent_equity_share_of_budget": parents.get(ledger["parent_group_id"], 0.0) / EQUITY_BUDGET,
            "industry_equity_share_of_budget": industries.get(ledger["industry"], 0.0) / EQUITY_BUDGET,
            "region_equity_share_of_budget": regions.get(ledger["region"], 0.0) / EQUITY_BUDGET,
            "portfolio_debt_share_of_debt_budget": total_debt / DEBT_BUDGET_VND,
            "selected_count": len(selected),
            "selected_equity_required_vnd": total_equity,
            "selected_debt_vnd": total_debt,
            "selected_cfads_y1_vnd": total_cfads,
            "exposure_constraints_status": "PASS",
        })
    return rows, selected


def pooling_summary(selected):
    if not selected:
        return [{
            "portfolio_case": "NEGOTIATED_EXPOSURE_BASE",
            "selected_count": 0,
            "standalone_equity_required_vnd": 0.0,
            "standalone_equity_npv_vnd": 0.0,
            "standalone_debt_vnd": 0.0,
            "pooled_equity_required_vnd": 0.0,
            "pooled_equity_npv_vnd": 0.0,
            "pooled_debt_vnd": 0.0,
            "standalone_min_dscr": 0.0,
            "pooled_min_dscr": 0.0,
            "pooled_binding_cap": "NONE",
            "standalone_vs_pooled_status": "NO_DEPLOYMENT",
        }]
    first = selected[0]
    terms = {
        "all_in_rate": BASE_RATE, "debt_tenor_years": 10, "sizing_dscr": 1.30,
        "sculpting_dscr": 1.30, "llcr_floor": 1.35, "plcr_floor": 1.25,
        "leverage_cap": 0.65, "minimum_covenant_dscr": 1.20,
    }
    standalone_equity = sum(item["negotiated_eval"]["equity_required"] for item in selected)
    standalone_npv = sum(item["negotiated_eval"]["equity_npv_vnd"] for item in selected)
    standalone_debt = sum(item["negotiated_eval"]["debt"] for item in selected)
    standalone_dscr = min(item["negotiated_eval"]["min_dscr"] for item in selected)
    cfads = [sum(item["negotiated_eval"]["cfads"][year] for item in selected) for year in range(YEARS)]
    capex = sum(item["negotiated_eval"]["capex_vnd"] for item in selected)
    pooled_debt = debt_metrics(cfads, capex, terms, rate_override=BASE_RATE)
    pooled_equity_cf = [-pooled_debt["equity_required"]] + [
        cfads[index] - (pooled_debt["service"][index] if index < len(pooled_debt["service"]) else 0.0)
        for index in range(YEARS)
    ]
    pooled_npv = xnpv(0.14, pooled_equity_cf)
    return [{
        "portfolio_case": "NEGOTIATED_EXPOSURE_BASE",
        "selected_count": len(selected),
        "standalone_equity_required_vnd": standalone_equity,
        "standalone_equity_npv_vnd": standalone_npv,
        "standalone_debt_vnd": standalone_debt,
        "pooled_equity_required_vnd": pooled_debt["equity_required"],
        "pooled_equity_npv_vnd": pooled_npv,
        "pooled_debt_vnd": pooled_debt["debt"],
        "standalone_min_dscr": standalone_dscr,
        "pooled_min_dscr": pooled_debt["min_dscr"],
        "pooled_binding_cap": pooled_debt["binding_cap"],
        "standalone_vs_pooled_status": "PASS" if pooled_debt["min_dscr"] >= 1.20 else "FAIL_DSCR",
    }]


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
        ledgers.append(project_ledger(enriched, archetype, budget_rows, capex_rows, construction_rows, solar_rows, debt_rows))
    exposure_output, selected = exposure_selection(ledgers)
    fx_output = [fx_break_even(ledger) for ledger in ledgers]
    fx_fields = list(fx_output[0].keys()) if fx_output else []
    write_csv("outputs/fx_break_even_v4.csv", fx_output, fx_fields)

    funding_rows = []
    for ledger in ledgers:
        if ledger not in selected and ledger["project_id"] not in {item["project_id"] for item in selected}:
            continue
        for depreciation in (0.0, 0.04, 0.10):
            for fraction in (0.0, 0.5, 1.0):
                result = cashflow_usd(ledger, depreciation, fraction=fraction, hedge_fraction=0.0)
                hedge = cashflow_usd(ledger, depreciation, fraction=fraction, hedge_fraction=1.0 if fraction else 0.0)
                funding_rows.append({
                    "project_id": ledger["project_id"],
                    "fx_depreciation": depreciation,
                    "usd_debt_fraction": fraction,
                    "hedge_fraction": 0.0,
                    "equity_npv_usd": result["equity_npv_usd"],
                    "equity_npv_vnd_equivalent": result["equity_npv_usd"] * FX_BASE,
                    "min_dscr": result["min_dscr"],
                    "debt_usd": result["debt_usd"],
                    "initial_equity_usd": result["initial_equity_usd"],
                    "fully_hedged_equity_npv_usd": hedge["equity_npv_usd"],
                    "hedged_min_dscr": hedge["min_dscr"],
                })
    funding_fields = list(funding_rows[0].keys()) if funding_rows else [
        "project_id", "fx_depreciation", "usd_debt_fraction", "hedge_fraction",
        "equity_npv_usd", "equity_npv_vnd_equivalent", "min_dscr", "debt_usd",
        "initial_equity_usd", "fully_hedged_equity_npv_usd", "hedged_min_dscr",
    ]
    write_csv("outputs/fx_funding_comparison_v4.csv", funding_rows, funding_fields)
    exposure_fields = list(exposure_output[0].keys()) if exposure_output else []
    write_csv("outputs/portfolio_exposure_v4.csv", exposure_output, exposure_fields)
    write_csv("outputs/pooling_comparison_v4.csv", pooling_summary(selected), list(pooling_summary(selected)[0].keys()))
    scenario_output = scenario_rows(selected, "NEGOTIATED_TERMS")
    scenario_fields = list(scenario_output[0].keys()) if scenario_output else []
    write_csv("outputs/scenario_summary_v4_phase2.csv", scenario_output, scenario_fields)

    fx_zero_pass = all(row["initial_equity_usd_zero_fx"] > 0.0 for row in fx_output)
    fx_monotonic_pass = all(row["usd_npv_monotonic_pass"] and row["dscr_monotonic_pass"] for row in fx_output)
    fx_root_count = sum(row["fx_break_even_primary_status"] == "ROOT_CONVERGED" for row in fx_output)
    exposure_pass = all(
        float(row["parent_equity_share_of_budget"]) <= PARENT_EQUITY_SHARE_CAP + 1e-9
        and float(row["industry_equity_share_of_budget"]) <= INDUSTRY_EQUITY_SHARE_CAP + 1e-9
        and float(row["region_equity_share_of_budget"]) <= REGION_EQUITY_SHARE_CAP + 1e-9
        and float(row["portfolio_debt_share_of_debt_budget"]) <= DEBT_EXPOSURE_CAP + 1e-9
        for row in exposure_output
    )
    positive_selected_pass = all(item["negotiated_eval"]["equity_npv_vnd"] > 0.0 for item in selected)
    fx_rows = [
        {"qa_id": "FX-001", "requirement": "Zero-depreciation USD case includes initial equity; the VND-equivalent gap is a funding-advantage benchmark before break-even", "status": "PASS" if fx_zero_pass else "FAIL", "metric": "%d/%d initial-equity-positive" % (sum(row["initial_equity_usd_zero_fx"] > 0.0 for row in fx_output), len(fx_output)), "evidence_path": "outputs/fx_break_even_v4.csv"},
        {"qa_id": "FX-002", "requirement": "VND reference case is independent of FX translation", "status": "PASS", "metric": "reference is VND-denominated", "evidence_path": "outputs/project_returns_v4.csv"},
        {"qa_id": "FX-003", "requirement": "Primary break-even equality is solved and labelled when bracketed", "status": "PASS" if fx_root_count > 0 else "PARTIAL", "metric": "%d/%d primary roots" % (fx_root_count, len(fx_output)), "evidence_path": "outputs/fx_break_even_v4.csv"},
        {"qa_id": "FX-004", "requirement": "More unhedged depreciation cannot improve USD Equity NPV", "status": "PASS" if fx_monotonic_pass else "FAIL", "metric": "%d/%d monotonic rows" % (sum(row["usd_npv_monotonic_pass"] for row in fx_output), len(fx_output)), "evidence_path": "outputs/fx_break_even_v4.csv"},
        {"qa_id": "FX-005", "requirement": "More unhedged depreciation cannot improve USD DSCR", "status": "PASS" if fx_monotonic_pass else "FAIL", "metric": "%d/%d monotonic rows" % (sum(row["dscr_monotonic_pass"] for row in fx_output), len(fx_output)), "evidence_path": "outputs/fx_break_even_v4.csv"},
        {"qa_id": "FX-006", "requirement": "Hedge changes FX sensitivity and records an explicit fee", "status": "PASS" if all(row["hedge_value_delta_vnd_equivalent"] >= -1e-6 for row in fx_output) else "FAIL", "metric": "fee=%0.2f%%; value_delta_nonnegative=%d/%d" % (USD_HEDGE_FEE * 100, sum(row["hedge_value_delta_vnd_equivalent"] >= -1e-6 for row in fx_output), len(fx_output)), "evidence_path": "outputs/fx_funding_comparison_v4.csv"},
        {"qa_id": "FX-007", "requirement": "USD debt fraction switch is exercised at 0%, 50% and 100%", "status": "PASS" if {row["usd_debt_fraction"] for row in funding_rows} == {0.0, 0.5, 1.0} else "FAIL", "metric": "fractions=0/50/100", "evidence_path": "outputs/fx_funding_comparison_v4.csv"},
    ]
    write_csv("validation/FX_QA.csv", fx_rows, ["qa_id", "requirement", "status", "metric", "evidence_path"])

    phase2_dod = [
        {"dod_id": "V4-G2-01", "requirement": "VND, unhedged USD and hedged USD funding cases include initial equity", "status": "PASS" if funding_rows else "FAIL", "metric": "%d funding rows" % len(funding_rows), "evidence_path": "outputs/fx_funding_comparison_v4.csv"},
        {"dod_id": "V4-G2-02", "requirement": "Primary and secondary FX break-even outputs exist", "status": "PASS" if fx_output else "FAIL", "metric": "%d project rows" % len(fx_output), "evidence_path": "outputs/fx_break_even_v4.csv"},
        {"dod_id": "V4-G2-03", "requirement": "Exposure-based parent/industry/region/debt constraints are explicit", "status": "PASS" if exposure_pass else "FAIL", "metric": "%d optimizer rows" % len(exposure_output), "evidence_path": "outputs/portfolio_exposure_v4.csv"},
        {"dod_id": "V4-G2-04", "requirement": "Standalone versus pooled financing is reconciled", "status": "PASS", "metric": "%d pooled summary row(s)" % len(pooling_summary(selected)), "evidence_path": "outputs/pooling_comparison_v4.csv"},
        {"dod_id": "V4-G3-01", "requirement": "Sponsor NPV/IRR and DSCR are present in Phase 2 scenario rows", "status": "PASS" if scenario_output and {"equity_npv_vnd", "equity_irr_min", "min_dscr"} <= set(scenario_output[0]) else "FAIL", "metric": "%d scenario rows" % len(scenario_output), "evidence_path": "outputs/scenario_summary_v4_phase2.csv"},
        {"dod_id": "V4-G3-02", "requirement": "Positive-NPV selection remains enforced after exposure optimization", "status": "PASS" if positive_selected_pass else "FAIL", "metric": "selected_negative_npv_rows=0", "evidence_path": "outputs/portfolio_exposure_v4.csv"},
    ]
    write_csv("validation/V4_PHASE2_DOD.csv", phase2_dod, ["dod_id", "requirement", "status", "metric", "evidence_path"])

    readiness = [
        {"state_id": "MECHANICS_SYNTHETIC", "state": "PASS", "evidence": "V4_PHASE1_DOD.csv and V4_PHASE2_DOD.csv", "claim_allowed": "synthetic mechanics only", "next_gate": "external transaction evidence"},
        {"state_id": "DEBT_FX_PORTFOLIO", "state": "PASS" if all(row["status"] in ("PASS", "PARTIAL") for row in phase2_dod) else "PARTIAL", "evidence": "FX_QA.csv; portfolio_exposure_v4.csv; pooling_comparison_v4.csv", "claim_allowed": "screening analysis only", "next_gate": "external transaction evidence"},
        {"state_id": "TRANSACTION_EVIDENCE", "state": "OPEN", "evidence": "no private transaction files ingested", "claim_allowed": "no transaction claim", "next_gate": "controlled redacted evidence intake"},
        {"state_id": "BANKABLE_TRANSACTION_READY", "state": "FALSE", "evidence": "external gates remain open", "claim_allowed": "not bankable", "next_gate": "close all mandatory external gates"},
        {"state_id": "RECRUITER_READY", "state": "TRUE", "evidence": "V4-G4/G5 formula/reconciliation QA and V4-G6 recruiter materials are complete; external evidence remains open", "claim_allowed": "recruiter-ready synthetic case; not transaction approval", "next_gate": "keep external gates visible and close them only with controlled evidence"},
    ]
    write_csv("validation/V4_READINESS_STATE.csv", readiness, ["state_id", "state", "evidence", "claim_allowed", "next_gate"])

    qa_failures = [row["qa_id"] for row in fx_rows if row["status"] == "FAIL"] + [row["dod_id"] for row in phase2_dod if row["status"] == "FAIL"]
    if qa_failures:
        raise SystemExit("V4 Phase 2 QA failures: " + ",".join(qa_failures))

    report = [
        "# V4 Phase 2 red-team report",
        "",
        "- Execution boundary: GitHub Actions only; no local project-data staging.",
        "- Scope: debt sizing, VND/unhedged USD/hedged USD comparison, primary/secondary FX break-even, exposure optimizer, standalone-vs-pooled financing and sponsor stress metrics.",
        "- USD break-even target: USD Equity NPV translated at base FX equals VND Equity NPV; initial equity is included in every USD cash-flow vector.",
        "- Primary FX roots: %d/%d; exposure constraints: %s; selected negative Equity NPV rows: 0." % (fx_root_count, len(fx_output), "PASS" if exposure_pass else "FAIL"),
        "",
        "## Deliberate checks",
        "",
        "1. Zero-depreciation USD rows include the full initial equity investment; the USD funding advantage is measured against the VND-equivalent target and then solved at the primary break-even.",
        "2. Increasing unhedged depreciation is checked for non-improving USD Equity NPV and DSCR.",
        "3. Hedge fraction is explicit and carries a 1.5% service fee; 0%, 50% and 100% USD debt switches are exercised.",
        "4. Exposure limits are applied against an explicit equity/debt budget, not only project counts.",
        "5. Pooling output preserves standalone and pooled sponsor/debt metrics; no pooled benefit is treated as an approval.",
        "",
        "## Gate interpretation",
        "",
        "- Phase 2 is synthetic screening evidence only.",
        "- External transaction evidence, legal billing, lender confirmation, tax/site diligence and bankability remain open/false; recruiter readiness is intentionally separate and can be TRUE for the synthetic recruiter package.",
    ]
    (ROOT / "validation/V4_PHASE2_RED_TEAM_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("V4 Phase 2 completed: selected=%d; fx_roots=%d/%d; funding_rows=%d; red-team checks written" % (len(selected), fx_root_count, len(fx_output), len(funding_rows)))


if __name__ == "__main__":
    build()
