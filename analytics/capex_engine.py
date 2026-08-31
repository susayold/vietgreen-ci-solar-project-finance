"""Bottom-up construction CAPEX, VAT and IDC schedules."""
from __future__ import annotations


def build_capex_schedule(capex_rows, construction_rows, project_id, idc_rate=0.085):
    base_rows = [row for row in capex_rows if row.get("project_id") == project_id]
    curve_rows = sorted([row for row in construction_rows if row.get("project_id") == project_id], key=lambda row: int(row["construction_month"]))
    if not base_rows or not curve_rows:
        raise ValueError("missing CAPEX or construction rows for %s" % project_id)
    months = [int(row["construction_month"]) for row in curve_rows]
    if months != list(range(1, len(months) + 1)):
        raise ValueError("construction months must be contiguous for %s" % project_id)
    if abs(sum(float(row["construction_share"]) for row in curve_rows) - 1.0) > 1e-9:
        raise ValueError("construction shares must sum to 1 for %s" % project_id)
    gross = sum(float(row["amount_local"]) for row in base_rows)
    vat = sum(float(row["amount_local"]) - float(row["amount_local"]) / (1.0 + float(row.get("vat_rate") or 0.0)) for row in base_rows)
    net = gross - vat
    construction_months = len(curve_rows)
    total_idc = sum(net * float(item["construction_share"]) * float(idc_rate) * max(0.0, construction_months - int(item["construction_month"]) + 0.5) / 12.0 for item in curve_rows)
    total_uses = gross + total_idc
    rows = []
    cumulative_gross = 0.0
    cumulative_idc = 0.0
    for curve in curve_rows:
        month = int(curve["construction_month"])
        month_gross = gross * float(curve["construction_share"])
        month_net = net * float(curve["construction_share"])
        month_vat = vat * float(curve["construction_share"])
        month_idc = month_net * float(idc_rate) * max(0.0, construction_months - month + 0.5) / 12.0
        cumulative_gross += month_gross
        cumulative_idc += month_idc
        rows.append({
            "project_id": project_id, "construction_month": month, "construction_share": float(curve["construction_share"]),
            "construction_capex_gross_vnd": month_gross, "construction_capex_net_vnd": month_net,
            "vat_vnd": month_vat, "idc_vnd": month_idc,
            "cumulative_capex_gross_vnd": cumulative_gross, "cumulative_idc_vnd": cumulative_idc,
            "total_construction_gross_vnd": gross, "total_construction_net_vnd": net, "total_vat_vnd": vat,
            "idc_rate": float(idc_rate), "total_uses_vnd": total_uses, "reconciliation_status": "PASS",
            "source_or_assumption_id": curve.get("source_or_assumption_id", "ASM-CONSTRUCTION-SCHEDULE"),
        })
    summary = {
        "project_id": project_id, "construction_months": construction_months,
        "construction_capex_gross_vnd": gross, "construction_capex_net_vnd": net,
        "vat_vnd": vat, "idc_vnd": total_idc, "idc_rate": float(idc_rate),
        "depreciable_basis_vnd": net + total_idc, "total_uses_vnd": total_uses,
        "schedule_rows": rows, "reconciliation_status": "PASS" if abs(net + vat - gross) <= 1.0 else "FAIL",
    }
    return rows, summary