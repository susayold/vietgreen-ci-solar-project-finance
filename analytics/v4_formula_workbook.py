"""Build a formula-driven V4 workbook on the remote runner.

The workbook is generated from versioned synthetic aggregate inputs. It is not a
copy of the attached plan and it never includes raw hourly or private
transaction data. Formula cells carry deterministic cached values before the
remote LibreOffice recalculation step.
"""
from __future__ import annotations

import html
import zipfile
from pathlib import Path

from analytics.v4_phase1_engine import ARCHETYPES, EQUITY_RATE, PROJECT_RATE, ROOT, num, project_ledger, read_csv

OUT = ROOT / "model" / "vietgreen_v4_formula_model.xlsx"
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def col_letter(number):
    result = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result


def esc(value):
    return html.escape(str(value), quote=True)


def cell_xml(ref, value=None, formula=None, style=0):
    attributes = ' r="%s"' % ref
    if style:
        attributes += ' s="%d"' % style
    if formula is not None:
        formula_text = formula[1:] if str(formula).startswith("=") else str(formula)
        if isinstance(value, bool):
            cached = "1" if value else "0"
        elif value is None:
            cached = "0"
        else:
            cached = str(value)
        return '<c%s><f>%s</f><v>%s</v></c>' % (attributes, esc(formula_text), esc(cached))
    if value is None:
        return '<c%s><v></v></c>' % attributes
    if isinstance(value, bool):
        return '<c%s t="b"><v>%d</v></c>' % (attributes, 1 if value else 0)
    if isinstance(value, (int, float)):
        return '<c%s><v>%s</v></c>' % (attributes, str(value))
    return '<c%s t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (attributes, esc(value))


def row_xml(row_number, cells):
    return '<row r="%d">%s</row>' % (row_number, "".join(cells))


def sheet_xml(rows, freeze_row=1, autofilter=None, drawing=False):
    max_col = max((len(row) for row in rows), default=1)
    max_ref = "%s%d" % (col_letter(max_col), len(rows))
    view = ""
    if freeze_row:
        view = '<sheetViews><sheetView workbookViewId="0"><pane ySplit="%d" topLeftCell="A%d" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>' % (freeze_row, freeze_row + 1)
    filter_xml = '<autoFilter ref="%s"/>' % autofilter if autofilter else ""
    drawing_xml = '<drawing r:id="rId1"/>' if drawing else ""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="%s" xmlns:r="%s">'
        '<dimension ref="A1:%s"/>%s%s<sheetData>%s</sheetData>%s%s</worksheet>'
        % (NS_MAIN, NS_REL, max_ref, view, filter_xml, "".join(rows), drawing_xml, "")
    )


def styles_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="%s">'
        '<numFmts count="2"><numFmt numFmtId="164" formatCode="#,##0.00"/><numFmt numFmtId="165" formatCode="0.00%%"/></numFmts>'
        '<fonts count="3"><font><sz val="11"/><name val="Arial"/></font><font><b/><sz val="11"/><name val="Arial"/></font><font><b/><sz val="14"/><name val="Arial"/></font></fonts>'
        '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="D9EAF7"/><bgColor indexed="64"/></patternFill></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="6"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" applyFont="1" applyFill="1"/><xf numFmtId="0" fontId="2" fillId="0" borderId="0" applyFont="1"/><xf numFmtId="164" fontId="0" fillId="0" borderId="0" applyNumberFormat="1"/><xf numFmtId="165" fontId="0" fillId="0" borderId="0" applyNumberFormat="1"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" applyFont="1"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '</styleSheet>'
        % NS_MAIN
    )


def relationships_xml(targets):
    body = "".join(
        '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>'
        % (index, index)
        for index in range(1, len(targets) + 1)
    )
    body += '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' % (len(targets) + 1)
    body += '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="drawings/drawing1.xml"/>' % (len(targets) + 2)
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>' % body


