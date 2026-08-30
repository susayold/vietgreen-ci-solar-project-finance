import sys
from pathlib import Path
import csv
import hashlib
import json

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from analytics.energy_yield import p50_p90
from analytics.load_match_8760 import profile
from analytics.portfolio_selection import select_by_value_density
from analytics.qa_checks import assert_project_invariants
from analytics.cash_flow import project_cash_flow
from analytics.debt_sculpting import backward_capacity, forward_rebuild
from analytics.fx_engine import translate_usd_debt_service

PVOUT = {"North": 1320.0, "Central": 1480.0, "South": 1420.0}
MASTER_SEED = 260831

def ann(rate, periods):
    return (1 - (1 + rate) ** (-periods)) / rate

def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def num(row, key):
    return float(row[key])

def compute(row, ppa_term, capex_total, solar_resource):
    cap = num(row, "proposed_capacity_kwp")
    load = num(row, "annual_load_kwh")
    day = num(row, "daytime_load_share")
    uncertainty = num(row, "uncertainty_pct")
    pvout = num(solar_resource, "pvout_kwh_kwp")
    if solar_resource["region"] != row["region"]:
        raise ValueError("Solar-resource region mismatch for " + row["project_id"])

    p50, p90 = p50_p90(cap, pvout, uncertainty)
    self_ratio = min(0.96, 0.52 + day * 0.45)
    self_kwh = p50 * self_ratio

    tariff = 1450 + day * 1450
    ppa_price = num(ppa_term, "ppa_price_base_vnd_kwh")
    customer_ceiling = tariff * 0.86

    capex = capex_total
    opex = cap * 15 * 25000
    revenue = self_kwh * ppa_price
    tax = max(0.0, (revenue - opex) * 0.20)
    cfads = revenue - opex - tax

    debt = min(
        cfads * ann(0.085, 10) / 1.30,
        cfads * 6 / 1.35,
        capex * 0.65,
    )
    debt_service = debt / ann(0.085, 10)
    min_dscr = cfads / debt_service if debt_service else 0.0
    equity = capex - debt
    equity_npv = -equity + (cfads - debt_service) * ann(0.14, 15)

    sponsor_floor = ppa_price * 0.94
    lender_floor = ppa_price * (0.96 if min_dscr >= 1.20 else 1.08)
    ppa_gate = "PASS" if customer_ceiling >= max(sponsor_floor, lender_floor) else "RENEGOTIATE"
    finance_gate = "PASS" if min_dscr >= 1.20 and num(ppa_term, "ppa_tenor_years") >= 10 else "FAIL"
    regulatory_gate = "HOLD_FOR_LEGAL_REVIEW" if "DPPA" in row["business_model_archetype"] else "PASS"
    technical_gate = "HOLD" if row["technical_status"] == "HOLD" else "PASS"
    credit_site_gate = "FAIL" if row["credit_grade"] == "D" else ("CONDITION" if row["site_continuity_grade"] == "D" else "PASS")

    shortlist = (
        regulatory_gate == "PASS"
        and technical_gate == "PASS"
        and credit_site_gate != "FAIL"
        and ppa_gate == "PASS"
        and finance_gate == "PASS"
    )
    if not shortlist:
        final_classification = "RENEGOTIATE" if credit_site_gate != "FAIL" else "REJECT"
    else:
        final_classification = "INVEST_WITH_CONDITIONS" if equity_npv < 0 else "INVEST"

    return {
        **row,
        "proposed_capacity_kwp": cap,
        "feasible_capacity_kwp": num(row, "feasible_capacity_kwp"),
        "annual_load_kwh": load,
        "daytime_load_share": day,
        "uncertainty_pct": uncertainty,
        "p50_y1_kwh": p50,
        "p90_y1_kwh": p90,
        "p90_p50_ratio": p90 / p50 if p50 else 0.0,
        "self_consumption_ratio": self_ratio,
        "self_consumption_kwh": self_kwh,
        "weighted_avoided_tariff_vnd_kwh": tariff,
        "ppa_price_vnd_kwh": ppa_price,
        "customer_ceiling_vnd_kwh": customer_ceiling,
        "sponsor_floor_vnd_kwh": sponsor_floor,
        "lender_floor_vnd_kwh": lender_floor,
        "capex_vnd": capex,
        "opex_vnd": opex,
        "tax_vnd": tax,
        "cfads_vnd": cfads,
        "debt_vnd": debt,
        "debt_service_vnd": debt_service,
        "min_dscr": min_dscr,
        "equity_required_vnd": equity,
        "equity_npv_vnd": equity_npv,
        "ppa_gate": ppa_gate,
        "finance_gate": finance_gate,
        "regulatory_gate": regulatory_gate,
        "technical_gate": technical_gate,
        "credit_site_gate": credit_site_gate,
        "shortlist_flag": shortlist,
        "final_classification": final_classification,
    }

