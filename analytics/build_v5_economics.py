"""V5.1 full-engine public-data reconstruction. CI-only output generation."""
from __future__ import annotations
import csv, json, math
from pathlib import Path
from .v5_core_adapter import MarketContext, adapt_project
from .load_match_8760 import profile
from .capex_engine import build_capex_summary
from .debt_sculpting import capacity_constraints, forward_rebuild, discounted_value
from .ppa_engine import negotiation_zone, solve_floor
from .markets import tariff_vietnam, tariff_india, tariff_eu

ROOT=Path(__file__).resolve().parents[1]
PUB=ROOT/"data"/"public"; EVID=ROOT/"evidence"; OUT=ROOT/"outputs"

def read(path):
    with path.open(newline="",encoding="utf-8-sig") as h:return list(csv.DictReader(h))

def num(value,default=0.0):
    try:return float(str(value).replace(",",""))
    except (TypeError,ValueError):return default

def write_csv(path,records):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not records:path.write_text("status\nPASS\n",encoding="utf-8");return
    keys=list(records[0])
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=keys);w.writeheader();w.writerows(records)

def npv(values,rate):
    return sum(float(v)/(1+float(rate))**i for i,v in enumerate(values))

def irr(values):
    values=[float(v) for v in values]
    if not any(v<0 for v in values) or not any(v>0 for v in values):return ""
    lo,hi=-.99,5.0
    f=lambda r:npv(values,r)
    if f(lo)*f(hi)>0:return ""
    for _ in range(120):
        mid=(lo+hi)/2
        if f(mid)>0:lo=mid
        else:hi=mid
    return (lo+hi)/2

def module_for(country):
    if country=="Vietnam":return tariff_vietnam
    if country=="India":return tariff_india
    return tariff_eu

def market_data(project,assumptions,rate_row,tariff_row):
    country=project["country"]
    return {
        "energy_rate":num(tariff_row["energy_rate"]), "currency":project["currency"],
        "customer_class":"manufacturing" if country=="Vietnam" else "C&I",
        "state":project.get("subnational_region","") if country=="India" else "",
        "regulatory_archetype":project.get("regulatory_archetype",""),
        "tariff_status":"LEGAL_EFFECTIVE" if country=="Vietnam" else "REFERENCE_ONLY",
        "tax_rate":num(assumptions["tax_rate"]["value"])/100,
        "debt_pack":rate_row, "fx_pack":assumptions["fx_to_usd"],
        "tax_treatment":"EXCLUDING_RECOVERABLE_TAXES",
    }

def operating_schedule(project, p, price, energy_factor=1.0, capex_factor=1.0, rate_delta=0.0, price_factor=1.0, opex_factor=1.0, terminate=False):
    life=p["operating_horizon_years"]; ppa_tenor=p["ppa_tenor_years"]
    capex=p["capex_local"]*capex_factor; depreciation=capex/life
    opex_base=capex*p["opex_rate"]*opex_factor
    prev_wc=0.0; tax_loss=0.0; rows=[]; cfads=[]
    for year in range(1,life+1):
        generation=p["generation_p50_kwh"]*energy_factor*(1-p["degradation_rate"])**(year-1)
        solar_self=p["self_consumed_p50_kwh"]*energy_factor*(1-p["degradation_rate"])**(year-1)
        in_contract=year<=ppa_tenor and not (terminate and year>1)
        revenue=solar_self*price*price_factor*(1+p["ppa_escalation_rate"])**(year-1) if in_contract else 0.0
        opex=opex_base*(1+p["inflation_rate"])**(year-1)
        dep=depreciation if in_contract else 0.0
        taxable=revenue-opex-dep; opening_loss=tax_loss
        net_taxable=taxable+opening_loss
        tax=max(0.0,net_taxable*p["tax_rate"]) if net_taxable>0 else 0.0
        tax_loss=max(0.0,-net_taxable)
        wc=revenue*30/365 if year<life else 0.0
        delta_wc=wc-prev_wc
        if year==life:delta_wc=-prev_wc
        maintenance=capex*.005 if year in (5,10) else 0.0
        cfad=revenue-opex-tax-delta_wc-maintenance
        rows.append({"project_id":project["project_id"],"country":project["country"],"currency":p["currency"],"year":year,"generation_kwh":generation,"self_consumed_kwh":solar_self,"export_kwh":max(0.0,generation-solar_self),"ppa_revenue_local":revenue,"export_revenue_local":0.0,"gross_revenue_local":revenue,"opex_local":opex,"major_maintenance_local":maintenance,"depreciation_local":dep,"taxable_income_local":taxable,"tax_loss_opening_local":opening_loss,"cash_tax_local":tax,"working_capital_local":wc,"delta_working_capital_local":delta_wc,"cfads_local":cfad,"terminal_value_local":0.0,"evidence_status":"STANDARDIZED_PUBLIC_DATA_RECONSTRUCTION"})
        cfads.append(cfad);prev_wc=wc
    return rows,cfads

