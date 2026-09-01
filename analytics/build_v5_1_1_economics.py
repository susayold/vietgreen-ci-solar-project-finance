"""V5.1.1 economics engine: observed facts, explicit overlay assumptions, and auditable PF outputs."""
from __future__ import annotations
import csv, json, math
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from .load_match_8760 import profile
from .debt_sculpting import capacity_constraints, forward_rebuild, discounted_value
from .tax_engine_v5 import apply_tax_loss, validate_tax_row
from .scenario_engine_v5 import apply_inputs, semantics

def _read_csv(path: Path) -> List[Dict[str,str]]:
    with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

def _write_csv(path: Path, rows: Iterable[Dict]) -> None:
    rows=list(rows); path.parent.mkdir(parents=True, exist_ok=True)
    fields=list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def _num(x, default=0.0):
    try: return float(x) if x not in ("",None) else float(default)
    except (TypeError,ValueError): return float(default)

def _rate(x, default=0.0):
    v=_num(x,default); return v/100.0 if abs(v)>1.0 else v

def _npv(values, rate):
    return sum(float(v)/(1+float(rate))**i for i,v in enumerate(values))

def _irr(values):
    if not values or not (any(v>0 for v in values) and any(v<0 for v in values)): return ""
    lo,hi=-.99,10.0
    for _ in range(100):
        mid=(lo+hi)/2; val=_npv(values,mid)
        if val>0: lo=mid
        else: hi=mid
    return (lo+hi)/2

def _assumptions(rows):
    out={}
    for r in rows: out.setdefault(r["project_id"],{})[r["parameter"]]=r
    return out

def _v(a, name, default=0.0):
    row=a.get(name,{})
    return _num(row.get("normalized_value") or row.get("value"), default)

def _solve_floor(fn, ceiling):
    hi=max(float(ceiling)*5.0, 1.0); f0=float(fn(0.0)); f1=float(fn(hi))
    if f0>=0: return 0.0, {"status":"SOLVED_AT_ZERO","residual":f0,"iterations":0,"bracket_high":hi}
    if f1<0: return "", {"status":"INSUFFICIENT_DATA","residual":f1,"iterations":0,"bracket_high":hi}
    lo=0.0; iterations=0
    for iterations in range(1,81):
        mid=(lo+hi)/2; fm=float(fn(mid))
        if fm>=0: hi=mid
        else: lo=mid
    value=(lo+hi)/2
    return value, {"status":"SOLVED","residual":float(fn(value)),"iterations":iterations,"bracket_high":hi}

def _project_inputs(project, a):
    cap=_num(project.get("installed_capacity_kwp_observed") or project.get("installed_capacity_kwp"))
    gen=_v(a,"annual_generation_kwh",_num(project.get("annual_generation_kwh_observed") or project.get("annual_generation_kwh")))
    ratio=_v(a,"self_consumption_ratio",.85)
    load=_v(a,"annual_customer_load_kwh",gen/max(ratio,.01))
    return {
        "project_id":project["project_id"], "country":project["country"], "currency":project.get("currency",""),
        "capacity_kwp":cap, "generation_p50_kwh":gen, "annual_load_kwh":load,
        "self_consumption_ratio":ratio, "capex_local":_v(a,"project_cost_local",cap*1000),
        "operating_horizon_years":int(_v(a,"operating_horizon_years",25)),
        "ppa_tenor_years":int(_v(a,"ppa_tenor_years",20)), "debt_tenor_years":int(_v(a,"debt_tenor_years",15)),
        "tax_rate":_rate(_v(a,"tax_rate",20)), "debt_rate":_rate(_v(a,"debt_all_in_rate",8)),
        "opex_rate":_rate(_v(a,"opex_percent_of_capex",1.5)),
        "customer_ceiling":_v(a,"customer_ceiling_local_per_kwh",0),
        "fx_to_usd":_v(a,"fx_to_usd",1), "project_discount_rate":_rate(_v(a,"project_discount_rate",10)),
        "equity_hurdle_rate":_rate(_v(a,"equity_hurdle_rate",14)),
        "customer_discount_rate":_rate(_v(a,"customer_discount_rate",8)),
        "llcr_discount_rate":_rate(_v(a,"llcr_discount_rate",8)),
        "plcr_discount_rate":_rate(_v(a,"plcr_discount_rate",8)),
        "inflation_rate":_rate(_v(a,"inflation_rate",2)), "degradation_rate":_rate(_v(a,"degradation",.5)),
        "ppa_mode":str(a.get("ppa_mode",{}).get("value") or "FRONTIER_ONLY"),
        "load_evidence_level":str(a.get("load_evidence_level",{}).get("value") or "LEVEL_4_NOT_DISCLOSED"),
        "debt_rate_type":"FLOATING_REFERENCE", "debt_sculpting_dscr":1.35,
        "leverage_cap":.70, "llcr_min":1.30, "plcr_min":1.20,
    }

