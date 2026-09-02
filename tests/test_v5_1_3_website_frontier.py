import json
from pathlib import Path
D=Path(__file__).parents[1]/"website/data"
def test_frontier_is_not_actual_ppa():
 d=json.loads((D/"frontier.json").read_text())
 assert d["referenceCase"]=="REFERENCE_CASE_NOT_ACTUAL_PPA"
 assert all(x["referenceCase"]=="REFERENCE_CASE_NOT_ACTUAL_PPA" for x in d["projects"])
