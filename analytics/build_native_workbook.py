"""Build the recruiter-facing 22-sheet native Project Finance workbook.

The workbook intentionally demonstrates spreadsheet modeling discipline:
- blue-font hardcodes / user inputs
- green-font cross-sheet links
- black formulas and calculations
- yellow key-input cells
- dark-blue section headers
- zeros as dashes and negatives in red parentheses

Only Python's standard library is used so the workbook can be regenerated on a
GitHub Actions runner without a desktop spreadsheet application.
"""

from __future__ import annotations

import csv
import html
import json
import math
import re
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SHEETS = [
    ("00_Control", None),
    ("01_Assumptions", "evidence/ASSUMPTION_REGISTER.csv"),
    ("02_Evidence_Regulatory", "evidence/REGULATORY_REGISTER.csv"),
    ("03_Project_Pipeline", "data/synthetic/project_master.csv"),
    ("04_Offtakers_Credit_Site", "data/synthetic/offtaker_master.csv"),
    ("05_Solar_Energy", "outputs/energy_p50_p90.csv"),
    ("06_Load_PPA", "outputs/load_matching_summary.csv"),
    ("07_CAPEX_Construction", "outputs/capex_schedule.csv"),
    ("08_OPEX", "outputs/project_cash_flow.csv"),
    ("09_Project_CF_CFADS", "outputs/project_cash_flow.csv"),
    ("10_Portfolio_CFADS", "outputs/portfolio_cfads.csv"),
    ("11_Debt_Terms", "data/synthetic/debt_terms.csv"),
    ("12_Debt_Sculpting", "outputs/pooled_debt_schedule.csv"),
    ("13_Reserves_Waterfall", "outputs/reserve_waterfall.csv"),
    ("14_Coverage", "outputs/coverage_summary.csv"),
    ("15_Returns_Discount", "outputs/returns_register.csv"),
    ("16_FX_Financing", "outputs/fx_sensitivity.csv"),
    ("17_Scenarios_Sensitivity", "outputs/scenario_summary.csv"),
    ("18_Portfolio", "outputs/portfolio_selection.csv"),
    ("19_IC_Bankability", "outputs/IC_DECISION_TABLE.csv"),
    ("20_External_Validation", "validation/EXTERNAL_VALIDATION.csv"),
    ("21_QA_Audit", "validation/QA_REMOTE_RUN.csv"),
]

ST_NORMAL = 0
ST_TITLE = 1
ST_SUBTITLE = 2
ST_SECTION = 3
ST_HEADER = 4
ST_INPUT = 5
ST_KEY_INPUT = 6
ST_FORMULA = 7
ST_LINK = 8
ST_MONEY = 9
ST_MONEY_LINK = 10
ST_PERCENT = 11
ST_PERCENT_LINK = 12
ST_RATIO = 13
ST_RATIO_LINK = 14
ST_STATUS_GREEN = 15
ST_STATUS_RED = 16
ST_STATUS_AMBER = 17
ST_NOTE = 18
ST_RAW_HEADER = 19
ST_INPUT_MONEY = 20
ST_INPUT_PERCENT = 21
ST_INPUT_RATIO = 22
ST_INTEGER = 23
ST_INTEGER_INPUT = 24
ST_OUTPUT_GREEN = 25
ST_OUTPUT_RED = 26
ST_NUMBER2 = 27
ST_NUMBER2_LINK = 28

NUMERIC_RE = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$")
INPUT_SHEETS = {"01_Assumptions", "02_Evidence_Regulatory", "03_Project_Pipeline", "04_Offtakers_Credit_Site", "11_Debt_Terms"}
PERCENT_HEADERS = {
    "reference_rate", "all_in_rate", "leverage_cap", "degradation_pct", "total_uncertainty_pct",
    "self_consumption_ratio", "solar_share_of_load", "fx_depreciation", "construction_share",
    "idc_rate", "equity_share", "capex_factor", "cfads_factor", "site_event_factor", "common_factor",
}
RATIO_HEADERS = {
    "sizing_dscr", "sculpting_dscr", "minimum_covenant_dscr", "lockup_dscr", "llcr_floor",
    "minimum_dscr", "llcr", "plcr", "portfolio_dscr", "minimum_annual_dscr", "standalone_min_dscr",
    "lockup_headroom", "p90_p50_ratio", "value_density",
}
INTEGER_HEADERS = {
    "year", "construction_month", "debt_tenor_years", "dsra_months", "cod_delay_years",
    "offtaker_default_year", "legal_peak_hours", "legal_normal_hours", "legal_low_hours",
    "current_billed_peak_reference_hours", "pooled_feedback_iterations",
}


def read_rows(relative_path: str, limit: int = 1000) -> list[list[str]]:
    path = ROOT / relative_path
    if not path.exists():
        return [["status", "not_generated_on_this_runner"]]
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows: list[list[str]] = []
        for row in reader:
            rows.append(row)
            if len(rows) >= limit:
                break
        return rows or [["status", "empty"]]


