"""Frontier-only shortlist logic with common-currency exposure controls."""
from __future__ import annotations
from typing import Iterable, Dict, List

def allocate(projects: Iterable[Dict], equity_budget: float=float("inf"),
             max_country_share: float=1.0, max_project_exposure: float=float("inf"),
             currency: str="USD", max_developer_share: float=1.0,
             max_offtaker_share: float=1.0, max_currency_share: float=1.0,
             max_industry_share: float=1.0) -> Dict:
    rows=[dict(p) for p in projects]; budget=float(equity_budget)
    ranked=sorted(rows,key=lambda p:(0 if p.get("zone_status") in ("FEASIBLE_NEGOTIATION_ZONE","FEASIBLE_ZONE") else 1,-float(p.get("equity_npv_usd_at_reference",p.get("equity_npv_local_at_reference",0)) or 0),-float(p.get("evidence_score",0) or 0),str(p.get("project_id",""))))
    selected=[]; spent=0.0
    dimensions={
        "country":({},float(max_country_share)),
        "developer":({},float(max_developer_share)),
        "offtaker":({},float(max_offtaker_share)),
        "currency":({},float(max_currency_share)),
        "industry":({},float(max_industry_share)),
    }
    def limit_value(share):
        return budget*share
    for p in ranked:
        need=max(0.0,float(p.get("equity_required_usd",p.get("equity_local",0)) or 0))
        if need>float(max_project_exposure)+1e-9 or spent+need>budget+1e-9:
            continue
        keys={"country":p.get("country","UNKNOWN"),"developer":p.get("developer","UNKNOWN"),
              "offtaker":p.get("offtaker","UNKNOWN"),"currency":p.get("currency",currency),
              "industry":p.get("industry","UNKNOWN")}
        if any(book.get(key,0.0)+need>limit_value(share)+1e-9 for book,share in dimensions.values() for key in [keys[next(name for name,(b,_) in dimensions.items() if b is book)]]):
            continue
        q=dict(p); q["equity_required_usd"]=need; q["currency"]=currency; selected.append(q)
        spent+=need
        for name,(book,_) in dimensions.items():
            book[keys[name]]=book.get(keys[name],0.0)+need
    exposures={name:book for name,(book,_) in dimensions.items()}
    return {"selected":selected,"spent_usd":spent,"budget_usd":budget,"remaining_usd":max(0,budget-spent),
            "exposures_usd":exposures,"country_spend_usd":exposures["country"],
            "budget_enforced":spent<=budget+1e-9,
            "exposure_enforced":all(value<=limit_value(share)+1e-9 for book,share in dimensions.values() for value in book.values()),
            "shortlist_type":"DILIGENCE_PRIORITY_SHORTLIST","capital_allocation_status":"NOT_INVESTMENT_APPROVAL"}

def shortlist(projects: Iterable[Dict], equity_budget: float, max_country_share: float=1.0) -> List[Dict]:
    return allocate(projects,equity_budget,max_country_share)["selected"]
