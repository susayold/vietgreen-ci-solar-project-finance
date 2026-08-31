"""Remote structural validator for the committed native workbook artifact.

This check runs on the ephemeral GitHub Actions runner. It is not a substitute
for independent engineering, lender, legal or desktop-Excel review.
"""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "model" / "vietgreen_core_model.xlsx"
RESULTS = ROOT / "validation" / "WORKBOOK_VALIDATION_RESULTS.csv"
REPORT = ROOT / "validation" / "WORKBOOK_VALIDATION_REPORT.md"

EXPECTED_SHEETS = [
    "00_Control", "01_Assumptions", "02_Evidence_Regulatory", "03_Project_Pipeline",
    "04_Offtakers_Credit_Site", "05_Solar_Energy", "06_Load_PPA", "07_CAPEX_Construction",
    "08_OPEX", "09_Project_CF_CFADS", "10_Portfolio_CFADS", "11_Debt_Terms",
    "12_Debt_Sculpting", "13_Reserves_Waterfall", "14_Coverage", "15_Returns_Discount",
    "16_FX_Financing", "17_Scenarios_Sensitivity", "18_Portfolio", "19_IC_Bankability",
    "20_External_Validation", "21_QA_Audit",
]
NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def run() -> dict[str, int]:
    checks = []

    def add(check_id, check, expected, actual, status, severity="CRITICAL", impact=""):
        checks.append({"check_id": check_id, "check": check, "expected": expected, "actual": actual, "status": status, "severity": severity, "impact": impact})

    if not WORKBOOK.exists():
        add("WB-001", "file_exists", "True", "False", "FAIL", impact="Workbook is missing.")
    else:
        raw = WORKBOOK.read_bytes()
        add("WB-001", "file_exists", "True", "True", "PASS", impact="Native workbook is present in the remote checkout.")
        add("WB-002", "zip_magic", "PK", raw[:2].decode("latin-1", errors="replace"), "PASS" if raw[:2] == b"PK" else "FAIL", impact="Confirms the binary is an OOXML ZIP package.")
        try:
            with zipfile.ZipFile(WORKBOOK) as zf:
                bad_member = zf.testzip()
                add("WB-003", "zip_integrity", "None", str(bad_member), "PASS" if bad_member is None else "FAIL", impact="Detects corrupt ZIP members.")
                members = set(zf.namelist())
                required = {"[Content_Types].xml", "_rels/.rels", "docProps/core.xml", "docProps/app.xml", "xl/workbook.xml", "xl/_rels/workbook.xml.rels", "xl/styles.xml"}
                missing = sorted(required - members)
                add("WB-004", "package_parts", "All required parts", "None missing" if not missing else ", ".join(missing), "PASS" if not missing else "FAIL", impact="Ensures the workbook has the core OOXML package topology.")
                workbook_root = ET.fromstring(zf.read("xl/workbook.xml"))
                sheet_nodes = workbook_root.findall("main:sheets/main:sheet", NS)
                sheet_names = [node.attrib.get("name", "") for node in sheet_nodes]
                add("WB-005", "sheet_count", str(len(EXPECTED_SHEETS)), str(len(sheet_names)), "PASS" if len(sheet_names) == len(EXPECTED_SHEETS) else "FAIL", impact="Checks the required 22-sheet architecture.")
                add("WB-006", "sheet_contract", json.dumps(EXPECTED_SHEETS, ensure_ascii=False), json.dumps(sheet_names, ensure_ascii=False), "PASS" if sheet_names == EXPECTED_SHEETS else "FAIL", impact="Prevents silent sheet renaming or reordering.")
                for index in range(1, len(EXPECTED_SHEETS) + 1):
                    member = "xl/worksheets/sheet%d.xml" % index
                    present = member in members
                    parseable = False
                    if present:
                        try:
                            sheet_root = ET.fromstring(zf.read(member))
                            parseable = sheet_root.tag.endswith("worksheet")
                        except ET.ParseError:
                            parseable = False
                    add("WB-SHEET-%02d" % index, "worksheet_%02d_xml" % index, "Present and parseable", "Present and parseable" if present and parseable else "Missing or invalid", "PASS" if present and parseable else "FAIL", impact="Validates each sheet XML member.")
                control_xml = zf.read("xl/worksheets/sheet1.xml").decode("utf-8", errors="replace")
                control_tokens = [
                    ("WB-030", "VietGreen_CI_Solar_Project_Finance", "Control sheet must identify the project."),
                    ("WB-031", "PASS_WITH_LIMITATIONS", "Control sheet must expose the release boundary."),
                ]
                for check_id, token, impact in control_tokens:
                    add(check_id, "control_metadata_token", token, "Present" if token in control_xml else "Missing", "PASS" if token in control_xml else "FAIL", impact=impact)
                dq_token_ok = "data_quality" in control_xml and "PASS" in control_xml
                add("WB-032", "control_metadata_token", "current DQ count / PASS", "Present" if dq_token_ok else "Missing", "PASS" if dq_token_ok else "FAIL", impact="Control sheet must expose data-quality status.")
        except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
            add("WB-999", "package_parse", "No exception", type(exc).__name__, "FAIL", impact="The workbook cannot be trusted as a readable OOXML package.")

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(checks[0].keys()) if checks else ["check_id"])
        writer.writeheader()
        writer.writerows(checks)
    failures = sum(1 for item in checks if item["status"] == "FAIL")
    REPORT.write_text(
        "# WORKBOOK_VALIDATION_REPORT\n\n"
        "Remote structural validation of the native workbook generated from the remote output set.\n\n"
        "- Checks run: %s\n"
        "- Passed: %s\n"
        "- Failed: %s\n"
        "- Scope: OOXML package integrity, 22-sheet contract, worksheet XML parsing and control metadata.\n"
        "- Limitation: this does not replace desktop Excel rendering, independent engineering review, lender review or legal/tax/site diligence.\n"
        % (len(checks), len(checks) - failures, failures),
        encoding="utf-8",
    )
    return {"checks": len(checks), "failures": failures}


if __name__ == "__main__":
    summary = run()
    if summary["failures"]:
        raise SystemExit(1)
    print(json.dumps(summary, sort_keys=True))
