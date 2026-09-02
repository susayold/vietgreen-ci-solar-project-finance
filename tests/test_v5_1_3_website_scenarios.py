import json
from pathlib import Path
D=Path(__file__).parents[1]/"website/data"
def test_all_scenarios_present():
 rows=json.loads((D/"risk.json").read_text())["scenarios"]; assert len(rows)==171
def test_no_new_debt_policy_is_visible():
 rows=json.loads((D/"risk.json").read_text())["scenarios"]
 modes=[x for x in rows if x["debtMode"]=="NO_NEW_DEBT"]
 assert modes and all(x["additionalDebt"] in (0,0.0,None) for x in modes)
