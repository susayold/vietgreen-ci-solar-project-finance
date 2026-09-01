import csv
from pathlib import Path
ROOT=Path(__file__).parents[1]
def rows(p):
 with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def test_v51_registers_are_scoped():
 assert all(r["source_id"]!="METHOD-V5-FX" for r in rows(ROOT/"evidence/FX_REGISTER.csv"))
 assert all(r["source_id"]!="METHOD-V5-TAX" for r in rows(ROOT/"evidence/TAX_BENCHMARK_REGISTER.csv"))
 assert all(r["comparability_grade"] in {"ASSET_LEVEL_HIGH","PORTFOLIO_LEVEL_MEDIUM","REGIONAL_CONTEXT","GLOBAL_CONTEXT","LOW_COMPARABILITY"} for r in rows(ROOT/"evidence/CAPEX_BENCHMARK_REGISTER.csv"))
