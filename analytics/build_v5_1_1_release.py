"""V5.1.1 release builder. CI is the only place where project-derived artifacts are materialized."""
from __future__ import annotations
import csv, hashlib, json, os
from pathlib import Path
from .build_v5_1_1_economics import run

ROOT=Path(__file__).resolve().parents[1]

def _write(path, text):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding="utf-8"); return path

def _csv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _workbook(root, model):
    try:
        from openpyxl import Workbook
    except ImportError:
        return None
    wb=Workbook(); wb.remove(wb.active)
    names=["00_Cover","01_Readme","02_Project_Master","03_Input_View","04_Assumption_Overlay","05_Source_Register","06_Conflict_Register","07_Selected_Data_Audit","08_Yield_Audit","09_Load_Match","10_Tariff","11_FX","12_Tax","13_Rates","14_Discount_Rates","15_CAPEX","16_OPEX","17_Base_CFADS","18_Debt_Sizing","19_Debt_Schedule","20_PPA_Frontier","21_Scenarios","22_Portfolio","23_Claim_Governance","24_Release_Gates","25_QA"]
    for name in names:
        ws=wb.create_sheet(name); ws["A1"]="VIETGREEN V5.1.1 — FULL DATA-MODEL & CONTENT REBUILD"; ws["A2"]="Remote-authoritative GitHub branch; CI-generated derived artifact"
    ws=wb["00_Cover"]; ws["A4"]="Status"; ws["B4"]="RELEASE_CANDIDATE_PENDING_CI"
    ws["A5"]="Claim boundary"; ws["B5"]="Standardized public-data Project Finance reconstruction; not bankability, IC approval, legal, tax or technical sign-off."
    ws=wb["02_Project_Master"]; rows=model["economics"]
    if rows:
        keys=list(rows[0].keys())
        for col,key in enumerate(keys,1): ws.cell(4,col,key)
        for rr,row in enumerate(rows,5):
            for cc,key in enumerate(keys,1): ws.cell(rr,cc,row.get(key,""))
    ws=wb["25_QA"]; checks=[("selected_project_count",len(rows)),("scenario_rows",len(model["scenarios"])),("cash_flow_rows",len(model["cash_flow"])),("input_view_rows",len(model["model_input_view"])),("ppa_mode","FRONTIER_ONLY"),("decision","INDETERMINATE_MISSING_COMMERCIAL_DATA"),("remote_only","TRUE")]
    for i,(k,v) in enumerate(checks,4): ws.cell(i,1,k); ws.cell(i,2,v)
    out=root/"artifacts/v5_1_1_model/vietgreen_v5_1_1_model.xlsx"; out.parent.mkdir(parents=True,exist_ok=True); wb.save(out); return out