def operating_schedule(p: Dict, price: float, scenario: Dict|None=None) -> Tuple[List[Dict],List[float]]:
    s=scenario or {}; delay=int(s.get("cod_delay_years",0)); life=p["operating_horizon_years"]
    energy=float(s.get("energy_factor",1)); capex_factor=float(s.get("capex_factor",1))
    opex_factor=float(s.get("opex_factor",1)); haircut=float(s.get("collection_haircut",1))
    term=s.get("termination_year"); rate=p["tax_rate"]; loss=0.0; rows=[]; cfads=[]
    total_years=life+delay
    for year in range(1,total_years+1):
        op_year=year-delay
        active=op_year>=1 and op_year<=life and not (term not in (None,"") and op_year>=int(term))
        gen=p["generation_p50_kwh"]*energy*((1-p["degradation_rate"])**max(op_year-1,0)) if active else 0.0
        revenue=gen*float(price)*haircut
        opex=p["capex_local"]*capex_factor*p["opex_rate"]*(1+p["inflation_rate"])**max(op_year-1,0)*opex_factor if active else 0.0
        dep=p["capex_local"]*capex_factor/life if active else 0.0
        tax_row=apply_tax_loss(revenue-opex-dep,loss,rate); validate_tax_row(tax_row); loss=tax_row["closing_loss"]
        cfads_value=revenue-opex-tax_row["tax"]
        rows.append({"year":year,"operating_year":op_year if active else 0,"cod_delay_years":delay,
          "active":str(bool(active)).upper(),"generation_kwh":gen,"gross_revenue_local":revenue,
          "opex_local":opex,"depreciation_local":dep,"pre_loss_taxable_income":tax_row["pre_loss_taxable_income"],
          "opening_tax_loss":tax_row["opening_loss"],"loss_used":tax_row["loss_used"],"tax_local":tax_row["tax"],
          "closing_tax_loss":tax_row["closing_loss"],"cfads_local":cfads_value,"collection_haircut":haircut,
          "capex_local":p["capex_local"]*capex_factor if year==1 else 0.0})
        cfads.append(cfads_value)
    return rows,cfads

def _debt_metrics(p, cfads):
    loan=cfads[:p["debt_tenor_years"]]; project=cfads
    debt,binding,constraints=capacity_constraints(loan,p["debt_rate"],p["debt_sculpting_dscr"],p["llcr_min"],p["plcr_min"],p["leverage_cap"],p["capex_local"],project_life_cfads=project)
    sched=forward_rebuild(debt,loan,p["debt_rate"],p["debt_sculpting_dscr"])
    dscr=[x["dscr"] for x in sched if x["dscr"] is not None]
    llcr=discounted_value(loan,p["llcr_discount_rate"])/debt if debt else 0.0
    plcr=discounted_value(project,p["plcr_discount_rate"])/debt if debt else 0.0
    return debt,binding,constraints,sched,min(dscr) if dscr else 0.0,llcr,plcr