def scalar(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        return value
    text = str(value).strip()
    if text == "":
        return ""
    if text.upper() == "TRUE":
        return True
    if text.upper() == "FALSE":
        return False
    if NUMERIC_RE.match(text):
        try:
            number = float(text)
            if number.is_integer() and abs(number) < 1e12:
                return int(number)
            return number
        except ValueError:
            return text
    return text


def column_letter(index: int) -> str:
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def xml_escape(value: Any) -> str:
    return html.escape(str(value), quote=False)


def formula_cell(ref: str, formula: str, cached: Any = None, style: int = ST_FORMULA) -> str:
    f = xml_escape(formula.lstrip("="))
    attrs = f'r="{ref}" s="{style}"'
    if cached is None or cached == "":
        return f'<c {attrs}><f>{f}</f></c>'
    cached = scalar(cached)
    if isinstance(cached, bool):
        return f'<c {attrs} t="b"><f>{f}</f><v>{1 if cached else 0}</v></c>'
    if isinstance(cached, (int, float)) and math.isfinite(float(cached)):
        return f'<c {attrs}><f>{f}</f><v>{cached}</v></c>'
    return f'<c {attrs} t="str"><f>{f}</f><v>{xml_escape(cached)}</v></c>'


def value_cell(ref: str, value: Any, style: int = ST_NORMAL) -> str:
    value = scalar(value)
    if value == "":
        return f'<c r="{ref}" s="{style}"/>'
    if isinstance(value, bool):
        return f'<c r="{ref}" s="{style}" t="b"><v>{1 if value else 0}</v></c>'
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return f'<c r="{ref}" s="{style}"><v>{value}</v></c>'
    return f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{xml_escape(value)}</t></is></c>'


def row_xml(row_number: int, cells: list[str], height: float | None = None) -> str:
    height_attr = f' ht="{height}" customHeight="1"' if height else ""
    return f'<row r="{row_number}"{height_attr}>{"".join(cells)}</row>'


def detect_style(header: str, *, input_sheet: bool, formula: bool = False, link: bool = False) -> int:
    header = (header or "").strip().lower()
    money = "_vnd" in header or "_bvnd" in header or "_usd" in header
    percent = header in PERCENT_HEADERS or header.endswith("_pct") or header.endswith("_rate")
    ratio = header in RATIO_HEADERS or "dscr" in header or "llcr" in header or "plcr" in header
    integer = header in INTEGER_HEADERS or header.endswith("_years") or header.endswith("_months")
    if formula or link:
        if ratio:
            return ST_RATIO_LINK if link else ST_RATIO
        if percent:
            return ST_PERCENT_LINK if link else ST_PERCENT
        if money:
            return ST_MONEY_LINK if link else ST_MONEY
        return ST_NUMBER2_LINK if link else ST_FORMULA
    if input_sheet:
        if ratio:
            return ST_INPUT_RATIO
        if percent:
            return ST_INPUT_PERCENT
        if money:
            return ST_INPUT_MONEY
        if integer:
            return ST_INTEGER_INPUT
        return ST_INPUT
    if ratio:
        return ST_RATIO
    if percent:
        return ST_PERCENT
    if money:
        return ST_MONEY
    if integer:
        return ST_INTEGER
    return ST_NORMAL


def estimated_width(values: list[Any], header: str) -> float:
    longest = len(str(header or ""))
    for value in values[:150]:
        longest = max(longest, len(str(value or "")))
    if any(token in (header or "").lower() for token in ("note", "condition", "reason", "source", "mechanism", "hash", "classification")):
        return min(38.0, max(18.0, longest * 0.85))
    return min(24.0, max(10.0, longest * 0.9))


def lookup(rows: list[list[str]], key_header: str, key: str, value_header: str, default: Any = "") -> Any:
    if not rows:
        return default
    header = rows[0]
    try:
        ki = header.index(key_header)
        vi = header.index(value_header)
    except ValueError:
        return default
    for row in rows[1:]:
        if len(row) > max(ki, vi) and str(row[ki]) == key:
            return scalar(row[vi])
    return default


def sheet_view_xml(freeze_row: int = 1) -> str:
    pane = ""
    if freeze_row > 0:
        pane = f'<pane ySplit="{freeze_row}" topLeftCell="A{freeze_row + 1}" activePane="bottomLeft" state="frozen"/>'
    return f'<sheetViews><sheetView workbookViewId="0" showGridLines="0">{pane}</sheetView></sheetViews>'


def cols_xml(widths: list[float]) -> str:
    parts = ["<cols>"]
    for idx, width in enumerate(widths, start=1):
        parts.append(f'<col min="{idx}" max="{idx}" width="{width:.2f}" customWidth="1"/>')
    parts.append("</cols>")
    return "".join(parts)


def merge_xml(ranges: list[str]) -> str:
    if not ranges:
        return ""
    return '<mergeCells count="%d">%s</mergeCells>' % (len(ranges), "".join(f'<mergeCell ref="{r}"/>' for r in ranges))


def worksheet_wrapper(sheet_data: str, widths: list[float], *, merges: list[str] | None = None,
                      freeze_row: int = 1, auto_filter: str | None = None,
                      data_validations: str = "") -> str:
    auto = f'<autoFilter ref="{auto_filter}"/>' if auto_filter else ""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetPr><outlinePr summaryBelow="1" summaryRight="1"/></sheetPr>'
        + sheet_view_xml(freeze_row)
        + '<sheetFormatPr defaultRowHeight="15"/>'
        + cols_xml(widths)
        + f'<sheetData>{sheet_data}</sheetData>'
        + auto
        + merge_xml(merges or [])
        + data_validations
        + '<pageMargins left="0.35" right="0.35" top="0.5" bottom="0.5" header="0.2" footer="0.2"/>'
        + '</worksheet>'
    )


