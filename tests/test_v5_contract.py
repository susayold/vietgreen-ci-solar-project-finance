from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
def read(p):
    with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def test_v5_config_and_candidate_target():
    c=json.loads((ROOT/"config"/"v5_global.yml").read_text())
    assert c["portfolio"]["minimum_projects"]==15 and c["portfolio"]["target_projects"]==20
    assert len(read(ROOT/"research"/"GLOBAL_PROJECT_CANDIDATES.csv"))>=50
def test_sources_and_scoring_are_registered_and_weighted():
    cs=read(ROOT/"research"/"GLOBAL_PROJECT_CANDIDATES.csv"); src={r["source_id"] for r in read(ROOT/"evidence"/"GLOBAL_SOURCE_REGISTER.csv")}; sc=read(ROOT/"research"/"CANDIDATE_SCORING.csv")
    assert {r["candidate_project_id"] for r in cs}=={r["candidate_project_id"] for r in sc}
    ws=[x+"_weight" for x in ["identity","location","developer","offtaker","business_model","installed_capacity","generation","commissioning_status","ppa_existence","ppa_tenor","load_self_consumption","project_cost","financing_amount","financing_structure","official_source_redundancy"]]
    for r in sc:
        assert set(r["candidate_project_id"].split("|")).issubset({r["candidate_project_id"]})
        assert sum(int(r[x] or 0) for x in ws)==int(r["total_score"])
    assert all(set(r["source_ids"].split("|")).issubset(src) for r in cs)
def test_selected_universe_is_frozen_and_constrained():
    rows=read(ROOT/"data"/"public"/"project_master_real.csv");sel=[r for r in rows if "SELECTED" in r["selection_status"]]
    assert len(sel)==20 and all(r["freeze_status"]=="FROZEN" for r in sel)
    counts={}
    for r in sel:counts[r["country"]]=counts.get(r["country"],0)+1
    assert max(counts.values())/len(sel)<=.40
    assert all(r["evidence_grade"] in {"GOLD","STRONG","ACCEPTABLE"} for r in sel)
def test_v5_freeze_and_claim_boundary():
    freeze=json.loads((ROOT/"release"/"V5_INPUT_FREEZE_MANIFEST.json").read_text())
    assert freeze["freeze_status"]=="FROZEN" and freeze["project_count"]==20
    cfg=json.loads((ROOT/"config"/"v5_global.yml").read_text())
    assert cfg["release"]["bankable_transaction_ready"] is False
def test_gate_surface_and_partial_reconstruction():
    s=(ROOT/"analytics"/"build_v5_release.py").read_text()
    assert all(f"G{i}" in s for i in range(10))
    assert "PARTIAL_RECONSTRUCTION" in (ROOT/"analytics"/"v5_model_interface.py").read_text()