def run(root: str|Path, output_dir: str|Path) -> Dict[str,List[Dict]]:
    root=Path(root); out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    projects=_read_csv(root/"data/public/project_master_real.csv"); overlays=_assumptions(_read_csv(root/"data/public/project_assumption_overlay.csv"))
    econ=[]; cash=[]; debt_rows=[]; scenario_rows=[]; input_view=[]; hourly=[]
    scenario_ids=["BASE","P90_ENERGY","CAPEX_OVERRUN","INTEREST_RATE_SHOCK","COD_DELAY","OPEX_INFLATION","OFFTAKER_NONPAYMENT","OFFTAKER_TERMINATION","COMBINED_DOWNSIDE"]
    for project in projects:
        if "SELECTED" not in project.get("selection_status",""): continue
        p=_project_inputs(project,overlays[project["project_id"]])
        solar=profile(p["annual_load_kwh"],p["generation_p50_kwh"],.75,2027)
        for h,(ts,load_kwh,solar_kwh,self_kwh,export_kwh) in enumerate(zip(solar["timestamps"],solar["load"],solar["solar"],solar["self_consumed"],solar["export"])):
            hourly.append({"project_id":project["project_id"],"timestamp":ts,"load_kwh":load_kwh,"solar_kwh":solar_kwh,"self_consumed_kwh":self_kwh,"export_kwh":export_kwh,"profile_year":solar["profile_year"]})
        ref=p["customer_ceiling"]; base_rows,base_cf=operating_schedule(p,ref)
        debt,binding,constraints,sched,dscr,llcr,plcr=_debt_metrics(p,base_cf)
        debt_service=[x["debt_service"] for x in sched]+[0.0]*max(0,len(base_cf)-len(sched))
        project_cf=[-p["capex_local"]]+base_cf
        equity_cf=[-p["capex_local"]+debt]+[base_cf[i]-debt_service[i] for i in range(len(base_cf))]
        sponsor_debt=debt
        def sponsor_fn(x):
            rows,cf=operating_schedule(p,x)
            service=[z["debt_service"] for z in forward_rebuild(sponsor_debt,cf[:p["debt_tenor_years"]],p["debt_rate"],p["debt_sculpting_dscr"])]
            service += [0.0]*max(0,len(cf)-len(service))
            return _npv([-p["capex_local"]+sponsor_debt]+[cf[i]-service[i] for i in range(len(cf))],p["equity_hurdle_rate"])
        sponsor_floor,sponsor_diag=_solve_floor(sponsor_fn,ref)
        target_debt=p["capex_local"]*p["leverage_cap"]
        def lender_fn(x):
            _,cf=operating_schedule(p,x)
            return _debt_metrics(p,cf)[0]-target_debt
        lender_floor,lender_diag=_solve_floor(lender_fn,ref)
        lower=max([v for v in (sponsor_floor,lender_floor) if v!=""] or [0.0]); upper=ref
        if sponsor_floor!="" and lender_floor!="":
            zone_status="FEASIBLE_NEGOTIATION_ZONE" if lower<=upper+1e-9 else "EMPTY_NEGOTIATION_ZONE"
        else:
            zone_status="INSUFFICIENT_DATA"
        row={"project_id":project["project_id"],"project_name":project["project_name"],"country":project["country"],"currency":p["currency"],
          "input_origin":"OBSERVED_FACTS_PLUS_EXPLICIT_OVERLAY","installed_capacity_kwp_observed":project.get("installed_capacity_kwp_observed",""),
          "generation_p50_kwh_observed":project.get("annual_generation_kwh_observed",""),"generation_p50_kwh_modeled":p["generation_p50_kwh"],
          "specific_yield_observed":_num(project.get("annual_generation_kwh_observed"))/p["capacity_kwp"] if p["capacity_kwp"] else "",
          "annual_load_kwh_modeled":p["annual_load_kwh"],"load_evidence_level":p["load_evidence_level"],"load_8760_rows":solar["hour_count"],
          "self_consumed_kwh_p50":solar["self_consumed_sum"],"export_kwh_p50":solar["export_sum"],"ppa_price_local_per_kwh":"",
          "customer_ceiling_local_per_kwh":ref,"sponsor_floor_local_per_kwh":sponsor_floor,"lender_floor_local_per_kwh":lender_floor,
          "negotiation_lower_local_per_kwh":lower,"negotiation_upper_local_per_kwh":upper,"negotiation_status":zone_status,
          "reference_case":"REFERENCE_CASE_NOT_ACTUAL_PPA","decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA",
          "capex_local":p["capex_local"],"capex_currency":p["currency"],"fx_local_per_usd":p["fx_to_usd"],
          "capex_usd":p["capex_local"]/p["fx_to_usd"] if p["fx_to_usd"] else "",
          "debt_capacity_local":debt,"debt_capacity_usd":debt/p["fx_to_usd"] if p["fx_to_usd"] else "",
          "debt_service_y1_local":debt_service[0] if debt_service else 0,"binding_debt_constraint":binding,
          "dscr_min":dscr,"llcr_loan_life":llcr,"plcr_project_life":plcr,
          "project_npv_local_at_reference":_npv(project_cf,p["project_discount_rate"]),"project_npv_usd_at_reference":_npv(project_cf,p["project_discount_rate"])/p["fx_to_usd"] if p["fx_to_usd"] else "",
          "project_irr_at_reference":_irr(project_cf),"equity_npv_local_at_reference":_npv(equity_cf,p["equity_hurdle_rate"]),
          "equity_npv_usd_at_reference":_npv(equity_cf,p["equity_hurdle_rate"])/p["fx_to_usd"] if p["fx_to_usd"] else "",
          "equity_irr_at_reference":_irr(equity_cf),"sponsor_target_metric":"LEVERAGED_EQUITY_NPV_AT_EQUITY_HURDLE",
          "lender_target_metric":"MINIMUM_TARIFF_SUPPORTING_TARGET_STANDARDIZED_LEVERAGE","lender_target_leverage":p["leverage_cap"],
          "sponsor_solver_status":sponsor_diag["status"],"sponsor_solver_residual":sponsor_diag["residual"],
          "lender_solver_status":lender_diag["status"],"lender_solver_residual":lender_diag["residual"],
          "debt_rate_type":p["debt_rate_type"],"ppa_mode":p["ppa_mode"],"evidence_boundary":"STANDARDIZED_PUBLIC_DATA_RECONSTRUCTION",
          "capital_allocation_status":"NOT_INVESTMENT_APPROVAL","shortlist_type":"DILIGENCE_PRIORITY_SHORTLIST"}
        econ.append({k:round(v,8) if isinstance(v,float) else v for k,v in row.items()})
        for cr in base_rows: cr.update({"project_id":project["project_id"],"currency":p["currency"]}); cash.append(cr)
        for i,z in enumerate(sched,1): debt_rows.append({"project_id":project["project_id"],"year":i,**z})
        for sid in scenario_ids:
            sp=apply_inputs(p,{"scenario_id":sid}); srows,scf=operating_schedule(p,ref,sp)
            mode=sp["debt_mode"]; rate=p["debt_rate"]+(sp["rate_delta"] if p["debt_rate_type"]=="FLOATING_REFERENCE" else 0.0)
            if mode=="RESIZED_DEBT":
                sp2=dict(p); sp2["debt_rate"]=rate; debt_s,bind_s,con_s,sch_s,ds_s,ll_s,pl_s=_debt_metrics(sp2,scf)
            else:
                debt_s=debt; sch_s=forward_rebuild(debt,scf[:p["debt_tenor_years"]],rate,p["debt_sculpting_dscr"])
                bind_s=binding; ds_s=min([x["dscr"] for x in sch_s if x["dscr"] is not None] or [0.0])
                ll_s=discounted_value(scf[:p["debt_tenor_years"]],rate)/debt if debt else 0; pl_s=discounted_value(scf,rate)/debt if debt else 0
            scenario_rows.append({"project_id":project["project_id"],"scenario_id":sid,"debt_mode":mode,"rate_response":sp["rate_delta"],
              "cod_delay_years":sp["cod_delay_years"],"energy_factor":sp["energy_factor"],"capex_factor":sp["capex_factor"],
              "opex_factor":sp["opex_factor"],"collection_haircut":sp["collection_haircut"],"termination_year":sp["termination_year"],
              "year_1_revenue_local":srows[0]["gross_revenue_local"],"first_operating_year":next((x["year"] for x in srows if x["active"]=="TRUE"),""),
              "debt_capacity_local":debt_s,"debt_capacity_change_local":debt_s-debt,"binding_constraint":bind_s,
              "dscr_min":ds_s,"llcr_loan_life":ll_s,"plcr_project_life":pl_s,
              "no_new_debt_increase":str(mode=="NO_NEW_DEBT" and debt_s<=debt+1e-8).upper(),
              "base_debt_schedule_preserved":str(mode=="FIXED_DEBT_SCHEDULE").upper(),
              "reference_case":"SCENARIO_REFERENCE_NOT_ACTUAL_PPA"})
        input_view.append({"project_id":project["project_id"],"country":project["country"],"observed_capacity_kwp":project.get("installed_capacity_kwp_observed",""),
          "observed_generation_kwh":project.get("annual_generation_kwh_observed",""),"observed_source_id":project.get("primary_source_id",""),
          "overlay_generation_input":p["generation_p50_kwh"],"overlay_self_consumption_ratio":p["self_consumption_ratio"],
          "overlay_annual_load_kwh":p["annual_load_kwh"],"overlay_project_cost_local":p["capex_local"],
          "overlay_evidence_classes":"EXPLICIT_OVERLAY_PER_PARAMETER","input_view_status":"READY_FOR_REVIEW"})
    _write_csv(out/"v5_1_1_economics_summary.csv",econ); _write_csv(out/"v5_1_1_cash_flow.csv",cash); _write_csv(out/"v5_1_1_debt_schedule.csv",debt_rows)
    _write_csv(out/"v5_1_1_scenario_results.csv",scenario_rows); _write_csv(out/"v5_1_1_model_input_view.csv",input_view)
    return {"economics":econ,"cash_flow":cash,"debt_schedule":debt_rows,"scenarios":scenario_rows,"model_input_view":input_view,"hourly":hourly}

if __name__=="__main__":
    root=Path(__file__).resolve().parents[1]
    run(root,root/"artifacts/v5_1_1_model")
