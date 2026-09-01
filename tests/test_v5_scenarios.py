import csv
from pathlib import Path
def test_scenario_library_complete_after_build():
 p=Path("outputs/v5_scenarios.csv")
 assert p.exists()
 rows=list(csv.DictReader(p.open(encoding="utf-8-sig")))
 required={"BASE","P90_ENERGY","CAPEX_OVERRUN","INTEREST_RATE_SHOCK","COD_DELAY","OPEX_INFLATION","OFFTAKER_NONPAYMENT","OFFTAKER_TERMINATION","COMBINED_DOWNSIDE"}
 assert required.issubset({x["scenario_id"] for x in rows})
 assert all(x["debt_response"] in {"FIXED_DEBT_SCHEDULE","RESIZED_DEBT","NO_NEW_DEBT"} for x in rows)
