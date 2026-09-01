"""V5 G0-G9 release control for the public-data reconstruction."""
from __future__ import annotations
import argparse, csv, hashlib, json, os
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PUB=ROOT/"data"/"public"; EVID=ROOT/"evidence"; RES=ROOT/"research"; REL=ROOT/"release"; OUT=ROOT/"outputs"
CLASSES={"OBSERVED_PROJECT_FACT","OBSERVED_TRANSACTION_FACT","OBSERVED_REGULATORY_FACT","OBSERVED_MARKET_FACT","DERIVED_FROM_OBSERVED","BENCHMARK_ASSUMPTION","ANALYST_ASSUMPTION","SCENARIO_ONLY","NOT_DISCLOSED","NOT_APPLICABLE"}
MODES={"FULL_RECONSTRUCTION","PARTIAL_RECONSTRUCTION","FRONTIER_ONLY","SCREENING_ONLY"}
GRADE={"GOLD":3,"STRONG":2,"ACCEPTABLE":1,"EXCLUDE":0}
def rows(p): 
    with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def fnum(x,default=None):
    try:return float(str(x).replace(",",""))
    except (TypeError,ValueError):return default
def req(path,fields,blockers):
    got=set(rows(path)[0].keys()) if rows(path) else set()
    for f in sorted(set(fields)-got):blockers.append(f"G2_SCHEMA_MISSING:{path.name}:{f}")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--final",action="store_true");ap.add_argument("--allow-incomplete",action="store_true");a=ap.parse_args()
    blockers=[]; config=json.loads((ROOT/"config"/"v5_global.yml").read_text(encoding="utf-8"))
    sources=rows(EVID/"GLOBAL_SOURCE_REGISTER.csv"); source_ids={r["source_id"] for r in sources}; rate_rows=rows(EVID/"RATE_REGISTER.csv")
    candidates=rows(RES/"GLOBAL_PROJECT_CANDIDATES.csv"); scoring=rows(RES/"CANDIDATE_SCORING.csv")
    master=rows(PUB/"project_master_real.csv"); overlay=rows(PUB/"project_assumption_overlay.csv"); raw=rows(PUB/"raw_project_observations.csv")
    entities=rows(PUB/"project_entity_map.csv"); packs=rows(EVID/"COUNTRY_BENCHMARK_PACKS.csv"); conflicts=rows(RES/"CONFLICT_REGISTER.csv")
    req(EVID/"GLOBAL_SOURCE_REGISTER.csv",{"source_id","source_tier","url","access_date","review_status"},blockers)
    req(RES/"GLOBAL_PROJECT_CANDIDATES.csv",{"candidate_project_id","country","source_ids","total_score","evidence_grade"},blockers)
    req(RES/"CANDIDATE_SCORING.csv",{"candidate_project_id","total_score","evidence_grade"},blockers)
    req(PUB/"raw_project_observations.csv",{"observation_id","candidate_project_id","field_name","raw_value","normalized_value","value_date","source_url","source_tier","evidence_class","source_status","conflict_flag"},blockers)
    req(PUB/"project_master_real.csv",{"project_id","country","benchmark_pack_id","evidence_grade","model_mode","selection_status","freeze_status","data_quality_status"},blockers)
    req(PUB/"project_assumption_overlay.csv",{"project_id","parameter","value","evidence_class","benchmark_pack_id","source_id","review_status"},blockers)
    req(RES/"CONFLICT_REGISTER.csv",{"conflict_id","candidate_project_id","resolution_status","base_case_treatment"},blockers)
    if len(source_ids)!=len(sources) or "" in source_ids:blockers.append("G0_SOURCE_REGISTER_DUPLICATE_OR_EMPTY")
    for s in sources:
        if s.get("source_tier") not in {"A1","A2","B1","B2","B3","C","D","E"}:blockers.append("G0_SOURCE_TIER_INVALID:"+s.get("source_id",""))
        if not s.get("access_date") or not s.get("url"):blockers.append("G3_SOURCE_DATE_OR_URL_MISSING:"+s.get("source_id",""))
    # G1 entity / identity
    mids=[r.get("project_id","") for r in master]; cids=[r.get("candidate_project_id","") for r in candidates]
    if len(mids)!=len(set(mids)) or any(not x for x in mids):blockers.append("G1_PROJECT_ID_DUPLICATE_OR_EMPTY")
    if set(mids)!={r.get("canonical_project_id") for r in entities}:blockers.append("G1_ENTITY_MAP_MISMATCH")
    if not set(mids).issubset(set(cids)):blockers.append("G1_SELECTED_PROJECT_NOT_IN_CANDIDATES")
    if any(x.startswith("CAND-") or x.startswith("SYN-") for x in mids):blockers.append("G1_SYNTHETIC_PROJECT_ID")
    # G2 units / evidence classes / exact score sums
    for r in raw:
        if r.get("evidence_class") not in CLASSES:blockers.append("G2_INVALID_EVIDENCE_CLASS:"+r.get("observation_id",""))
        if not r.get("normalized_unit") and r.get("field_name") not in {"developer","offtaker","country","project_status","business_model","ppa_exists","self_consumption_signal"}:blockers.append("G2_UNIT_MISSING:"+r.get("observation_id",""))
        if not r.get("value_date"):blockers.append("G3_VALUE_DATE_MISSING:"+r.get("observation_id",""))
        if r.get("source_id") and r.get("source_id") not in source_ids:blockers.append("G0_UNREGISTERED_RAW_SOURCE:"+r.get("observation_id",""))
    weights=["identity_weight","location_weight","developer_weight","offtaker_weight","business_model_weight","installed_capacity_weight","generation_weight","commissioning_status_weight","ppa_existence_weight","ppa_tenor_weight","load_self_consumption_weight","project_cost_weight","financing_amount_weight","financing_structure_weight","official_source_redundancy_weight"]
    smap={r.get("candidate_project_id"):r for r in scoring}
    if set(smap)!=set(cids):blockers.append("G3_SCORING_CANDIDATE_SET_MISMATCH")
    for r in scoring:
        total=sum(int(r.get(w) or 0) for w in weights)
        if total!=int(r.get("total_score") or -1):blockers.append("G3_SCORE_WEIGHT_SUM_MISMATCH:"+r.get("candidate_project_id",""))
        if not 0<=total<=100:blockers.append("G3_SCORE_OUT_OF_RANGE:"+r.get("candidate_project_id",""))
    # G3 source lineage / candidate registration
    for c in candidates:
        refs=[x for x in c.get("source_ids","").split("|") if x]
        if not refs or not set(refs).issubset(source_ids):blockers.append("G3_CANDIDATE_SOURCE_UNREGISTERED:"+c.get("candidate_project_id",""))
    for r in overlay:
        if r.get("source_id") not in source_ids:blockers.append("G3_OVERLAY_SOURCE_UNREGISTERED:"+r.get("project_id","")+":"+r.get("parameter",""))
        if r.get("evidence_class") not in CLASSES:blockers.append("G2_OVERLAY_EVIDENCE_INVALID:"+r.get("project_id",""))
    # G4 country benchmark packs and registered links
    pmap={r.get("benchmark_pack_id"):r for r in packs}
    for r in master:
        if r.get("benchmark_pack_id") not in pmap:blockers.append("G4_PACK_MISSING:"+r.get("project_id",""))
        elif pmap[r["benchmark_pack_id"]].get("status")!="READY_FOR_ECONOMICS":blockers.append("G4_PACK_NOT_READY:"+r.get("benchmark_pack_id",""))
        if r.get("primary_source_id") not in source_ids:blockers.append("G3_PRIMARY_SOURCE_UNREGISTERED:"+r.get("project_id",""))
        if r.get("model_mode") not in MODES:blockers.append("G5_MODEL_MODE_INVALID:"+r.get("project_id",""))
        if GRADE.get(r.get("evidence_grade",""),0)<GRADE["ACCEPTABLE"]:blockers.append("G0_EVIDENCE_BELOW_ACCEPTABLE:"+r.get("project_id",""))
        if r.get("freeze_status")!="FROZEN":blockers.append("G3_PROJECT_NOT_FROZEN:"+r.get("project_id",""))
    # G5 economics universe and evidence quality
    selected=[r for r in master if "SELECTED" in r.get("selection_status","")]
    if len(selected)<int(config["portfolio"]["minimum_projects"]):blockers.append(f"G5_MINIMUM_UNIVERSE:{len(selected)}")
    if len(selected)>int(config["portfolio"]["maximum_projects"]):blockers.append(f"G5_MAXIMUM_UNIVERSE:{len(selected)}")
    if selected and sum(GRADE.get(r.get("evidence_grade",""),0)>=2 for r in selected)/len(selected)<float(config["portfolio"]["minimum_gold_strong_share"]):blockers.append("G5_SELECTED_GOLD_STRONG_SHARE")
    for r in selected:
        ps=[x for x in overlay if x.get("project_id")==r.get("project_id")]
        have={x.get("parameter") for x in ps}
        for p in {"annual_generation_kwh","ppa_price_local_per_kwh","project_cost_local","financing_amount_local","operating_horizon_years","tax_rate","debt_all_in_rate"}:
            if p not in have:blockers.append("G5_OVERLAY_PARAMETER_MISSING:"+r.get("project_id","")+":"+p)
    # G5 portfolio concentration
    counts=Counter(r.get("country") for r in selected); total=len(selected) or 1
    shares={k:round(v/total,4) for k,v in counts.items()}
    if shares and max(shares.values())>float(config["portfolio"]["hard_max_country_share"]):blockers.append("G5_COUNTRY_CONCENTRATION:"+json.dumps(shares,sort_keys=True))
    # G8 conflict/reconciliation resolution
    for r in conflicts:
        if r.get("resolution_status") not in {"DISCLOSED_NOT_USED","RESOLVED","SUPERSEDED"}:blockers.append("G8_CONFLICT_OPEN:"+r.get("conflict_id",""))
    # G6 debt: standardized debt must be explicit, linked to a rate register and bounded.
    rate_countries={r.get("country") for r in rate_rows if r.get("status") in {"READY_FOR_SCREENING","READY_FOR_ECONOMICS"}}
    for r in selected:
        if r.get("country") not in rate_countries:blockers.append("G6_DEBT_RATE_REGISTER_MISSING:"+r.get("project_id",""))
        ps={x.get("parameter"):x for x in overlay if x.get("project_id")==r.get("project_id")}
        for p in {"financing_amount_local","debt_all_in_rate"}:
            if p not in ps or fnum(ps[p].get("value")) is None:blockers.append("G6_DEBT_INPUT_MISSING:"+r.get("project_id","")+":"+p)
    # G7 stress: the plan requires named downside scenarios before release.
    scenario_rows=rows(ROOT/"config"/"v5_scenarios.yml")
    required_scenarios={"BASE","P90_ENERGY","CAPEX_OVERRUN","INTEREST_RATE_SHOCK","COD_DELAY","COMBINED_DOWNSIDE"}
    if required_scenarios-{x.get("scenario_id") for x in scenario_rows}:blockers.append("G7_STRESS_SCENARIO_MATRIX_INCOMPLETE")
    if a.final and (not (OUT/"v5_scenarios.csv").exists() or len(rows(OUT/"v5_scenarios.csv"))<len(selected)*len(required_scenarios)):blockers.append("G7_STRESS_OUTPUT_INCOMPLETE")
    # G8 final reconciliation / output surface
    if a.final:
        econ=OUT/"v5_project_economics.csv"; scen=OUT/"v5_scenarios.csv"; rec=OUT/"v5_reconciliation.csv"
        if not econ.exists() or not scen.exists() or not rec.exists():blockers.append("G8_OUTPUTS_MISSING")
        else:
            if len(rows(econ))!=len(selected):blockers.append("G8_ECONOMICS_ROW_RECONCILIATION")
            if any(r.get("status")!="PASS" for r in rows(rec)):blockers.append("G8_RECONCILIATION_FAIL")
    # G9 claim governance
    claim=config["release"].get("claim_boundary","")
    if not claim or config["release"].get("bankable_transaction_ready") is not False:blockers.append("G9_CLAIM_BOUNDARY_INVALID")
    status="READY_FOR_SCREENING_RECONSTRUCTION" if a.final and not blockers else ("READY_FOR_ECONOMICS" if not blockers else "INPUT_DATA_BLOCKED")
    release={"release_id":"V5-GLOBAL-REAL-DATA","release_version":"V5.0.0","release_date":"2026-09-01","git_sha":os.getenv("GITHUB_SHA","RUNTIME_SHA_REQUIRED"),"release_status":status,"manifest_status":"FINAL_RECONCILED" if a.final and not blockers else "INPUT_CONTROL_VALIDATED","project_count":len(selected),"candidate_count":len(candidates),"observed_fact_count":sum(x.get("evidence_class","").startswith("OBSERVED_") for x in raw),"benchmark_assumption_count":sum(x.get("evidence_class")=="BENCHMARK_ASSUMPTION" for x in overlay),"analyst_assumption_count":sum(x.get("evidence_class")=="ANALYST_ASSUMPTION" for x in overlay),"country_share":shares,"evidence_grade_distribution":dict(Counter(r.get("evidence_grade") for r in selected)),"model_modes_present":sorted({r.get("model_mode") for r in selected}),"freeze_status":"FROZEN","transaction_evidence_status":"OPEN","bankable_transaction_ready":False,"recruiter_ready":not blockers,"claim_boundary":claim,"gate_status":{f"G{i}":("BLOCKED" if any(x.startswith(f"G{i}") for x in blockers) else "PASS") for i in range(10)},"blockers":sorted(set(blockers)),"input_hashes":{"source_register":sha(EVID/"GLOBAL_SOURCE_REGISTER.csv"),"project_master":sha(PUB/"project_master_real.csv"),"overlay":sha(PUB/"project_assumption_overlay.csv"),"candidates":sha(RES/"GLOBAL_PROJECT_CANDIDATES.csv")}}
    REL.mkdir(exist_ok=True);(REL/"V5_BUILD_STATUS.json").write_text(json.dumps(release,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"release_status":status,"project_count":len(selected),"candidate_count":len(candidates),"blocker_count":len(blockers),"blockers":sorted(set(blockers))},ensure_ascii=False))
    raise SystemExit(0 if a.allow_incomplete or not blockers else 2)
if __name__=="__main__":main()