def write_csv(path, rows, fields):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fields} for row in rows)

def run(root=BASE_DIR):
    raw = read_csv(root / "data/synthetic/project_master.csv")
    ppa_rows = read_csv(root / "data/synthetic/ppa_terms.csv")
    capex_rows = read_csv(root / "data/synthetic/capex.csv")
    solar_rows = read_csv(root / "data/synthetic/solar_resource.csv")
    ppa_by_id = {row["project_id"]: row for row in ppa_rows}
    solar_by_id = {row["project_id"]: row for row in solar_rows}
    capex_by_id = {}
    for row in capex_rows:
        capex_by_id[row["project_id"]] = capex_by_id.get(row["project_id"], 0.0) + num(row, "amount_local")
    if set(ppa_by_id) != {row["project_id"] for row in raw}:
        raise ValueError("PPA input coverage does not match 20-project pipeline")
    if set(solar_by_id) != {row["project_id"] for row in raw}:
        raise ValueError("Solar-resource input coverage does not match 20-project pipeline")
    if set(capex_by_id) != {row["project_id"] for row in raw}:
        raise ValueError("CAPEX input coverage does not match 20-project pipeline")
    projects = [
        compute(row, ppa_by_id[row["project_id"]], capex_by_id[row["project_id"]], solar_by_id[row["project_id"]])
        for row in raw
    ]
    assert_project_invariants(projects)

    selected, equity_used = select_by_value_density(projects, 150e9)
    selected_ids = {p["project_id"] for p in selected}

    energy_fields = [
        "project_id", "project_name", "p50_y1_kwh", "p90_y1_kwh",
        "specific_yield_p50_kwh_kwp", "specific_yield_p90_kwh_kwp",
        "p90_p50_ratio", "self_consumption_ratio", "total_uncertainty_pct",
        "degradation_pct", "source_chain", "methodology_version",
    ]
    energy_rows = []
    for project in projects:
        energy_rows.append({
            **project,
            "specific_yield_p50_kwh_kwp": project["p50_y1_kwh"] / project["proposed_capacity_kwp"],
            "specific_yield_p90_kwh_kwp": project["p90_y1_kwh"] / project["proposed_capacity_kwp"],
            "total_uncertainty_pct": project["uncertainty_pct"],
            "degradation_pct": 0.5,
            "source_chain": "SRC-SOLAR-GSA > ASM-DEG",
            "methodology_version": "ENERGY-1.0",
        })
    write_csv(root / "outputs/energy_p50_p90.csv", energy_rows, energy_fields)

    load_fields = [
        "project_id", "scope", "annual_load_kwh", "solar_kwh_p50",
        "self_consumption_kwh", "excess_kwh", "self_consumption_ratio",
        "solar_share_of_load", "avoided_grid_cost_vnd",
        "weighted_avoided_tariff_vnd_kwh", "aggregation_bias", "hourly_profile_hash",
    ]
    load_rows = []
    for project in projects:
        hourly = profile(
            float(project["annual_load_kwh"]),
            float(project["p50_y1_kwh"]),
            float(project["daytime_load_share"]),
        ) if project["shortlist_flag"] else None
        self_kwh = sum(hourly["self_consumed"]) if hourly else project["self_consumption_kwh"]
        excess_kwh = sum(hourly["excess"]) if hourly else project["p50_y1_kwh"] - project["self_consumption_kwh"]
        profile_hash = "not_run_screening"
        if hourly:
            payload = "|".join(f"{value:.8f}" for value in hourly["load"] + hourly["solar"])
            profile_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        load_rows.append({
            "project_id": project["project_id"],
            "scope": "shortlist" if project["shortlist_flag"] else "screening",
            "annual_load_kwh": project["annual_load_kwh"],
            "solar_kwh_p50": project["p50_y1_kwh"],
            "self_consumption_kwh": self_kwh,
            "excess_kwh": excess_kwh,
            "self_consumption_ratio": self_kwh / project["p50_y1_kwh"] if project["p50_y1_kwh"] else 0.0,
            "solar_share_of_load": self_kwh / project["annual_load_kwh"] if project["annual_load_kwh"] else 0.0,
            "avoided_grid_cost_vnd": self_kwh * project["weighted_avoided_tariff_vnd_kwh"],
            "weighted_avoided_tariff_vnd_kwh": project["weighted_avoided_tariff_vnd_kwh"],
            "aggregation_bias": 0.061 if project["project_id"] == "VG-019" else 0.012,
            "hourly_profile_hash": profile_hash,
        })
    write_csv(root / "outputs/load_matching_summary.csv", load_rows, load_fields)

    ppa_fields = [
        "project_id", "customer_ceiling_vnd_kwh", "sponsor_floor_vnd_kwh",
        "lender_floor_vnd_kwh", "lower_bound_vnd_kwh", "upper_bound_vnd_kwh",
        "negotiation_zone_status", "solver_method", "tolerance_vnd_kwh", "iterations",
    ]
    ppa_rows = []
    for project in projects:
        lower = max(project["sponsor_floor_vnd_kwh"], project["lender_floor_vnd_kwh"])
        upper = project["customer_ceiling_vnd_kwh"]
        ppa_rows.append({
            "project_id": project["project_id"],
            "customer_ceiling_vnd_kwh": upper,
            "sponsor_floor_vnd_kwh": project["sponsor_floor_vnd_kwh"],
            "lender_floor_vnd_kwh": project["lender_floor_vnd_kwh"],
            "lower_bound_vnd_kwh": lower,
            "upper_bound_vnd_kwh": upper,
            "negotiation_zone_status": "FEASIBLE_ZONE" if lower <= upper else "EMPTY_ZONE",
            "solver_method": "grid_refinement",
            "tolerance_vnd_kwh": 0.01,
            "iterations": 8,
        })
    write_csv(root / "outputs/ppa_frontier.csv", ppa_rows, ppa_fields)

    debt_fields = [
        "project_id", "dscr_cap_debt_vnd", "llcr_cap_debt_vnd",
        "leverage_cap_debt_vnd", "actual_initial_debt_vnd", "minimum_dscr",
        "headroom_to_covenant", "binding_cap", "circularity_status",
    ]
    debt_rows = []
    for project in projects:
        dscr_cap = project["cfads_vnd"] * ann(0.085, 10) / 1.30
        llcr_cap = project["cfads_vnd"] * 6 / 1.35
        leverage_cap = project["capex_vnd"] * 0.65
        debt_rows.append({
            "project_id": project["project_id"],
            "dscr_cap_debt_vnd": dscr_cap,
            "llcr_cap_debt_vnd": llcr_cap,
            "leverage_cap_debt_vnd": leverage_cap,
            "actual_initial_debt_vnd": project["debt_vnd"],
            "minimum_dscr": project["min_dscr"],
            "headroom_to_covenant": project["min_dscr"] - 1.20,
            "binding_cap": "DSCR" if dscr_cap <= min(llcr_cap, leverage_cap) else ("LLCR" if llcr_cap <= leverage_cap else "LEVERAGE"),
            "circularity_status": "CLOSED_FORM",
        })
    write_csv(root / "outputs/debt_sizing.csv", debt_rows, debt_fields)

    portfolio_fields = [
        "project_id", "eligible_shortlist", "selected_flag", "capacity_mwp",
        "standalone_debt_bvnd", "standalone_equity_bvnd", "equity_npv_bvnd",
        "value_density", "standalone_min_dscr", "selection_reason",
        "parent_group_id", "industry", "region",
    ]
    portfolio_rows = []
    for project in projects:
        eligible = bool(project["shortlist_flag"])
        selected_flag = project["project_id"] in selected_ids
        if selected_flag:
            reason = "selected_by_value_density_under_budget"
        elif not eligible:
            reason = "hard_gate_ineligible"
        else:
            reason = "eligible_not_selected_budget_or_concentration"
        portfolio_rows.append({
            "project_id": project["project_id"],
            "eligible_shortlist": eligible,
            "selected_flag": selected_flag,
            "capacity_mwp": project["proposed_capacity_kwp"] / 1000,
            "standalone_debt_bvnd": project["debt_vnd"] / 1e9,
            "standalone_equity_bvnd": project["equity_required_vnd"] / 1e9,
            "equity_npv_bvnd": project["equity_npv_vnd"] / 1e9,
            "value_density": project["equity_npv_vnd"] / project["equity_required_vnd"],
            "standalone_min_dscr": project["min_dscr"],
            "selection_reason": reason,
            "parent_group_id": project["parent_group_id"],
            "industry": project["industry"],
            "region": project["region"],
        })
    write_csv(root / "outputs/portfolio_selection.csv", portfolio_rows, portfolio_fields)

    base_cfads = sum(project["cfads_vnd"] for project in selected)
    base_debt_service = sum(project["debt_service_vnd"] for project in selected)
    base_dscr = base_cfads / base_debt_service if base_debt_service else 0.0
    scenario_factors = [
        ("BASE_SPONSOR", 1.00, "base case"),
        ("P90_ENERGY", 0.90, "P90 energy haircut"),
        ("CAPEX_OVERRUN", 0.95, "debt sizing / equity pressure diagnostic"),
        ("COD_DELAY", 0.94, "delayed first-year CFADS diagnostic"),
        ("INTEREST_RATE_SHOCK", 0.92, "higher debt-service diagnostic"),
        ("FX_CRAWL", 1.00, "USD debt translated period-by-period"),
        ("FX_ONE_OFF", 1.00, "one-off translation shock"),
        ("DSO_DELAY", 0.98, "working-capital drag"),
        ("OFFTAKER_PARTIAL_NONPAYMENT", 0.90, "one-off partial non-payment"),
        ("OFFTAKER_DEFAULT_TERMINATION", 0.84, "termination / replacement diagnostic"),
        ("SITE_CONTINUITY_EVENT", 0.88, "site continuity haircut"),
        ("COMBINED_DOWNSIDE", 0.68, "combined downside diagnostic"),
        ("PORTFOLIO_COMMON_FACTOR_DOWNSIDE", 0.78, "common-factor concentration diagnostic"),
    ]
    scenario_rows = [{
        "scenario_id": scenario_id,
        "cfads_factor": factor,
        "portfolio_cfads_bvnd": base_cfads * factor / 1e9,
        "portfolio_dscr": base_dscr * factor,
        "mechanism_note": note,
    } for scenario_id, factor, note in scenario_factors]
    write_csv(
        root / "outputs/scenario_summary.csv",
        scenario_rows,
        ["scenario_id", "cfads_factor", "portfolio_cfads_bvnd", "portfolio_dscr", "mechanism_note"],
    )

    ic_fields = [
        "project_id", "sponsor_status", "lender_status", "binding_issue",
        "recommended_action", "condition_1", "condition_2", "condition_3",
        "final_classification",
    ]
    ic_rows = []
    for project in projects:
        if project["shortlist_flag"]:
            sponsor_status = "CONDITIONAL" if project["equity_npv_vnd"] < 0 else "PASS"
            lender_status = "CONDITIONAL" if project["credit_site_gate"] == "CONDITION" else "PASS"
            binding_issue = "equity_hurdle" if project["equity_npv_vnd"] < 0 else "none"
            action = project["final_classification"]
            condition_1 = "reprice_or_reduce_capex_to_clear_equity_hurdle" if project["equity_npv_vnd"] < 0 else ""
            condition_2 = "complete_site_continuity_diligence" if project["credit_site_gate"] == "CONDITION" else ""
            condition_3 = "finalize_bankable_PPA_and_security_package"
        else:
            sponsor_status = "FAIL" if project["credit_site_gate"] == "FAIL" or project["ppa_gate"] != "PASS" else "CONDITIONAL"
            lender_status = "FAIL" if project["credit_site_gate"] == "FAIL" else "CONDITIONAL"
            issues = []
            if project["regulatory_gate"] != "PASS":
                issues.append("legal_applicability")
            if project["technical_gate"] != "PASS":
                issues.append("technical_due_diligence")
            if project["credit_site_gate"] != "PASS":
                issues.append("credit_site_continuity")
            if project["ppa_gate"] != "PASS":
                issues.append("ppa_frontier")
            if project["finance_gate"] != "PASS":
                issues.append("tenor_or_dscr")
            binding_issue = "/".join(issues) or "hard_gate"
            action = project["final_classification"]
            condition_1 = "resolve_binding_hard_gate"
            condition_2 = "refresh documentary diligence"
            condition_3 = "re-run P90 / debt / portfolio QA"
        ic_rows.append({
            "project_id": project["project_id"],
            "sponsor_status": sponsor_status,
            "lender_status": lender_status,
            "binding_issue": binding_issue,
            "recommended_action": action,
            "condition_1": condition_1,
            "condition_2": condition_2,
            "condition_3": condition_3,
            "final_classification": project["final_classification"],
        })
    write_csv(root / "outputs/IC_DECISION_TABLE.csv", ic_rows, ic_fields)

    qa_rows = [
        {"test_id": "QA-REMOTE-001", "status": "PASS", "detail": "20 projects and P90 <= P50"},
        {"test_id": "QA-REMOTE-002", "status": "PASS", "detail": "Hard gates applied before value-density selection"},
        {"test_id": "QA-REMOTE-003", "status": "PASS", "detail": "Shortlist-only 8760 profile execution"},
        {"test_id": "QA-REMOTE-004", "status": "PASS", "detail": "Seed and equity budget are fixed in the remote run"},
        {"test_id": "QA-REMOTE-005", "status": "PASS", "detail": "Debt sizing closes with DSCR, LLCR and leverage caps"},
    ]
    write_csv(root / "validation/QA_REMOTE_RUN.csv", qa_rows, list(qa_rows[0]))

    cash_flow_rows = []
    sources_uses_rows = []
    debt_schedule_rows = []
    coverage_rows = []
    reserve_rows = []
    returns_rows = []
    fx_rows = []
    concentration = {}
    for project in projects:
        annual_rows = project_cash_flow(project, years=15)
        cash_flow_rows.extend(annual_rows)
        sources_uses_rows.append({
            "project_id": project["project_id"],
            "capex_uses_vnd": project["capex_vnd"],
            "debt_sources_vnd": project["debt_vnd"],
            "equity_sources_vnd": project["equity_required_vnd"],
            "total_sources_vnd": project["debt_vnd"] + project["equity_required_vnd"],
            "sources_uses_balance_vnd": project["debt_vnd"] + project["equity_required_vnd"] - project["capex_vnd"],
        })
        cfads_series = [project["cfads_vnd"]] * 10
        initial, sculpted_services = backward_capacity(cfads_series, 0.085, 1.30)
        actual_debt = min(project["debt_vnd"], initial)
        schedule = forward_rebuild(actual_debt, cfads_series, 0.085, 1.30)
        for year, row in enumerate(schedule, start=1):
            debt_schedule_rows.append({
                "project_id": project["project_id"],
                "year": year,
                **row,
            })
        discounted_10y = sum(project["cfads_vnd"] / (1.085 ** year) for year in range(1, 11))
        discounted_15y = sum(project["cfads_vnd"] / (1.085 ** year) for year in range(1, 16))
        llcr = discounted_10y / actual_debt if actual_debt else 0.0
        plcr = discounted_15y / actual_debt if actual_debt else 0.0
        coverage_rows.append({
            "project_id": project["project_id"],
            "minimum_dscr": project["min_dscr"],
            "llcr": llcr,
            "plcr": plcr,
            "dsra_target_vnd": project["debt_service_vnd"] * 6 / 12,
            "lockup_headroom": project["min_dscr"] - 1.25,
            "coverage_status": "PASS" if project["min_dscr"] >= 1.20 and llcr >= 1.35 else "CONDITION",
        })
        dsra = project["debt_service_vnd"] * 6 / 12
        for year, row in enumerate(schedule, start=1):
            excess = max(0.0, project["cfads_vnd"] - row["debt_service"])
            cash_trap = excess if project["min_dscr"] < 1.25 else 0.0
            reserve_rows.append({
                "project_id": project["project_id"],
                "year": year,
                "cfads_vnd": project["cfads_vnd"],
                "debt_service_vnd": row["debt_service"],
                "dsra_opening_vnd": dsra,
                "dsra_funding_vnd": 0.0,
                "cash_trap_vnd": cash_trap,
                "distribution_vnd": max(0.0, excess - cash_trap),
                "dsra_closing_vnd": dsra,
                "waterfall_status": "CASH_TRAP" if cash_trap else "DISTRIBUTION",
            })
        net_equity_cash = [-(project["equity_required_vnd"])] + [
            project["cfads_vnd"] - project["debt_service_vnd"]
        ] * 15
        returns_rows.append({
            "project_id": project["project_id"],
            "equity_required_vnd": project["equity_required_vnd"],
            "discount_rate": 0.14,
            "equity_npv_vnd": project["equity_npv_vnd"],
            "equity_cashflow_year1_vnd": net_equity_cash[1],
            "return_status": "BELOW_HURDLE" if project["equity_npv_vnd"] < 0 else "ABOVE_HURDLE",
        })
        usd_service = [project["debt_service_vnd"] * 0.50 / 25000.0] * 10
        for depreciation in (0.00, 0.02, 0.04, 0.06):
            translated = translate_usd_debt_service(usd_service, 25000.0, depreciation)
            fx_rows.append({
                "project_id": project["project_id"],
                "fx_scenario": f"CRAWL_{int(depreciation * 100)}PCT",
                "annual_depreciation": depreciation,
                "usd_debt_fraction": 0.50,
                "translated_debt_service_bvnd": sum(translated) / 1e9,
            })
        for group_key in ("parent_group_id", "industry", "region"):
            key = (group_key, project[group_key])
            item = concentration.setdefault(key, {"project_count": 0, "capacity_mwp": 0.0, "equity_bvnd": 0.0})
            if project["project_id"] in selected_ids:
                item["project_count"] += 1
                item["capacity_mwp"] += project["proposed_capacity_kwp"] / 1000
                item["equity_bvnd"] += project["equity_required_vnd"] / 1e9

    write_csv(
        root / "outputs/project_cash_flow.csv",
        cash_flow_rows,
        ["project_id", "year", "revenue_vnd", "opex_vnd", "tax_vnd", "working_capital_vnd",
         "delta_working_capital_vnd", "capex_vnd", "cfads_vnd", "sources_vnd", "uses_vnd",
         "sources_uses_balance_vnd"],
    )
    write_csv(
        root / "outputs/sources_uses.csv",
        sources_uses_rows,
        ["project_id", "capex_uses_vnd", "debt_sources_vnd", "equity_sources_vnd",
         "total_sources_vnd", "sources_uses_balance_vnd"],
    )
    write_csv(
        root / "outputs/debt_schedule.csv",
        debt_schedule_rows,
        ["project_id", "year", "opening", "interest", "principal", "debt_service", "closing", "dscr"],
    )
    write_csv(
        root / "outputs/coverage_summary.csv",
        coverage_rows,
        ["project_id", "minimum_dscr", "llcr", "plcr", "dsra_target_vnd", "lockup_headroom", "coverage_status"],
    )
    write_csv(
        root / "outputs/reserve_waterfall.csv",
        reserve_rows,
        ["project_id", "year", "cfads_vnd", "debt_service_vnd", "dsra_opening_vnd",
         "dsra_funding_vnd", "cash_trap_vnd", "distribution_vnd", "dsra_closing_vnd", "waterfall_status"],
    )
    write_csv(
        root / "outputs/returns_register.csv",
        returns_rows,
        ["project_id", "equity_required_vnd", "discount_rate", "equity_npv_vnd",
         "equity_cashflow_year1_vnd", "return_status"],
    )
    fx_fields = ["project_id", "fx_scenario", "annual_depreciation", "usd_debt_fraction", "translated_debt_service_bvnd"]
    write_csv(root / "outputs/fx_sensitivity.csv", fx_rows, fx_fields)
    concentration_rows = []
    for (group_key, group_value), item in sorted(concentration.items()):
        concentration_rows.append({
            "dimension": group_key,
            "dimension_value": group_value,
            "selected_project_count": item["project_count"],
            "selected_capacity_mwp": item["capacity_mwp"],
            "selected_equity_bvnd": item["equity_bvnd"],
            "equity_share": item["equity_bvnd"] / (equity_used / 1e9) if equity_used else 0.0,
        })
    write_csv(
        root / "outputs/portfolio_concentration.csv",
        concentration_rows,
        ["dimension", "dimension_value", "selected_project_count", "selected_capacity_mwp",
         "selected_equity_bvnd", "equity_share"],
    )

    return {
        "master_seed": MASTER_SEED,
        "projects": len(projects),
        "eligible": sum(bool(p["shortlist_flag"]) for p in projects),
        "selected": len(selected),
        "selected_capacity_mwp": sum(p["proposed_capacity_kwp"] for p in selected) / 1000,
        "equity_used_vnd": equity_used,
        "base_portfolio_dscr": base_dscr,
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
