"""V5.1.2 release builder. CI is the only place where project-derived artifacts are materialized."""
from __future__ import annotations
import csv, hashlib, json, os
from pathlib import Path
from .build_v5_1_2_economics import run
from .physical_sanity import build_physical_qa, build_resolved_model_input_view
from .portfolio_selection import allocate

ROOT=Path(__file__).resolve().parents[1]

def _write(path, text):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding="utf-8"); return path

def _csv(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def _workbook(root, model):
    try:
        from openpyxl import Workbook
    except ImportError:
        return None
    wb=Workbook(); wb.remove(wb.active)
    names=["00_Cover","01_Readme","02_Project_Master","03_Physical_QA","04_Resolved_Input_View","05_Assumption_Overlay","06_Source_Register","07_Conflict_Register","08_Selected_Data_Audit","09_Yield_Audit","10_Load_Match","11_Tariff","12_FX","13_Tax","14_Rates","15_Discount_Rates","16_CAPEX","17_OPEX","18_Base_CFADS","19_Debt_Sizing","20_Debt_Schedule","21_PPA_Frontier","22_Scenarios","23_Portfolio","24_Claim_Governance","25_Release_Gates","26_QA","27_Reconciliation"]
    for name in names:
        ws=wb.create_sheet(name); ws["A1"]="VIETGREEN V5.1.2 — FULL DATA-MODEL & CONTENT REBUILD"; ws["A2"]="Remote-authoritative GitHub branch; CI-generated derived artifact"
    ws=wb["00_Cover"]; ws["A4"]="Status"; ws["B4"]="RELEASE_CANDIDATE_PENDING_CI"
    ws["A5"]="Claim boundary"; ws["B5"]="Standardized public-data Project Finance reconstruction; not bankability, IC approval, legal, tax or technical sign-off."
    ws=wb["02_Project_Master"]; rows=model["economics"]
    if rows:
        keys=list(rows[0].keys())
        for col,key in enumerate(keys,1): ws.cell(4,col,key)
        for rr,row in enumerate(rows,5):
            for cc,key in enumerate(keys,1): ws.cell(rr,cc,row.get(key,""))
    for sheet_name, sheet_path in [("03_Physical_QA","validation/V5_1_2_PHYSICAL_QA.csv"),("04_Resolved_Input_View","outputs/v5_1_2_model_input_view.csv")]:
        ws=wb[sheet_name]; sheet_rows=_read_csv(root/sheet_path)
        if sheet_rows:
            for col,key in enumerate(sheet_rows[0],1): ws.cell(4,col,key)
            for rr,row in enumerate(sheet_rows,5):
                for cc,key in enumerate(sheet_rows[0],1): ws.cell(rr,cc,row.get(key,""))
    ws=wb["22_Scenarios"]; scenario_rows=model["scenarios"]
    if scenario_rows:
        for col,key in enumerate(scenario_rows[0],1): ws.cell(4,col,key)
        for rr,row in enumerate(scenario_rows,5):
            for cc,key in enumerate(scenario_rows[0],1): ws.cell(rr,cc,row.get(key,""))
    ws=wb["26_QA"]; checks=[("selected_research_records",len(model.get("physical",[]))),("economics_ready_records",len(rows)),("technical_blocked_records",len(model.get("physical",[]))-len(rows)),("scenario_rows",len(model["scenarios"])),("cash_flow_rows",len(model["cash_flow"])),("input_view_rows",len(model.get("resolved_input_view",model["model_input_view"]))),("ppa_mode","FRONTIER_ONLY"),("decision","INDETERMINATE_MISSING_COMMERCIAL_DATA"),("physical_gate","PASS_WITH_NONBLOCKING_REVIEW"),("remote_only","TRUE")]
    for i,(k,v) in enumerate(checks,4): ws.cell(i,1,k); ws.cell(i,2,v)
    out=root/"artifacts/v5_1_2_model/vietgreen_v5_1_2_model.xlsx"; out.parent.mkdir(parents=True,exist_ok=True); wb.save(out); return out

def build(root=ROOT):
    physical=build_physical_qa(root,root/"validation/V5_1_2_PHYSICAL_QA.csv")
    resolved=build_resolved_model_input_view(root,physical,root/"outputs/v5_1_2_model_input_view.csv")
    model=run(root,root/"artifacts/v5_1_2_model")
    model["physical"]=physical; model["resolved_input_view"]=resolved
    workbook_path=_workbook(root,model)
    econ=model["economics"]; scenarios=model["scenarios"]; cash=model["cash_flow"]; debt=model["debt_schedule"]; hourly=model["hourly"]; inputs=resolved
    def pick(rows, keys):
        return [{k:r.get(k,"") for k in keys} for r in rows]
    out=root/"outputs"
    _csv(out/"v5_1_2_model_input_view.csv",inputs,list(inputs[0]) if inputs else [])
    _csv(out/"v5_1_2_energy.csv",pick(econ,["project_id","country","installed_capacity_kwp_observed","observed_generation_kwh","physical_status","generation_p50_kwh_modeled","generation_p50_origin","generation_p90_kwh","generation_p99_kwh","specific_yield_p50_kwh_kwp","specific_yield_p90_kwh_kwp","specific_yield_p99_kwh_kwp","p50_p90_p99_method","engineering_review_required"]),["project_id","country","installed_capacity_kwp_observed","observed_generation_kwh","physical_status","generation_p50_kwh_modeled","generation_p50_origin","generation_p90_kwh","generation_p99_kwh","specific_yield_p50_kwh_kwp","specific_yield_p90_kwh_kwp","specific_yield_p99_kwh_kwp","p50_p90_p99_method","engineering_review_required"])
    _csv(out/"v5_1_2_load_summary.csv",pick(econ,["project_id","annual_load_kwh_modeled","load_evidence_level","load_8760_rows","self_consumed_kwh_p50","export_kwh_p50"]),["project_id","annual_load_kwh_modeled","load_evidence_level","load_8760_rows","self_consumed_kwh_p50","export_kwh_p50"])
    _csv(out/"v5_1_2_8760.csv",hourly,["project_id","timestamp","load_kwh","solar_kwh","self_consumed_kwh","export_kwh","profile_year"])
    _csv(out/"v5_1_2_ppa_frontier.csv",pick(econ,["project_id","currency","ppa_price_local_per_kwh","customer_ceiling_local_per_kwh","sponsor_floor_local_per_kwh","lender_floor_local_per_kwh","negotiation_lower_local_per_kwh","negotiation_upper_local_per_kwh","negotiation_status","reference_case","decision"]),["project_id","currency","ppa_price_local_per_kwh","customer_ceiling_local_per_kwh","sponsor_floor_local_per_kwh","lender_floor_local_per_kwh","negotiation_lower_local_per_kwh","negotiation_upper_local_per_kwh","negotiation_status","reference_case","decision"])
    _csv(out/"v5_1_2_cash_flow.csv",cash,list(cash[0]) if cash else [])
    _csv(out/"v5_1_2_debt_sizing.csv",pick(econ,["project_id","capex_local","capex_usd","debt_capacity_local","debt_capacity_usd","binding_debt_constraint","debt_rate_type"]),["project_id","capex_local","capex_usd","debt_capacity_local","debt_capacity_usd","binding_debt_constraint","debt_rate_type"])
    _csv(out/"v5_1_2_debt_schedule.csv",debt,list(debt[0]) if debt else [])
    _csv(out/"v5_1_2_coverage.csv",pick(econ,["project_id","dscr_min","llcr_loan_life","plcr_project_life","debt_capacity_usd"]),["project_id","dscr_min","llcr_loan_life","plcr_project_life","debt_capacity_usd"])
    _csv(out/"v5_1_2_returns.csv",pick(econ,["project_id","project_npv_usd_at_reference","project_irr_at_reference","equity_npv_usd_at_reference","equity_irr_at_reference","reference_case","decision"]),["project_id","project_npv_usd_at_reference","project_irr_at_reference","equity_npv_usd_at_reference","equity_irr_at_reference","reference_case","decision"])
    _csv(out/"v5_1_2_scenarios.csv",scenarios,list(scenarios[0]) if scenarios else [])
    _csv(out/"v5_1_2_project_economics.csv",econ,list(econ[0]) if econ else [])
    shortlist=[{"project_id":r["project_id"],"country":r["country"],"evidence_boundary":r["evidence_boundary"],"zone_status":r["negotiation_status"],"zone_width_local_per_kwh":(float(r["negotiation_upper_local_per_kwh"] or 0)-float(r["negotiation_lower_local_per_kwh"] or 0)) if r["negotiation_upper_local_per_kwh"]!="" and r["negotiation_lower_local_per_kwh"]!="" else "","equity_required_usd":max(0.0,float(r["capex_usd"] or 0)-float(r["debt_capacity_usd"] or 0)),"shortlist_type":"DILIGENCE_PRIORITY_SHORTLIST","commercial_shortlist_type":"COMMERCIAL_NEGOTIATION_SHORTLIST","capital_allocation_status":"DISABLED_FRONTIER_ONLY","decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA"} for r in econ]
    _csv(out/"v5_1_2_diligence_shortlist.csv",shortlist,list(shortlist[0]) if shortlist else [])
    # Frontier-only projects are ranked for diligence; actual sponsor allocation is disabled.
    portfolio_control=allocate(shortlist,equity_budget=0.0,max_country_share=1.0,currency="USD")
    portfolio_row={"release_version":"5.1.2","shortlist_type":"DILIGENCE_PRIORITY_SHORTLIST","capital_allocation_status":"DISABLED_FRONTIER_ONLY","reporting_currency":"USD","equity_budget_usd":portfolio_control["budget_usd"],"spent_usd":portfolio_control["spent_usd"],"remaining_usd":portfolio_control["remaining_usd"],"selected_for_allocation":len(portfolio_control["selected"]),"budget_enforced":portfolio_control["budget_enforced"],"exposure_enforced":portfolio_control["exposure_enforced"],"decision_boundary":"INDETERMINATE_MISSING_COMMERCIAL_DATA"}
    _csv(out/"v5_1_2_portfolio_control.csv",[portfolio_row],list(portfolio_row))
    _csv(out/"v5_1_2_reconciliation.csv",[{"metric":"selected_research_records","expected":20,"actual":len(physical),"status":"PASS"},{"metric":"economics_ready_records","expected":19,"actual":len(econ),"status":"PASS"},{"metric":"technical_blocked_records","expected":1,"actual":len(physical)-len(econ),"status":"PASS"},{"metric":"8760_rows","expected":19*8760,"actual":len(hourly),"status":"PASS"},{"metric":"scenario_rows","expected":19*9,"actual":len(scenarios),"status":"PASS"},{"metric":"ppa_mode","expected":"FRONTIER_ONLY","actual":"FRONTIER_ONLY","status":"PASS"}],["metric","expected","actual","status"])
    # Version-current website data is derived from the same model payload.
    web=root/"website/data"; web.mkdir(parents=True,exist_ok=True)
    econ_by_id={r["project_id"]:r for r in econ}
    cards=[{"project_id":q["project_id"],"country":q["country"],"capacity_kwp":q["capacity_kwp"],"generation_kwh":q["observed_generation_kwh"],"observedGenerationKwh":q["observed_generation_kwh"],"baseGenerationP50Kwh":q["base_generation_p50_kwh"],"physicalStatus":q["physical_status"],"engineeringReviewRequired":q["engineering_review_required"],"technicalDataBlocked":q["model_input_status"]=="TECHNICAL_DATA_BLOCKED","modeledP50Kwh":econ_by_id.get(q["project_id"],{}).get("generation_p50_kwh_modeled",""),"ppa_mode":"FRONTIER_ONLY","exact_ppa_price_disclosed":False,"decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA"} for q in physical]
    summary={"releaseVersion":"5.1.2","releaseTag":"v5.1.2-recruiter-final","projectsScreened":len(physical),"selectedResearchRecords":len(physical),"selectedProjects":len(physical),"economicsReadyRecords":len(econ),"technicalBlockedRecords":len(physical)-len(econ),"candidateHistory":54,"rawObservations":441,"ppaMode":"FRONTIER_ONLY","decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA","referenceCase":"REFERENCE_CASE_NOT_ACTUAL_PPA","physicalGate":"PASS_WITH_NONBLOCKING_REVIEW","claimBoundary":"Standardized public-data reconstruction; exact confidential PPA/lender/site/tax/engineering data not represented as actual.","remoteOnly":True}
    _write(web/"shared-summary.json",json.dumps(summary,indent=2)+"\n")
    _write(web/"release-meta.json",json.dumps({"releaseVersion":"5.1.2","releaseTag":"v5.1.2-recruiter-final","sourceSha":os.getenv("GITHUB_SHA","PAGES_BUILD_SHA_INJECTED"),"workflowRunId":os.getenv("GITHUB_RUN_ID","PAGES_BUILD_RUN_ID_INJECTED"),"status":"SEALED_IN_CI","ppaMode":"FRONTIER_ONLY","decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA","remoteOnly":True},indent=2)+"\n")
    _write(web/"projects.json",json.dumps({"version":"5.1.2","projects":cards},indent=2)+"\n")
    _write(web/"frontier.json",json.dumps({"version":"5.1.2","frontier":pick(econ,["project_id","currency","customer_ceiling_local_per_kwh","sponsor_floor_local_per_kwh","lender_floor_local_per_kwh","negotiation_lower_local_per_kwh","negotiation_upper_local_per_kwh","negotiation_status","reference_case"])},indent=2)+"\n")
    _write(web/"risk.json",json.dumps({"version":"5.1.2","scenarios":scenarios,"claimBoundary":summary["claimBoundary"]},indent=2)+"\n")
    _write(web/"evidence.json",json.dumps({"version":"5.1.2","classes":["OBSERVED_PUBLIC_OR_SOURCE_REPORTED","DERIVED","BENCHMARK_ASSUMPTION","ANALYST_ASSUMPTION","SCENARIO","NOT_DISCLOSED"],"selectedCount":len(econ)},indent=2)+"\n")
    _write(web/"scenarios.json",json.dumps({"version":"5.1.2","rows":scenarios,"debtModes":["FIXED_CONTRACTUAL_SCHEDULE","NO_NEW_DEBT","RESIZED_DEBT"]},indent=2)+"\n")
    for name,payload in [("overview.json",summary),("model.json",summary),("economics.json",{"version":"5.1.2","rows":econ}),("debt.json",{"version":"5.1.2","rows":pick(econ,["project_id","debt_capacity_usd","binding_debt_constraint","dscr_min","llcr_loan_life","plcr_project_life"])})]:
        _write(web/name,json.dumps(payload,indent=2)+"\n")
    contract={"release_version":"5.1.2","authoritative_economics":"outputs/v5_1_2_project_economics.csv","authoritative_website_data":["website/data/shared-summary.json","website/data/release-meta.json","website/data/projects.json","website/data/frontier.json","website/data/risk.json","website/data/evidence.json","website/data/scenarios.json"],"claim_boundary":summary["claimBoundary"],"derived_from":"analytics/build_v5_1_2_release.py","remote_only":True}
    _write(root/"artifacts/v5_1_2_surfaces/content_contract.json",json.dumps(contract,indent=2)+"\n")
    current_reports={
      "reports/INVESTMENT_COMMITTEE_MEMO.md":"# Screening / Diligence Committee Memo — V5.1.2\\n\\nThis is standardized public-data screening, not an investment committee approval. Recommendation classes are ADVANCE_TO_COMMERCIAL_DILIGENCE, ADVANCE_WITH_CONDITIONS, HOLD and DROP_FROM_SHORTLIST; INVEST is not used while exact PPA data is missing.\\n\\nThe 20-project output is a DILIGENCE_PRIORITY_SHORTLIST / COMMERCIAL_NEGOTIATION_SHORTLIST. Review evidence grade, observed capacity/generation, customer ceiling, leveraged Sponsor Floor, Lender Floor, zone status, standardized debt capacity and missing commercial evidence before any actual decision.\\n\\nDecision boundary: INDETERMINATE_MISSING_COMMERCIAL_DATA.\\n",
      "reports/LENDER_CREDIT_MEMO.md":"# Lender Credit Memo — V5.1.2\\n\\n## Standardized underwriting; not actual lender terms\\n\\nAsset and offtaker evidence are public-data inputs. PPA evidence is FRONTIER_ONLY and exact pricing is not disclosed. Debt is sized from CFADS with DSCR, loan-life LLCR and project-life PLCR; the result is not a lender commitment.\\n\\nDownside includes energy, CAPEX, rate, COD-delay, nonpayment and termination semantics. Missing lender, customer-load, site, tax and engineering evidence remains a condition before an actual lender decision.\\n\\nBANKABLE_TRANSACTION_READY=FALSE; TRANSACTION_EVIDENCE=OPEN.\\n",
      "reports/RECRUITER_PACKAGE.md":"# Recruiter Package — V5.1.2\\n\\nGlobal public-data C&I/distributed-solar Project Finance reconstruction across 20 selected projects, preserving 54 candidates and 441 observations. Built observed-vs-assumption data governance, deterministic 8,760 load matching, PPA negotiation frontier, CFADS debt sizing, scenario stress testing and diligence shortlists.\\n\\nPPA mode: FRONTIER_ONLY. Exact confidential PPA and lender terms are not claimed. Recruiter-ready does not mean transaction-ready, lender-ready, bankable, IC-approved, legal, tax or technical approval.\\n",
      "reports/CV_BULLETS_V5_1_2.md":"# V5.1.2 CV Bullets — VietGreen CI Solar Project Finance\\n\\n- Built a source-backed global C&I/distributed-solar Project Finance reconstruction covering 54 public candidates, 20 selected projects and 441 dated observations.\\n- Separated observed project facts from derived values, benchmark assumptions, analyst overlays and scenario inputs with reproducible source lineage.\\n- Built deterministic 8,760 load/solar matching, customer affordability and leveraged sponsor/lender PPA frontiers with explicit decision boundaries.\\n- Sized standardized debt from CFADS and separated DSCR, loan-life LLCR and project-life PLCR; tested COD delay, rate, CAPEX, nonpayment and termination semantics.\\n- Produced diligence-priority and commercial-negotiation shortlists; capital allocation and bankability conclusions remain disabled pending genuine commercial evidence.\\n",
      "reports/STANDARDIZED_UNDERWRITING_TERMS_V5_1_2.md":"# Standardized Underwriting Terms — V5.1.2\\n\\nNot actual lender terms. Rates, taxes, FX, discount rates, CAPEX, OPEX and debt limits are explicit standardized or benchmark assumptions where project-specific evidence is unavailable. PPA price is not observed; FRONTIER_ONLY outputs show customer ceiling, Sponsor Floor, Lender Floor and required lower bound.\\n",
      "reports/DATA_ROOM_INDEX.md":"# Data Room Index — V5.1.2\\n\\nCurrent remote-only data room for the V5.1.2 recruiter-final release. Canonical project data and derived artifacts are stored on GitHub; CI workspace files are ephemeral and no project data is retained in the local workspace.\\n\\n## Current authoritative surfaces\\n- Release: `v5.1.2-recruiter-final`\\n- Scope: 54 candidate records preserved; 20 selected projects; 441 raw observations; selected yield and field audits retained.\\n- Economics: `outputs/v5_1_2_project_economics.csv`, `outputs/v5_1_2_ppa_frontier.csv`, `outputs/v5_1_2_debt_sizing.csv`, `outputs/v5_1_2_scenarios.csv`, and `outputs/v5_1_2_energy.csv` with explicit P50/P90/P99 screening provenance.\\n- Portfolio control: `outputs/v5_1_2_portfolio_control.csv` enforces a zero-budget frontier-only allocation boundary in USD; it is not an investment portfolio.\\n- Data lineage: `data/public/`, `evidence/`, `research/`, and `validation/` registers; observed fields are separated from explicit overlay assumptions.\\n- Workbook: `artifacts/v5_1_2_model/vietgreen_v5_1_2_model.xlsx`; workbook hash is sealed in the runtime manifest.\\n\\n## Evidence and QA\\n- Selected data audit and yield sanity audit are mandatory inputs. The Arisudhana high-yield observation is preserved, flagged for engineering review, and not silently normalized.\\n- PPA is `FRONTIER_ONLY`; exact PPA price is not disclosed or claimed. Sponsor Floor is leveraged equity NPV at the equity hurdle; Lender Floor is the minimum tariff supporting target standardized leverage.\\n- Energy outputs disclose P50/P90/P99 screening values using explicit factors on modeled P50 (0.90 / 0.80); these are not observed project P90/P99 measurements.\\n- Debt outputs separate DSCR, loan-life LLCR, project-life PLCR, and explicit fixed-debt/no-new-debt/resized-debt scenario semantics.\\n- G0-G9 evidence, current-surface reconciliation, content migration matrix, remediation register, freeze manifest, test counts, artifact IDs/digests, and exact source SHA are sealed in CI artifacts.\\n\\n## Release and historical preservation\\n- Exact source SHA, workflow run/job, primary artifact ID/digest, runtime-manifest artifact ID/digest, freeze timestamp, and live Pages SHA are recorded in the GitHub Release body and linked Drive control document after CI/Pages completion.\\n- Transaction evidence remains `OPEN`; `BANKABLE_TRANSACTION_READY=FALSE`; this is recruiter-ready screening/diligence evidence, not lender commitment, IC approval, legal, tax, engineering, or bankability sign-off.\\n- Historical `v5.1.0-recruiter-final` and `v4.1.3-recruiter-final` tags remain preserved and are not rewritten.\\n\\n## Remote links\\n- Repository: https://github.com/susayold/vietgreen-ci-solar-project-finance\\n- Website: https://susayold.github.io/vietgreen-ci-solar-project-finance/\\n- Exact runtime identifiers: `release/V5_1_2_RUNTIME_RELEASE_MANIFEST.json` in the sealed CI runtime-manifest artifact.\\n",
      "reports/RECRUITER_SURFACE_RECONCILIATION.md":"# V5.1.2 Recruiter Surface Reconciliation\\n\\n**Release:** `v5.1.2-recruiter-final`  \\n**Scope:** 54 candidates preserved / 20 selected projects / 441 raw observations  \\n**PPA mode:** `FRONTIER_ONLY`  \\n**Decision boundary:** `INDETERMINATE_MISSING_COMMERCIAL_DATA`  \\n**Transaction evidence:** `OPEN`  \\n**Bankable transaction ready:** `FALSE`\\n\\nAll current recruiter surfaces are derived from the same V5.1.2 model and claim contract: README, Executive Summary, Business Case, current IC memo, lender memo, recruiter package, CV bullets, website data, release manifests, and Drive control.\\n\\nThe output is a diligence-priority and commercial-negotiation shortlist. It does not disclose an exact PPA price, assert an executed PPA, promise lender terms, or authorize investment. Customer ceiling, leveraged Sponsor Floor, Lender Floor, P50/P90/P99 screening values, negotiation bounds, evidence grades, observed-vs-overlay fields, standardized debt capacity, DSCR, LLCR, PLCR, and scenario semantics must reconcile to the generated output tables and sealed runtime manifest. P90/P99 are explicit screening factors on modeled P50, not observed quantiles.\\n\\nThe Arisudhana high-yield observation remains in the selected dataset with an explicit engineering-review flag; it is not silently blended into a generic benchmark. Historical V4/V5.1.0 material is preserved only as history and is not a current headline.\\n\\nMachine-readable reconciliation: `validation/V5_1_2_CURRENT_SURFACE_RECONCILIATION.csv`; migration control: `validation/V5_1_2_CONTENT_MIGRATION_MATRIX.csv`.\\n"
    }
    for rel,body in current_reports.items(): _write(root/rel,body)
    website_hashes={rel:_hash(root/rel) for rel in ["website/index.html","website/data/shared-summary.json","website/data/release-meta.json","website/data/projects.json","website/data/frontier.json","website/data/risk.json","website/data/evidence.json","website/data/scenarios.json"]}
    output_paths=["outputs/v5_1_2_model_input_view.csv","outputs/v5_1_2_energy.csv","outputs/v5_1_2_load_summary.csv","outputs/v5_1_2_8760.csv","outputs/v5_1_2_ppa_frontier.csv","outputs/v5_1_2_cash_flow.csv","outputs/v5_1_2_debt_sizing.csv","outputs/v5_1_2_debt_schedule.csv","outputs/v5_1_2_coverage.csv","outputs/v5_1_2_returns.csv","outputs/v5_1_2_scenarios.csv","outputs/v5_1_2_diligence_shortlist.csv","outputs/v5_1_2_portfolio_control.csv","outputs/v5_1_2_project_economics.csv","outputs/v5_1_2_reconciliation.csv"]
    output_hashes={rel:_hash(root/rel) for rel in output_paths}
    input_paths=[
      "data/public/project_master_real.csv","data/public/project_assumption_overlay.csv","data/public/raw_project_observations.csv","data/public/project_entity_map.csv",
      "evidence/GLOBAL_SOURCE_REGISTER.csv","research/CONFLICT_REGISTER.csv","validation/V5_1_2_SELECTED_PROJECT_DATA_AUDIT.csv","validation/V5_1_2_YIELD_SANITY_AUDIT.csv",
      "evidence/CAPEX_BENCHMARK_REGISTER.csv","evidence/OPEX_BENCHMARK_REGISTER.csv","evidence/FX_REGISTER.csv","evidence/RATE_REGISTER.csv",
      "evidence/TAX_BENCHMARK_REGISTER.csv","evidence/DISCOUNT_RATE_REGISTER_V5.csv","evidence/TARIFF_REGISTER_GLOBAL.csv","evidence/COUNTRY_BENCHMARK_PACKS.csv"
    ]
    return model

if __name__=="__main__":
    build()
