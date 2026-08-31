"""Final remote release-control checks; mechanical failures stop CI."""
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read_rows(relative):
    with (ROOT/relative).open(newline="",encoding="utf-8") as handle: return list(csv.DictReader(handle))
def main():
    checks=[]
    def add(cid,status,actual,detail): checks.append({"control_id":cid,"status":status,"actual":actual,"detail":detail})
    projects=read_rows("data/synthetic/project_master.csv"); energy=read_rows("outputs/energy_p50_p90.csv"); load=read_rows("outputs/load_matching_summary.csv")
    qa=read_rows("validation/QA_REMOTE_RUN.csv"); dq=read_rows("validation/DATA_QUALITY_RESULTS.csv"); tariff=read_rows("evidence/TARIFF_MASTER.csv")
    sources=read_rows("evidence/SOURCE_REGISTER.csv"); regulatory=read_rows("evidence/REGULATORY_REGISTER.csv")
    add("REL-001","PASS" if len(projects)==20 else "FAIL",len(projects),"locked 20-project synthetic population")
    add("REL-002","PASS" if len(energy)==20 and len(load)==20 else "FAIL","%d energy / %d load"%(len(energy),len(load)),"final one-row-per-project outputs")
    add("REL-003","PASS" if all(len(row.get("hourly_profile_hash",""))==64 for row in energy) else "FAIL","20 profile hashes","8,760 profile lineage")
    add("REL-004","PASS" if all(row.get("scope")=="final_8760" for row in load) else "FAIL","final_8760","hourly output scope explicit")
    add("REL-005","PASS" if all(float(row["p90_y1_kwh"])<=float(row["p50_y1_kwh"]) for row in energy) else "FAIL","P90<=P50","uncertainty monotonicity")
    add("REL-006","PASS" if all(row.get("pvout_double_count_check")=="PASS" for row in load) else "FAIL","PVOUT double-count check","no generic PR layered on PVOUT")
    add("REL-007","PASS" if all(row.get("billing_status")=="WATCH" for row in energy) else "FAIL","WATCH","legal schedule versus billed implementation")
    source_ids={row.get("source_id") for row in sources}|{row.get("assumption_id") for row in read_rows("evidence/ASSUMPTION_REGISTER.csv")}
    referenced={row.get("source_id") for row in tariff}|{row.get("source_id") for row in regulatory}
    add("REL-008","PASS" if referenced<=source_ids else "FAIL","%d referenced / %d registered"%(len(referenced),len(referenced&source_ids)),"tariff/regulatory lineage resolves")
    derived=[]
    for project,out in zip(projects,load): derived.append(abs(float(project["self_consumption_ratio"])-float(out["self_consumption_ratio"]))<=1e-8)
    add("REL-009","PASS" if all(derived) else "FAIL","master derived fields reconcile","screening and final ratio tie")
    add("REL-010","PASS" if not any(row.get("status")=="FAIL" for row in dq) else "FAIL","DQ %d/%d"%(sum(row.get("status")=="PASS" for row in dq),len(dq)),"no DQ failures")
    add("REL-011","PASS" if not any(row.get("status")=="FAIL" for row in qa) else "FAIL","QA %d/%d"%(sum(row.get("status")=="PASS" for row in qa),len(qa)),"no remote QA failures")
    manifest=json.loads((ROOT/"release/MODEL_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    add("REL-012","WARN",manifest.get("release_status"),"candidate manifest is refreshed after the immutable workflow artifact")
    add("REL-013","PASS" if all(row.get("raw_snapshot_path")=="NOT_STORED_LOCAL" for row in sources) else "FAIL","remote source policy","no desktop snapshots")
    out=ROOT/"validation/RELEASE_CONTROL_RESULTS.csv"
    with out.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=["control_id","status","actual","detail"]); writer.writeheader(); writer.writerows(checks)
    report=["# RELEASE_CONTROL_REPORT","","Generated on the GitHub Actions runner; no project data is written to the desktop workspace.","","- Mechanical controls: %d PASS, %d FAIL."%(sum(row["status"]=="PASS" for row in checks),sum(row["status"]=="FAIL" for row in checks)),"- Billed-tariff confirmation and independent lender/legal/tax/technical/site diligence remain open.","- Manifest linkage is refreshed after the workflow produces the artifact and workbook commit."]
    (ROOT/"validation/RELEASE_CONTROL_REPORT.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps({"release_controls": checks}, indent=2, sort_keys=True))
    return 1 if any(row["status"]=="FAIL" for row in checks) else 0
if __name__=="__main__": raise SystemExit(main())
