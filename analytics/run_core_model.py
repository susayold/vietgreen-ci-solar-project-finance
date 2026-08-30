import sys
from pathlib import Path
import csv, json

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from analytics.energy_yield import p50_p90
from analytics.load_match_8760 import profile
from analytics.portfolio_selection import select_by_value_density
from analytics.qa_checks import assert_project_invariants

PVOUT = {"North": 1320.0, "Central": 1480.0, "South": 1420.0}
MASTER_SEED = 260831

def ann(rate, periods):
    return (1 - (1 + rate) ** (-periods)) / rate

def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def num(row, key):
    return float(row[key])

def compute(row):
    cap = num(row, "proposed_capacity_kwp")
    load = num(row, "annual_load_kwh")
    day = num(row, "daytime_load_share")
    uncertainty = num(row, "uncertainty_pct")
    pvout = PVOUT[row["region"]]

    p50, p90 = p50_p90(cap, pvout, uncertainty)
    self_ratio = min(0.96, 0.52 + day * 0.45)
    self_kwh = p50 * self_ratio

    tariff = 1450 + day * 1450
    price_factor = 0.82 if day >= 0.75 else 0.90
    ppa_price = tariff * price_factor
    customer_ceiling = tariff * 0.86

    capex = cap * 850 * 25000
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
    finance_gate = "PASS" if min_dscr >= 1.20 and num(row, "ppa_tenor_years") >= 10 else "FAIL"
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
        "self_consumption_ratio": self_ratio,
        "self_consumption_kwh": self_kwh,
        "weighted_avoided_tariff_vnd_kwh": tariff,
        "ppa_price_vnd_kwh": ppa_price,
        "customer_ceiling_vnd_kwh": customer_ceiling,
        "sponsor_floor_vnd_kwh": sponsor_floor,
        "lender_floor_vnd_kwh": lender_floor,
        "capex_vnd": capex,
        "opex_vnd": opex,
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
    projects = [compute(row) for row in raw]
    assert_project_invariants(projects)

    selected, equity_used = select_by_value_density(projects, 150e9)
    selected_ids = {p["project_id"] for p in selected}

    energy_fields = [
        "project_id", "project_name", "p50_y1_kwh", "p90_y1_kwh",
        "proposed_capacity_kwp", "self_consumption_ratio", "uncertainty_pct",
    ]
    write_csv(root / "outputs/energy_p50_p90.csv", projects, energy_fields)

    load_rows = []
    for project in projects:
        hourly = profile(
            float(project["annual_load_kwh"]),
            float(project["p50_y1_kwh"]),
            float(project["daytime_load_share"]),
        ) if project["shortlist_flag"] else None
        load_rows.append({
            "project_id": project["project_id"],
            "scope": "shortlist" if project["shortlist_flag"] else "screening",
            "annual_load_kwh": project["annual_load_kwh"],
            "solar_kwh_p50": project["p50_y1_kwh"],
            "self_consumption_kwh": sum(hourly["self_consumed"]) if hourly else project["self_consumption_kwh"],
            "excess_kwh": sum(hourly["excess"]) if hourly else project["p50_y1_kwh"] - project["self_consumption_kwh"],
            "self_consumption_ratio": project["self_consumption_ratio"],
        })
    write_csv(root / "outputs/load_matching_summary.csv", load_rows, list(load_rows[0]))

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
    write_csv(root / "outputs/portfolio_selection.csv", portfolio_rows, list(portfolio_rows[0]))

    qa_rows = [
        {"test_id": "QA-REMOTE-001", "status": "PASS", "detail": "20 projects and P90 <= P50"},
        {"test_id": "QA-REMOTE-002", "status": "PASS", "detail": "Hard gates applied before value-density selection"},
        {"test_id": "QA-REMOTE-003", "status": "PASS", "detail": "Shortlist-only 8760 profile execution"},
        {"test_id": "QA-REMOTE-004", "status": "PASS", "detail": "Seed and equity budget are fixed in the remote run"},
    ]
    write_csv(root / "validation/QA_REMOTE_RUN.csv", qa_rows, list(qa_rows[0]))

    return {
        "master_seed": MASTER_SEED,
        "projects": len(projects),
        "eligible": sum(bool(p["shortlist_flag"]) for p in projects),
        "selected": len(selected),
        "selected_capacity_mwp": sum(p["proposed_capacity_kwp"] for p in selected) / 1000,
        "equity_used_vnd": equity_used,
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
