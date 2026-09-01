import csv
from pathlib import Path
def test_python_excel_reconciliation_passes():
 rows=list(csv.DictReader(Path("outputs/v5_reconciliation.csv").open(encoding="utf-8-sig")))
 assert len(rows)==20 and all(x["status"]=="PASS" for x in rows)
