import json
from pathlib import Path
D=Path(__file__).parents[1]/"website/data"
def read(n): return json.loads((D/n).read_text())
def test_route_payloads_exist():
 for n in ["overview","case","economics","debt","portfolio","risk","model","evidence","frontier","scenarios","projects","release-meta","shared-summary"]:
  assert (D/(n+".json")).exists()
def test_shared_identity():
 s=read("shared-summary.json")
 assert (s["candidateCount"],s["selectedCount"],s["economicsReadyCount"],s["observationCount"],s["scenarioRows"])==(54,20,19,441,171)
 assert s["modelSourceSha"]=="ff69e15d211ff1abc88200500574242ed2f1db49074"
