#!/usr/bin/env python3
"""Fail-closed validator for the CV website frozen-model payload."""
from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"website"/"public"/"data"
SYNTHETIC={"FR-GY-MONTREAU","FR-GY-LYON-LOGISTICS","FR-GY-SOLARIS","FR-GY-ATLANTIS","IN-GY-SURAT","IN-GY-PUNE","IT-GY-MILAN","SK-GY-BRATISLAVA","ES-GY-MADRID","VN-GY-HANOI-ONE"}
SHEETS=["00_Cover","01_Readme","02_Project_Master","03_Physical_QA","04_Resolved_Input_View","05_Assumption_Overlay","06_Source_Register","07_Conflict_Register","08_Selected_Data_Audit","09_Yield_Audit","10_Load_Match","11_Tariff","12_FX","13_Tax","14_Rates","15_Discount_Rates","16_CAPEX","17_OPEX","18_Base_CFADS","19_Debt_Sizing","20_Debt_Schedule","21_PPA_Frontier","22_Scenarios","23_Portfolio","24_Claim_Governance","25_Release_Gates","26_QA","27_Reconciliation"]
def load(name): return json.loads((DATA/name).read_text(encoding="utf-8"))
summary,projects,economics,energy,risk,model,release=[load(n) for n in ["summary.json","projects.json","economics.json","energy.json","risk.json","model.json","release.json"]]
items=projects["projects"]; ids={x["projectId"] for x in items}; statuses=Counter(x["physicalStatus"] for x in items)
if len(items)!=20 or len(ids)!=20: raise SystemExit("FAIL project universe")
if ids&SYNTHETIC: raise SystemExit("FAIL synthetic project ID")
blocked=[x for x in items if x["technicalDataBlocked"]]
if len(blocked)!=1 or blocked[0]["projectId"]!="IN-FPEL-ARISUDHANA": raise SystemExit("FAIL blocked boundary")
if blocked[0]["p50Gwh"] is not None or len(economics["projects"])!=19: raise SystemExit("FAIL blocked data leakage")
if statuses!=Counter({"PASS_WITHIN_SCREENING_BAND":15,"LOW_YIELD_REVIEW":4,"EXTREME_OUTLIER_BLOCK_BASE":1}): raise SystemExit(f"FAIL physical distribution {statuses}")
ready=ids-{blocked[0]["projectId"]}
if set(economics["projects"])!=ready: raise SystemExit("FAIL economics IDs")
if len(energy["projects"])!=19 or any(len(x["representativeDay"]["loadKwh"])!=24 for x in energy["projects"].values()): raise SystemExit("FAIL 24-hour profiles")
if len(risk["rows"])!=171 or len(risk["heatmap"])!=19 or any(len(x)!=9 for x in risk["heatmap"].values()): raise SystemExit("FAIL 19x9 risk pivot")
if len({(x["projectId"],x["scenario"]) for x in risk["rows"]})!=171: raise SystemExit("FAIL scenario keys")
if model["workbookSheets"]!=SHEETS: raise SystemExit("FAIL workbook sheets")
if summary["ppaMode"]!="FRONTIER_ONLY" or summary["decision"]!="INDETERMINATE_MISSING_COMMERCIAL_DATA": raise SystemExit("FAIL claim boundary")
if summary["transactionEvidence"]!="OPEN" or summary["capitalAllocation"]!="DISABLED": raise SystemExit("FAIL transaction boundary")
if release["modelSha"]!="ff69e15d211ff1abc88200574242ed2f1db49074": raise SystemExit("FAIL model SHA")
with (ROOT/"validation"/"CV_WEBSITE_FROZEN_MODEL_RECONCILIATION.csv").open("r",encoding="utf-8",newline="") as h:
    recon=list(csv.DictReader(h))
if not recon or any(x["status"]!="PASS" for x in recon): raise SystemExit("FAIL reconciliation")
print(json.dumps({"status":"PASS","projects":20,"ready":19,"blocked":1,"scenarios":171,"sheets":28,"reconciliationRows":len(recon)}))