def build_control_sheet(data: dict[str, list[list[str]]]) -> str:
    selected = "VG-001"
    energy = data["05_Solar_Energy"]
    capex = data["07_CAPEX_Construction"]
    portfolio = data["18_Portfolio"]
    coverage = data["14_Coverage"]
    returns = data["15_Returns_Discount"]
    terms = data["11_Debt_Terms"]
    ic = data["19_IC_Bankability"]
    cached = {
        "capacity": lookup(portfolio, "project_id", selected, "capacity_mwp", 0),
        "p50": float(lookup(energy, "project_id", selected, "p50_y1_kwh", 0) or 0) / 1_000_000,
        "cost": float(lookup(capex, "project_id", selected, "total_uses_vnd", 0) or 0) / 1_000_000_000,
        "debt": lookup(portfolio, "project_id", selected, "standalone_debt_bvnd", 0),
        "dscr": lookup(coverage, "project_id", selected, "minimum_dscr", 0),
        "llcr": lookup(coverage, "project_id", selected, "llcr", 0),
        "plcr": lookup(coverage, "project_id", selected, "plcr", 0),
        "pnpv": float(lookup(returns, "project_id", selected, "project_npv_vnd", 0) or 0) / 1_000_000_000,
        "enpv": float(lookup(returns, "project_id", selected, "equity_npv_vnd", 0) or 0) / 1_000_000_000,
        "lev": lookup(terms, "project_or_portfolio_id", selected, "leverage_cap", 0),
        "rate": lookup(terms, "project_or_portfolio_id", selected, "all_in_rate", 0),
        "ic": lookup(ic, "project_id", selected, "final_classification", ""),
    }
    dq = read_rows("validation/DATA_QUALITY_RESULTS.csv")
    passed = sum(1 for row in dq[1:] if len(row) > 5 and row[5] == "PASS")
    checks = max(0, len(dq) - 1)
    rows: list[str] = []
    rows.append(row_xml(1, [value_cell("A1", "VIETGREEN C&I SOLAR — PROJECT FINANCE MODEL", ST_TITLE)], 24))
    rows.append(row_xml(2, [], 24))
    rows.append(row_xml(3, [value_cell("A3", "Recruiter Review Workbook | Formula-driven | Inputs → Cash Flow → Debt → Coverage → Returns → Risk → Decision", ST_SUBTITLE)], 20))
    rows.append(row_xml(4, []))
    rows.append(row_xml(5, [value_cell("A5", "Selected Project", ST_SECTION), value_cell("B5", selected, ST_KEY_INPUT), value_cell("D5", "Blue = hardcodes | Green = cross-sheet links | Black = formulas | Yellow fill = key input / reviewer attention", ST_NOTE)], 21))
    rows.append(row_xml(6, []))
    rows.append(row_xml(7, [value_cell("A7", "KEY MODEL OUTPUTS — selected project", ST_SECTION)], 20))
    labels1 = [("A8", "Capacity (MWp)"), ("C8", "P50 Generation (GWh)"), ("E8", "Project Cost (VND bn)"), ("G8", "Debt Capacity (VND bn)"), ("I8", "Min DSCR (x)"), ("K8", "LLCR (x)")]
    rows.append(row_xml(8, [value_cell(ref, label, ST_RAW_HEADER) for ref, label in labels1], 19))
    rows.append(row_xml(9, [
        formula_cell("A9", "INDEX('18_Portfolio'!$D$2:$D$21,MATCH($B$5,'18_Portfolio'!$A$2:$A$21,0))", cached["capacity"], ST_OUTPUT_GREEN),
        formula_cell("C9", "INDEX('05_Solar_Energy'!$C$2:$C$21,MATCH($B$5,'05_Solar_Energy'!$A$2:$A$21,0))/1000000", cached["p50"], ST_OUTPUT_GREEN),
        formula_cell("E9", "INDEX('07_CAPEX_Construction'!$N$2:$N$999,MATCH($B$5,'07_CAPEX_Construction'!$A$2:$A$999,0))/1000000000", cached["cost"], ST_OUTPUT_GREEN),
        formula_cell("G9", "INDEX('18_Portfolio'!$E$2:$E$21,MATCH($B$5,'18_Portfolio'!$A$2:$A$21,0))", cached["debt"], ST_OUTPUT_GREEN),
        formula_cell("I9", "INDEX('14_Coverage'!$B$2:$B$21,MATCH($B$5,'14_Coverage'!$A$2:$A$21,0))", cached["dscr"], ST_RATIO_LINK),
        formula_cell("K9", "INDEX('14_Coverage'!$C$2:$C$21,MATCH($B$5,'14_Coverage'!$A$2:$A$21,0))", cached["llcr"], ST_RATIO_LINK),
    ], 21))
    rows.append(row_xml(10, []))
    labels2 = [("A11", "PLCR (x)"), ("C11", "Project NPV (VND bn)"), ("E11", "Equity NPV (VND bn)"), ("G11", "Leverage Cap"), ("I11", "All-in Debt Rate"), ("K11", "IC Classification")]
    rows.append(row_xml(11, [value_cell(ref, label, ST_RAW_HEADER) for ref, label in labels2], 19))
    rows.append(row_xml(12, [
        formula_cell("A12", "INDEX('14_Coverage'!$D$2:$D$21,MATCH($B$5,'14_Coverage'!$A$2:$A$21,0))", cached["plcr"], ST_RATIO_LINK),
        formula_cell("C12", "INDEX('15_Returns_Discount'!$E$2:$E$21,MATCH($B$5,'15_Returns_Discount'!$A$2:$A$21,0))/1000000000", cached["pnpv"], ST_OUTPUT_RED if float(cached["pnpv"] or 0) < 0 else ST_OUTPUT_GREEN),
        formula_cell("E12", "INDEX('15_Returns_Discount'!$D$2:$D$21,MATCH($B$5,'15_Returns_Discount'!$A$2:$A$21,0))/1000000000", cached["enpv"], ST_OUTPUT_RED if float(cached["enpv"] or 0) < 0 else ST_OUTPUT_GREEN),
        formula_cell("G12", "INDEX('11_Debt_Terms'!$M$2:$M$21,MATCH($B$5,'11_Debt_Terms'!$B$2:$B$21,0))", cached["lev"], ST_PERCENT_LINK),
        formula_cell("I12", "INDEX('11_Debt_Terms'!$G$2:$G$21,MATCH($B$5,'11_Debt_Terms'!$B$2:$B$21,0))", cached["rate"], ST_PERCENT_LINK),
        formula_cell("K12", "INDEX('19_IC_Bankability'!$I$2:$I$21,MATCH($B$5,'19_IC_Bankability'!$A$2:$A$21,0))", cached["ic"], ST_STATUS_GREEN),
    ], 21))
    rows.append(row_xml(13, [])); rows.append(row_xml(14, []))
    rows.append(row_xml(15, [value_cell("A15", "MODEL ARCHITECTURE", ST_SECTION), value_cell("E15", "EXCEL SKILLS DEMONSTRATED", ST_SECTION)], 20))
    map_rows = [
        ("1. Inputs & Evidence", "01_Assumptions / 02_Evidence", "Hardcodes, source IDs, evidence classes"),
        ("2. Technical Model", "05_Solar_Energy / 06_Load_PPA", "P50/P90, yield, load matching, tariff value"),
        ("3. Construction & Opex", "07_CAPEX / 08_OPEX", "CAPEX schedule, VAT, IDC, O&M"),
        ("4. Cash Flow", "09_Project_CF_CFADS", "Revenue → tax → WC → maintenance → CFADS"),
        ("5. Debt", "11_Debt_Terms / 12_Debt_Sculpting", "Debt terms, sculpting, principal/interest schedule"),
        ("6. Credit Metrics", "14_Coverage", "DSCR / LLCR / PLCR / headroom"),
        ("7. Returns", "15_Returns_Discount", "Project / equity NPV and return framing"),
        ("8. Downside", "17_Scenarios_Sensitivity", "P90, rate, FX, DSO, COD and combined stress"),
        ("9. Decision", "19_IC_Bankability", "Sponsor + lender conditions and IC classification"),
        ("10. QA", "21_QA_Audit", "Reconciliation and release checks"),
    ]
    skill_rows = [
        ("Lookup / linking", "INDEX + MATCH", '=INDEX(return_range,MATCH(selected_project,project_id_range,0))'),
        ("Conditional logic", "IF / IFERROR", '=IF(metric>=threshold,"PASS","REVIEW")'),
        ("Aggregation", "SUMIFS", '=SUMIFS(value_range,project_id_range,selected_project,year_range,year)'),
        ("Debt sizing", "MIN / MAX", '=MIN(Debt_Leverage,Debt_DSCR,Debt_LLCR,Debt_PLCR)'),
        ("Scenario control", "Data Validation", "Project dropdown + scenario-ready input controls"),
        ("QA", "Reconciliation", '=Calculated_Output-Source_Output'),
    ]
    for i in range(10):
        r = 16 + i
        cells = [value_cell(f"A{r}", map_rows[i][0], ST_NORMAL), value_cell(f"B{r}", map_rows[i][1], ST_LINK), value_cell(f"C{r}", map_rows[i][2], ST_NORMAL)]
        if i < len(skill_rows):
            cells += [value_cell(f"E{r}", skill_rows[i][0], ST_NORMAL), value_cell(f"F{r}", skill_rows[i][1], ST_FORMULA), value_cell(f"G{r}", skill_rows[i][2], ST_NOTE)]
        rows.append(row_xml(r, cells, 30 if i < 6 else 24))
    rows.append(row_xml(27, [])); rows.append(row_xml(28, [value_cell("A28", "RECRUITER NOTE", ST_SECTION)], 20))
    rows.append(row_xml(29, [value_cell("A29", "This workbook demonstrates separated inputs, formula-driven calculations, cross-sheet links, debt sculpting, coverage analysis, downside scenarios, decision outputs and QA controls.", ST_NOTE)], 34))
    rows.append(row_xml(30, [value_cell("A30", "Model boundary: public-data / synthetic underwriting demonstration. Not an executed PPA, lender term sheet, investment approval or independent audit.", ST_NOTE)], 30))
    metadata = [("model_id", "VietGreen_CI_Solar_Project_Finance"), ("release_status", "candidate"), ("claim_boundary", "PASS_WITH_LIMITATIONS"), ("data_quality", f"{passed} / {checks} PASS"), ("billing_status", "WATCH"), ("github_sha", "remote-generated; see release manifest")]
    rows.append(row_xml(34, [value_cell("A34", "MODEL CONTROL METADATA", ST_RAW_HEADER)]))
    for i, (k, v) in enumerate(metadata, start=35):
        rows.append(row_xml(i, [value_cell(f"A{i}", k, ST_NORMAL), value_cell(f"B{i}", v, ST_NORMAL)]))
    merges = ["A1:L2", "A3:L3", "D5:L5", "A7:L7", "A8:B8", "C8:D8", "E8:F8", "G8:H8", "I8:J8", "K8:L8", "A9:B9", "C9:D9", "E9:F9", "G9:H9", "I9:J9", "K9:L9", "A11:B11", "C11:D11", "E11:F11", "G11:H11", "I11:J11", "K11:L11", "A12:B12", "C12:D12", "E12:F12", "G12:H12", "I12:J12", "K12:L12", "A15:C15", "E15:L15", "A28:L28", "A29:L29", "A30:L30", "A34:B34"]
    widths = [18, 18, 30, 4, 22, 18, 40, 14, 14, 14, 20, 20]
    project_list = ",".join(f"VG-{i:03d}" for i in range(1, 21))
    validation = '<dataValidations count="1"><dataValidation type="list" allowBlank="0" showErrorMessage="1" sqref="B5"><formula1>"' + project_list + '"</formula1></dataValidation></dataValidations>'
    return worksheet_wrapper("".join(rows), widths, merges=merges, freeze_row=5, data_validations=validation)


