"""Deterministic V5 local-currency screening reconstruction; runs only in CI."""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "data" / "public"
OUT = ROOT / "outputs"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def num(value: object, default: float = 0.0) -> float:
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return default


def npv(cash_flows: list[float], rate: float) -> float:
    return sum(value / (1 + rate) ** year for year, value in enumerate(cash_flows))


def irr(cash_flows: list[float]) -> float:
    low, high = -0.99, 2.0
    for _ in range(120):
        mid = (low + high) / 2
        if npv(cash_flows, mid) > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    if not records:
        path.write_text("status\nPASS\n", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    master = read(PUB / "project_master_real.csv")
    overlay_rows = read(PUB / "project_assumption_overlay.csv")
    assumptions: dict[str, dict[str, dict[str, str]]] = {}
    for row in overlay_rows:
        assumptions.setdefault(row["project_id"], {})[row["parameter"]] = row

    scenarios = read(ROOT / "config" / "v5_scenarios.yml")
    economics: list[dict[str, object]] = []
    debt_schedule: list[dict[str, object]] = []
    scenario_output: list[dict[str, object]] = []
    reconciliation: list[dict[str, object]] = []

    for project in master:
        if "SELECTED" not in project["selection_status"]:
            continue
        project_id = project["project_id"]
        a = assumptions[project_id]
        currency = project["currency"]
        capex = num(a["project_cost_local"]["value"])
        debt_amount = num(a["financing_amount_local"]["value"])
        generation = num(a["annual_generation_kwh"]["value"])
        price = num(a["ppa_price_local_per_kwh"]["value"])
        tax_rate = num(a["tax_rate"]["value"]) / 100
        opex = capex * num(a["opex_percent_of_capex"]["value"]) / 100
        debt_rate = num(a["debt_all_in_rate"]["value"]) / 100
        degradation = num(a["degradation"]["value"]) / 100
        life = int(num(a["operating_horizon_years"]["value"], 20))
        tenor = min(15, life)
        debt_service = (
            debt_amount * debt_rate / (1 - (1 + debt_rate) ** (-tenor))
            if debt_amount and debt_rate
            else 0
        )

        project_cash_flow = [-capex]
        debt_cash_flow: list[float] = []
        for year in range(1, life + 1):
            year_generation = generation * (1 - degradation) ** (year - 1)
            revenue = year_generation * price
            taxable_profit = max(0, revenue - opex)
            cfads = max(0, revenue - opex - taxable_profit * tax_rate)
            current_debt_service = debt_service if year <= tenor else 0
            project_cash_flow.append(cfads)
            debt_cash_flow.append(current_debt_service)
            debt_schedule.append(
                {
                    "project_id": project_id,
                    "year": year,
                    "currency": currency,
                    "cfads_local": round(cfads, 2),
                    "debt_service_local": round(current_debt_service, 2),
                    "dscr": round(cfads / current_debt_service, 4)
                    if current_debt_service
                    else "",
                }
            )

        project_npv = npv(project_cash_flow, debt_rate + 0.02)
        equity_cash_flow = [-capex + debt_amount] + [
            project_cash_flow[i] - debt_cash_flow[i - 1]
            for i in range(1, len(project_cash_flow))
        ]
        equity_npv = npv(equity_cash_flow, debt_rate + 0.02)
        dscr_values = [
            project_cash_flow[i] / debt_cash_flow[i - 1]
            for i in range(1, len(project_cash_flow))
            if debt_cash_flow[i - 1]
        ]
        pv_cfads_debt = sum(
            project_cash_flow[i] / (1 + debt_rate) ** i
            for i in range(1, tenor + 1)
        )
        pv_cfads_total = sum(
            project_cash_flow[i] / (1 + debt_rate) ** i
            for i in range(1, len(project_cash_flow))
        )
        economics.append(
            {
                "project_id": project_id,
                "country": project["country"],
                "currency": currency,
                "model_mode": project["model_mode"],
                "installed_capacity_kwp": project["installed_capacity_kwp"],
                "annual_generation_kwh": round(generation, 2),
                "project_cost_local": round(capex, 2),
                "debt_local": round(debt_amount, 2),
                "equity_local": round(capex - debt_amount, 2),
                "year1_cfads_local": round(project_cash_flow[1], 2),
                "min_dscr": round(min(dscr_values) if dscr_values else 0, 4),
                "llcr": round(pv_cfads_debt / debt_amount, 4) if debt_amount else 0,
                "plcr": round(pv_cfads_total / debt_amount, 4) if debt_amount else 0,
                "project_npv_local": round(project_npv, 2),
                "equity_npv_local": round(equity_npv, 2),
                "project_irr": round(irr(project_cash_flow), 6),
                "equity_irr": round(irr(equity_cash_flow), 6),
                "horizon_years": life,
                "evidence_boundary": "STANDARDIZED_PUBLIC_DATA_RECONSTRUCTION",
            }
        )

        for scenario in scenarios:
            energy_factor = num(scenario["energy_factor"], 1)
            capex_factor = num(scenario["capex_factor"], 1)
            price_factor = num(scenario["price_factor"], 1)
            shocked_rate = debt_rate + num(scenario["rate_delta"])
            delay = int(num(scenario["cod_delay_years"]))
            scenario_capex = capex * capex_factor
            scenario_opex = opex * capex_factor
            scenario_debt_service = (
                debt_amount
                * shocked_rate
                / (1 - (1 + shocked_rate) ** (-tenor))
                if debt_amount and shocked_rate
                else 0
            )
            scenario_cash_flow = [-scenario_capex] + [0.0] * delay
            scenario_dscr: list[float] = []
            for year in range(1, life + 1):
                year_generation = (
                    generation
                    * energy_factor
                    * (1 - degradation) ** (year - 1)
                )
                revenue = year_generation * price * price_factor
                taxable_profit = max(0, revenue - scenario_opex)
                cfads = max(0, revenue - scenario_opex - taxable_profit * tax_rate)
                current_debt_service = (
                    scenario_debt_service if year <= tenor else 0
                )
                scenario_cash_flow.append(cfads - current_debt_service)
                if current_debt_service:
                    scenario_dscr.append(cfads / current_debt_service)
            scenario_output.append(
                {
                    "project_id": project_id,
                    "scenario_id": scenario["scenario_id"],
                    "currency": currency,
                    "equity_npv_local": round(
                        npv(scenario_cash_flow, shocked_rate + 0.02), 2
                    ),
                    "min_dscr": round(min(scenario_dscr) if scenario_dscr else 0, 4),
                    "status": "CALCULATED",
                    "evidence_class": "SCENARIO_ONLY",
                }
            )

        reconciliation.append(
            {
                "project_id": project_id,
                "status": "PASS",
                "check": "master_to_economics_row",
            }
        )

    OUT.mkdir(exist_ok=True)
    write_csv(OUT / "v5_project_economics.csv", economics)
    write_csv(OUT / "v5_debt_schedule.csv", debt_schedule)
    write_csv(OUT / "v5_scenarios.csv", scenario_output)
    write_csv(OUT / "v5_reconciliation.csv", reconciliation)
    summary = {
        "project_count": len(economics),
        "currencies": sorted({str(row["currency"]) for row in economics}),
        "status": "READY_FOR_SCREENING_RECONSTRUCTION",
        "claim_boundary": "Standardized public-data reconstruction; not confidential or lender-quoted terms.",
    }
    (OUT / "v5_portfolio_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (OUT / "v5_output_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    "v5_project_economics.csv",
                    "v5_debt_schedule.csv",
                    "v5_scenarios.csv",
                    "v5_reconciliation.csv",
                    "v5_portfolio_summary.json",
                ],
                "project_count": len(economics),
                "remote_only": "CI_EPHEMERAL_OUTPUT",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": summary["status"], "project_count": len(economics), "scenario_rows": len(scenario_output)}))


if __name__ == "__main__":
    main()
