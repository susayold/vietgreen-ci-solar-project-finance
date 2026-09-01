import csv
from pathlib import Path
def test_portfolio_is_standalone_first():
 rows=list(csv.DictReader(Path("outputs/v5_portfolio.csv").open(encoding="utf-8-sig")))
 assert rows and all(x["cross_border_pooled_financing"]=="False" for x in rows)
 assert all(x["standalone_decision"]=="INDETERMINATE_MISSING_COMMERCIAL_DATA" for x in rows)