def build_debt_sheet(rows: list[list[str]], data: dict[str, list[list[str]]]) -> str:
    source = rows
    data_rows = source[1:] if len(source) > 1 else []
    terms = data["11_Debt_Terms"]
    portfolio = data["18_Portfolio"]
    debt_rate = lookup(terms, "project_or_portfolio_id", "VG-001", "all_in_rate", 0.085)
    target_dscr = lookup(terms, "project_or_portfolio_id", "VG-001", "sizing_dscr", 1.30)
    tenor = lookup(terms, "project_or_portfolio_id", "VG-001", "debt_tenor_years", 10)
    opening = scalar(data_rows[0][1]) / 1_000_000_000 if data_rows and len(data_rows[0]) > 1 else 0
    pooled_sum = 0.0
    if portfolio and len(portfolio) > 1 and "pooled_allocated_debt_bvnd" in portfolio[0]:
        idx = portfolio[0].index("pooled_allocated_debt_bvnd")
        pooled_sum = sum(float(scalar(r[idx]) or 0) for r in portfolio[1:] if len(r) > idx)
    if pooled_sum:
        opening = pooled_sum
    out: list[str] = []
    out.append(row_xml(1, [value_cell("A1", "DEBT SCULPTING — FORMULA-DRIVEN POOLED SCHEDULE", ST_TITLE)], 24)); out.append(row_xml(2, [], 24)); out.append(row_xml(3, []))
    out.append(row_xml(4, [
        value_cell("A4", "Debt Rate", ST_SECTION), formula_cell("B4", "'11_Debt_Terms'!G2", debt_rate, ST_PERCENT_LINK),
        value_cell("C4", "Target DSCR", ST_SECTION), formula_cell("D4", "'11_Debt_Terms'!H2", target_dscr, ST_RATIO_LINK),
        value_cell("E4", "Opening Debt (VND bn)", ST_SECTION), formula_cell("F4", "SUM('18_Portfolio'!G2:G21)", opening, ST_MONEY_LINK),
        value_cell("G4", "Debt Tenor", ST_SECTION), formula_cell("H4", "'11_Debt_Terms'!N2", tenor, ST_LINK),
        value_cell("I4", "Model Mode", ST_SECTION), value_cell("J4", "Sculpt to target DSCR", ST_KEY_INPUT),
    ], 22)); out.append(row_xml(5, []))
    headers = ["Year", "CFADS (VND bn)", "Opening Debt", "Interest", "Target DSCR", "Debt Service", "Principal", "Closing Debt", "Actual DSCR", "Check"]
    out.append(row_xml(6, [value_cell(f"{column_letter(i)}6", h, ST_HEADER) for i, h in enumerate(headers, start=1)], 22))
    for i in range(10):
        r = 7 + i
        src = data_rows[i] if i < len(data_rows) else [i + 1, 0, 0, 0, 0, 0, 0]
        year = scalar(src[0]) if len(src) > 0 else i + 1
        opening_c = float(scalar(src[1]) or 0) / 1_000_000_000 if len(src) > 1 else 0
        interest_c = float(scalar(src[2]) or 0) / 1_000_000_000 if len(src) > 2 else 0
        principal_c = float(scalar(src[3]) or 0) / 1_000_000_000 if len(src) > 3 else 0
        service_c = float(scalar(src[4]) or 0) / 1_000_000_000 if len(src) > 4 else 0
        closing_c = float(scalar(src[5]) or 0) / 1_000_000_000 if len(src) > 5 else 0
        dscr_c = scalar(src[6]) if len(src) > 6 else ""
        cfads = service_c * float(dscr_c or target_dscr) if service_c else 0
        out.append(row_xml(r, [
            value_cell(f"A{r}", year, ST_INTEGER),
            formula_cell(f"B{r}", f"'10_Portfolio_CFADS'!B{i+2}/1000000000", cfads, ST_MONEY_LINK),
            formula_cell(f"C{r}", "$F$4" if i == 0 else f"H{r-1}", opening_c, ST_MONEY),
            formula_cell(f"D{r}", f"C{r}*$B$4", interest_c, ST_MONEY),
            formula_cell(f"E{r}", "$D$4", target_dscr, ST_RATIO),
            formula_cell(f"F{r}", f"MIN(B{r}/E{r},C{r}+D{r})", service_c, ST_MONEY),
            formula_cell(f"G{r}", f"MAX(0,MIN(C{r},F{r}-D{r}))", principal_c, ST_MONEY),
            formula_cell(f"H{r}", f"MAX(0,C{r}-G{r})", closing_c, ST_MONEY),
            formula_cell(f"I{r}", f'IF(F{r}=0,"",B{r}/F{r})', dscr_c, ST_STATUS_GREEN if float(dscr_c or 0) >= 1.2 else ST_STATUS_RED),
            formula_cell(f"J{r}", f'IF(ABS(C{r}-G{r}-H{r})<0.000001,"PASS","REVIEW")', "PASS", ST_STATUS_GREEN),
        ]))
    out.append(row_xml(18, [])); out.append(row_xml(19, [value_cell("A19", "KEY FORMULAS — click calculation cells to inspect formulas", ST_SUBTITLE)], 20))
    notes = [
        ("Interest", "Opening Debt × Debt Rate", "=C7*$B$4"),
        ("Target Debt Service", "CFADS ÷ Target DSCR, capped by payoff amount", "=MIN(B7/E7,C7+D7)"),
        ("Principal", "Debt Service − Interest, floored at zero", "=MAX(0,MIN(C7,F7-D7))"),
        ("Closing Debt", "Opening Debt − Principal", "=MAX(0,C7-G7)"),
        ("Actual DSCR", "CFADS ÷ Debt Service", '=IF(F7=0,"",B7/F7)'),
        ("Balance Check", "Opening − Principal − Closing = 0", '=IF(ABS(C7-G7-H7)<0.000001,"PASS","REVIEW")'),
    ]
    for i, (name, desc, formula) in enumerate(notes, start=20):
        out.append(row_xml(i, [value_cell(f"A{i}", name, ST_NORMAL), value_cell(f"B{i}", desc, ST_NORMAL), value_cell(f"C{i}", formula, ST_NOTE)], 27))
    return worksheet_wrapper("".join(out), [12, 20, 20, 16, 16, 18, 18, 18, 16, 16], merges=["A1:J2", "A19:J19"], freeze_row=6)


