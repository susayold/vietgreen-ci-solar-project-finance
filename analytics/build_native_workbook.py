"""Build the native 22-sheet workbook on the remote Actions runner.

The workbook is generated from the checked-out GitHub CSV outputs/evidence and
then committed back to GitHub by the workflow. The desktop workspace receives
no project data.
"""

from __future__ import annotations

import csv
import html
import json
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEETS = [
    ("00_Control", None),
    ("01_Assumptions", "evidence/ASSUMPTION_REGISTER.csv"),
    ("02_Evidence_Regulatory", "evidence/REGULATORY_REGISTER.csv"),
    ("03_Project_Pipeline", "data/synthetic/project_master.csv"),
    ("04_Offtakers_Credit_Site", "data/synthetic/offtaker_master.csv"),
    ("05_Solar_Energy", "outputs/energy_p50_p90.csv"),
    ("06_Load_PPA", "outputs/load_matching_summary.csv"),
    ("07_CAPEX_Construction", "data/synthetic/capex.csv"),
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


def read_rows(relative_path, limit=600):
    path = ROOT / relative_path
    if not path.exists():
        return [["status", "not_generated_on_this_runner"]]
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = []
        for row in reader:
            rows.append(row)
            if len(rows) >= limit:
                break
        return rows or [["status", "empty"]]


def cell(value):
    text = html.escape(str(value), quote=False)
    return '<c t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % text


def worksheet_xml(rows):
    row_xml = []
    for row_number, row in enumerate(rows, start=1):
        cells = "".join(cell(value) for value in row)
        row_xml.append('<row r="%d">%s</row>' % (row_number, cells))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<sheetData>%s</sheetData></worksheet>" % "".join(row_xml)
    )


def build_control_rows():
    dq = read_rows("validation/DATA_QUALITY_RESULTS.csv")
    passed = sum(1 for row in dq[1:] if len(row) > 5 and row[5] == "PASS")
    checks = max(0, len(dq) - 1)
    return [
        ["control", "value"],
        ["project", "VietGreen_CI_Solar_Project_Finance"],
        ["release_status", "candidate"],
        ["claim_boundary", "PASS_WITH_LIMITATIONS"],
        ["data_quality", "%d / %d PASS" % (passed, checks)],
        ["billing_status", "WATCH"],
        ["github_sha", os.environ.get("GITHUB_SHA", "remote-run")],
        ["storage_policy", "GitHub + Google Drive only; no desktop project data"],
    ]


def build():
    output = ROOT / "model" / "vietgreen_core_model.xlsx"
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook_xml = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
        "<sheets>",
    ]
    relationships = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
    ]
    sheet_payloads = {}
    for index, (name, source) in enumerate(SHEETS, start=1):
        rows = build_control_rows() if source is None else read_rows(source)
        sheet_payloads[index] = worksheet_xml(rows)
        workbook_xml.append('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (html.escape(name, quote=True), index, index))
        relationships.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (index, index))
        content_types.append('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % index)
    workbook_xml.extend(["</sheets>", "</workbook>"])
    relationships.extend([
        '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
        "</Relationships>",
    ])
    content_types.append("</Types>")
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rIdWorkbook" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellXfs>'
        '</styleSheet>'
    )
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "".join(content_types))
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("xl/workbook.xml", "".join(workbook_xml))
        archive.writestr("xl/_rels/workbook.xml.rels", "".join(relationships))
        archive.writestr("xl/styles.xml", styles)
        for index, xml in sheet_payloads.items():
            archive.writestr("xl/worksheets/sheet%d.xml" % index, xml)
    print(json.dumps({"path": str(output), "sheets": len(SHEETS), "bytes": output.stat().st_size}, sort_keys=True))


if __name__ == "__main__":
    build()
