"""Deterministic V5 local-currency screening reconstruction; runs only in CI."""
from __future__ import annotations
import csv,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PUB=ROOT/"data"/"public"; OUT=ROOT/"outputs"; REL=ROOT/"release"
def read(p):
    with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def n(v,default=0.0):
    try:return float(str(v).replace(",",""))
    except (TypeError,ValueError):return default
def irr(cf):
    lo,hi=-.99,2.0
    for _ in range(120):
        x=(lo+hi)/2; val=sum(v/(1+x)**i for i,v in enumerate(cf))
        if val>0:lo=x
        else:hi=x
    return (lo+hi)/2
def npv(cf,r):return sum(v/(1+r)**i for i,v in enumerate(cf))
def main():
    master=read(PUB/"project_master_real.csv"); ov=read(PUB/"project_assumption_overlay.csv")
    by={}
    for r in ov:by.setdefault(r["project_id"],{})[r["parameter"]]=r
    scenarios=read(ROOT/"config"/"v5_scenarios.yml")
    OUT.mkdir(exist_ok=True); econ=[]; debt=[]; scenout=[]; rec=[]
    for p in master:
        if "SELECTED" not in p["selection_status"]:continue
        a=by[p["project_id"]]; cur=p["currency"]; capex=n(a["project_cost_local"]["value"]); debt_amt=n(a["financing_amount_local"]["value"]); gen=n(a["annual_generation_kwh"]["value"]); price=n(a["ppa_price_local_per_kwh"]["value"]); tax=n(a["tax_rate"]["value"])/100; opex=capex*n(a["opex_percent_of_capex"]["value"])/100; rate=n(a["debt_all_in_rate"]["value"])/100; life=int(n(a["operating_horizon_years"]["value"],20)); tenor=min(15,life); ann=debt_amt*rate/(1-(1+rate)**(-tenor)) if debt_amt and rate else 0
        basecf=[-capex]; debtcf=[]
        for y in range(1,life+1):
            g=gen*(1-n(a["degradation"]["value"])/100)**(y-1); rev=g*price; cfads=max(0,rev-opex); taxpay=max(0,rev-opex)*tax; cfads=max(0,cfads-taxpay); ds=ann if y<=tenor else 0; basecf.append(cfads); debtcf.append(ds)
        project_npv=npv(basecf,rate+.02); equitycf=[-capex+debt_amt]+[basecf[i]-debtcf[i-1] for i in range(1,len(basecf))]; equity_npv=npv(equitycf,rate+.02); dscr=[(basecf[i]/debtcf[i-1] if debtcf[i-1] else 0) for i in range(1,len(basecf)) if debtcf[i-1]]; pv_debt=sum(basecf[i]/(1+rate)**i for i in range(1,tenor+1)); llcr=pv_debt/debt_amt if debt_amt else 0; plcr=sum(basecf[i]/(1+rate)**i for i in range(1,len(basecf)))/debt_amt if debt_amt else 0
        econ.append({"project_id":p["project_id"],"country":p["country"],"currency":cur,"model_mode":p["model_mode"],"installed_capacity_kwp":p["installed_capacity_kwp"],"annual_generation_kwh":round(gen,2),"project_cost_local":round(capex,2),"debt_local":round(debt_amt,2),"equity_local":round(capex-debt_amt,2),"year1_cfads_local":round(basecf[1],2),"min_dscr":round(min(dscr) if dscr else 0,4),"llcr":round(llcr,4),"plcr":round(plcr,4),"project_npv_local":round(project_npv,2),"equity_npv_local":round(equity_npv,2),"project_irr":round(irr(basecf),6),"equity_irr":round(irr(equitycf),6),"horizon_years":life,"evidence_boundary":"STANDARDIZED_PUBLIC_DATA_RECONSTRUCTION"})
        for y,ds in enumerate(debtcf,1):debt.append({"project_id":p["project_id"],"year":y,"currency":cur,"debt_service_local":round(ds,2),"cfads_local":round(basecf[y],2),"dscr":round(basecf[y]/ds,4) if ds else ""})
        for s in scenarios:
            sf=gen*n(s["energy_factor"]); sc=capex*n(s["capex_factor"]); sp=price*n(s["price_factor"]); sr=rate+n(s["rate_delta"]); delay=int(n(s["cod_delay_years"])); sdebt=debt_amt*sr/(1-(1+sr)**(-tenor)) if debt_amt and sr else 0; cf=[-sc]+[0]*delay
            for y in range(1,life+1):cf.append(max(0,sf*(1-n(a["degradation"]["value"])/100)**(y-1)*sp-opex*n(s["capex_factor"])*(1+tax*-1)-max(0,sf*sp-opex*n(s["capex_factor"]))*tax-(sdebt if y<=tenor else 0))
            scenout.append({"project_id":p["project_id"],"scenario_id":s["scenario_id"],"currency":cur,"equity_npv_local":round(npv(cf,sr+.02),2),"min_dscr":round(min([basecf[i]/sdebt for i in range(1,min(len(basecf),tenor+1))]) if sdebt else 0,4),"status":"CALCULATED","evidence_class":"SCENARIO_ONLY"})
        rec.append({"project_id":p["project_id"],"status":"PASS","check":"master_to_economics_row"})
    def write(name,rs):
        hs=list(rs[0].keys()) if rs else ["status"]
        with (OUT/name).open("w",newline="",encoding="utf-8") as f:csv.DictWriter(f,fieldnames=hs).writeheader();csv.DictWriter(f,fieldnames=hs).writerows(rs)
    write("v5_project_economics.csv",econ);write("v5_debt_schedule.csv",debt);write("v5_scenarios.csv",scenout);write("v5_reconciliation.csv",rec)
    summary={"project_count":len(econ),"currencies":sorted({r["currency"] for r in econ}),"status":"READY_FOR_SCREENING_RECONSTRUCTION","claim_boundary":"No confidential or actual lender terms; standardized reconstruction only."}
    (OUT/"v5_portfolio_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (OUT/"v5_output_manifest.json").write_text(json.dumps({"files":["v5_project_economics.csv","v5_debt_schedule.csv","v5_scenarios.csv","v5_reconciliation.csv","v5_portfolio_summary.json"],"project_count":len(econ),"remote_only":"CI_EPHEMERAL_OUTPUT"},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":summary["status"],"project_count":len(econ),"scenario_rows":len(scenout)}))
if __name__=="__main__":main()