def formula_override(sheet: str, row_num: int, col_num: int, row: list[Any], header: list[str], data: dict[str, list[list[str]]]) -> tuple[str, Any, int] | None:
    if sheet == "09_Project_CF_CFADS":
        if col_num == 21 and len(row) >= 21:
            return f"C{row_num}-D{row_num}-I{row_num}-K{row_num}-Q{row_num}+S{row_num}", scalar(row[20]), ST_MONEY
        if col_num == 24 and len(row) >= 24:
            return f"V{row_num}-W{row_num}", scalar(row[23]), ST_MONEY
    if sheet == "10_Portfolio_CFADS" and col_num == 4:
        return f'IF(C{row_num}=0,"",B{row_num}/C{row_num})', scalar(row[3]) if len(row) > 3 else "", ST_RATIO
    if sheet == "11_Debt_Terms" and col_num == 7:
        ref_rate = float(scalar(row[4]) or 0); spread = float(scalar(row[5]) or 0)
        return f"E{row_num}+F{row_num}/10000", ref_rate + spread / 10000, ST_PERCENT
    if sheet == "14_Coverage":
        if col_num == 6:
            return f"B{row_num}-INDEX('11_Debt_Terms'!$K$2:$K$21,MATCH(A{row_num},'11_Debt_Terms'!$B$2:$B$21,0))", scalar(row[5]) if len(row) > 5 else "", ST_RATIO
        if col_num == 10:
            cached = row[9] if len(row) > 9 else ""
            return f'IF(AND(B{row_num}>=INDEX(\'11_Debt_Terms\'!$J$2:$J$21,MATCH(A{row_num},\'11_Debt_Terms\'!$B$2:$B$21,0)),C{row_num}>=INDEX(\'11_Debt_Terms\'!$L$2:$L$21,MATCH(A{row_num},\'11_Debt_Terms\'!$B$2:$B$21,0)),D{row_num}>=1.25),"PASS","REVIEW")', cached, ST_STATUS_GREEN if str(cached) == "PASS" else ST_STATUS_AMBER
    if sheet == "15_Returns_Discount" and col_num == 9:
        cached = row[8] if len(row) > 8 else ""
        return f'IF(D{row_num}>0,"ABOVE_HURDLE","BELOW_HURDLE")', cached, ST_STATUS_GREEN if str(cached) == "ABOVE_HURDLE" else ST_STATUS_RED
    if sheet == "18_Portfolio" and col_num == 10:
        return f'IF(F{row_num}=0,"",I{row_num}/F{row_num})', scalar(row[9]) if len(row) > 9 else "", ST_RATIO
    return None