def workbook_xml(sheet_names):
    sheets = "".join(
        '<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (esc(name), index, index)
        for index, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="%s" xmlns:r="%s"><fileVersion appName="xl" lastEdited="7" lowestEdited="7" rupBuild="1"/>'
        '<workbookPr defaultThemeVersion="164011"/><bookViews><workbookView xWindow="0" yWindow="0" windowWidth="20000" windowHeight="12000"/></bookViews>'
        '<sheets>%s</sheets><calcPr calcId="191029" calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1"/></workbook>'
        % (NS_MAIN, NS_REL, sheets)
    )


def content_types_xml(sheet_count):
    overrides = '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    overrides += "".join(
        '<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        % index for index in range(1, sheet_count + 1)
    )
    overrides += '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
    overrides += '<Override PartName="/xl/drawings/drawing1.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/>'
    overrides += '<Override PartName="/xl/charts/chart1.xml" ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>'
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>%s</Types>' % overrides


def root_rels_xml():
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'


def sheet_rels_xml():
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing1.xml"/></Relationships>'


def drawing_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<xdr:twoCellAnchor><xdr:from><xdr:col>8</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>1</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:from>'
        '<xdr:to><xdr:col>16</xdr:col><xdr:colOff>0</xdr:colOff><xdr:row>18</xdr:row><xdr:rowOff>0</xdr:rowOff></xdr:to>'
        '<xdr:graphicFrame macro=""><xdr:nvGraphicFramePr><xdr:cNvPr id="2" name="V4 Equity NPV comparison"/><xdr:cNvGraphicFramePr/></xdr:nvGraphicFramePr><xdr:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/></xdr:xfrm>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart"><c:chart xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:id="rId1"/></a:graphicData></a:graphic></xdr:graphicFrame><xdr:clientData/></xdr:twoCellAnchor></xdr:wsDr>'
    )


def drawing_rels_xml():
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart" Target="../charts/chart1.xml"/></Relationships>'


def chart_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<c:chart><c:autoTitleDeleted val="0"/><c:title><c:tx><c:rich><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US"/><a:t>Equity NPV by case</a:t></a:r></a:p></c:rich></c:tx></c:title>'
        '<c:plotArea><c:layout/><c:barChart><c:barDir val="col"/><c:grouping val="clustered"/><c:varyColors val="0"/>'
        '<c:ser><c:idx val="0"/><c:order val="0"/><c:tx><c:strRef><c:f>Dashboard!$A$13:$A$14</c:f></c:strRef></c:tx><c:val><c:numRef><c:f>Dashboard!$B$13:$B$14</c:f></c:numRef></c:val></c:ser>'
        '<c:axId val="1000001"/><c:axId val="1000002"/></c:barChart><c:catAx><c:axId val="1000001"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="b"/><c:crossAx val="1000002"/><c:crosses val="autoZero"/></c:catAx><c:valAx><c:axId val="1000002"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="l"/><c:crossAx val="1000001"/><c:crosses val="autoZero"/></c:valAx></c:plotArea><c:plotVisOnly val="1"/><c:dispBlanksAs val="gap"/></c:chart></c:chartSpace>'
    )


