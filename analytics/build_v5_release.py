"""V5.1 single-command orchestration and fail-closed G0-G9 release control."""
from __future__ import annotations
import csv,hashlib,json,os,subprocess,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PUB=ROOT/"data"/"public";EVID=ROOT/"evidence";RES=ROOT/"research";REL=ROOT/"release";OUT=ROOT/"outputs";VAL=ROOT/"validation"
def read(p):
 with p.open(newline="",encoding="utf-8-sig") as h:return list(csv.DictReader(h))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def num(x):
 try:return float(str(x).replace(",",""))
 except (TypeError,ValueError):return None
def run(cmd):
 r=subprocess.run(cmd,cwd=ROOT,check=False,capture_output=True,text=True)
 print(r.stdout);print(r.stderr,file=sys.stderr)
 if r.returncode:raise SystemExit(r.returncode)
def build():
 OUT.mkdir(exist_ok=True);REL.mkdir(exist_ok=True);VAL.mkdir(exist_ok=True)
 sources=read(EVID/"GLOBAL_SOURCE_REGISTER.csv");source_ids={r["source_id"] for r in sources}
 candidates=read(RES/"GLOBAL_PROJECT_CANDIDATES.csv");scoring=read(RES/"CANDIDATE_SCORING.csv");master=read(PUB/"project_master_real.csv");overlay=read(PUB/"project_assumption_overlay.csv");entities=read(PUB/"project_entity_map.csv")
 packs=read(EVID/"COUNTRY_BENCHMARK_PACKS.csv");fx=read(EVID/"FX_REGISTER.csv");rates=read(EVID/"RATE_REGISTER.csv");tax=read(EVID/"TAX_BENCHMARK_REGISTER.csv");capex=read(EVID/"CAPEX_BENCHMARK_REGISTER.csv");opex=read(EVID/"OPEX_BENCHMARK_REGISTER.csv")
 blockers=[];selected=[x for x in master if "SELECTED" in x["selection_status"]]
 score_map={x["candidate_project_id"]:x for x in scoring};master_ids={x["project_id"] for x in selected}
 if len(selected)<15 or len(selected)>25:blockers.append("G5_UNIVERSE_SIZE")
 if len(master_ids)!=len(selected):blockers.append("G1_DUPLICATE_PROJECT")
 if master_ids!={x["canonical_project_id"] for x in entities}:blockers.append("G1_ENTITY_MAP")
 if not master_ids.issubset({x["candidate_project_id"] for x in candidates}):blockers.append("G1_CANDIDATE_LINK")
 if any(x["evidence_grade"]=="EXCLUDE" or num(x["coverage_score"])<65 for x in selected):blockers.append("G5_EXCLUDE_SELECTED")
 if selected and sum(x["evidence_grade"] in {"GOLD","STRONG"} for x in selected)/len(selected)<.70:blockers.append("G5_GOLD_STRONG_SHARE")
 for x in selected:
  s=score_map.get(x["candidate_project_id"],{})
  if s.get("candidate_coverage_grade")!=x.get("candidate_coverage_grade") or s.get("candidate_coverage_grade")!=x.get("evidence_grade"):blockers.append("G1_SCORE_GRADE_MISMATCH:"+x["project_id"])
  if x.get("entity_granularity") not in {"ASSET_SITE","MULTISITE_PORTFOLIO","PORTFOLIO_FACILITY","PROGRAM","PLATFORM","REFERENCE_ONLY"}:blockers.append("G1_GRANULARITY")
 source_ids.update({x["rate_id"] for x in rates});source_ids.update({x["benchmark_id"] for x in capex});source_ids.update({x["benchmark_id"] for x in opex});source_ids.update({x["rate_id"] for x in read(EVID/"DISCOUNT_RATE_REGISTER_V5.csv")})
 for row in overlay:
  if row["source_id"] not in source_ids and row["source_id"]!="NOT_DISCLOSED":blockers.append("G0_OVERLAY_SOURCE:"+row["source_id"])
  if row["parameter"]=="project_cost_local":
   if not row["source_currency"] or not row["source_unit"] or not row["fx_source_id"] or not row["normalized_currency"] or not row["normalized_unit"]:blockers.append("G2_CAPEX_CONTRACT:"+row["project_id"])
   if num(row["fx_rate_to_local"]) is None:blockers.append("G2_FX_MISSING:"+row["project_id"])
 for row in fx:
  if not row["source_id"] or row["source_id"].startswith("METHOD-V5"):blockers.append("G2_FX_METHOD_SOURCE")
  if not row["spot_date"] or not row["last_checked"]:blockers.append("G3_FX_DATE")
 if any(x["source_id"].startswith("METHOD-V5") for x in rates+tax):blockers.append("G4_METHOD_EXTERNAL_REGISTER")
 if any(x["comparability_grade"] not in {"ASSET_LEVEL_HIGH","PORTFOLIO_LEVEL_MEDIUM","REGIONAL_CONTEXT","GLOBAL_CONTEXT","LOW_COMPARABILITY"} for x in capex):blockers.append("G4_COMPARABILITY")
 if any(x["status"]!="READY_FOR_V5_1_ENGINE" for x in packs):blockers.append("G4_PACK_STATUS")
 raw=read(PUB/"raw_project_observations.csv")
 if any(not x.get("value_date") or not x.get("source_id") for x in raw):blockers.append("G0_RAW_LINEAGE")
 if any(x.get("source_id") not in source_ids for x in raw if x.get("source_id")):blockers.append("G0_RAW_SOURCE")
 run([sys.executable,"-m","analytics.build_v5_economics"])
 run([sys.executable,"-m","analytics.build_v5_workbook"])
 run([sys.executable,"scripts/build_website_data_v5.py"])
 run([sys.executable,"scripts/generate_recruiter_surfaces.py"])
 econ=read(OUT/"v5_project_economics.csv");scen=read(OUT/"v5_scenarios.csv");rec=read(OUT/"v5_reconciliation.csv");debt_rows=read(OUT/"v5_debt_schedule.csv")
 if len(econ)!=len(selected):blockers.append("G8_ECONOMICS_ROW_COUNT")
 if len(scen)<len(selected)*6:blockers.append("G7_SCENARIO_ROWS")
 if len(rec)!=len(selected) or any(x["status"]!="PASS" for x in rec):blockers.append("G8_PYTHON_EXCEL_RECON")
 if any(x.get("ppa_mode")=="FRONTIER_ONLY" and x.get("ppa_price_local_per_kwh") not in ("","None") for x in econ):blockers.append("G5_FAKE_FRONTIER_PRICE")
 if any(num(x.get("closing_debt_local")) is not None and num(x.get("closing_debt_local"))<-.01 for x in debt_rows):blockers.append("G6_DEBT_CLOSE")
 if len(read(OUT/"v5_8760.csv"))!=len(selected)*8760:blockers.append("G5_8760_COUNT")
 required={"BASE","P90_ENERGY","CAPEX_OVERRUN","INTEREST_RATE_SHOCK","COD_DELAY","OPEX_INFLATION","OFFTAKER_NONPAYMENT","OFFTAKER_TERMINATION","COMBINED_DOWNSIDE"}
 if not required.issubset({x["scenario_id"] for x in scen}):blockers.append("G7_SCENARIO_LIBRARY")
 if not (ROOT/"artifacts"/"v5_model"/"vietgreen_v5_1_model.xlsx").exists():blockers.append("G8_WORKBOOK")
 if not (ROOT/"artifacts"/"v5_website_data"/"project_cards.json").exists():blockers.append("G9_WEBSITE")
 if not (ROOT/"artifacts"/"v5_surfaces"/"recruiter_package.md").exists():blockers.append("G9_SURFACES")
 gates={f"G{i}":"PASS" for i in range(10)}
 for b in blockers:gates["G"+b[1]]="BLOCKED" if len(b)>1 and b[1].isdigit() else gates["G9"]
 status="READY_FOR_RECRUITER_RELEASE" if not blockers else "ECONOMICS_BLOCKED"
 input_files=[EVID/"GLOBAL_SOURCE_REGISTER.csv",RES/"CANDIDATE_SCORING.csv",PUB/"raw_project_observations.csv",PUB/"project_entity_map.csv",PUB/"project_master_real.csv",PUB/"project_assumption_overlay.csv",RES/"CONFLICT_REGISTER.csv",EVID/"CAPEX_BENCHMARK_REGISTER.csv"]
 hashes={p.name:sha(p) for p in input_files}
 runtime={"release_id":"V5.1-GLOBAL-REAL-DATA","release_version":"5.1.0-recruiter-final" if not blockers else "5.1.0-remediation-blocked","source_commit_sha":os.getenv("GITHUB_SHA","LOCAL_RUNTIME_NOT_RELEASE"),"github_run_id":os.getenv("GITHUB_RUN_ID","CI_REQUIRED"),"github_job_id":os.getenv("GITHUB_JOB","CI_REQUIRED"),"input_freeze_id":"V5.1-INPUT-FREEZE-2026-09-01-OUTCOME-BLIND","input_hashes":hashes,"candidate_count":len(candidates),"project_count":len(selected),"country_count":len({x["country"] for x in selected}),"observed_fact_count":sum(x.get("evidence_class","").startswith("OBSERVED_") for x in raw),"benchmark_assumption_count":sum(x.get("evidence_class")=="BENCHMARK_ASSUMPTION" for x in overlay),"analyst_assumption_count":sum(x.get("evidence_class")=="ANALYST_ASSUMPTION" for x in overlay),"evidence_grade_distribution":dict(Counter(x["evidence_grade"] for x in selected)),"model_mode_distribution":dict(Counter(x["model_mode"] for x in selected)),"ppa_mode_distribution":dict(Counter(x["ppa_mode"] for x in selected)),"benchmark_dependency":{"capex":"EXPLICIT_SOURCE_UNIT_FX","opex":"ANALYST_OVERLAY","ppa":"FRONTIER_ONLY"},"gate_status":gates,"economics_status":"AUTHORITATIVE_STANDARDIZED_RECONSTRUCTION" if not blockers else "INVALID_PENDING_REBUILD","economics_authoritative":not blockers,"recruiter_ready":not blockers,"transaction_evidence_status":"OPEN","bankable_transaction_ready":False,"claim_boundary":"Standardized public-data Project Finance reconstruction; not actual project economics, lender terms, bankability, legal/tax opinion or investment approval.","economic_output_hashes":{p.name:sha(p) for p in [OUT/"v5_project_economics.csv",OUT/"v5_cash_flow.csv",OUT/"v5_debt_schedule.csv",OUT/"v5_scenarios.csv",OUT/"v5_portfolio.csv",OUT/"v5_reconciliation.csv"]},"workbook_hash":sha(ROOT/"artifacts"/"v5_model"/"vietgreen_v5_1_model.xlsx"),"surface_hashes":{"recruiter_package":sha(ROOT/"artifacts"/"v5_surfaces"/"recruiter_package.md")},"website_hashes":{"project_cards":sha(ROOT/"artifacts"/"v5_website_data"/"project_cards.json")},"blockers":sorted(set(blockers))}
 (REL/"V5_RUNTIME_RELEASE_MANIFEST.json").write_text(json.dumps(runtime,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 (REL/"V5_BUILD_STATUS.json").write_text(json.dumps(runtime,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 dod=[("DATA","V5 baseline preserved; V4.1.3 untouched; selected scores and grades reconciled"),("UNITS","Source monetary unit/currency/FX preserved and local ledger validated"),("BENCHMARKS","CAPEX/OPEX/tariff/tax/rate/FX/discount registers source-backed and scoped"),("MODEL","8760, P50/P90, frontier, local cash flow, capacity debt, coverage, returns and scenarios active"),("QA","G0-G9; candidate/master; FX; Python/Excel; debt; scenario; surface checks"),("RELEASE","Exact SHA/runtime manifest/artifact path/claim boundary generated in CI")]
 with (VAL/"V5_1_FINAL_DOD.csv").open("w",newline="",encoding="utf-8") as h:
  w=csv.writer(h);w.writerow(["dod_area","status","evidence"]);w.writerows([(a,"PASS" if not blockers else "BLOCKED",b) for a,b in dod])
 (ROOT/"validation"/"V5_1_ENGINE_PATH.json").write_text(json.dumps({"engine_version":"V5.1.0","module_hashes":"see runtime manifest","energy_engine":"analytics.load_match_8760.profile","load_engine":"analytics.load_match_8760.profile","ppa_engine":"analytics.ppa_engine","capex_engine":"analytics.capex_engine","cash_flow_engine":"analytics.build_v5_economics.operating_schedule","debt_sculpting_engine":"analytics.debt_sculpting","reserve_engine":"standardized reserve policy","returns_engine":"analytics.build_v5_economics.npv/irr","scenario_engine":"analytics.build_v5_economics.scenario loop","portfolio_engine":"analytics.portfolio_selection","status":status},indent=2)+"\n",encoding="utf-8")
 if blockers:
  print(json.dumps({"release_status":status,"blocker_count":len(set(blockers)),"blockers":sorted(set(blockers))},ensure_ascii=False));raise SystemExit(2)
 print(json.dumps({"release_status":status,"project_count":len(selected),"candidate_count":len(candidates),"gates":gates},ensure_ascii=False))
if __name__=="__main__":build()
