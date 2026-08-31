"""Project cash flow, tax, VAT and working-capital schedules.

All arrays are held in memory on the GitHub Actions runner. No hourly or project
data is written to the local desktop workspace.
"""

from __future__ import annotations


def project_cash_flow(
    project,
    years=15,
    tax_rate=0.20,
    dso_days=30.0,
    degradation=0.005,
    ppa_escalation=0.01,
    opex_escalation=0.02,
    vat_rate=0.08,
    major_maintenance_rate=0.005,
    terminal_branch="ZERO_RESIDUAL_NO_SALE",
    capex_summary=None,
):
    """Return annual rows with explicit tax/VAT/WC/terminal branches.

    Revenue is driven by the 8,760 self-consumed-energy result supplied in
    project["self_consumption_kwh"]; it is not a flat annual load heuristic.
    Tax uses straight-line depreciation and a loss carryforward proxy. VAT is
    split from all-in construction CAPEX and is reconciled in sources/uses.
    Debt sizing happens after this operating schedule, so year-zero sources
    gracefully use zero debt and full-equity placeholders during the first pass.
    """
    rows = []
    previous_nwc = 0.0
    tax_losses = 0.0
    capex_total = float(project["capex_vnd"])
    if capex_summary:
        capex_total = float(capex_summary["total_uses_vnd"])
        capex_net = float(capex_summary["depreciable_basis_vnd"])
        capex_vat = float(capex_summary["vat_vnd"])
        construction_capex = float(capex_summary["construction_capex_gross_vnd"])
        idc = float(capex_summary["idc_vnd"])
    else:
        capex_net = capex_total / (1.0 + vat_rate)
        capex_vat = capex_total - capex_net
        construction_capex = capex_total
        idc = 0.0
    depreciation = capex_net / years if years else 0.0
    debt_source = float(project.get("debt_vnd", 0.0))
    equity_source = float(project.get("equity_required_vnd", capex_total))
    for year in range(years + 1):
        in_contract = 0 < year <= int(float(project["ppa_tenor_years"]))
        if year == 0:
            revenue = 0.0
            opex = 0.0
            depreciation_expense = 0.0
            tax = 0.0
            working_capital = 0.0
            delta_working_capital = 0.0
            capex = capex_total
            capex_net_use = capex_net
            capex_vat_paid = capex_vat
            construction_capex_paid = construction_capex
            idc_paid = idc
            major_maintenance = 0.0
            terminal_value = 0.0
            terminal_release = 0.0
            taxable_income = 0.0
            tax_loss_opening = 0.0
            tax_loss_closing = 0.0
        else:
            generation = float(project.get("p50_y1_kwh", 0.0)) * (1.0 - degradation) ** (year - 1)
            self_energy = float(project["self_consumption_kwh"]) * (1.0 - degradation) ** (year - 1)
            revenue = (
                self_energy
                * float(project["ppa_price_vnd_kwh"])
                * (1.0 + ppa_escalation) ** (year - 1)
                if in_contract
                else 0.0
            )
            opex = (
                float(project["opex_vnd"]) * (1.0 + opex_escalation) ** (year - 1)
                if generation > 0.0
                else 0.0
            )
            depreciation_expense = depreciation if in_contract else 0.0
            taxable_income = revenue - opex - depreciation_expense
            tax_loss_opening = tax_losses
            if taxable_income >= tax_loss_opening:
                tax = max(0.0, (taxable_income - tax_loss_opening) * tax_rate)
                tax_loss_closing = 0.0
            else:
                tax = 0.0
                tax_loss_closing = tax_loss_opening - taxable_income
            tax_losses = tax_loss_closing
            billed_nwc = revenue * dso_days / 365.0
            working_capital = 0.0 if year == years else billed_nwc
            delta_working_capital = working_capital - previous_nwc
            if year == years:
                delta_working_capital = -previous_nwc
            capex = 0.0
            capex_net_use = 0.0
            capex_vat_paid = 0.0
            construction_capex_paid = 0.0
            idc_paid = 0.0
            major_maintenance = capex_net * major_maintenance_rate if year in (5, 10) else 0.0
            terminal_value = 0.0
            terminal_release = max(0.0, previous_nwc) if year == years else 0.0
        cfads = revenue - opex - tax - delta_working_capital - major_maintenance
        sources = debt_source + equity_source if year == 0 else 0.0
        uses = capex
        rows.append(
            {
                "project_id": project["project_id"],
                "year": year,
                "revenue_vnd": revenue,
                "opex_vnd": opex,
                "depreciation_vnd": depreciation_expense,
                "taxable_income_vnd": taxable_income,
                "tax_loss_opening_vnd": tax_loss_opening,
                "tax_loss_closing_vnd": tax_loss_closing,
                "tax_vnd": tax,
                "working_capital_vnd": working_capital,
                "delta_working_capital_vnd": delta_working_capital,
                "capex_vnd": capex,
                "capex_net_vnd": capex_net_use,
                "vat_paid_vnd": capex_vat_paid,
                "construction_capex_vnd": construction_capex_paid,
                "idc_vnd": idc_paid,
                "major_maintenance_vnd": major_maintenance,
                "terminal_value_vnd": terminal_value,
                "terminal_release_vnd": terminal_release,
                "terminal_branch": terminal_branch,
                "cfads_vnd": cfads,
                "sources_vnd": sources,
                "uses_vnd": uses,
                "sources_uses_balance_vnd": sources - uses,
            }
        )
        previous_nwc = working_capital
    return rows


def cfads_y1(project, **kwargs):
    return project_cash_flow(project, years=1, **kwargs)[1]["cfads_vnd"]