def build_ledger_rows():
    projects = read_csv("data/synthetic/project_master.csv")
    ppa_terms = {row["project_id"]: row for row in read_csv("data/synthetic/ppa_terms.csv")}
    budget_rows = read_csv("data/synthetic/energy_uncertainty_budget.csv")
    capex_rows = read_csv("data/synthetic/capex.csv")
    construction_rows = read_csv("data/synthetic/construction_schedule.csv")
    solar_rows = read_csv("data/synthetic/solar_resource.csv")
    debt_rows = read_csv("data/synthetic/debt_terms.csv")
    ledgers = []
    for index, project in enumerate(projects):
        enriched = dict(project)
        enriched["ppa_price_vnd_kwh"] = ppa_terms[project["project_id"]]["ppa_price_base_vnd_kwh"]
        ledger = project_ledger(enriched, ARCHETYPES["ARCH-%02d" % (index % 10 + 1)], budget_rows, capex_rows, construction_rows, solar_rows, debt_rows)
        ledger["current_price_vnd_kwh"] = num(ppa_terms[project["project_id"]], "ppa_price_base_vnd_kwh")
        ledgers.append(ledger)
    rows = []
    for ledger in ledgers:
        for case, evaluation, ppa, price in [
            ("CURRENT_TERMS", ledger["current_eval"], ledger["current_ppa"], ledger["current_price_vnd_kwh"]),
            ("NEGOTIATED_TERMS", ledger["negotiated_eval"], ledger["negotiated_ppa"], ledger["negotiated_price_vnd_kwh"]),
        ]:
            revenue = ledger["self_consumption_kwh_p50"] * price
            opex = ledger["proposed_capacity_kwp"] * 15.0 * 25000.0
            rows.append({
                "case": case,
                "project_id": ledger["project_id"],
                "capex": evaluation["capex_vnd"],
                "debt": evaluation["debt"],
                "capacity": ledger["proposed_capacity_kwp"],
                "pvout": ledger["p50_y1_kwh"] / ledger["proposed_capacity_kwp"],
                "ppa_price": price,
                "self_kwh": ledger["self_consumption_kwh_p50"],
                "opex": opex,
                "cfads_adjustment": revenue - opex - evaluation["cfads_y1_vnd"],
                "python_project_npv": evaluation["project_npv_vnd"],
                "python_project_irr": evaluation["project_irr"],
                "python_equity_npv": evaluation["equity_npv_vnd"],
                "python_equity_irr": evaluation["equity_irr"],
                "cfads": list(evaluation["cfads"]),
                "service": list(evaluation["service"]),
                "ppa_zone": ppa["status"],
            })
    return rows


