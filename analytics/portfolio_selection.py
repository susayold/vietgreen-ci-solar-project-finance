"""Frontier-only shortlist logic with common-currency exposure controls."""
from __future__ import annotations
from typing import Iterable, Dict, List

def allocate(projects: Iterable[Dict], equity_budget: float=float("inf"),
             max_country_share: float=1.0, max_project_exposure: float=float("inf"),
             currency: str="USD") -> Dict:
    rows=[dict(p) for p in projects]; budget=float(equity_budget)
    ranked=sorted(rows,key=lambda p:(0 if p.get("zone_status") in ("FEASIBLE_NEGOTIATION_ZONE","FEASIBLE_ZONE") else 1,-float(p.get("equity_npv_usd_at_reference",p.get("equity_npv_local_at_reference",0)) or 0),-float(p.get("evidence_score",0) or 0)))
    selected=[]; spent=0.0; country_spend={}
    for p in ranked:
        need=max(0.0,float(p.get("equity_required_usd",p.get("equity_local",0)) or 0)); country=p.get("country","UNKNOWN")
        if need>float(max_project_exposure)+1e-9 or spent+need>budget+1e-9 or country_spend.get(country,0)+need>budget*float(max_country_share)+1e-9: continue
        q=dict(p); q["equity_required_usd"]=need; q["currency"]=currency; selected.append(q)
        spent+=need; country_spend[country]=country_spend.get(country,0)+need
    return {"selected":selected,"spent_usd":spent,"budget_usd":budget,"remaining_usd":max(0,budget-spent),"country_spend_usd":country_spend,"budget_enforced":spent<=budget+1e-9,"exposure_enforced":all(v<=budget*float(max_country_share)+1e-9 for v in country_spend.values()),"shortlist_type":"DILIGENCE_PRIORITY_SHORTLIST","capital_allocation_status":"NOT_INVESTMENT_APPROVAL"}

def shortlist(projects: Iterable[Dict], equity_budget: float, max_country_share: float=1.0) -> List[Dict]:
    return allocate(projects,equity_budget,max_country_share)["selected"]