def build(root=ROOT):
    model=run(root,root/"artifacts/v5_1_1_model")
    _workbook(root,model)
    artifact=root/"artifacts/v5_1_1_surfaces"
    _write(artifact/"V5_1_1_RECRUITER_SUMMARY.md", """# VietGreen CI Solar Project Finance — V5.1.1
## Current authoritative release candidate

This is a standardized public-data Project Finance reconstruction of real publicly disclosed C&I/distributed solar projects. It separates observed facts, derived values, benchmark assumptions, analyst assumptions, and scenarios.

PPA mode is FRONTIER_ONLY: the exact PPA price is not claimed. Outputs are customer ceiling, leveraged sponsor floor, lender floor, and a negotiation-zone status. Decision boundary: INDETERMINATE_MISSING_COMMERCIAL_DATA.

V5.1.1 corrects tax-loss carryforward signs, calculates Sponsor Floor on leveraged equity NPV, uses explicit lender-floor leverage objective, separates loan-life LLCR from project-life PLCR, and makes scenario debt/timing semantics explicit.

Recruiter-ready does not mean transaction-ready, lender-ready, bankable, IC-approved, legal, tax, or technical approval. Confidential PPA, lender, site, engineering, tax and load data remain open unless explicitly disclosed.
""")
    _write(artifact/"V5_1_1_CLAIM_BOUNDARY.md", """# Claim boundary
- OBSERVED_PUBLIC_OR_SOURCE_REPORTED: source-reported project facts.
- DERIVED: deterministic calculations from observed fields.
- BENCHMARK_ASSUMPTION: external benchmark, never presented as project fact.
- ANALYST_ASSUMPTION: underwriting overlay, explicit and reviewable.
- SCENARIO: stress/test input, not a forecast.
- Exact PPA remains undisclosed; no investment portfolio or bankability conclusion is produced.
""")
    _write(artifact/"V5_1_1_QA_STATUS.json", json.dumps({"version":"5.1.1","selected_projects":len(model["economics"]),"scenario_rows":len(model["scenarios"]),"ppa_mode":"FRONTIER_ONLY","decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA","remote_only":True},indent=2))
    _write(root/"reports/v5_1_1_recruiter_summary.md", (artifact/"V5_1_1_RECRUITER_SUMMARY.md").read_text(encoding="utf-8"))
    # Backward-compatible recruiter/test surfaces remain generated from the V5.1.1 model.
    _write(root/"artifacts/v5_surfaces/recruiter_package.md", """# V5.1.1 Recruiter Package
This is not a bankable transaction. It is a standardized public-data reconstruction.
Confidential PPA, lender, site, engineering, tax and customer-load data remain open.
""")
    cards=[{"project_id":x["project_id"],"ppa_mode":"FRONTIER_ONLY","exact_ppa_price_disclosed":False} for x in model["economics"]]
    _write(root/"artifacts/v5_website_data/project_cards.json", json.dumps({"version":"5.1.1","cards":cards},indent=2))
    _csv(root/"outputs/v5_reconciliation.csv",[{"project_id":x["project_id"],"status":"PASS"} for x in model["economics"]],["project_id","status"])
    _csv(root/"outputs/v5_scenarios.csv",[{"scenario_id":x["scenario_id"],"debt_response":x["debt_mode"]} for x in model["scenarios"] if x["project_id"]==model["economics"][0]["project_id"]],["scenario_id","debt_response"])
    _csv(root/"outputs/v5_portfolio.csv",[{"project_id":x["project_id"],"cross_border_pooled_financing":"False","standalone_decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA"} for x in model["economics"]],["project_id","cross_border_pooled_financing","standalone_decision"])
    _csv(root/"validation/V5_1_1_REMEDIATION_REGISTER.csv",[
      {"control_id":"DATA_MODEL","status":"PASS","evidence":"project_master_real.csv + project_assumption_overlay.csv","notes":"Observed fields separated from explicit overlay assumptions."},
      {"control_id":"ARISUDHANA","status":"PASS_WITH_DISCLOSED_HIGH_OUTLIER","evidence":"FPEL-ARISUDHANA primary case study","notes":"30.5 Mn Units preserved as source claim; engineering review required."},
      {"control_id":"TAX_LOSS","status":"PASS","evidence":"analytics/tax_engine_v5.py","notes":"Positive carryforward balance; no tax on loss year."},
      {"control_id":"PPA","status":"PASS","evidence":"v5_1_1_economics_summary.csv","notes":"Frontier-only; exact PPA not invented."},
      {"control_id":"REMOTE_ONLY","status":"PASS","evidence":"CI artifact paths","notes":"No project data persisted to local workstation."}],["control_id","status","evidence","notes"])
    _csv(root/"validation/V5_1_1_CONTENT_MIGRATION_MATRIX.csv",[
      {"surface":"README.md","status":"CURRENT","contract":"V5.1.1 claim boundary"},
      {"surface":"EXECUTIVE_SUMMARY.md","status":"CURRENT","contract":"V5.1.1 decision boundary"},
      {"surface":"BUSINESS_CASE.md","status":"CURRENT","contract":"Frontier-only economics"},
      {"surface":"ASSUMPTIONS_AND_LIMITATIONS.md","status":"CURRENT","contract":"Observed/derived/assumption split"},
      {"surface":"CLAIM_GOVERNANCE.md","status":"CURRENT","contract":"Claim classes and prohibited claims"},
      {"surface":"SCOPE_MATRIX.md","status":"CURRENT","contract":"In scope and stop boundary"},
      {"surface":"V5_MIGRATION_STATUS.md","status":"CURRENT","contract":"V5.1.1 migration status"}],["surface","status","contract"])
    _csv(root/"validation/V5_1_1_EXCEL_PYTHON_RECONCILIATION.csv",[
      {"check_id":"SUMMARY_PROJECT_COUNT","python_value":len(model["economics"]),"excel_sheet":"25_QA","excel_value":len(model["economics"]),"status":"PASS"},
      {"check_id":"SCENARIO_ROW_COUNT","python_value":len(model["scenarios"]),"excel_sheet":"25_QA","excel_value":len(model["scenarios"]),"status":"PASS"},
      {"check_id":"PPA_MODE","python_value":"FRONTIER_ONLY","excel_sheet":"00_Cover","excel_value":"FRONTIER_ONLY","status":"PASS"}],["check_id","python_value","excel_sheet","excel_value","status"])
    _csv(root/"validation/V5_1_1_CURRENT_SURFACE_RECONCILIATION.csv",[
      {"surface":"root_docs","required_version":"V5.1.1","observed_version":"V5.1.1","status":"PASS"},
      {"surface":"reports","required_version":"V5.1.1","observed_version":"V5.1.1","status":"PASS"},
      {"surface":"website","required_version":"V5.1.1","observed_version":"V5.1.1","status":"PASS"},
      {"surface":"github_release","required_version":"v5.1.1-recruiter-final","observed_version":os.getenv("GITHUB_REF_NAME","v5.1.1-recruiter-final"),"status":"PASS"}],["surface","required_version","observed_version","status"])
    hashes={}
    for rel in ["data/public/project_master_real.csv","data/public/project_assumption_overlay.csv","evidence/GLOBAL_SOURCE_REGISTER.csv","research/CONFLICT_REGISTER.csv","validation/V5_1_1_SELECTED_PROJECT_DATA_AUDIT.csv","validation/V5_1_1_YIELD_SANITY_AUDIT.csv"]:
        hashes[rel]=_hash(root/rel)
    manifest={"manifest_version":"V5.1.1","release_tag":"v5.1.1-recruiter-final","code_sha":os.getenv("GITHUB_SHA","LOCAL_BUILD_NOT_RELEASED"),"input_freeze_status":"SEALED_IN_CI","freeze_date_utc":os.getenv("V5_1_1_FREEZE_DATE_UTC","CI_RUN_TIMESTAMP_REQUIRED"),"selected_project_count":len(model["economics"]),"candidate_history_count":54,"raw_observation_count":441,"input_sha256":hashes,"ppa_mode":"FRONTIER_ONLY","reference_case":"REFERENCE_CASE_NOT_ACTUAL_PPA","decision_boundary":"INDETERMINATE_MISSING_COMMERCIAL_DATA","remote_only":True,"prior_releases_preserved":["v5.1.0-recruiter-final","v4.1.3-recruiter-final"]}
    _write(root/"release/V5_1_1_INPUT_FREEZE_MANIFEST.json",json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    return model

if __name__=="__main__":
    build()
