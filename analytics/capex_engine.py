"""Local-currency CAPEX/construction/IDC engine."""

def build_capex_summary(project, construction_periods=2, idc_rate=0.0, vat_rate=0.0):
    capex = float(project["capex_local"])
    net = capex / (1 + vat_rate) if vat_rate else capex
    vat = capex - net
    idc = (
        sum(
            capex / construction_periods * (1 + idc_rate) ** i
            - capex / construction_periods
            for i in range(construction_periods)
        )
        if idc_rate
        else 0.0
    )
    return {
        "currency": project["currency"],
        "total_uses_local": capex + idc,
        "construction_capex_gross_local": capex,
        "depreciable_basis_local": net,
        "vat_local": vat,
        "idc_local": idc,
        "construction_periods": construction_periods,
    }


def build_capex_schedule(capex_rows, construction_rows, project_id, idc_rate=0.0):
    """Build a month-level CAPEX schedule while preserving the gross source amount.

    The legacy V5 test contract supplies gross CAPEX and a VAT rate.  The
    schedule keeps the calculation currency-neutral and exposes the historical
    *_vnd summary keys for compatibility with that contract.
    """
    matches = [row for row in capex_rows if row.get("project_id") == project_id]
    if not matches:
        raise ValueError(f"CAPEX row not found for {project_id}")
    capex_row = matches[0]
    gross = float(capex_row["amount_local"])
    vat_rate = float(capex_row.get("vat_rate", 0.0) or 0.0)
    net = gross / (1.0 + vat_rate) if vat_rate else gross
    vat = gross - net
    periods = [row for row in construction_rows if row.get("project_id") == project_id]
    if not periods:
        raise ValueError(f"Construction schedule not found for {project_id}")
    share_total = sum(float(row.get("construction_share", 0.0) or 0.0) for row in periods)
    if abs(share_total - 1.0) > 1e-8:
        raise ValueError(f"Construction shares must sum to 1.0, got {share_total}")

    rows = []
    cumulative_spend = 0.0
    for period in periods:
        share = float(period.get("construction_share", 0.0) or 0.0)
        gross_period = gross * share
        net_period = net * share
        vat_period = vat * share
        cumulative_spend += gross_period
        remaining_after_spend = max(gross - cumulative_spend, 0.0)
        idc_period = remaining_after_spend * float(idc_rate) / 12.0
        rows.append({
            "project_id": project_id,
            "construction_month": int(period["construction_month"]),
            "construction_share": share,
            "construction_capex_gross_vnd": gross_period,
            "construction_capex_net_vnd": net_period,
            "vat_vnd": vat_period,
            "idc_vnd": idc_period,
            "source_or_assumption_id": period.get("source_or_assumption_id", ""),
        })

    idc = sum(row["idc_vnd"] for row in rows)
    summary = {
        "project_id": project_id,
        "construction_capex_gross_vnd": gross,
        "construction_capex_net_vnd": net,
        "vat_vnd": vat,
        "idc_vnd": idc,
        "total_uses_vnd": gross + idc,
    }
    return rows, summary
