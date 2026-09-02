import json
from pathlib import Path
D=Path(__file__).parents[1]/"website/data"
def j(n): return json.loads((D/n).read_text())
def test_claim_boundary():
 s=j("shared-summary.json"); r=j("release-meta.json")
 assert s["ppaMode"]=="FRONTIER_ONLY"; assert s["transactionEvidenceStatus"]=="OPEN"
 assert s["bankableTransactionReady"] is False; assert s["capitalAllocationStatus"]=="DISABLED_FRONTIER_ONLY"
 assert r["modelDevelopmentFreeze"] is True
def test_blocked_physical_project_is_separate():
 b=j("economics.json")["blockedProject"]; assert b["status"]=="TECHNICAL_DATA_BLOCKED"
