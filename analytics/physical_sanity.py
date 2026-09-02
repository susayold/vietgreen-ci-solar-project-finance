"""V5.1.2 generic physical QA and observed-to-base-generation firewall."""
from __future__ import annotations
import csv
from pathlib import Path
from typing import Dict, Iterable, List

LOWER_KWHP=900.0
UPPER_KWHP=1600.0
EXTREME_MULTIPLIER=2.0

def _rows(path: Path) -> List[Dict[str,str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def _num(value):
    try:
        return float(value) if value not in ("", None) else None
    except (TypeError, ValueError):
        return None

def classify_specific_yield(value, lower=LOWER_KWHP, upper=UPPER_KWHP, extreme_multiplier=EXTREME_MULTIPLIER):
    if value is None:
        return "INSUFFICIENT_PHYSICAL_DATA"
    value=float(value)
    if value > float(upper)*float(extreme_multiplier):
        return "EXTREME_OUTLIER_BLOCK_BASE"
    if value < float(lower):
        return "LOW_YIELD_REVIEW"
    if value > float(upper):
        return "HIGH_YIELD_REVIEW"
    return "PASS_WITHIN_SCREENING_BAND"

def _overlay(rows):
    out={}
    for row in rows:
        out.setdefault(row["project_id"],{})[row["parameter"]]=row
    return out

def _overlay_value(a, name, default=""):
    row=a.get(name,{})
    return row.get("normalized_value") or row.get("value") or default

def build_physical_qa(root: str|Path, output_path: str|Path) -> List[Dict[str,str]]:
    root=Path(root); output_path=Path(output_path)
    master=_rows(root/"data/public/project_master_real.csv")
    result=[]
    for project in master:
        if "SELECTED" not in project.get("selection_status",""):
            continue
        cap=_num(project.get("installed_capacity_kwp_observed") or project.get("installed_capacity_kwp"))
        observed=_num(project.get("annual_generation_kwh_observed") or project.get("annual_generation_kwh"))
        yield_value=(observed/cap) if observed is not None and cap not in (None,0) else None
        status=classify_specific_yield(yield_value)
        review=status != "PASS_WITHIN_SCREENING_BAND"
        extreme=status=="EXTREME_OUTLIER_BLOCK_BASE"
        if extreme:
            base=""; origin="MISSING_BLOCKED"; input_status="TECHNICAL_DATA_BLOCKED"
            eligible="FALSE"; notes="Preserved source claim is outside 2x upper screening bound; no defensible replacement is inserted."
        elif yield_value is None:
            base=""; origin="MISSING_BLOCKED"; input_status="TECHNICAL_DATA_BLOCKED"
            eligible="FALSE"; notes="Capacity or annual generation is missing; economics fails closed."
        else:
            base=str(observed); origin="OBSERVED_SOURCE_REPORTED_WITH_REVIEW" if review else "OBSERVED_SOURCE_REPORTED"
            input_status="READY_FOR_ECONOMICS"; eligible="TRUE"; notes="Observed generation retained; physical review status is disclosed."
        result.append({
            "project_id":project["project_id"],"project_name":project["project_name"],"country":project["country"],
            "capacity_kwp":"" if cap is None else str(cap),"observed_generation_kwh":"" if observed is None else str(observed),
            "observed_specific_yield_kwh_kwp":"" if yield_value is None else f"{yield_value:.8f}",
            "screening_lower":str(LOWER_KWHP),"screening_upper":str(UPPER_KWHP),
            "extreme_upper":str(UPPER_KWHP*EXTREME_MULTIPLIER),"physical_status":status,
            "source_claim_preserved":"TRUE" if observed is not None else "FALSE",
            "engineering_review_required":"TRUE" if review else "FALSE",
            "observed_base_case_eligible":eligible,"base_generation_p50_kwh":base,
            "base_generation_origin":origin,"base_generation_source_id":project.get("primary_source_id",""),
            "model_input_status":input_status,"notes":notes
        })
    fields=list(result[0]) if result else []
    output_path.parent.mkdir(parents=True,exist_ok=True)
    with output_path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(result)
    return result

def build_resolved_model_input_view(root: str|Path, physical_rows: Iterable[Dict[str,str]], output_path: str|Path) -> List[Dict[str,str]]:
    root=Path(root); output_path=Path(output_path); master={r["project_id"]:r for r in _rows(root/"data/public/project_master_real.csv")}
    overlays=_overlay(_rows(root/"data/public/project_assumption_overlay.csv")); out=[]
    for qa in physical_rows:
        a=overlays.get(qa["project_id"],{}); p=master[qa["project_id"]]
        capex=float(_overlay_value(a,"project_cost_local",0) or 0)
        opex_pct=float(_overlay_value(a,"opex_percent_of_capex",0) or 0)
        out.append({
            "project_id":qa["project_id"],"country":qa["country"],"currency":p.get("currency",""),
            "capacity_kwp":qa["capacity_kwp"],"observed_generation_kwh":qa["observed_generation_kwh"],
            "observed_specific_yield":qa["observed_specific_yield_kwh_kwp"],"physical_status":qa["physical_status"],
            "base_generation_p50_kwh":qa["base_generation_p50_kwh"],"base_generation_origin":qa["base_generation_origin"],
            "engineering_review_required":qa["engineering_review_required"],
            "annual_load_kwh":_overlay_value(a,"annual_customer_load_kwh",""),
            "load_origin":a.get("annual_customer_load_kwh",{}).get("input_origin","ANALYST_ASSUMPTION"),
            "self_consumption_ratio":_overlay_value(a,"self_consumption_ratio",""),
            "capex_local":str(capex),"opex_local":str(capex*opex_pct/100.0),
            "tax_rate":_overlay_value(a,"tax_rate",""),"debt_rate":_overlay_value(a,"debt_all_in_rate",""),
            "debt_rate_type":"FLOATING_REFERENCE","debt_tenor_years":_overlay_value(a,"debt_tenor_years",""),
            "customer_ceiling":_overlay_value(a,"customer_ceiling_local_per_kwh",""),
            "ppa_mode":_overlay_value(a,"ppa_mode","FRONTIER_ONLY"),
            "input_ready_status":qa["model_input_status"]
        })
    fields=list(out[0]) if out else []
    output_path.parent.mkdir(parents=True,exist_ok=True)
    with output_path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    return out
