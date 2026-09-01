import csv
from pathlib import Path
ROOT=Path(__file__).parents[1]
def rows(p):
 with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def test_candidate_master_reconcile():
 s={x["candidate_project_id"]:x for x in rows(ROOT/"research/CANDIDATE_SCORING.csv")}
 m=[x for x in rows(ROOT/"data/public/project_master_real.csv") if "SELECTED" in x["selection_status"]]
 assert len(m)==20
 assert all(float(x["coverage_score"])>=65 and x["evidence_grade"]==s[x["candidate_project_id"]]["candidate_coverage_grade"] for x in m)
 assert sum(x["evidence_grade"] in {"GOLD","STRONG"} for x in m)/20>=.7
 assert not any(x["evidence_grade"]=="EXCLUDE" for x in m)
