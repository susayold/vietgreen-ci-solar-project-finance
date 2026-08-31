"""Remote synthetic-input gate and deterministic lineage checks."""
from __future__ import annotations
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_MASTER_SEED=260831

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as handle: return list(csv.DictReader(handle))

def read_seed(path=ROOT/"config/synthetic_seed.yml"):
    values={}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key,value=line.split(":",1); values[key.strip()]=value.strip()
    return values

def validate_input_csv(path=ROOT/"data/synthetic/project_master.csv"):
    rows=read_csv(path)
    if len(rows)!=20: raise ValueError("expected 20 projects")
    ids={row.get("project_id") for row in rows}
    if len(ids)!=20 or None in ids: raise ValueError("project IDs must be unique and populated")
    seed=read_seed()
    if int(seed.get("master_seed",-1))!=EXPECTED_MASTER_SEED: raise ValueError("master seed is not locked")
    if seed.get("public_model_must_not_depend_on_hidden_truth","").lower()!="true":
        raise ValueError("hidden-truth firewall is not enabled")
    for row in rows:
        if float(row["proposed_capacity_kwp"])>float(row["feasible_capacity_kwp"]):
            raise ValueError("proposed capacity exceeds feasible capacity for "+row["project_id"])
        if float(row["p90_y1_kwh"])>float(row["p50_y1_kwh"]):
            raise ValueError("P90 exceeds P50 for "+row["project_id"])
    required={
      "ppa_terms.csv":{"project_id"},"solar_resource.csv":{"project_id","source_id"},
      "debt_terms.csv":{"project_or_portfolio_id"},"capex.csv":{"project_id","source_or_assumption_id"},
      "offtaker_master.csv":{"offtaker_id"},"site_risk.csv":{"site_id","project_id"}}
    for filename,columns in required.items():
        child=ROOT/"data/synthetic"/filename; child_rows=read_csv(child)
        if not child_rows or not columns.issubset(child_rows[0]):
            raise ValueError("missing required columns in "+filename)
    return rows

if __name__=="__main__":
    validate_input_csv(); print("PIPELINE_INPUT_VALID")