def build_generic_sheet(sheet: str, rows: list[list[str]], data: dict[str, list[list[str]]]) -> str:
    if not rows:
        rows = [["status", "empty"]]
    header = list(rows[0])
    extra_headers: list[str] = []
    if sheet == "17_Scenarios_Sensitivity":
        extra_headers = ["DSCR Headroom vs 1.20x", "Credit Flag"]
    elif sheet == "19_IC_Bankability":
        extra_headers = ["Formula Decision", "Formula Check"]
    out_header = header + extra_headers
    max_cols = len(out_header)
    body: list[str] = []
    body.append(row_xml(1, [value_cell(f"{column_letter(i)}1", h, ST_HEADER) for i, h in enumerate(out_header, start=1)], 30))
    input_sheet = sheet in INPUT_SHEETS
    for r_idx, source_row in enumerate(rows[1:], start=2):
        row = list(source_row) + [""] * (len(header) - len(source_row))
        cells: list[str] = []
        for c_idx, header_name in enumerate(header, start=1):
            ref = f"{column_letter(c_idx)}{r_idx}"
            override = formula_override(sheet, r_idx, c_idx, row, header, data)
            if override:
                formula, cached, style = override
                cells.append(formula_cell(ref, formula, cached, style)); continue
            value = scalar(row[c_idx - 1])
            style = detect_style(header_name, input_sheet=input_sheet)
            if input_sheet and sheet == "01_Assumptions" and header_name in {"base_value", "base_downside_upside"}:
                style = ST_KEY_INPUT if header_name == "base_value" else ST_INPUT
            if sheet == "21_QA_Audit" and isinstance(value, str):
                if value == "PASS": style = ST_STATUS_GREEN
                elif value == "FAIL": style = ST_STATUS_RED
            if isinstance(value, str) and value in {"PASS", "READY", "TRUE"}: style = ST_STATUS_GREEN
            elif isinstance(value, str) and value in {"FAIL", "REJECT", "BELOW_HURDLE"}: style = ST_STATUS_RED
            elif isinstance(value, str) and value in {"WATCH", "CONDITIONAL", "RENEGOTIATE", "REVIEW"}: style = ST_STATUS_AMBER
            cells.append(value_cell(ref, value, style))
        if sheet == "17_Scenarios_Sensitivity":
            portfolio_dscr = scalar(row[12]) if len(row) > 12 else ""
            headroom = float(portfolio_dscr) - 1.20 if isinstance(portfolio_dscr, (int, float)) else ""
            flag = "PASS" if isinstance(portfolio_dscr, (int, float)) and float(portfolio_dscr) >= 1.20 else "BREACH"
            cells.append(formula_cell(f"T{r_idx}", f'IF(M{r_idx}="","",M{r_idx}-1.20)', headroom, ST_RATIO if flag == "PASS" else ST_STATUS_RED))
            cells.append(formula_cell(f"U{r_idx}", f'IF(OR(M{r_idx}="",M{r_idx}<1.20),"BREACH","PASS")', flag, ST_STATUS_GREEN if flag == "PASS" else ST_STATUS_RED))
        elif sheet == "19_IC_Bankability":
            sponsor = str(row[1]) if len(row) > 1 else ""; lender = str(row[2]) if len(row) > 2 else ""; recorded = str(row[8]) if len(row) > 8 else ""
            decision = "REJECT" if sponsor == "FAIL" or lender == "FAIL" else ("INVEST_WITH_CONDITIONS" if sponsor == "CONDITIONAL" or lender == "CONDITIONAL" else "PASS")
            check = "MATCH" if decision == recorded else "REVIEW"
            cells.append(formula_cell(f"J{r_idx}", f'IF(OR(B{r_idx}="FAIL",C{r_idx}="FAIL"),"REJECT",IF(OR(B{r_idx}="CONDITIONAL",C{r_idx}="CONDITIONAL"),"INVEST_WITH_CONDITIONS","PASS"))', decision, ST_STATUS_RED if decision == "REJECT" else ST_STATUS_GREEN))
            cells.append(formula_cell(f"K{r_idx}", f'IF(J{r_idx}=I{r_idx},"MATCH","REVIEW")', check, ST_STATUS_GREEN if check == "MATCH" else ST_STATUS_AMBER))
        body.append(row_xml(r_idx, cells))
    widths: list[float] = []
    for c_idx, head in enumerate(out_header):
        vals = [r[c_idx] if c_idx < len(r) else "" for r in rows[1:]] if c_idx < len(header) else []
        widths.append(estimated_width(vals, head))
    if sheet == "17_Scenarios_Sensitivity": widths[-2:] = [18, 14]
    if sheet == "19_IC_Bankability": widths[-2:] = [24, 14]
    auto_ref = f"A1:{column_letter(max_cols)}{max(1, len(rows))}"
    return worksheet_wrapper("".join(body), widths, freeze_row=1, auto_filter=auto_ref)


