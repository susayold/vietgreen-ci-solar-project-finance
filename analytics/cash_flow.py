def project_cash_flow(project, years=15, tax_rate=0.20, dso_days=30.0, degradation=0.005, ppa_escalation=0.01, opex_escalation=0.02):
    rows = []
    previous_nwc = 0.0
    for year in range(years + 1):
        if year == 0:
            revenue = 0.0
            opex = 0.0
            tax = 0.0
            working_capital = 0.0
            delta_working_capital = 0.0
            capex = float(project["capex_vnd"])
        else:
            in_contract = year <= int(float(project["ppa_tenor_years"]))
            revenue = 0.0
            if in_contract:
                revenue = (
                    float(project["self_consumption_kwh"])
                    * (1.0 - degradation) ** (year - 1)
                    * float(project["ppa_price_vnd_kwh"])
                    * (1.0 + ppa_escalation) ** (year - 1)
                )
            opex = float(project["opex_vnd"]) * (1.0 + opex_escalation) ** (year - 1)
            tax = max(0.0, (revenue - opex) * tax_rate)
            working_capital = revenue * dso_days / 365.0
            delta_working_capital = working_capital - previous_nwc
            capex = 0.0
        cfads = revenue - opex - tax - delta_working_capital
        sources = float(project["debt_vnd"]) + float(project["equity_required_vnd"]) if year == 0 else 0.0
        uses = capex
        rows.append({
            "project_id": project["project_id"],
            "year": year,
            "revenue_vnd": revenue,
            "opex_vnd": opex,
            "tax_vnd": tax,
            "working_capital_vnd": working_capital,
            "delta_working_capital_vnd": delta_working_capital,
            "capex_vnd": capex,
            "cfads_vnd": cfads,
            "sources_vnd": sources,
            "uses_vnd": uses,
            "sources_uses_balance_vnd": sources - uses,
        })
        previous_nwc = working_capital
    return rows

def cfads_y1(project, tax_rate=0.20, dso_days=30.0):
    return project_cash_flow(project, years=1, tax_rate=tax_rate, dso_days=dso_days)[1]["cfads_vnd"]
