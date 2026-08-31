"""Export derived 8,760 profiles to remote workflow artifacts only."""
from __future__ import annotations
import csv,gzip,hashlib
from pathlib import Path
from analytics.load_match_8760 import profile
ROOT=Path(__file__).resolve().parents[1]
PVOUT={"North":1320.0,"Central":1480.0,"South":1420.0}
def projects():
    with (ROOT/"data/synthetic/project_master.csv").open(newline="",encoding="utf-8") as handle: return list(csv.DictReader(handle))
def write_profile(path,records,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(path,"wt",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields); writer.writeheader(); writer.writerows(records)
def main():
    loads,solars=[],[]
    for project in projects():
        p50=float(project["proposed_capacity_kwp"])*PVOUT[project["region"]]
        hourly=profile(float(project["annual_load_kwh"]),p50,float(project["daytime_load_share"]))
        for i,timestamp in enumerate(hourly["timestamps"]):
            loads.append({"project_id":project["project_id"],"timestamp_local":timestamp,"load_kwh":"%.10f"%hourly["load"][i]})
            solars.append({"project_id":project["project_id"],"timestamp_local":timestamp,"solar_kwh_p50":"%.10f"%hourly["solar"][i],"self_consumed_kwh":"%.10f"%hourly["self_consumed"][i],"excess_kwh":"%.10f"%hourly["excess"][i]})
    load_path=ROOT/"remote_derived/load_8760.csv.gz"; solar_path=ROOT/"remote_derived/solar_8760.csv.gz"
    write_profile(load_path,loads,["project_id","timestamp_local","load_kwh"])
    write_profile(solar_path,solars,["project_id","timestamp_local","solar_kwh_p50","self_consumed_kwh","excess_kwh"])
    index=[]
    for path,count in ((load_path,len(loads)),(solar_path,len(solars))):
        index.append({"path":str(path.relative_to(ROOT)).replace("\\","/"),"row_count":count,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"storage":"GitHub Actions artifact","local_storage":"NONE"})
    with (ROOT/"validation/REMOTE_8760_INDEX.csv").open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(index[0])); writer.writeheader(); writer.writerows(index)
if __name__=="__main__": main()