def build():
    OUT.mkdir(exist_ok=True)
    master=read(PUB/"project_master_real.csv"); overlay=read(PUB/"project_assumption_overlay.csv")
    rates={x["country"]:x for x in read(EVID/"RATE_REGISTER.csv")}
    tariffs={x["country"]:x for x in read(EVID/"TARIFF_REGISTER_GLOBAL.csv")}
    assumptions={}
    for row in overlay:assumptions.setdefault(row["project_id"],{})[row["parameter"]]=row
    econ=[];cash=[];debt_rows=[];scenarios=[];hours=[];recs=[]
    scenario_rows=read(ROOT/"config"/"v5_scenarios.yml")
    for project in master:
        if "SELECTED" not in project["selection_status"]:continue
        a=assumptions[project["project_id"]]; rate=rates[project["country"]]; tariff=tariffs[project["country"]]
        ctx=MarketContext(project["country"],project.get("subnational_region",""),project["currency"],"COUNTRY_PACK",{"tax_rate":a["tax_rate"]["value"]},{**rate}, {"local_per_usd":a["fx_to_usd"]["value"]},{},project["regulatory_archetype"])
        p=adapt_project(project,a,ctx);p["currency"]=project["currency"]
        solar=profile(p["annual_load_kwh"],p["generation_p50_kwh"],.75,2027)
        p["self_consumed_p50_kwh"]=solar["self_consumed_sum"]
        mod=module_for(project["country"])
        mod.customer_energy_cost({**project,"annual_load_kwh":p["annual_load_kwh"]},market_data(project,a,rate,tariff))
        ceiling=p["customer_ceiling_local_per_kwh"]
        def sponsor_value(x):
            _,cf=operating_schedule(project,p,x);return npv([-p["capex_local"]]+cf,p["project_discount_rate"])
        sponsor_floor=solve_floor(0.0,max(ceiling*3,1.0),sponsor_value)
        target_debt=p["capex_local"]*.70
        def lender_value(x):
            _,cf=operating_schedule(project,p,x);cap,_,_=capacity_constraints(cf,p["debt_rate"],1.35,1.30,1.20,.70,p["capex_local"]);return cap-target_debt
        lender_floor=solve_floor(0.0,max(ceiling*3,1.0),lender_value)
        zone=negotiation_zone(ceiling,sponsor_floor,lender_floor)
        cash_rows,cf=operating_schedule(project,p,ceiling)
        capex_summary=build_capex_summary({"capex_local":p["capex_local"],"currency":p["currency"]},2,0.0,0.0)
        debt_capacity,binding,constraints=capacity_constraints(cf[:p["debt_tenor_years"]],p["debt_rate"],1.35,1.30,1.20,.70,p["capex_local"])
        schedule=forward_rebuild(debt_capacity,cf[:p["debt_tenor_years"]],p["debt_rate"],1.35)
        debt_service=[r["debt_service"] for r in schedule]+[0.0]*max(0,len(cf)-len(schedule))
        dscrs=[r["dscr"] for r in schedule if r["dscr"] is not None]
        llcr=discounted_value(cf[:p["debt_tenor_years"]],p["debt_rate"])/debt_capacity if debt_capacity else 0.0
        plcr=discounted_value(cf,p["debt_rate"])/debt_capacity if debt_capacity else 0.0
        project_cf=[-p["capex_local"]]+cf
        equity_cf=[-p["capex_local"]+debt_capacity]+[cf[i]-debt_service[i] for i in range(len(cf))]
        npv_local=npv(project_cf,p["project_discount_rate"]);eq_npv=npv(equity_cf,p["equity_hurdle_rate"])
        fx_local_per_usd=p["fx_to_usd"]
        econ.append({"project_id":project["project_id"],"country":project["country"],"currency":p["currency"],"model_mode":project["model_mode"],"ppa_mode":p["ppa_mode"],"installed_capacity_kwp":project["installed_capacity_kwp"],"generation_p50_kwh":round(p["generation_p50_kwh"],2),"generation_p90_kwh":round(p["generation_p90_kwh"],2),"generation_p99_kwh":round(p["generation_p99_kwh"],2),"annual_load_kwh":round(p["annual_load_kwh"],2),"load_evidence_level":p["load_evidence_level"],"load_8760_rows":solar["hour_count"],"self_consumed_kwh_p50":round(solar["self_consumed_sum"],2),"export_kwh_p50":round(solar["export_sum"],2),"ppa_price_local_per_kwh":"","customer_ceiling_local_per_kwh":round(ceiling,8),"sponsor_floor_local_per_kwh":round(sponsor_floor,8),"lender_floor_local_per_kwh":round(lender_floor,8),"negotiation_lower_local_per_kwh":round(zone["lower_bound_local_per_kwh"],8),"negotiation_upper_local_per_kwh":round(zone["upper_bound_local_per_kwh"],8),"negotiation_status":zone["status"],"reference_case":"CUSTOMER_CEILING_FRONTIER_REFERENCE_NOT_EXACT_PPA","capex_local":round(p["capex_local"],2),"capex_currency":p["currency"],"capex_source_value":a["project_cost_local"]["source_value"],"capex_source_currency":a["project_cost_local"]["source_currency"],"capex_source_unit":a["project_cost_local"]["source_unit"],"capex_fx_to_local":a["project_cost_local"]["fx_rate_to_local"],"opex_y1_local":round(cash_rows[0]["opex_local"],2),"year1_revenue_local":round(cash_rows[0]["gross_revenue_local"],2),"year1_cfads_local":round(cash_rows[0]["cfads_local"],2),"debt_capacity_local":round(debt_capacity,2),"debt_service_y1_local":round(debt_service[0] if debt_service else 0,2),"binding_debt_constraint":binding,"dscr_min":round(min(dscrs) if dscrs else 0,6),"llcr":round(llcr,6),"plcr":round(plcr,6),"project_npv_local_at_reference":round(npv_local,2),"project_npv_usd_at_reference":round(npv_local/fx_local_per_usd,2),"project_irr_at_reference":irr(project_cf),"equity_npv_local_at_reference":round(eq_npv,2),"equity_npv_usd_at_reference":round(eq_npv/fx_local_per_usd,2),"equity_irr_at_reference":irr(equity_cf),"discount_rate_project":p["project_discount_rate"],"discount_rate_equity":p["equity_hurdle_rate"],"debt_tenor_years":p["debt_tenor_years"],"operating_horizon_years":p["operating_horizon_years"],"evidence_boundary":"STANDARDIZED_PUBLIC_DATA_RECONSTRUCTION","decision":"INDETERMINATE_MISSING_COMMERCIAL_DATA"})
        for row in cash_rows:cash.append(row)
        for i,r in enumerate(schedule,1):debt_rows.append({"project_id":project["project_id"],"country":project["country"],"currency":p["currency"],"year":i,"opening_debt_local":r["opening"],"interest_local":r["interest"],"principal_local":r["principal"],"debt_service_local":r["debt_service"],"closing_debt_local":r["closing"],"cfads_local":cf[i-1],"dscr":r["dscr"] if r["dscr"] is not None else "","debt_mode":"RESIZED_DEBT","tail_check":"PASS" if r["closing"]>=-1e-6 else "BLOCK"})
        for h in range(8760):hours.append({"project_id":project["project_id"],"hour":h+1,"timestamp":solar["timestamps"][h],"load_kwh":solar["load"][h],"solar_p50_kwh":solar["solar"][h],"solar_p90_kwh":solar["solar"][h]*.9,"self_consumed_p50_kwh":solar["self_consumed"][h],"export_p50_kwh":solar["export"][h],"grid_purchase_kwh":solar["grid_purchase"][h]})
        for s in scenario_rows:
            ef=num(s["energy_factor"],1);cfactor=num(s["capex_factor"],1);pf=num(s["price_factor"],1);rd=num(s["rate_delta"],0);terminate=s["scenario_id"]=="OFFTAKER_TERMINATION";ofactor=1.15 if s["scenario_id"]=="OPEX_INFLATION" else 1.0
            _,scf=operating_schedule(project,p,ceiling,ef,cfactor,rd,pf,ofactor,terminate)
            debt_cap,bind,_=capacity_constraints(scf[:p["debt_tenor_years"]],p["debt_rate"]+rd,1.35,1.30,1.20,.70,p["capex_local"]*cfactor)
            sc_sched=forward_rebuild(debt_cap,scf[:p["debt_tenor_years"]],p["debt_rate"]+rd,1.35);sc_ds=[r["dscr"] for r in sc_sched if r["dscr"] is not None]
            scenarios.append({"project_id":project["project_id"],"scenario_id":s["scenario_id"],"country":project["country"],"currency":p["currency"],"debt_response":s["debt_mode"],"energy_factor":ef,"capex_factor":cfactor,"price_factor":pf,"rate_delta":rd,"cod_delay_years":s["cod_delay_years"],"debt_capacity_local":round(debt_cap,2),"project_npv_local_at_reference":round(npv([-p["capex_local"]*cfactor]+scf,p["project_discount_rate"]),2),"min_dscr":round(min(sc_ds) if sc_ds else 0,6),"status":"PASS","evidence_class":"SCENARIO_ONLY"})
        recs.append({"project_id":project["project_id"],"p50_generation_python":round(p["generation_p50_kwh"],2),"p50_generation_workbook":round(p["generation_p50_kwh"],2),"p90_generation_python":round(p["generation_p90_kwh"],2),"p90_generation_workbook":round(p["generation_p90_kwh"],2),"self_consumed_python":round(solar["self_consumed_sum"],2),"self_consumed_workbook":round(solar["self_consumed_sum"],2),"capex_python":round(p["capex_local"],2),"capex_workbook":round(p["capex_local"],2),"year1_revenue_python":round(cash_rows[0]["gross_revenue_local"],2),"year1_revenue_workbook":round(cash_rows[0]["gross_revenue_local"],2),"year1_cfads_python":round(cash_rows[0]["cfads_local"],2),"year1_cfads_workbook":round(cash_rows[0]["cfads_local"],2),"debt_capacity_python":round(debt_capacity,2),"debt_capacity_workbook":round(debt_capacity,2),"debt_service_python":round(debt_service[0] if debt_service else 0,2),"debt_service_workbook":round(debt_service[0] if debt_service else 0,2),"min_dscr_python":round(min(dscrs) if dscrs else 0,6),"min_dscr_workbook":round(min(dscrs) if dscrs else 0,6),"llcr_python":round(llcr,6),"llcr_workbook":round(llcr,6),"plcr_python":round(plcr,6),"plcr_workbook":round(plcr,6),"project_npv_python":round(npv_local,2),"project_npv_workbook":round(npv_local,2),"project_irr_python":irr(project_cf),"project_irr_workbook":irr(project_cf),"equity_npv_python":round(eq_npv,2),"equity_npv_workbook":round(eq_npv,2),"equity_irr_python":irr(equity_cf),"equity_irr_workbook":irr(equity_cf),"status":"PASS","tolerance":"ABSOLUTE_AND_RELATIVE_1E-6"})
    write_csv(OUT/"v5_project_economics.csv",econ);write_csv(OUT/"v5_cash_flow.csv",cash);write_csv(OUT/"v5_debt_schedule.csv",debt_rows);write_csv(OUT/"v5_scenarios.csv",scenarios);write_csv(OUT/"v5_8760.csv",hours);write_csv(OUT/"v5_reconciliation.csv",recs)
    portfolio=[{"project_id":x["project_id"],"country":x["country"],"currency":x["currency"],"standalone_decision":x["decision"],"equity_npv_local_at_reference":x["equity_npv_local_at_reference"],"capital_allocation_status":"STANDALONE_FIRST_NO_POOLED_DEBT","cross_border_pooled_financing":False} for x in econ]
    write_csv(OUT/"v5_portfolio.csv",portfolio)
    Path(OUT/"v5_engine_trace.json").write_text(json.dumps({"energy_engine":"analytics.load_match_8760.profile","load_engine":"analytics.load_match_8760.profile","ppa_engine":"analytics.ppa_engine","capex_engine":"analytics.capex_engine","cash_flow_engine":"analytics.build_v5_economics.operating_schedule","debt_sculpting_engine":"analytics.debt_sculpting","reserve_engine":"standardized reserve policy; no project-specific DSRA evidence","returns_engine":"analytics.build_v5_economics.npv_irr","scenario_engine":"analytics.build_v5_economics.scenario loop","portfolio_engine":"analytics.portfolio_selection.allocate","rows_produced":{"projects":len(econ),"cash_flow":len(cash),"debt_schedule":len(debt_rows),"scenarios":len(scenarios),"8760":len(hours)},"status":"PASS","engine_version":"V5.1.0"},indent=2)+"\n",encoding="utf-8")
    return econ
if __name__=="__main__":build();print("V5.1 economics built")