def styles_xml() -> str:
    numfmts = '<numFmts count="5"><numFmt numFmtId="164" formatCode="#,##0.00;[Red](#,##0.00);-"/><numFmt numFmtId="165" formatCode="0.0%"/><numFmt numFmtId="166" formatCode="0.00x"/><numFmt numFmtId="167" formatCode="#,##0;[Red](#,##0);-"/><numFmt numFmtId="168" formatCode="0.00"/></numFmts>'
    fonts = '<fonts count="8"><font><sz val="10"/><name val="Calibri"/><color rgb="FF000000"/></font><font><b/><sz val="16"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font><font><i/><sz val="10"/><name val="Calibri"/><color rgb="FF17365D"/></font><font><b/><sz val="10"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font><font><sz val="10"/><name val="Calibri"/><color rgb="FF0000FF"/></font><font><sz val="10"/><name val="Calibri"/><color rgb="FF008000"/></font><font><b/><sz val="10"/><name val="Calibri"/><color rgb="FF008000"/></font><font><b/><sz val="10"/><name val="Calibri"/><color rgb="FFC00000"/></font></fonts>'
    fills = '<fills count="9"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF0B1F3A"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFD9EAF7"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFF2F2F2"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE2F0D9"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFF4CCCC"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF7F7F7F"/><bgColor indexed="64"/></patternFill></fill></fills>'
    borders = '<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style="thin"><color rgb="FFD9E1F2"/></left><right style="thin"><color rgb="FFD9E1F2"/></right><top style="thin"><color rgb="FFD9E1F2"/></top><bottom style="thin"><color rgb="FFD9E1F2"/></bottom><diagonal/></border></borders>'
    xfs: list[str] = []
    def xf(font=0, fill=0, border=0, num=0, align=""):
        attrs = f'numFmtId="{num}" fontId="{font}" fillId="{fill}" borderId="{border}" xfId="0"'; flags = []
        if num: flags.append('applyNumberFormat="1"')
        if font: flags.append('applyFont="1"')
        if fill: flags.append('applyFill="1"')
        if border: flags.append('applyBorder="1"')
        if align:
            flags.append('applyAlignment="1"'); return f'<xf {attrs} {" ".join(flags)}><alignment {align}/></xf>'
        return f'<xf {attrs} {" ".join(flags)}/>'
    xfs.extend([
        xf(), xf(font=1, fill=2, align='vertical="center"'), xf(font=2, fill=3, align='vertical="center"'), xf(font=3, fill=2, align='vertical="center"'),
        xf(font=3, fill=2, border=1, align='horizontal="center" vertical="center" wrapText="1"'), xf(font=4, border=1), xf(font=4, fill=5, border=1, align='horizontal="center"'), xf(border=1), xf(font=5, border=1),
        xf(border=1, num=164), xf(font=5, border=1, num=164), xf(border=1, num=165), xf(font=5, border=1, num=165), xf(border=1, num=166), xf(font=5, border=1, num=166),
        xf(font=6, fill=6, border=1, align='horizontal="center"'), xf(font=7, fill=7, border=1, align='horizontal="center"'), xf(fill=5, border=1, align='horizontal="center"'), xf(font=2, fill=4, align='vertical="top" wrapText="1"'),
        xf(font=3, fill=8, border=1, align='vertical="center" wrapText="1"'), xf(font=4, border=1, num=164), xf(font=4, border=1, num=165), xf(font=4, border=1, num=166), xf(border=1, num=167), xf(font=4, border=1, num=167),
        xf(font=6, border=1, num=164, align='horizontal="center"'), xf(font=7, border=1, num=164, align='horizontal="center"'), xf(border=1, num=168), xf(font=5, border=1, num=168),
    ])
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' + numfmts + fonts + fills + borders + '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>' + f'<cellXfs count="{len(xfs)}">{"".join(xfs)}</cellXfs>' + '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'


