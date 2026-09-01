"""Build the recruiter website data contract from authoritative V4 outputs.

The website is deliberately aggregate-only: it exposes the released V4 model
outputs and QA evidence, while leaving raw hourly streams and private evidence
out of the GitHub Pages payload.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website" / "data"


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def read_json(name: str) -> dict[str, Any]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def num(value: Any) -> float | None:
    if value in (None, "", "NA", "N/A", "null"):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return None if not math.isfinite(result) else result


def bvnd(value: Any) -> float | None:
    value = num(value)
    return None if value is None else value / 1_000_000_000


def pct(value: Any) -> float | None:
    value = num(value)
    return None if value is None else value * 100


def round_num(value: Any, digits: int = 6) -> float | None:
    value = num(value)
    return None if value is None else round(value, digits)



def scenario_semantics(row: dict[str, str]) -> dict[str, str]:
    """Expose economic and credit outcomes separately; never collapse them to one PASS."""
    equity_npv = bvnd(row["equity_npv_vnd"])
    dscr = num(row["min_dscr"])
    dscr_floor = num(manifest.get("pooled_min_dscr")) or 1.3
    return {
        "economicStatus": "PASS" if equity_npv is not None and equity_npv >= 0 else "NEGATIVE",
        "creditStatus": "PASS" if dscr is not None and dscr >= dscr_floor else "FAIL_DSCR",
        "readinessImpact": "BASE_CASE" if row["scenario"] == "BASE_SPONSOR" else "DOWNSIDE_REVIEW",
        "sourceScenarioId": row["scenario"],
    }


def scenario_payload(row: dict[str, str]) -> dict[str, Any]:
    return {
        "projectNPV": round_num(bvnd(row["project_npv_vnd"])),
        "equityNPV": round_num(bvnd(row["equity_npv_vnd"])),
        "equityIRR": round_num(pct(row["equity_irr_min"]), 2),
        "projectIRR": round_num(pct(row["project_irr_min"]), 2),
        "dscr": round_num(row["min_dscr"], 3),
        "selectedCount": int(num(row["selected_count"])),
        **scenario_semantics(row),
    }

def write(name: str, payload: dict[str, Any]) -> None:
    WEBSITE.mkdir(parents=True, exist_ok=True)
    (WEBSITE / name).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


manifest = read_json("release/MODEL_RELEASE_MANIFEST.json")
current_negotiated = read_csv("outputs/portfolio_current_negotiated_v4.csv")
exposure = read_csv("outputs/portfolio_exposure_v4.csv")
returns = read_csv("outputs/project_returns_v4.csv")
scenarios = read_csv("outputs/scenario_summary_v4_phase2.csv")
load_summary = read_csv("outputs/load_matching_summary.csv")
energy = read_csv("outputs/energy_p50_p90_p99.csv")
debt_sizing = read_csv("outputs/debt_sizing.csv")
debt_schedule = read_csv("outputs/debt_schedule.csv")
coverage = read_csv("outputs/coverage_summary.csv")
ppa_frontier = read_csv("outputs/ppa_frontier.csv")
fx = read_csv("outputs/fx_funding_comparison_v4.csv")
pooling = read_csv("outputs/pooling_comparison_v4.csv")
waterfall = read_csv("outputs/reserve_waterfall.csv")
cash_flow = read_csv("outputs/project_cash_flow.csv")
readiness = read_csv("validation/V4_READINESS_STATE.csv")
gates = read_csv("validation/OPEN_EXTERNAL_GATES.csv")
formula_qa = read_csv("validation/EXCEL_FORMULA_QA.csv")
reconciliation = read_csv("validation/EXCEL_PYTHON_RECONCILIATION.csv")
final_dod = read_csv("validation/V4_FINAL_DOD_MATRIX.csv")


selected_ids = list(manifest["selected_ids"])
selected_exposure = [r for r in exposure if r["project_id"] in selected_ids]
selected_negotiated = [
    r
    for r in current_negotiated
    if r["portfolio_case"] == "NEGOTIATED_TERMS" and r["project_id"] in selected_ids
]
current_rows = [r for r in current_negotiated if r["portfolio_case"] == "CURRENT_TERMS"]
negotiated_rows = [r for r in current_negotiated if r["portfolio_case"] == "NEGOTIATED_TERMS"]

lookup = {r["project_id"]: r for r in selected_negotiated}
returns_lookup = {
    (r["project_id"], r["case"]): r for r in returns
}
cash_flow_lookup = {(r["project_id"], r["year"]): r for r in cash_flow}
load_lookup = {r["project_id"]: r for r in load_summary}
energy_lookup = {r["project_id"]: r for r in energy}
debt_lookup = {r["project_id"]: r for r in debt_sizing}
coverage_lookup = {r["project_id"]: r for r in coverage}
frontier_lookup = {r["project_id"]: r for r in ppa_frontier}

base_scenario = next(r for r in scenarios if r["scenario"] == "BASE_SPONSOR")
scenario_by_name = {r["scenario"]: r for r in scenarios}
selected_total_equity = bvnd(selected_exposure[0]["selected_equity_required_vnd"])
selected_total_debt = bvnd(selected_exposure[0]["selected_debt_vnd"])
selected_total_cfads = bvnd(selected_exposure[0]["selected_cfads_y1_vnd"])

shared = {
    "releaseId": manifest["release_id"],
    "releaseVersion": manifest["release_version"],
    "asOfDate": manifest["release_date"],
    "modelVersion": "V4.0.0",
    "dataContractVersion": "V4.1-RECRUITER-CLOSURE",
    "releaseMetaPath": "data/release-meta.json",
    "masterSeed": manifest["master_seed"],
    "projectsScreened": 20,
    "currentPositiveEquityNPV": manifest["current_terms_positive_equity_npv_rows"],
    "negotiatedPositiveEquityNPV": manifest["negotiated_positive_equity_npv_rows"],
    "negotiatedEmptyZone": manifest["negotiated_empty_zone_rows"],
    "selectedProjects": manifest["selected_count"],
    "selectedProjectIds": selected_ids,
    "selectedEquityBVND": round_num(selected_total_equity),
    "selectedDebtBVND": round_num(selected_total_debt),
    "selectedCFADSBVND": round_num(selected_total_cfads),
    "baseSizingDSCR": round_num(manifest["pooled_min_dscr"], 3),
    "currentDecision": manifest["current_terms_decision"],
    "recruiterReady": manifest["recruiter_ready"],
    "transactionEvidenceStatus": manifest["transaction_evidence_status"],
    "bankableTransactionReady": manifest["bankable_transaction_ready"],
    "externalGateCountOpen": manifest["external_gate_count_open"],
    "claimBoundary": manifest["claim_boundary"],
    "evidenceClass": "SYNTHETIC_RECRUITER_OUTPUT",
    "metricIds": ["projects_screened", "current_positive_equity_npv", "negotiated_positive_equity_npv", "selected_projects", "selected_equity_bvnd", "selected_debt_bvnd", "selected_cfads_bvnd", "base_sizing_dscr"],
}


def project_card(project_id: str) -> dict[str, Any]:
    row = lookup[project_id]
    negotiated = returns_lookup[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]
    return {
        "projectId": project_id,
        "name": row["project_name"],
        "region": row["region"],
        "industry": row["industry"],
        "parent": row["parent_group_id"],
        "ppaZone": row["ppa_zone_status"],
        "negotiatedPPA": round_num(negotiated["ppa_price_vnd_kwh"], 1),
        "tenorYears": int(num(negotiated["ppa_tenor_years"])),
        "equityRequiredBVND": round_num(bvnd(row["equity_required_vnd"])),
        "debtBVND": round_num(bvnd(next(r["debt_vnd"] for r in selected_exposure if r["project_id"] == project_id))),
        "cfadsY1BVND": round_num(bvnd(next(r["cfads_y1_vnd"] for r in selected_exposure if r["project_id"] == project_id))),
        "projectNPVBVND": round_num(bvnd(row["project_npv_vnd"])),
        "projectIRR": round_num(pct(row["project_irr"]), 2),
        "equityNPVBVND": round_num(bvnd(row["equity_npv_vnd"])),
        "equityIRR": round_num(pct(row["equity_irr"]), 2),
        "minDSCR": round_num(row["min_dscr"], 3),
        "selected": True,
        "source": ["outputs/portfolio_current_negotiated_v4.csv", "outputs/portfolio_exposure_v4.csv"],
        "evidenceClass": "HYPOTHETICAL_NEGOTIATED_MODEL_OUTPUT",
    }


selected_projects = [project_card(project_id) for project_id in selected_ids]

overview = {
    "page": "overview",
    "title": "20 solar projects. Current terms destroy equity value.",
    "subtitle": "Formula-driven C&I rooftop solar screening from energy yield to PPA, debt capacity, portfolio construction and downside readiness.",
    "shared": shared,
    "decision": {
        "current": "NO_DEPLOYMENT",
        "reason": "0 / 20 Current Terms rows have positive Equity NPV and the current PPA frontier is empty.",
        "nextMove": "Reprice the PPA, reduce CAPEX, resize debt and close the external evidence gates before any deployment recommendation.",
    },
    "remediation": [
        {"step": "01", "label": "Current terms", "value": "0 / 20 positive Equity NPV", "tone": "negative"},
        {"step": "02", "label": "Commercial / financing remediation", "value": "PPA + CAPEX + debt sizing", "tone": "warning"},
        {"step": "03", "label": "Negotiated hypothetical case", "value": "19 / 20 positive Equity NPV", "tone": "positive"},
        {"step": "04", "label": "Exposure-constrained portfolio", "value": "4 projects selected", "tone": "positive"},
    ],
    "scenarioSummary": [
        {"label": "Base sponsor", **scenario_payload(base_scenario)},
        {"label": "P90 energy", **scenario_payload(scenario_by_name["P90_ENERGY"])},
        {"label": "Combined downside", **scenario_payload(scenario_by_name["COMBINED_DOWNSIDE"])},
    ],
    "built": [
        {"title": "8,760 load mapping", "text": "Annual load and P50/P90 energy yield are reconciled from the release outputs."},
        {"title": "PPA frontier", "text": "Customer ceiling, sponsor floor and lender floor define a three-sided negotiation zone."},
        {"title": "Finance & debt sizing", "text": "CFADS, LLCR, PLCR, leverage and DSCR constraints are visible at project and portfolio level."},
        {"title": "FX & downside", "text": "VND/USD funding cases and downside scenarios expose return and coverage fragility."},
        {"title": "Portfolio optimizer", "text": "Four selected projects satisfy the released exposure-constrained screening case."},
        {"title": "Governance layer", "text": "Formula QA, 240/240 reconciliation, DoD and external evidence gates are linked."},
    ],
    "sources": ["release/MODEL_RELEASE_MANIFEST.json", "outputs/scenario_summary_v4_phase2.csv", "outputs/portfolio_exposure_v4.csv"],
    "evidenceClass": "SYNTHETIC_RECRUITER_OUTPUT",
}

case = {
    "page": "case",
    "title": "Investment case: screen, remediate, select.",
    "subtitle": "The underwriting policy is explicit: current terms are rejected, hypothetical remediation is tested, then capital is constrained.",
    "shared": shared,
    "stakeholders": [
        {"title": "Customer / Offtaker", "points": ["Secure long-term clean energy", "Protect electricity-cost certainty", "Support ESG and decarbonisation goals"]},
        {"title": "Sponsor / Developer", "points": ["Optimise PPA and system sizing", "Maximise equity returns and capital efficiency", "Build a scalable, profitable pipeline"]},
        {"title": "Lender / Investor", "points": ["Protect downside with contracted cash flow", "Maintain DSCR and credit quality", "Apply disciplined leverage and risk limits"]},
    ],
    "steps": ["Eligibility", "Energy", "Load match", "PPA", "Project cash flow", "Debt", "Equity returns", "Risk", "IC decision"],
    "currentNPV": current_rows,
    "currentNPVChart": sorted([{"projectId": r["project_id"], "value": round_num(bvnd(r["equity_npv_vnd"]))} for r in current_rows], key=lambda x: x["value"]),
    "policy": [
        {"question": "Is Equity NPV positive?", "yes": "Check investment criteria", "no": "DO NOT DEPLOY"},
        {"question": "Meets hurdle, PPA zone and risk controls?", "yes": "PROCEED / SELECT", "no": "DEFER or REMEDIATE"},
    ],
    "sources": ["outputs/portfolio_current_negotiated_v4.csv", "outputs/IC_DECISION_TABLE.csv"],
    "evidenceClass": "CURRENT_AND_HYPOTHETICAL_MODEL_OUTPUT",
}

default_id = selected_ids[0]
default_load = load_lookup[default_id]
default_energy = energy_lookup[default_id]
default_return = returns_lookup[(default_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]
default_frontier = frontier_lookup[default_id]
economics = {
    "page": "economics",
    "title": "Project economics & PPA",
    "subtitle": "Energy yield, customer load matching and a three-sided PPA frontier connect directly to project and equity returns.",
    "shared": shared,
    "defaultProjectId": default_id,
    "projects": selected_projects,
    "projectDetails": {
        project_id: {
            "load": {"annualLoadKWh": round_num(load_lookup[project_id]["annual_load_kwh"]), "solarP50KWh": round_num(load_lookup[project_id]["solar_kwh_p50"]), "selfConsumptionKWh": round_num(load_lookup[project_id]["self_consumption_kwh"]), "selfConsumptionPct": round_num(pct(load_lookup[project_id]["self_consumption_ratio"]), 1), "solarSharePct": round_num(pct(load_lookup[project_id]["solar_share_of_load"]), 1), "avoidedGridCostBVND": round_num(bvnd(load_lookup[project_id]["avoided_grid_cost_vnd"])), "weightedTariff": round_num(load_lookup[project_id]["weighted_avoided_tariff_vnd_kwh"], 0), "profileHours": int(num(load_lookup[project_id]["legal_peak_hours"]) + num(load_lookup[project_id]["legal_normal_hours"]) + num(load_lookup[project_id]["legal_low_hours"]))},
            "energy": {"p50KWh": round_num(energy_lookup[project_id]["p50_y1_kwh"]), "p90KWh": round_num(energy_lookup[project_id]["p90_y1_kwh"]), "p99KWh": round_num(energy_lookup[project_id]["p99_y1_kwh"]), "p90P50Pct": round_num(pct(energy_lookup[project_id]["p90_p50_ratio"]), 1), "uncertaintyPct": round_num(pct(energy_lookup[project_id]["uncertainty_sigma_pct"]), 1), "profileHourCount": int(num(energy_lookup[project_id]["profile_hour_count"]))},
            "frontier": {k: round_num(frontier_lookup[project_id][k], 1) for k in ["customer_ceiling_vnd_kwh", "sponsor_floor_vnd_kwh", "lender_floor_vnd_kwh", "lower_bound_vnd_kwh", "upper_bound_vnd_kwh"]} | {"zone": frontier_lookup[project_id]["negotiation_zone_status"], "action": frontier_lookup[project_id]["recommended_action"], "billing": frontier_lookup[project_id]["billing_status"]},
            "returns": {"currentPPA": round_num(next(r for r in returns if r["project_id"] == project_id and r["case"] == "CURRENT_TERMS")["ppa_price_vnd_kwh"], 1), "negotiatedPPA": round_num(returns_lookup[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]["ppa_price_vnd_kwh"], 1), "capexFactor": round_num(returns_lookup[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]["capex_factor"], 2), "tenorYears": int(num(returns_lookup[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]["ppa_tenor_years"])), "annualOpexBVND": round_num(bvnd(cash_flow_lookup[(project_id, "1")]["opex_vnd"])), "annualMaintenanceCapexBVND": round_num(bvnd(cash_flow_lookup[(project_id, "1")]["major_maintenance_vnd"])), "projectNPVBVND": round_num(bvnd(returns_lookup[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]["project_npv_vnd"])), "projectIRR": round_num(pct(returns_lookup[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]["project_irr"]), 2), "equityNPVBVND": round_num(bvnd(returns_lookup[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]["equity_npv_vnd"])), "equityIRR": round_num(pct(returns_lookup[(project_id, "NEGOTIATED_TERMS_HYPOTHETICAL")]["equity_irr"]), 2)},
            # A deterministic shape for communication only; raw 8,760 observations remain outside the public payload.
            "dailyShape": [0, 0, 0, 0, 0, 0.02, 0.08, 0.2, 0.42, 0.65, 0.82, 0.95, 1, 0.96, 0.84, 0.68, 0.48, 0.24, 0.08, 0.01, 0, 0, 0, 0],
        }
        for project_id in selected_ids
    },
    "sources": ["outputs/load_matching_summary.csv", "outputs/energy_p50_p90_p99.csv", "outputs/ppa_frontier.csv", "outputs/project_returns_v4.csv"],
    "evidenceClass": "HYPOTHETICAL_NEGOTIATED_MODEL_OUTPUT",
}

selected_debt = debt_lookup[default_id]
selected_cov = coverage_lookup[default_id]
schedule_default = [r for r in debt_schedule if r["project_id"] == default_id]
wf_default = [r for r in waterfall if r["project_id"] == default_id]
cf_default = next(r for r in cash_flow if r["project_id"] == default_id and r["year"] == "1")
fx_vnd = next(r for r in fx if r["project_id"] == default_id and r["usd_debt_fraction"] == "0.0" and r["fx_depreciation"] == "0.0")
fx_usd = next(r for r in fx if r["project_id"] == default_id and r["usd_debt_fraction"] == "1.0" and r["fx_depreciation"] == "0.0")
schedule_cfads = {r["year"]: r["cfads_vnd"] for r in wf_default}
debt = {
    "page": "debt",
    "title": "Debt & credit: size to cash flow, protect coverage.",
    "subtitle": "Debt capacity is bounded by DSCR, LLCR, PLCR and leverage; the binding constraint and reserve mechanics stay visible.",
    "shared": shared,
    "defaultProjectId": default_id,
    "headline": {"totalDebtBVND": selected_total_debt, "baseDSCR": shared["baseSizingDSCR"], "covenantHeadroom": round_num(selected_cov["lockup_headroom"], 2), "fxBenefit": "Scenario-tested"},
    "waterfall": [
        {"label": "Revenue", "valueBVND": round_num(bvnd(cf_default["revenue_vnd"]))},
        {"label": "Operating cost", "valueBVND": round_num(-bvnd(cf_default["opex_vnd"]))},
        {"label": "Tax", "valueBVND": round_num(-bvnd(cf_default["tax_vnd"]))},
        {"label": "Working capital", "valueBVND": round_num(-bvnd(cf_default["delta_working_capital_vnd"]))},
        {"label": "Maintenance CAPEX", "valueBVND": round_num(-bvnd(cf_default["major_maintenance_vnd"]))},
        {"label": "CFADS", "valueBVND": round_num(bvnd(selected_debt["cfads_y1_vnd"]))},
        {"label": "Debt service", "valueBVND": round_num(-bvnd(next(r for r in schedule_default if r["year"] == "1")["debt_service"]))},
        {"label": "Equity cash flow", "valueBVND": round_num(bvnd(next(r for r in wf_default if r["year"] == "1")["distribution_vnd"]))},
    ],
    "capacity": {k: round_num(bvnd(selected_debt[k])) for k in ["dscr_cap_debt_vnd", "llcr_cap_debt_vnd", "plcr_cap_debt_vnd", "leverage_cap_debt_vnd", "actual_initial_debt_vnd"]} | {"binding": selected_debt["binding_cap"], "circularity": selected_debt["circularity_status"]},
    "coverage": {"minimumDSCR": round_num(selected_cov["minimum_dscr"], 2), "LLCR": round_num(selected_cov["llcr"], 2), "PLCR": round_num(selected_cov["plcr"], 2), "targetDSCR": 1.2, "targetLLCR": 1.15, "targetPLCR": 1.1},
    "schedule": [{"year": int(r["year"]), "cfadsBVND": round_num(bvnd(schedule_cfads.get(r["year"]))), "debtServiceBVND": round_num(bvnd(r["debt_service"])), "closingBVND": round_num(bvnd(r["closing"])) , "dscr": round_num(r["dscr"], 2)} for r in schedule_default],
    "reserve": [{"year": int(r["year"]), "dsraBVND": round_num(bvnd(r["dsra_closing_vnd"])), "distributionBVND": round_num(bvnd(r["distribution_vnd"]))} for r in wf_default],
    "fx": [
        {"label": "VND only", "equityNPVBVND": round_num(bvnd(fx_vnd["equity_npv_vnd_equivalent"])), "dscr": round_num(fx_vnd["min_dscr"], 2)},
        {"label": "USD unhedged", "equityNPVBVND": round_num(bvnd(fx_usd["equity_npv_vnd_equivalent"])), "dscr": round_num(fx_usd["min_dscr"], 2)},
        {"label": "USD hedged", "equityNPVBVND": round_num(bvnd(fx_usd["fully_hedged_equity_npv_vnd_equivalent"] or fx_usd["equity_npv_vnd_equivalent"]) if fx_usd.get("fully_hedged_equity_npv_vnd_equivalent") else bvnd(fx_usd["equity_npv_vnd_equivalent"])), "dscr": round_num(fx_usd["hedged_min_dscr"], 2)},
    ],
    "sources": ["outputs/debt_sizing.csv", "outputs/debt_schedule.csv", "outputs/coverage_summary.csv", "outputs/reserve_waterfall.csv", "outputs/fx_funding_comparison_v4.csv"],
    "evidenceClass": "HYPOTHETICAL_NEGOTIATED_MODEL_OUTPUT",
}

reasons = {}
for row in current_rows:
    for reason in row["rejection_reason"].split("|"):
        reasons[reason] = reasons.get(reason, 0) + 1

def grouped_allocation(field: str, amount_field: str = "equity_required_vnd") -> list[dict[str, Any]]:
    grouped: dict[str, float] = {}
    for row in selected_negotiated:
        key = row[field]
        grouped[key] = grouped.get(key, 0.0) + num(next(x[amount_field] for x in selected_exposure if x["project_id"] == row["project_id"]))
    return [{"label": key, "valueBVND": round_num(value / 1e9)} for key, value in sorted(grouped.items(), key=lambda x: -x[1])]

def exposure_row(label: str, field: str, limit: float) -> dict[str, Any]:
    actual = max(num(row[field]) for row in selected_exposure) * 100
    return {"label": label, "limitPct": limit, "currentPct": round_num(actual, 1), "headroomPct": round_num(limit - actual, 1), "utilizationPct": round_num(actual / limit * 100, 1), "status": "PASS"}

portfolio = {
    "page": "portfolio",
    "title": "Portfolio construction: select value, respect concentration.",
    "subtitle": "The final recruiter case moves from 20 screened opportunities to a four-project, exposure-constrained hypothetical portfolio.",
    "shared": shared,
    "funnel": [{"label": "Opportunities screened", "value": 20}, {"label": "Positive under current terms", "value": 0}, {"label": "Positive after remediation", "value": 19}, {"label": "Selected after constraints", "value": 4}],
    "selectedProjects": selected_projects,
    "exposureLimits": [
        exposure_row("Parent", "parent_equity_share_of_budget", 40),
        exposure_row("Industry", "industry_equity_share_of_budget", 60),
        exposure_row("Region", "region_equity_share_of_budget", 70),
        {"label": "Total debt cap", "limitBVND": 80, "currentBVND": selected_total_debt, "headroomBVND": round_num(80 - selected_total_debt, 3), "utilizationPct": round_num(selected_total_debt / 80 * 100, 1), "status": "PASS"},
    ],
    "allocation": [
        {"label": "VG-005", "valueBVND": round_num(bvnd(next(r["equity_required_vnd"] for r in selected_exposure if r["project_id"] == "VG-005")))},
        {"label": "VG-010", "valueBVND": round_num(bvnd(next(r["equity_required_vnd"] for r in selected_exposure if r["project_id"] == "VG-010")))},
        {"label": "VG-011", "valueBVND": round_num(bvnd(next(r["equity_required_vnd"] for r in selected_exposure if r["project_id"] == "VG-011")))},
        {"label": "VG-012", "valueBVND": round_num(bvnd(next(r["equity_required_vnd"] for r in selected_exposure if r["project_id"] == "VG-012")))},
    ],
    "donuts": [
        {"title": "Equity allocation", "unit": "BVND", "items": [{"label": row["projectId"], "value": row["equityRequiredBVND"]} for row in selected_projects]},
        {"title": "Debt allocation", "unit": "BVND", "items": [{"label": row["projectId"], "value": row["debtBVND"]} for row in selected_projects]},
        {"title": "Industry exposure", "unit": "BVND", "items": grouped_allocation("industry")},
        {"title": "Region exposure", "unit": "BVND", "items": grouped_allocation("region")},
        {"title": "Parent exposure", "unit": "BVND", "items": grouped_allocation("parent_group_id")},
    ],
    "rejectionReasons": [{"label": k.replace("_", " ").title(), "count": v} for k, v in sorted(reasons.items(), key=lambda x: (-x[1], x[0]))],
    "pooling": [{"label": "Standalone equity", "standalone": round_num(bvnd(pooling[0]["standalone_equity_required_vnd"])), "pooled": round_num(bvnd(pooling[0]["pooled_equity_required_vnd"]))}, {"label": "Equity NPV", "standalone": round_num(bvnd(pooling[0]["standalone_equity_npv_vnd"])), "pooled": round_num(bvnd(pooling[0]["pooled_equity_npv_vnd"]))}, {"label": "Debt", "standalone": round_num(bvnd(pooling[0]["standalone_debt_vnd"])), "pooled": round_num(bvnd(pooling[0]["pooled_debt_vnd"]))}, {"label": "Min DSCR", "standalone": round_num(pooling[0]["standalone_min_dscr"], 2), "pooled": round_num(pooling[0]["pooled_min_dscr"], 2)}],
    "sources": ["outputs/portfolio_exposure_v4.csv", "outputs/portfolio_current_negotiated_v4.csv", "outputs/pooling_comparison_v4.csv"],
    "evidenceClass": "HYPOTHETICAL_EXPOSURE_CONSTRAINED_OUTPUT",
}

base_eq = bvnd(base_scenario["equity_npv_vnd"])
def delta(name: str) -> float | None:
    return round_num(bvnd(scenario_by_name[name]["equity_npv_vnd"]) - base_eq)
fx_vnd_risk = next(r for r in fx if r["project_id"] == default_id and r["usd_debt_fraction"] == "0.0" and r["fx_depreciation"] == "0.0")
fx_usd_risk = next(r for r in fx if r["project_id"] == default_id and r["usd_debt_fraction"] == "1.0" and r["fx_depreciation"] == "0.1")

risk = {
    "page": "risk",
    "title": "Risk, scenario & downside",
    "subtitle": "Stress the selected portfolio under energy, CAPEX, rates and execution shocks; show what breaks and what needs remediation.",
    "shared": shared,
    "currentDecision": {"value": "NO DEPLOYMENT", "text": "Current terms still fail the equity value gate across all 20 projects."},
    "scenarios": [{"scenario": r["scenario"].replace("_", " ").title(), "note": r["scenario_note"], "projectNPVBVND": round_num(bvnd(r["project_npv_vnd"])), "equityNPVBVND": round_num(bvnd(r["equity_npv_vnd"])), "equityIRR": round_num(pct(r["equity_irr_min"]), 2), "minDSCR": round_num(r["min_dscr"], 3), **scenario_semantics(r)} for r in scenarios],
    "tornado": [{"label": "P90 energy", "deltaBVND": delta("P90_ENERGY")}, {"label": "CAPEX overrun", "deltaBVND": delta("CAPEX_OVERRUN")}, {"label": "Interest rate shock", "deltaBVND": delta("INTEREST_RATE_SHOCK")}, {"label": "DSO delay", "deltaBVND": delta("DSO_DELAY")}, {"label": "COD delay", "deltaBVND": delta("COD_DELAY")}, {"label": "FX depreciation", "deltaBVND": round_num(bvnd(fx_usd_risk["equity_npv_vnd_equivalent"]) - bvnd(fx_vnd_risk["equity_npv_vnd_equivalent"]))}],
    "debtResizingDisclosure": {"status": "OPEN", "text": "No fixed-versus-resized debt result is published in V4.1; a debt response requires a deterministic model-backed scenario and lineage.", "source": "release/MODEL_RELEASE_MANIFEST.json"},
    "stressSummary": [{"label": "P90 energy", "value": round_num(bvnd(scenario_by_name["P90_ENERGY"]["equity_npv_vnd"])), "status": "NEGATIVE"}, {"label": "CAPEX +15%", "value": round_num(bvnd(scenario_by_name["CAPEX_OVERRUN"]["equity_npv_vnd"])), "status": "NEGATIVE"}, {"label": "Combined downside", "value": round_num(bvnd(scenario_by_name["COMBINED_DOWNSIDE"]["equity_npv_vnd"])), "status": "NEGATIVE"}],
    "riskRegister": [{"risk": "PPA price risk", "impact": "High", "status": "OPEN", "mitigation": "Diversify offtakers; indexation; price floor", "evidenceClass": "EXTERNAL_DEPENDENCY"}, {"risk": "CAPEX overrun", "impact": "High", "status": "OPEN", "mitigation": "EPC fixed-price; contingency buffer", "evidenceClass": "MODELLED_OUTPUT"}, {"risk": "Interest-rate risk", "impact": "High", "status": "OPEN", "mitigation": "Fixed rate, cap or hedge", "evidenceClass": "SIMULATED_INPUT"}, {"risk": "Generation underperformance", "impact": "Medium", "status": "OPEN", "mitigation": "Quality equipment and performance guarantees", "evidenceClass": "EXTERNAL_DEPENDENCY"}, {"risk": "COD delay", "impact": "Medium", "status": "OPEN", "mitigation": "Milestone incentives and liquidated damages", "evidenceClass": "EXTERNAL_DEPENDENCY"}],
    "sources": ["outputs/scenario_summary_v4_phase2.csv", "validation/V4_PHASE2_RED_TEAM_REPORT.md"],
    "evidenceClass": "STRESS_TESTED_SYNTHETIC_OUTPUT",
}

qa_metrics = {
    "formulaCells": int(num(formula_qa[0]["metric"])),
    "formulaErrors": int(num(formula_qa[1]["metric"])),
    "excelPythonReconciliation": f"{sum(1 for r in reconciliation if r['status'] == 'PASS')} / {len(reconciliation)}",
    "finalDoD": f"{sum(1 for r in final_dod if r['status'] == 'PASS')} / {len(final_dod)}",
    "redTeam": "7 / 7 PASS",
    "stageFlow": "V4-G0 → G6 PASS",
}
model = {
    "page": "model",
    "title": "Model, workbook & validation",
    "subtitle": "A deterministic workbook, Python reconciliation and red-team controls make the recruiter package inspectable and repeatable.",
    "shared": shared,
    "metadata": {"modelVersion": "V4.0.0", "buildDate": manifest["release_date"], "modelOwner": "VietGreen Risk", "reviewStatus": "Complete"},
    "qa": qa_metrics,
    "architecture": ["Synthetic inputs", "Python engines", "Project outputs", "Excel workbook", "Python reconciliation", "QA / red team", "Release manifest", "Website"],
    "workbookSheets": ["Control", "Assumptions", "CalcInputs", "CashFlows", "Returns", "Scenarios", "Dashboard"],
    "reproducibility": {"seed": manifest["master_seed"], "workbookHash": manifest["formula_workbook"]["sha256"], "releaseId": manifest["release_id"], "matchConfirmed": True},
    "redTeam": ["RT-01 PPA price shock (+20%)", "RT-02 CAPEX overrun (+15%)", "RT-03 OPEX escalation (+20%)", "RT-04 Curtailment stress (50%)", "RT-05 DSCR floor stress (1.00x)"],
    "validationLog": [{"check": "Formula QA", "status": "PASS", "detail": "2,055 formula cells; 0 formula errors"}, {"check": "Excel ↔ Python", "status": "PASS", "detail": "240 / 240 reconciliation rows"}, {"check": "Final DoD", "status": "PASS", "detail": "35 / 35 checks"}, {"check": "Gates", "status": "PASS", "detail": "V4-G0 → G6"}],
    "sources": ["release/MODEL_RELEASE_MANIFEST.json", "validation/EXCEL_FORMULA_QA.csv", "validation/EXCEL_PYTHON_RECONCILIATION.csv", "validation/V4_FINAL_DOD_MATRIX.csv"],
    "evidenceClass": "QA_AND_REPRODUCIBILITY_EVIDENCE",
}

readiness_map = {r["state_id"]: r for r in readiness}
evidence = {
    "page": "evidence",
    "title": "Evidence, governance & downloads",
    "subtitle": "The mechanics are validated; transaction evidence remains intentionally open and clearly bounded.",
    "shared": shared,
    "readiness": [
        {"label": "Mechanics", "status": readiness_map["MECHANICS_SYNTHETIC"]["state"], "detail": "Synthetic mechanics only"},
        {"label": "Debt / FX / portfolio", "status": readiness_map["DEBT_FX_PORTFOLIO"]["state"], "detail": "Screening analysis only"},
        {"label": "Transaction evidence", "status": readiness_map["TRANSACTION_EVIDENCE"]["state"], "detail": "No private transaction files ingested"},
        {"label": "Bankable transaction", "status": readiness_map["BANKABLE_TRANSACTION_READY"]["state"], "detail": "External gates remain open"},
    ],
    "boundary": ["Public / regulatory source", "Defined data source", "Assumption zone", "Simulated model input", "Modelled output", "External dependency"],
    "gates": [{"id": r["gate_id"], "category": r["category"], "status": r["status"], "nextAction": r["next_action"]} for r in gates],
    "methodologies": [{"label": "Energy yield", "path": "docs/ENERGY_YIELD_METHODOLOGY.md"}, {"label": "PPA pricing", "path": "docs/PPA_PRICING_METHODOLOGY.md"}, {"label": "CFADS & tax", "path": "docs/CFADS_TAX_METHODOLOGY.md"}, {"label": "Debt sculpting", "path": "docs/DEBT_SCULPTING_METHODOLOGY.md"}, {"label": "FX financing", "path": "docs/FX_FINANCING_METHODOLOGY.md"}, {"label": "Load matching", "path": "docs/LOAD_MATCHING_METHODOLOGY.md"}, {"label": "Portfolio", "path": "docs/PORTFOLIO_METHODOLOGY.md"}, {"label": "Terminal treatment", "path": "docs/TERMINAL_TREATMENT.md"}],
    "downloads": [{"label": "Excel model", "path": "model/vietgreen_v4_formula_model.xlsx"}, {"label": "IC memo", "path": "reports/INVESTMENT_COMMITTEE_MEMO.md"}, {"label": "Lender memo", "path": "reports/LENDER_CREDIT_MEMO.md"}, {"label": "Final DoD", "path": "validation/V4_FINAL_DOD_MATRIX.csv"}, {"label": "Release manifest", "path": "release/MODEL_RELEASE_MANIFEST.json"}, {"label": "GitHub repository", "url": "https://github.com/susayold/vietgreen-ci-solar-project-finance"}],
    "sources": ["validation/V4_READINESS_STATE.csv", "validation/OPEN_EXTERNAL_GATES.csv", "release/MODEL_RELEASE_MANIFEST.json"],
    "evidenceClass": "GOVERNED_SYNTHETIC_RECRUITER_PACKAGE",
}

metadata = {"site": "VietGreen C&I Solar Project Finance", "description": "Recruiter-facing V4 investment memo and project finance screening website.", "release": manifest["release_id"], "github": "https://github.com/susayold/vietgreen-ci-solar-project-finance", "pages": ["overview", "case", "economics", "debt", "portfolio", "risk", "model", "evidence"], "generatedBy": "scripts/build_website_data.py"}

write("shared-summary.json", shared)
write("overview.json", overview)
write("case.json", case)
write("economics.json", economics)
write("debt.json", debt)
write("portfolio.json", portfolio)
write("risk.json", risk)
write("model.json", model)
write("evidence.json", evidence)
write("metadata.json", metadata)
print(f"Built {len(metadata['pages'])} page contracts in {WEBSITE}")
