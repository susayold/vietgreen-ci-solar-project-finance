#!/usr/bin/env python3
"""Validate the generated CV website payload before it can be published."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"website"/"public"/"data"
def load(name): return json.loads((DATA/name).read_text(encoding="utf-8"))
summary=load("summary.json")
expected={"candidateProjects":54,"selectedRecords":20,"economicsReadyProjects":19,"technicalBlockedProjects":1,"observations":441,"countries":7,"developers":5,"economicsReadyCapacityMw":129.853,"readySourceGenerationGwh":148.221,"modeledHourlyRows":166440,"scenarios":171,"workbookSheets":28,"regressionTests":26,"semanticControls":26}
for key,val in expected.items():
    actual=summary.get(key)
    if isinstance(val,float): assert abs(float(actual)-val)<1e-3,(key,actual,val)
    else: assert actual==val,(key,actual,val)
assert summary["modelSha"]=="ff69e15d211ff1abc88200574242ed2f1db49074"
assert summary["ppaMode"]=="FRONTIER_ONLY" and summary["remoteOnly"] is True
projects=load("projects.json")["projects"]
assert len(projects)==20
assert sum(p["economicsStatus"]=="READY_FOR_ECONOMICS" for p in projects)==19
assert sum(p["economicsStatus"]!="READY_FOR_ECONOMICS" for p in projects)==1
physical=load("physical.json")
assert physical["withinBand"]==15 and physical["lowYieldReview"]==4 and physical["extremeBlock"]==1
energy=load("energy.json")
assert len(energy["projects"])==20 and len(energy["featured"]["representativeDay"]["load"])==24
economics=load("economics.json")
assert economics["featured"]["projectId"]=="VN-GY-GOMALL" and economics["featuredFrontier"]["status"]=="EMPTY_NEGOTIATION_ZONE"
debt=load("debt.json")
assert debt["featured"]["minimumDscr"]==1.35 and len(debt["featured"]["schedule"])==15
risk=load("risk.json")
assert len(risk["featured"]["scenarios"])==9 and len(risk["scenarios"])==171
diligence=load("diligence.json")
assert len(diligence["projects"])==19 and diligence["approvedAllocations"]==0 and diligence["equityBudgetUsd"]==0
model=load("model.json")
assert model["workbookSheets"]==28 and model["regressionTests"]==26 and model["semanticControls"]==26
release=load("release.json")
assert release["modelSha"]==summary["modelSha"] and release["websiteSourceSha"]==summary["websiteSourceSha"]
print("CV website data validation PASS: 20 projects / 19 ready / 171 scenarios / exact model SHA")