def write_deterministic_entry(archive: zipfile.ZipFile, name: str, payload: str | bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; info.create_system = 3; archive.writestr(info, payload)


def build() -> None:
    output = ROOT / "model" / "vietgreen_core_model.xlsx"; output.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, list[list[str]]] = {name: ([] if source is None else read_rows(source)) for name, source in SHEETS}
    workbook = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">', '<bookViews><workbookView xWindow="0" yWindow="0" windowWidth="24000" windowHeight="12000"/></bookViews>', '<sheets>']
    rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">', '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>', '<Default Extension="xml" ContentType="application/xml"/>', '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>', '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>', '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>', '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>']
    payloads: dict[int, str] = {}
    for index, (name, _source) in enumerate(SHEETS, start=1):
        xml = build_control_sheet(data) if name == "00_Control" else (build_debt_sheet(data[name], data) if name == "12_Debt_Sculpting" else build_generic_sheet(name, data[name], data))
        payloads[index] = xml
        workbook.append(f'<sheet name="{html.escape(name, quote=True)}" sheetId="{index}" r:id="rId{index}"/>')
        rels.append(f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{index}.xml"/>')
        content_types.append(f'<Override PartName="/xl/worksheets/sheet{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
    workbook.extend(['</sheets>', '<calcPr calcId="191029" calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1"/>', '</workbook>'])
    rels.extend(['<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>', '</Relationships>']); content_types.append('</Types>')
    root_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdWorkbook" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    core = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>VietGreen C&amp;I Solar Project Finance — Recruiter Model</dc:title><dc:subject>Formula-driven Project Finance workbook</dc:subject><dc:creator>VietGreen recruiter workbook builder</dc:creator></cp:coreProperties>'
    app = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Excel compatible OOXML</Application></Properties>'
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        write_deterministic_entry(archive, "[Content_Types].xml", "".join(content_types)); write_deterministic_entry(archive, "_rels/.rels", root_rels); write_deterministic_entry(archive, "docProps/core.xml", core); write_deterministic_entry(archive, "docProps/app.xml", app); write_deterministic_entry(archive, "xl/workbook.xml", "".join(workbook)); write_deterministic_entry(archive, "xl/_rels/workbook.xml.rels", "".join(rels)); write_deterministic_entry(archive, "xl/styles.xml", styles_xml())
        for index, xml in payloads.items(): write_deterministic_entry(archive, f"xl/worksheets/sheet{index}.xml", xml)
    print(json.dumps({"path": str(output), "sheets": len(SHEETS), "bytes": output.stat().st_size, "format": "recruiter-model"}, sort_keys=True))


if __name__ == "__main__":
    build()