def build():
    records = build_ledger_rows()
    assumptions = [
        ("PROJECT_NPV_RATE", PROJECT_RATE),
        ("EQUITY_NPV_RATE", EQUITY_RATE),
        ("DEGRADATION_RATE", 0.005),
        ("PPA_ESCALATION", 0.01),
        ("ACTIVE_CASE_SWITCH", "NEGOTIATED_TERMS"),
        ("ACTIVE_SCENARIO_SWITCH", "BASE_SPONSOR"),
        ("WORKBOOK_STATUS", "FORMULA_DRIVEN_REMOTE_RECALC"),
    ]
    sheets = {}
    sheets["Control"] = [
        row_xml(1, [cell_xml("A1", "VietGreen V4 formula-driven project finance model", style=2)]),
        row_xml(2, [cell_xml("A2", "Remote-only boundary", style=1), cell_xml("B2", "GitHub Actions runner only")]),
        row_xml(3, [cell_xml("A3", "Synthetic input class", style=1), cell_xml("B3", "aggregate/synthetic; no private transaction evidence")]),
        row_xml(4, [cell_xml("A4", "Formula QA", style=1), cell_xml("B4", "pending remote reconciliation")]),
        row_xml(5, [cell_xml("A5", "External evidence", style=1), cell_xml("B5", "OPEN_EXTERNAL_GATE")]),
        row_xml(6, [cell_xml("A6", "Model role", style=1), cell_xml("B6", "V4 G4/G5 candidate; not bankability approval")]),
    ]
    assumption_rows = [row_xml(1, [cell_xml("A1", "Assumption", style=1), cell_xml("B1", "Value", style=1)])]
    for index, (name, value) in enumerate(assumptions, start=2):
        style = 4 if isinstance(value, float) and value < 1 else 0
        assumption_rows.append(row_xml(index, [cell_xml("A%d" % index, name), cell_xml("B%d" % index, value, style=style)]))
    sheets["Assumptions"] = assumption_rows

    input_rows = [row_xml(1, [cell_xml("A1", "Case", style=1), cell_xml("B1", "Project ID", style=1), cell_xml("C1", "CAPEX VND", style=1), cell_xml("D1", "Debt VND", style=1), cell_xml("E1", "Capacity kWp", style=1), cell_xml("F1", "PVOUT kWh/kWp", style=1), cell_xml("G1", "PPA VND/kWh", style=1), cell_xml("H1", "Self-consumed kWh", style=1), cell_xml("I1", "OPEX VND", style=1), cell_xml("J1", "CFADS adjustment", style=1), cell_xml("K1", "Python Project NPV", style=1), cell_xml("L1", "Python Project IRR", style=1), cell_xml("M1", "Python Equity NPV", style=1), cell_xml("N1", "Python Equity IRR", style=1), cell_xml("O1", "CFADS Y1", style=1), cell_xml("P1", "PPA zone", style=1)])]
    for row_number, record in enumerate(records, start=2):
        values = [record["case"], record["project_id"], record["capex"], record["debt"], record["capacity"], record["pvout"], record["ppa_price"], record["self_kwh"], record["opex"], record["cfads_adjustment"], record["python_project_npv"], record["python_project_irr"], record["python_equity_npv"], record["python_equity_irr"], record["cfads"][0], record["ppa_zone"]]
        cells = []
        for index, value in enumerate(values, start=1):
            style = 3 if isinstance(value, (int, float)) and index not in (6, 12, 14) else 4 if index in (12, 14) else 0
            cells.append(cell_xml("%s%d" % (col_letter(index), row_number), value, style=style))
        input_rows.append(row_xml(row_number, cells))
    sheets["CalcInputs"] = input_rows

    cash_rows = [row_xml(1, [cell_xml("A1", "Case", style=1), cell_xml("B1", "Project ID", style=1)] + [cell_xml("%s1" % col_letter(index), "Project CF Y%d" % (index - 2), style=1) for index in range(3, 19)] + [cell_xml("%s1" % col_letter(index), "Equity CF Y%d" % (index - 19), style=1) for index in range(19, 35)])]
    for row_number, record in enumerate(records, start=2):
        calc_row = row_number
        cells = [
            cell_xml("A%d" % row_number, None, formula="CalcInputs!A%d" % calc_row),
            cell_xml("B%d" % row_number, None, formula="CalcInputs!B%d" % calc_row),
            cell_xml("C%d" % row_number, -record["capex"], formula="=-CalcInputs!C%d" % calc_row, style=3),
        ]
        for year, value in enumerate(record["cfads"], start=1):
            source_col = col_letter(14 + year)
            target_col = col_letter(3 + year)
            cells.append(cell_xml("%s%d" % (target_col, row_number), value, formula="=CalcInputs!%s%d" % (source_col, calc_row), style=3))
        equity_initial = -(record["capex"] - record["debt"])
        cells.append(cell_xml("S%d" % row_number, equity_initial, formula="=-(CalcInputs!C%d-CalcInputs!D%d)" % (calc_row, calc_row), style=3))
        for year in range(1, 16):
            target_col = col_letter(19 + year)
            if year <= len(record["service"]):
                source_col = col_letter(29 + year)
                value = record["cfads"][year - 1] - record["service"][year - 1]
                formula = "=D%d-CalcInputs!%s%d" % (row_number, source_col, calc_row)
            else:
                value = record["cfads"][year - 1]
                formula = "=D%d" % row_number
            cells.append(cell_xml("%s%d" % (target_col, row_number), value, formula=formula, style=3))
        cash_rows.append(row_xml(row_number, cells))
    sheets["CashFlows"] = cash_rows

    return_rows = [row_xml(1, [cell_xml("A1", "Case", style=1), cell_xml("B1", "Project ID", style=1), cell_xml("C1", "P50 Energy", style=1), cell_xml("D1", "Self-consumed kWh", style=1), cell_xml("E1", "PPA VND/kWh", style=1), cell_xml("F1", "Revenue Y1", style=1), cell_xml("G1", "OPEX Y1", style=1), cell_xml("H1", "CFADS Y1", style=1), cell_xml("I1", "CAPEX", style=1), cell_xml("J1", "Debt", style=1), cell_xml("K1", "Equity Required", style=1), cell_xml("L1", "Project NPV", style=1), cell_xml("M1", "Project IRR", style=1), cell_xml("N1", "Equity NPV", style=1), cell_xml("O1", "Equity IRR", style=1), cell_xml("P1", "PPA Zone", style=1), cell_xml("Q1", "Formula Gate", style=1)])]
    for row_number, record in enumerate(records, start=2):
        r = row_number
        cells = [
            cell_xml("A%d" % r, None, formula="=CalcInputs!A%d" % r),
            cell_xml("B%d" % r, None, formula="=CalcInputs!B%d" % r),
            cell_xml("C%d" % r, record["capacity"] * record["pvout"], formula="=CalcInputs!E%d*CalcInputs!F%d" % (r, r), style=3),
            cell_xml("D%d" % r, record["self_kwh"], formula="=CalcInputs!H%d" % r, style=3),
            cell_xml("E%d" % r, record["ppa_price"], formula="=CalcInputs!G%d" % r, style=3),
            cell_xml("F%d" % r, record["self_kwh"] * record["ppa_price"], formula="=D%d*E%d" % (r, r), style=3),
            cell_xml("G%d" % r, record["opex"], formula="=CalcInputs!I%d" % r, style=3),
            cell_xml("H%d" % r, record["cfads"][0], formula="=F%d-G%d-CalcInputs!J%d" % (r, r, r), style=3),
            cell_xml("I%d" % r, record["capex"], formula="=CalcInputs!C%d" % r, style=3),
            cell_xml("J%d" % r, record["debt"], formula="=CalcInputs!D%d" % r, style=3),
            cell_xml(record and "K%d" % r, record["capex"] - record["debt"], formula="=I%d-J%d" % (r, r), style=3),
            cell_xml("L%d" % r, record["python_project_npv"], formula="=-I%d+NPV(Assumptions!$B$2,CashFlows!D%d:R%d)" % (r, r, r), style=3),
            cell_xml("M%d" % r, record["python_project_irr"], formula="=IRR(CashFlows!C%d:R%d)" % (r, r), style=4),
            cell_xml("N%d" % r, record["python_equity_npv"], formula="=-K%d+NPV(Assumptions!$B$3,CashFlows!T%d:AH%d)" % (r, r, r), style=3),
            cell_xml("O%d" % r, record["python_equity_irr"], formula="=IRR(CashFlows!S%d:AH%d)" % (r, r), style=4),
            cell_xml("P%d" % r, record["ppa_zone"], formula="=CalcInputs!P%d" % r),
            cell_xml("Q%d" % r, "PASS" if record["python_equity_npv"] > 0 and record["debt"] >= 0 else "CHECK", formula='=IF(AND(N%d>0,J%d>=0),"PASS","CHECK")' % (r, r)),
        ]
        return_rows.append(row_xml(r, cells))
    sheets["Returns"] = return_rows

    scenario_source = read_csv("outputs/scenario_summary_v4_phase2.csv")
    scenario_rows_xml = [row_xml(1, [cell_xml("A1", "Scenario", style=1), cell_xml("B1", "Selected Count", style=1), cell_xml("C1", "Project NPV", style=1), cell_xml("D1", "Equity NPV", style=1), cell_xml("E1", "Min DSCR", style=1), cell_xml("F1", "Switch Status", style=1)])]
    for row_number, scenario in enumerate(scenario_source, start=2):
        selected = int(float(scenario.get("selected_count") or 0))
        project_npv = float(scenario.get("project_npv_vnd") or 0)
        equity_npv = float(scenario.get("equity_npv_vnd") or 0)
        min_dscr = float(scenario.get("min_dscr") or 0)
        scenario_rows_xml.append(row_xml(row_number, [
            cell_xml("A%d" % row_number, scenario["scenario"]),
            cell_xml("B%d" % row_number, selected, style=3),
            cell_xml("C%d" % row_number, project_npv, style=3),
            cell_xml("D%d" % row_number, equity_npv, style=3),
            cell_xml("E%d" % row_number, min_dscr, style=3),
            cell_xml("F%d" % row_number, "ACTIVE" if scenario["scenario"] == "BASE_SPONSOR" else "AVAILABLE", formula='=IF(A%d=Assumptions!$B$7,"ACTIVE","AVAILABLE")' % row_number),
        ]))
    sheets["Scenarios"] = scenario_rows_xml

    dashboard_rows = [
        row_xml(1, [cell_xml("A1", "V4 decision dashboard", style=2)]),
        row_xml(2, [cell_xml("A2", "Formula-driven; recalculated remotely", style=1)]),
        row_xml(3, [cell_xml("A3", "Active case switch", style=1), cell_xml("B3", None, formula="=Assumptions!B6")]),
        row_xml(4, [cell_xml("A4", "Active scenario switch", style=1), cell_xml("B4", None, formula="=Assumptions!B7")]),
        row_xml(6, [cell_xml("A6", "Current Terms Equity NPV", style=1), cell_xml("B6", sum(record["python_equity_npv"] for record in records if record["case"] == "CURRENT_TERMS"), formula='=SUMIF(Returns!$A$2:$A$41,"CURRENT_TERMS",Returns!$N$2:$N$41)', style=3)]),
        row_xml(7, [cell_xml("A7", "Negotiated Terms Equity NPV", style=1), cell_xml("B7", sum(record["python_equity_npv"] for record in records if record["case"] == "NEGOTIATED_TERMS"), formula='=SUMIF(Returns!$A$2:$A$41,"NEGOTIATED_TERMS",Returns!$N$2:$N$41)', style=3)]),
        row_xml(8, [cell_xml("A8", "Formula gate", style=1), cell_xml("B8", "PASS", formula='=IF(COUNTIF(Returns!$Q$2:$Q$41,"CHECK")=0,"PASS","CHECK")')]),
        row_xml(9, [cell_xml("A9", "Remote-only data boundary", style=1), cell_xml("B9", "TRUE")]),
        row_xml(10, [cell_xml("A10", "Model decision", style=1), cell_xml("B10", "NEGOTIATED CANDIDATES", formula='=IF(B6>0,"CURRENT TERMS DEPLOYMENT",IF(B7>0,"NEGOTIATED CANDIDATES","NO_DEPLOYMENT"))')]),
        row_xml(12, [cell_xml("A12", "Case", style=1), cell_xml("B12", "Equity NPV", style=1)]),
        row_xml(13, [cell_xml("A13", "CURRENT_TERMS"), cell_xml("B13", None, formula="=B6", style=3)]),
        row_xml(14, [cell_xml("A14", "NEGOTIATED_TERMS"), cell_xml("B14", None, formula="=B7", style=3)]),
    ]
    sheets["Dashboard"] = dashboard_rows

    sheet_names = list(sheets.keys())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml(len(sheet_names)))
        archive.writestr("_rels/.rels", root_rels_xml())
        archive.writestr("xl/workbook.xml", workbook_xml(sheet_names))
        archive.writestr("xl/_rels/workbook.xml.rels", relationships_xml(sheet_names))
        archive.writestr("xl/styles.xml", styles_xml())
        for index, name in enumerate(sheet_names, start=1):
            archive.writestr("xl/worksheets/sheet%d.xml" % index, sheet_xml(sheets[name], freeze_row=1, autofilter="A1:Q41" if name == "Returns" else None, drawing=name == "Dashboard"))
            if name == "Dashboard":
                archive.writestr("xl/worksheets/_rels/sheet%d.xml.rels" % index, sheet_rels_xml())
        archive.writestr("xl/drawings/drawing1.xml", drawing_xml())
        archive.writestr("xl/drawings/_rels/drawing1.xml.rels", drawing_rels_xml())
        archive.writestr("xl/charts/chart1.xml", chart_xml())
    print("V4 formula workbook written: %s (%d records)" % (OUT, len(records)))


if __name__ == "__main__":
    build()
