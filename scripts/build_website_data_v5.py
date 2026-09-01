"""Generate V5 website data in CI artifacts; no V4 figures are read."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"artifacts"/"v5_website_data"; OUT.mkdir(parents=True,exist_ok=True)
def read(p):
    with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def main():
    m=json.loads((ROOT/"release"/"V5_BUILD_STATUS.json").read_text(encoding="utf-8")); e=read(ROOT/"outputs"/"v5_project_economics.csv"); s=read(ROOT/"outputs"/"v5_scenarios.csv")
    bycountry={}
    for r in e:bycountry[r["country"]]=bycountry.get(r["country"],0)+1
    payload={"site":"VietGreen V5 Global Real-Data Reconstruction","releaseStatus":m["release_status"],"projectCount":len(e),"candidateCount":m["candidate_count"],"countryCount":len(bycountry),"countries":bycountry,"modelModes":m["model_modes_present"],"claimBoundary":m["claim_boundary"],"evidenceClass":"STANDARDIZED_PUBLIC_DATA_RECONSTRUCTION","economics":{"rows":len(e),"scenarioRows":len(s),"currencySet":m.get("currencies",sorted({r["currency"] for r in e}))}}
    (OUT/"metadata.json").write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/"overview.json").write_text(json.dumps({"title":payload["site"],"headline":"Outcome-blind public-data reconstruction across selected real C&I solar records.","status":m["release_status"],"metrics":payload["economics"],"boundary":payload["claimBoundary"]},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/"projects.json").write_text(json.dumps(e,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"built={OUT} rows={len(e)}")
if __name__=="__main__":main()
