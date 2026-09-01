"""Build evidence-labelled website data from V5.1 economics."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"outputs";DEST=ROOT/"artifacts"/"v5_website_data"
def rows(p):
 with p.open(newline="",encoding="utf-8-sig") as h:return list(csv.DictReader(h))
def build():
 DEST.mkdir(parents=True,exist_ok=True);econ=rows(OUT/"v5_project_economics.csv")
 cards=[]
 for x in econ:
  cards.append({"project_id":x["project_id"],"country":x["country"],"capacity_kwp":x["installed_capacity_kwp"],"generation_p50_kwh":x["generation_p50_kwh"],"generation_p90_kwh":x["generation_p90_kwh"],"model_mode":x["model_mode"],"ppa_mode":x["ppa_mode"],"evidence_labels":["OBSERVED PUBLIC FACT","DERIVED PUBLIC FACT","BENCHMARK RECONSTRUCTION","ANALYST ASSUMPTION","STANDARDIZED UNDERWRITING","SCENARIO","NOT DISCLOSED"],"economics_label":"Standardized public-data Project Finance reconstruction.","exact_ppa_price_disclosed":False,"customer_ceiling_local_per_kwh":x["customer_ceiling_local_per_kwh"],"sponsor_floor_local_per_kwh":x["sponsor_floor_local_per_kwh"],"lender_floor_local_per_kwh":x["lender_floor_local_per_kwh"],"reference_npv_is_not_exact_ppa":True,"decision":x["decision"],"transaction_evidence_status":"OPEN","bankable_transaction_ready":False})
 (DEST/"project_cards.json").write_text(json.dumps({"release":"V5.1","claim_boundary":"Public-data reconstruction only","cards":cards},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 (OUT/"v5_website_data.csv").write_text("project_id,country,ppa_mode,economics_label,transaction_evidence_status,bankable_transaction_ready\n"+"".join(f'{x["project_id"]},{x["country"]},{x["ppa_mode"]},"Standardized public-data Project Finance reconstruction.",OPEN,FALSE\n' for x in econ),encoding="utf-8")
if __name__=="__main__":build()
