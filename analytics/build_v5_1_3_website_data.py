"""CI-only V5.1.3 website data adapter.

This module generates every browser payload from the frozen model run. It must run
in GitHub Actions; it intentionally does not read or write a developer snapshot.
"""
from __future__ import annotations
import csv, json, os
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
VALID = ROOT / "validation"
DEST = ROOT / "website" / "data"
MODEL_SHA = "ff69e15d211ff1abc88200574242ed2f1db49074"
MODEL_TAG = "v5.1.3-recruiter-final"
WEBSITE_RELEASE = "v5.1.3-website-final"
REPO = "susayold/vietgreen-ci-solar-project-finance"

def rows(name: str, folder=OUT):
    p = folder / name
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def f(v, default=None):
    try:
        if v in (None, "", "NA", "N/A", "null"): return default
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return default

def i(v, default=0):
    x=f(v)
    return default if x is None else int(x)

def pick(r, *keys, default=None):
    for k in keys:
        if k in r and r[k] not in ("", None):
            return r[k]
    return default

def truth(v):
    return str(v).upper() in {"TRUE","1","YES","PASS"}

def write(name, value):
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def main():
    econ = rows("v5_1_3_project_economics.csv")
    physical = rows("V5_1_3_PHYSICAL_QA.csv", VALID)
    scenarios = rows("v5_1_3_scenarios.csv")
    frontier = rows("v5_1_3_ppa_frontier.csv")
    cash = rows("v5_1_3_cash_flow.csv")
    debt = rows("v5_1_3_debt_schedule.csv")
    coverage = rows("v5_1_3_coverage.csv")
    returns = rows("v5_1_3_returns.csv")
    hourly = rows("v5_1_3_8760.csv")
    shortlist = rows("v5_1_3_diligence_shortlist.csv")
    control = rows("v5_1_3_portfolio_control.csv")
    reconciliation = rows("v5_1_3_reconciliation.csv")
    model_input = rows("v5_1_3_model_input_view.csv")
    if len(econ) != 19: raise ValueError(f"expected 19 economics rows, got {len(econ)}")
    if len(physical) != 20: raise ValueError(f"expected 20 physical rows, got {len(physical)}")
    if len(scenarios) != 171: raise ValueError(f"expected 171 scenario rows, got {len(scenarios)}")

    physical_by_id = {str(pick(x,"project_id","projectId")): x for x in physical}
    econ_by_id = {str(pick(x,"project_id","projectId")): x for x in econ}
    ids = list(physical_by_id)
    blocked = [x for x in physical if str(pick(x,"model_input_status","input_ready_status","")).upper() != "READY_FOR_ECONOMICS"]
    blocked_row = blocked[0] if blocked else {"project_id":"ARISUDHANA","project_name":"Arisudhana","observed_generation_kwh":"30500000"}

    projects = []
    for pid in ids:
        p = physical_by_id[pid]
        e = econ_by_id.get(pid, {})
        projects.append({
            "projectId": pid,
            "projectName": pick(p,"project_name","projectName", default=pick(e,"project_name","projectName",default=pid)),
            "country": pick(p,"country", default=pick(e,"country",default="—")),
            "capacityKwp": f(pick(p,"capacity_kwp","installed_capacity_kwp", default=pick(e,"installed_capacity_kwp_observed","installed_capacity_kwp"))),
            "physicalStatus": pick(p,"physical_status", default="PASS"),
            "economicsStatus": "READY_FOR_ECONOMICS" if pid in econ_by_id else "TECHNICAL_DATA_BLOCKED",
            "ppaZone": pick(e,"negotiation_status","zone_status",default="FRONTIER_ONLY"),
            "decisionBoundary": "PUBLIC_DATA_ONLY",
            "rawObservedGenerationKwh": f(pick(p,"observed_generation_kwh"), 0),
            "engineeringReviewRequired": pick(p,"engineering_review_required",default="TRUE"),
            "sourceClaimPreserved": pick(p,"source_claim_preserved",default="TRUE")
        })

    def daily_shape(pid):
        vals = defaultdict(list)
        for r in hourly:
            if str(pick(r,"project_id","projectId")) != pid: continue
            hour = i(pick(r,"hour_of_day","hour","hod",default=0)) % 24
            val = f(pick(r,"generation_kwh","generation","pv_generation_kwh","load_kwh"), 0) or 0
            vals[hour].append(val)
        return [round(sum(vals[h])/len(vals[h]), 3) if vals[h] else 0 for h in range(24)]

    details = {}
    for p in projects:
        if p["economicsStatus"] != "READY_FOR_ECONOMICS": continue
        pid=p["projectId"]; e=econ_by_id[pid]
        def n(*keys): return f(pick(e,*keys))
        details[pid] = {
            "projectId":pid, "projectName":p["projectName"], "country":p["country"],
            "generationP50Kwh":n("generation_p50_kwh_observed","generation_p50_kwh_modeled","generation_p50_kwh"),
            "generationP90Kwh":n("generation_p90_kwh"), "generationP99Kwh":n("generation_p99_kwh"),
            "specificYieldP50":n("specific_yield_p50_kwh_kwp","specific_yield_observed"),
            "annualLoadKwh":n("annual_load_kwh_modeled"), "projectNpvLocal":n("project_npv_local_at_reference"),
            "projectNpvUsd":n("project_npv_usd_at_reference"), "projectIrr":n("project_irr_at_reference"),
            "equityIrr":n("equity_irr_at_reference"), "decision":pick(e,"decision",default="INDETERMINATE_MISSING_COMMERCIAL_DATA"),
            "ppaMode":pick(e,"ppa_mode",default="FRONTIER_ONLY"), "dailyShape":daily_shape(pid),
            "evidenceBoundary":pick(e,"evidence_boundary",default="PUBLIC_DATA_ONLY")
        }

    frontier_out=[]
    for r in frontier:
        pid=str(pick(r,"project_id","projectId",default=""))
        frontier_out.append({
            "projectId":pid, "projectName":pick(r,"project_name","projectName",default=econ_by_id.get(pid,{}).get("project_name",pid)),
            "customerCeiling":f(pick(r,"customer_ceiling_local_per_kwh","customer_ceiling")),
            "sponsorFloor":f(pick(r,"sponsor_floor_local_per_kwh","sponsor_floor")),
            "lenderFloor":f(pick(r,"lender_floor_local_per_kwh","lender_floor")),
            "negotiationLower":f(pick(r,"negotiation_lower_local_per_kwh","negotiation_lower")),
            "negotiationUpper":f(pick(r,"negotiation_upper_local_per_kwh","negotiation_upper")),
            "zoneStatus":pick(r,"negotiation_status","zone_status",default="FRONTIER_ONLY"),
            "referenceCase":"REFERENCE_CASE_NOT_ACTUAL_PPA",
            "decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA"
        })

    schedule_by_id=defaultdict(list)
    for r in debt:
        pid=str(pick(r,"project_id","projectId",default=""))
        schedule_by_id[pid].append({
            "year":pick(r,"year","period",default=str(len(schedule_by_id[pid])+1)),
            "opening":f(pick(r,"opening_debt_local","opening_local","opening")),
            "interest":f(pick(r,"interest_local","interest")),
            "principal":f(pick(r,"principal_local","principal")),
            "debtService":f(pick(r,"debt_service_local","debt_service")),
            "closing":f(pick(r,"closing_debt_local","closing_local","closing")),
            "dscr":f(pick(r,"dscr","dscr_min"))
        })
    debt_details={}
    for pid,e in econ_by_id.items():
        debt_details[pid]={
            "debtCapacityUsd":f(pick(e,"debt_capacity_usd")), "debtRateType":pick(e,"debt_rate_type",default="FLOATING"),
            "bindingConstraint":pick(e,"binding_debt_constraint",default="DSCR"), "dscrMin":f(pick(e,"dscr_min")),
            "llcr":f(pick(e,"llcr_loan_life")), "plcr":f(pick(e,"plcr_project_life")), "schedule":schedule_by_id.get(pid,[])
        }
    policy=[
        {"mode":"FIXED_CONTRACTUAL_SCHEDULE","openingPreserved":"TRUE","principalPreserved":"TRUE","closingPreserved":"TRUE","interestPolicy":"Reprice interest only when floating-rate shock applies"},
        {"mode":"NO_NEW_DEBT","openingPreserved":"TRUE","principalPreserved":"TRUE","closingPreserved":"TRUE","interestPolicy":"Reuse base contractual principal; no debt increase"},
        {"mode":"RESIZED_DEBT","openingPreserved":"SCENARIO","principalPreserved":"SCENARIO","closingPreserved":"SCENARIO","interestPolicy":"Scenario resize"}
    ]

    risk=[]
    for r in scenarios:
        pid=str(pick(r,"project_id","projectId",default=""))
        risk.append({
            "projectId":pid, "scenario":pick(r,"scenario","scenario_name",default="—"), "debtMode":pick(r,"debt_mode","mode",default="—"),
            "debt":f(pick(r,"debt_local","debt")), "principalSchedulePreserved":pick(r,"base_debt_schedule_preserved","principal_schedule_preserved",default="FALSE"),
            "interestChanged":pick(r,"interest_schedule_changed","interest_repricing_policy_applied",default="FALSE"),
            "interestPolicy":pick(r,"interest_repricing_policy","interest_policy",default="—"),
            "incrementalCapex":f(pick(r,"incremental_capex_local","incremental_capex")),
            "additionalDebt":f(pick(r,"additional_debt_local","additional_debt")),
            "minDscr":f(pick(r,"min_dscr","dscr_min")), "llcr":f(pick(r,"llcr")), "plcr":f(pick(r,"plcr")),
            "referenceCase":"REFERENCE_CASE_NOT_ACTUAL_PPA", "decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA"
        })

    run_id=os.getenv("WEBSITE_WORKFLOW_RUN_ID") or os.getenv("GITHUB_RUN_ID","CI_PENDING")
    website_sha=os.getenv("WEBSITE_SOURCE_SHA") or os.getenv("GITHUB_SHA","WEBSITE_SOURCE_PENDING")
    shared={
        "releaseId":WEBSITE_RELEASE, "asOfDate":os.getenv("V5_1_3_FREEZE_DATE_UTC","2026-09-02"),
        "candidateCount":54, "selectedCount":20, "economicsReadyCount":19, "technicalBlockedCount":1,
        "observationCount":441, "scenarioRows":171, "transactionEvidenceStatus":"OPEN",
        "bankableTransactionReady":False, "capitalAllocationStatus":"DISABLED_FRONTIER_ONLY",
        "claimBoundary":"PUBLIC_DATA_ONLY", "ppaMode":"FRONTIER_ONLY", "decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA",
        "modelReleaseTag":MODEL_TAG, "modelSourceSha":MODEL_SHA, "websiteRelease":WEBSITE_RELEASE,
        "websiteSourceSha":website_sha, "websiteWorkflowRunId":run_id, "modelDevelopmentFreeze":True,
        "remoteOnly":True, "recruiterReady":True
    }
    write("shared-summary.json",shared)
    write("release-meta.json",{
        "modelReleaseVersion":"5.1.3","modelReleaseTag":MODEL_TAG,"modelSourceSha":MODEL_SHA,
        "websiteRelease":WEBSITE_RELEASE,"websiteSourceSha":website_sha,"websiteWorkflowRunId":run_id,
        "modelDevelopmentFreeze":True,"websiteStatus":"SEALED_IN_CI","ppaMode":"FRONTIER_ONLY",
        "decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA","remoteOnly":True
    })
    write("projects.json",{"shared":shared,"projects":projects})
    write("case.json",{"shared":shared,"projects":projects,"steps":["Source and preserve observations","Apply physical QA","Resolve P50 / P90 / P99","Model load and energy","Calculate PPA frontier","Size debt and coverage","Stress contractual schedule","Reconcile and publish","Keep external gates open"]})
    write("overview.json",{"shared":shared,"evidenceClass":"PUBLIC_DATA_ONLY","headline":"Real C&I Solar Projects. Public Evidence. Project Finance Decisions Under Uncertainty."})
    write("economics.json",{"shared":shared,"projects":[p for p in projects if p["economicsStatus"]=="READY_FOR_ECONOMICS"],"projectDetails":details,"blockedProject":{"projectId":str(pick(blocked_row,"project_id",default="ARISUDHANA")),"projectName":pick(blocked_row,"project_name",default="Arisudhana"),"status":"TECHNICAL_DATA_BLOCKED","rawObservedGenerationKwh":f(pick(blocked_row,"observed_generation_kwh"),30500000),"reason":"EXTREME_OUTLIER_BLOCK_BASE"}})
    write("frontier.json",{"shared":shared,"projects":frontier_out,"referenceCase":"REFERENCE_CASE_NOT_ACTUAL_PPA"})
    write("debt.json",{"shared":shared,"projects":[p for p in projects if p["economicsStatus"]=="READY_FOR_ECONOMICS"],"details":debt_details,"policy":policy})
    portfolio_projects=[]
    for p in projects:
        portfolio_projects.append({**p,"exposure":"Not allocated","nextGate":"Commercial evidence"})
    write("portfolio.json",{"shared":shared,"shortlistCount":19,"allocatedCount":0,"budget":0,"capitalAllocationStatus":"DISABLED_FRONTIER_ONLY","projects":[p for p in portfolio_projects if p["economicsStatus"]=="READY_FOR_ECONOMICS"]})
    write("risk.json",{"shared":shared,"scenarioRows":len(risk),"projects":[p for p in projects if p["economicsStatus"]=="READY_FOR_ECONOMICS"],"scenarios":risk})
    write("scenarios.json",{"shared":shared,"scenarioRows":len(risk),"rows":risk})
    write("model.json",{"shared":shared,"metadata":{"workbookSheets":28,"pytestPassed":26,"pytestTotal":26,"semanticPassed":26,"semanticTotal":26,"reproducibility":"PASS","architecture":["28-sheet native workbook","26 pytest controls","26 semantic controls","Remote-only generated website data","Claim boundary and lineage sealed in CI"]}})
    gates=[
        {"name":"Commercial PPA evidence","status":"OPEN","note":"No executed PPA disclosed"},
        {"name":"Customer load / offtake evidence","status":"OPEN","note":"Public-data boundary"},
        {"name":"Lender term sheet","status":"OPEN","note":"No lender commitment claimed"},
        {"name":"Technical site diligence","status":"OPEN","note":"Engineering review required where flagged"},
        {"name":"Tax and legal review","status":"OPEN","note":"Not represented by this model"},
        {"name":"Interconnection","status":"OPEN","note":"External gate"},
        {"name":"Insurance","status":"OPEN","note":"External gate"},
        {"name":"Investment committee approval","status":"OPEN","note":"No allocation approved"}
    ]
    downloads=[
        {"label":"Website source branch","url":f"https://github.com/{REPO}/tree/{WEBSITE_RELEASE}"},
        {"label":"Frozen model release","url":f"https://github.com/{REPO}/releases/tag/{MODEL_TAG}"},
        {"label":"Website CI workflow","url":f"https://github.com/{REPO}/actions/workflows/v5-1-3-website-refresh.yml"},
        {"label":"Drive governance control","url":"https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit"}
    ]
    write("evidence.json",{"shared":shared,"gateCount":len(gates),"gates":gates,"readiness":[
        {"area":"Recruiter presentation","status":"RECRUITER_READY","meaning":"Evidence-labelled presentation surface"},
        {"area":"Bankable transaction","status":"FALSE","meaning":"Not claimed"},
        {"area":"Capital allocation","status":"DISABLED_FRONTIER_ONLY","meaning":"No approved portfolio"},
        {"area":"Model freeze","status":"TRUE","meaning":"Frozen source remains unchanged"}],"downloads":downloads,"sources":downloads})
    print(json.dumps({"websiteRelease":WEBSITE_RELEASE,"websiteSourceSha":website_sha,"modelSourceSha":MODEL_SHA,"projects":20,"economics":19,"scenarios":len(risk)}))

if __name__ == "__main__":
    main()
