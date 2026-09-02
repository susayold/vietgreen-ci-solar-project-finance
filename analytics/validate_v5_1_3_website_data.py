"""Validate the generated V5.1.3 website data contract."""
import json
from pathlib import Path
D=Path(__file__).resolve().parents[1]/"website"/"data"
def j(n): return json.loads((D/n).read_text(encoding="utf-8"))
def main():
 s=j("shared-summary.json"); assert s["candidateCount"]==54; assert s["selectedCount"]==20; assert s["economicsReadyCount"]==19; assert s["observationCount"]==441; assert s["scenarioRows"]==171
 assert s["modelSourceSha"]=="ff69e15d211ff1abc88200500574242ed2f1db49074"; assert s["ppaMode"]=="FRONTIER_ONLY"; assert s["remoteOnly"] is True
 assert len(j("case.json")["projects"])==20; assert len(j("economics.json")["projects"])==19; assert len(j("risk.json")["scenarios"])==171
 assert j("economics.json")["blockedProject"]["status"]=="TECHNICAL_DATA_BLOCKED"
 assert j("portfolio.json")["allocatedCount"]==0 and j("portfolio.json")["capitalAllocationStatus"]=="DISABLED_FRONTIER_ONLY"
 assert j("release-meta.json")["modelDevelopmentFreeze"] is True
 print("website data contract PASS")
if __name__=="__main__": main()
