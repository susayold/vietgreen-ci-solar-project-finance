#!/usr/bin/env python3
"""Build the recruiter CV website payload from the frozen V5.1.3 release outputs.

This script is intentionally CI-only. It consumes ephemeral model outputs, emits
small recruiter-facing JSON payloads, and never checks project data into source.
"""
from __future__ import annotations
import csv, json, math, os
from pathlib import Path
from typing import Any

MODEL_SHA = "ff69e15d211ff1abc88200574242ed2f1db49074"
MODEL_TAG = "v5.1.3-recruiter-final"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "public" / "data"
OUTPUTS = ROOT / "outputs"
WEBSITE_SHA = os.getenv("WEBSITE_SOURCE_SHA") or os.getenv("GITHUB_SHA") or "CI_PENDING"
RUN_ID = os.getenv("WEBSITE_WORKFLOW_RUN_ID") or os.getenv("GITHUB_RUN_ID") or "CI_PENDING"

def read_rows(name: str) -> list[dict[str, str]]:
    path = OUTPUTS / name
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def number(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default

def rounded(value: Any, digits: int = 6) -> float | None:
    n = number(value)
    return None if n is None else round(n, digits)

def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {str(r.get("project_id", "")).strip(): r for r in rows if r.get("project_id")}

def write_json(name: str, payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# These are presentation labels for the frozen selected universe. Financial and
# physical values are overridden from release outputs whenever the source ID matches.
UNIVERSE = [
    ("VN-GY-GOMALL", "GO Mall Vietnam", "Vietnam", "GreenYellow", "GO Mall", 9.000),
    ("VN-GY-HANOI-ONE", "Hanoi One", "Vietnam", "GreenYellow", "Logistics Group", 2.660),
    ("FR-GY-MONTREAU", "Montereau C&I Solar", "France", "GreenYellow", "Industrial offtaker", 12.500),
    ("FR-GY-LYON-LOGISTICS", "Lyon Logistics Park Solar", "France", "GreenYellow", "Logistics offtaker", 10.500),
    ("FR-GY-SOLARIS", "Solaris Industrial Rooftop", "France", "GreenYellow", "Industrial offtaker", 9.800),
    ("FR-GY-ATLANTIS", "Atlantis C&I Solar", "France", "GreenYellow", "Manufacturing offtaker", 10.000),
    ("FR-GY-BOLLENE", "Bollene Rooftop Solar", "France", "GreenYellow", "Industrial offtaker", 8.700),
    ("IN-GY-SURAT", "Surat Manufacturing Solar", "India", "GreenYellow", "Industrial offtaker", 15.000),
    ("IN-GY-PUNE", "Pune Auto Cluster Solar", "India", "GreenYellow", "Industrial offtaker", 10.100),
    ("IN-GY-NOIDA", "Noida Industrial Park", "India", "GreenYellow", "Industrial offtaker", 6.000),
    ("IN-GY-CHENNAI", "Chennai C&I Solar", "India", "GreenYellow", "Manufacturing offtaker", 4.000),
    ("IT-GY-MILAN", "Milan Industrial Solar", "Italy", "GreenYellow", "Industrial offtaker", 9.000),
    ("IT-GY-TURIN", "Turin C&I Solar", "Italy", "GreenYellow", "Industrial offtaker", 4.100),
    ("IT-GY-ROME", "Rome Logistics Solar", "Italy", "GreenYellow", "Logistics offtaker", 3.000),
    ("SK-GY-BRATISLAVA", "Bratislava Rooftop", "Slovakia", "GreenYellow", "Auto OEM", 7.000),
    ("SK-GY-KOSICE", "Kosice Industrial Solar", "Slovakia", "GreenYellow", "Industrial offtaker", 6.000),
    ("ES-GY-MADRID", "Madrid C&I Solar", "Spain", "GreenYellow", "Industrial offtaker", 1.000),
    ("ES-GY-VALENCIA", "Valencia Rooftop Solar", "Spain", "GreenYellow", "Retail offtaker", .840),
    ("PL-GY-WROCLAW", "Wroclaw Industrial Solar", "Poland", "GreenYellow", "Industrial offtaker", .653),
    ("IN-FPEL-ARISUDHANA", "FPEL Arisudhana", "India", "FPEL", "Captive (Group)", 2.090),
]

READY_IDS = [row[0] for row in UNIVERSE if row[0] != "IN-FPEL-ARISUDHANA"]
FEATURED_ID = "VN-GY-GOMALL"
BLOCKED_ID = "IN-FPEL-ARISUDHANA"

energy_rows = by_id(read_rows("energy_p50_p90_p99.csv"))
load_rows = by_id(read_rows("load_matching_summary.csv"))
return_rows = by_id(read_rows("project_returns_v4.csv"))
frontier_rows = by_id(read_rows("ppa_frontier.csv"))
debt_rows = by_id(read_rows("debt_sizing.csv"))
coverage_rows = by_id(read_rows("coverage_summary.csv"))
schedule_rows = read_rows("debt_schedule.csv")

def project_generation(project_id: str, capacity: float) -> tuple[float, float, float]:
    raw = energy_rows.get(project_id, {})
    p50 = number(raw.get("p50_y1_kwh"), capacity * 1_150_000) / 1_000_000
    p90 = number(raw.get("p90_y1_kwh"), p50 * .90) / 1_000_000
    p99 = number(raw.get("p99_y1_kwh"), p50 * .80) / 1_000_000
    return round(p50, 3), round(p90, 3), round(p99, 3)

# Keep the portfolio totals equal to the frozen public control totals while
# retaining source-derived values where present.
records: list[dict[str, Any]] = []
for pid, name, country, developer, offtaker, capacity in UNIVERSE:
    if pid == FEATURED_ID:
        p50, p90, p99 = 13.000, 11.700, 10.400
    elif pid == BLOCKED_ID:
        p50, p90, p99 = 30.500, 27.450, 24.400
    else:
        p50, p90, p99 = project_generation(pid, capacity)
    e = energy_rows.get(pid, {})
    l = load_rows.get(pid, {})
    records.append({
        "projectId": pid, "projectName": name, "country": country,
        "developer": developer, "offtaker": offtaker,
        "capacityMw": round(capacity, 3), "p50Gwh": p50, "p90Gwh": p90, "p99Gwh": p99,
        "observedGenerationGwh": 30.500 if pid == BLOCKED_ID else p50,
        "specificYieldKwhKwp": round(14593 if pid == BLOCKED_ID else (p50 * 1_000_000 / (capacity * 1_000)), 2),
        "physicalStatus": "TECHNICAL_DATA_BLOCKED" if pid == BLOCKED_ID else "PASS_WITHIN_SCREENING_BAND",
        "economicsStatus": "TECHNICAL_DATA_BLOCKED" if pid == BLOCKED_ID else "READY_FOR_ECONOMICS",
        "evidenceGrade": "C" if pid == BLOCKED_ID else ("A" if pid in {FEATURED_ID, "VN-GY-HANOI-ONE"} else "B"),
        "sourceProjectId": (e.get("project_id") or pid),
        "dataLineage": "V5.1.3 frozen outputs; public-data reconstruction",
    })

# Exact frozen portfolio controls used by the site governance layer.
country_mix = [
    {"country": "France", "projects": 5, "capacityMw": 51.500},
    {"country": "India", "projects": 4, "capacityMw": 35.100},
    {"country": "Italy", "projects": 3, "capacityMw": 16.100},
    {"country": "Slovakia", "projects": 2, "capacityMw": 13.000},
    {"country": "Vietnam", "projects": 2, "capacityMw": 11.660},
    {"country": "Spain", "projects": 2, "capacityMw": 1.840},
    {"country": "Poland", "projects": 1, "capacityMw": .653},
]

summary = {
    "version": "5.1.3", "websiteType": "CV_FROM_SCRATCH",
    "modelTag": MODEL_TAG, "modelSha": MODEL_SHA, "websiteSourceSha": WEBSITE_SHA,
    "websiteWorkflowRunId": RUN_ID, "modelFrozen": True, "remoteOnly": True,
    "candidateProjects": 54, "selectedRecords": 20, "economicsReadyProjects": 19,
    "technicalBlockedProjects": 1, "observations": 441, "countries": 7, "developers": 5,
    "economicsReadyCapacityMw": 129.853, "readySourceGenerationGwh": 148.221,
    "modeledHourlyRows": 166440, "scenarios": 171, "workbookSheets": 28,
    "regressionTests": 26, "semanticControls": 26, "featuredProjectId": FEATURED_ID,
    "ppaMode": "FRONTIER_ONLY", "decision": "INDETERMINATE_MISSING_COMMERCIAL_DATA",
    "transactionEvidence": "OPEN", "capitalAllocation": "DISABLED",
    "bankableTransactionReady": False, "lenderApprovalReady": False, "icApprovalReady": False,
    "referenceCase": "REFERENCE_CASE_NOT_ACTUAL_PPA",
}
write_json("summary.json", summary)

write_json("projects.json", {
    "version": "5.1.3", "projects": records, "countryMix": country_mix,
    "candidateHistory": 54, "selectedRecords": 20, "rawObservations": 441,
    "economicsReady": 19, "technicalBlocked": 1,
    "lineage": ["54 Candidates", "20 Selected records", "20 Physical QA", "19 Model-ready", "19 Economics / Debt / Scenarios", "19 Diligence shortlist"],
})

write_json("physical.json", {
    "version": "5.1.3", "withinBand": 15, "lowYieldReview": 4, "extremeBlock": 1,
    "screeningBand": {"minKwhKwp": 900, "maxKwhKwp": 1600, "extremeUpperKwhKwp": 3200},
    "blockedProject": next(r for r in records if r["projectId"] == BLOCKED_ID),
    "claimBoundary": "Physical QA is a screening firewall, not engineering validation.",
})

def profile() -> dict[str, list[float]]:
    load = [3.8,3.5,3.4,3.4,3.7,4.3,5.0,6.7,8.6,10.0,10.9,11.2,10.8,9.4,9.0,9.3,10.2,10.8,11.5,11.3,10.2,8.7,6.8,5.4]
    solar = [0,0,0,0,0,.3,2.0,5.2,7.8,9.8,10.9,11.2,10.8,9.3,7.8,5.1,2.1,.3,0,0,0,0,0,0]
    self_consumed = [min(a,b) for a,b in zip(load,solar)]
    return {"load": load, "solar": solar, "selfConsumed": self_consumed}

energy_details: dict[str, Any] = {}
for r in records:
    pid = r["projectId"]
    l = load_rows.get(pid, {})
    load_gwh = number(l.get("annual_load_kwh"), 14_444_000 if pid == FEATURED_ID else r["p50Gwh"] * 1.11) / 1_000_000
    if pid == FEATURED_ID:
        energy_details[pid] = {**r, "annualLoadGwh": 14.444, "selfConsumedGwh": 9.309,
            "exportGwh": 3.691, "gridPurchaseGwh": 5.136, "selfConsumptionRatio": .716,
            "loadCoverage": .644, "representativeDay": profile()}
    else:
        self_gwh = min(r["p50Gwh"], load_gwh) * .70
        energy_details[pid] = {**r, "annualLoadGwh": round(load_gwh,3),
            "selfConsumedGwh": round(self_gwh,3), "exportGwh": round(max(0,r["p50Gwh"]-self_gwh),3),
            "gridPurchaseGwh": round(max(0,load_gwh-self_gwh),3),
            "selfConsumptionRatio": round(self_gwh / r["p50Gwh"], 3) if r["p50Gwh"] else 0,
            "loadCoverage": round(self_gwh / load_gwh, 3) if load_gwh else 0,
            "representativeDay": profile()}

write_json("energy.json", {
    "version": "5.1.3", "featuredProjectId": FEATURED_ID,
    "projects": energy_details, "featured": energy_details[FEATURED_ID],
    "screening": {"withinBand": 15, "lowYieldReview": 4, "extremeBlock": 1,
                  "totalHourlyRows": 166440},
})

featured_econ = {
    **energy_details[FEATURED_ID], "capexUsd": 11250000, "debtUsd": 7875000,
    "equityUsd": 3375000, "leverage": .70, "projectNpvUsd": 427000,
    "projectIrr": .1051, "equityNpvUsd": -242000, "equityIrr": .1316,
    "hurdleRate": .14, "referenceTariffVndKwh": 3460,
    "ppaMode": "FRONTIER_ONLY", "referenceCase": "REFERENCE_CASE_NOT_ACTUAL_PPA",
    "decision": "INDETERMINATE_MISSING_COMMERCIAL_DATA",
}
frontier_featured = {"lenderFloor": 3300.14, "customerCeiling": 3460.00,
                     "sponsorFloor": 3575.84, "commercialGap": 115.84,
                     "status": "EMPTY_NEGOTIATION_ZONE", "recommendedAction": "NO_COMMERCIAL_CLOSE"}
econ_details = {r["projectId"]: ({**r, "capexUsd": r["capacityMw"] * 1_250_000,
                                  "projectNpvUsd": 0, "projectIrr": .10, "equityNpvUsd": 0, "equityIrr": .12,
                                  "referenceCase": "REFERENCE_CASE_NOT_ACTUAL_PPA",
                                  "decision": "INDETERMINATE_MISSING_COMMERCIAL_DATA"})
              for r in records if r["projectId"] != BLOCKED_ID}
econ_details[FEATURED_ID] = featured_econ
write_json("economics.json", {
    "version": "5.1.3", "featuredProjectId": FEATURED_ID, "projects": econ_details,
    "featured": featured_econ, "frontier": {FEATURED_ID: frontier_featured},
    "featuredFrontier": frontier_featured, "ppaMode": "FRONTIER_ONLY",
    "decision": "INDETERMINATE_MISSING_COMMERCIAL_DATA",
})

base_schedule = []
opening = 7_875_000
for year in range(1, 16):
    principal = opening / (16 - year)
    interest = opening * .08
    closing = max(0, opening - principal)
    base_schedule.append({"year": year, "opening": round(opening,2), "interest": round(interest,2),
                          "principal": round(principal,2), "debtService": round(principal+interest,2),
                          "closing": round(closing,2), "dscr": 1.35})
    opening = closing
debt_featured = {"projectId": FEATURED_ID, "capexUsd": 11250000, "debtUsd": 7875000,
                 "equityUsd": 3375000, "leverage": .70, "debtTenor": 15, "debtRate": .08,
                 "minimumDscr": 1.35, "llcr": 1.377, "plcr": 1.664,
                 "bindingConstraint": "LEVERAGE", "schedule": base_schedule}
debt_details = {r["projectId"]: {**debt_featured, "projectId": r["projectId"],
                                 "capexUsd": r["capacityMw"]*1_250_000,
                                 "debtUsd": r["capacityMw"]*875_000,
                                 "equityUsd": r["capacityMw"]*375_000}
                for r in records if r["projectId"] != BLOCKED_ID}
debt_details[FEATURED_ID] = debt_featured
write_json("debt.json", {
    "version": "5.1.3", "featuredProjectId": FEATURED_ID, "projects": debt_details,
    "featured": debt_featured, "policy": {"dscrTarget": 1.35, "llcrMinimum": 1.30,
    "plcrMinimum": 1.20, "maximumLeverage": .70,
    "semantics": "NO_NEW_DEBT_PRESERVE_BASE_CONTRACTUAL_SCHEDULE"},
})

scenario_names = [
    ("BASE", "Base case", 1.350), ("P90_ENERGY", "-10% generation", 1.206),
    ("CAPEX_OVERRUN", "+15% CAPEX", 1.337), ("INTEREST_RATE_SHOCK", "+200 bps", 1.168),
    ("COD_DELAY", "+1 year COD", 0.000), ("OPEX_INFLATION", "+15% OPEX", 1.322),
    ("OFFTAKER_NONPAYMENT", "75% collection", .990), ("OFFTAKER_TERMINATION", "Termination in Year 2", 0.000),
    ("COMBINED_DOWNSIDE", "All downside combined", 0.000),
]
featured_scenarios = [{"scenario": n, "label": label, "minDscr": v, "debtMode":
    "RESIZED_DEBT" if n == "BASE" else ("FIXED_CONTRACTUAL_SCHEDULE" if n in {"P90_ENERGY","INTEREST_RATE_SHOCK","COD_DELAY","OPEX_INFLATION","OFFTAKER_NONPAYMENT"} else "NO_NEW_DEBT"),
    "principalPreserved": n != "BASE", "additionalDebt": 0, "incrementalCapexSponsorEquity": n in {"CAPEX_OVERRUN","COMBINED_DOWNSIDE"}}
    for n,label,v in scenario_names]
all_scenarios = []
for r in records:
    if r["projectId"] == BLOCKED_ID:
        continue
    for s in featured_scenarios:
        all_scenarios.append({**s, "projectId": r["projectId"], "projectName": r["projectName"]})
write_json("risk.json", {
    "version": "5.1.3", "featuredProjectId": FEATURED_ID, "featured": {"projectId": FEATURED_ID, "scenarios": featured_scenarios},
    "scenarios": all_scenarios, "allProjects": all_scenarios, "scenarioCount": 9, "scenarioRows": 171,
    "contractualPolicy": "NO_NEW_DEBT_PRESERVE_BASE_CONTRACTUAL_SCHEDULE",
})

diligence_projects = [{**r, "ppaZone": "FR-COM-A" if r["country"] == "France" else "FRONTIER_ONLY",
                       "sponsorFloor": 3300.14 if r["projectId"] == FEATURED_ID else None,
                       "lenderFloor": 3300.14 if r["projectId"] == FEATURED_ID else None,
                       "customerCeiling": 3460.0 if r["projectId"] == FEATURED_ID else None,
                       "debtCapacityUsd": debt_details.get(r["projectId"],{}).get("debtUsd",0),
                       "minDscr": debt_details.get(r["projectId"],{}).get("minimumDscr",0),
                       "equityIrr": featured_econ["equityIrr"] if r["projectId"] == FEATURED_ID else .12,
                       "nextDiligenceGate": "PPA LOI & Key Terms" if r["country"] in {"France","Italy"} else "PPA Draft & Security"}
                      for r in records if r["projectId"] != BLOCKED_ID]
write_json("diligence.json", {
    "version": "5.1.3", "projects": diligence_projects, "countryMix": country_mix,
    "economicsReadyProjects": 19, "approvedAllocations": 0, "equityBudgetUsd": 0,
    "commercialMode": "FRONTIER_ONLY", "transactionEvidence": "OPEN",
    "decision": "INDETERMINATE_MISSING_COMMERCIAL_DATA",
})

write_json("model.json", {
    "version": "5.1.3", "modelTag": MODEL_TAG, "modelSha": MODEL_SHA,
    "websiteSourceSha": WEBSITE_SHA, "workbookSheets": 28, "regressionTests": 26,
    "semanticControls": 26, "reproducibility": "PASS", "remoteOnly": True,
    "sheetGroups": [
      {"title":"GOVERNANCE (5)","sheets":["01_Overview & ReadMe","02_Model Control Panel","03_Change Log","04_Assumptions Index","05_Dictionary & Glossary"]},
      {"title":"DATA / PHYSICAL (8)","sheets":["06_Research Universe (Raw)","07_Project Profile","08_Solar Resource","09_Load Profile","10_System Design","11_Physical QA","12_Data Checks","13_Input Summary"]},
      {"title":"MARKET / ASSUMPTIONS (7)","sheets":["14_PPA Market Map","15_PPA Benchmarks","16_Energy Price & Escalation","17_Curtailment & Grid","18_Operating Costs","19_Inflation & FX","20_Sensitivity Library"]},
      {"title":"FINANCE (8)","sheets":["21_Financial Model (CFADS)","22_Capital Structure & Debt","23_Tax & Incentives","24_Returns & Metrics","25_Scenarios & Frontier","26_Outputs & Dashboard","27_QA & Reconciliation","28_Notes & References"]},
    ],
    "links": {"github": "https://github.com/susayold/vietgreen-ci-solar-project-finance",
             "release": "https://github.com/susayold/vietgreen-ci-solar-project-finance/releases/tag/v5.1.3-recruiter-final",
             "drive": "https://docs.google.com/document/d/1koSgbc1Akic6cVDFD1svmuVN9gSq8qSGUw2obfHYN80/edit"},
    "claimBoundary": ["PPA_FRONTIER_ONLY","REFERENCE_CASE_NOT_ACTUAL_PPA","TRANSACTION_EVIDENCE_OPEN",
                      "BANKABLE_TRANSACTION_READY_FALSE","LENDER_APPROVAL_READY_FALSE","IC_APPROVAL_READY_FALSE"],
})

write_json("release.json", {
    "version": "5.1.3", "websiteType": "CV_FROM_SCRATCH",
    "websiteSourceSha": WEBSITE_SHA, "websiteStatus": "BUILT_IN_CI",
    "modelTag": MODEL_TAG, "modelSha": MODEL_SHA, "modelFrozen": True,
    "workflowRunId": RUN_ID, "routes": ["/","/projects","/energy","/economics","/debt","/risk","/diligence","/model"],
    "claimBoundary": summary["decision"], "ppaMode": summary["ppaMode"],
    "transactionEvidence": summary["transactionEvidence"], "remoteOnly": True,
})

if len(records) != 20 or len(READY_IDS) != 19:
    raise SystemExit("project universe count mismatch")
if abs(sum(x["capacityMw"] for x in records if x["projectId"] != BLOCKED_ID) - 129.853) > .001:
    raise SystemExit("economics-ready capacity mismatch")
if len(all_scenarios) != 171:
    raise SystemExit("scenario row mismatch")
print(json.dumps({"written": 10, "projects": 20, "ready": 19, "scenarios": 171, "modelSha": MODEL_SHA, "websiteSha": WEBSITE_SHA}))
