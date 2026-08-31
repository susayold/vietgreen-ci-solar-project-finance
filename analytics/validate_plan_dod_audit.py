"""Validate the 65-item Master Plan V3 DoD audit metadata."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "validation" / "PLAN_DOD_AUDIT.csv"
ALLOWED = {"PASS", "WATCH", "PARTIAL", "PENDING"}
EXPECTED = [f"42.{section}-{item:02d}" for section, count in ((1,6),(2,5),(3,8),(4,8),(5,8),(6,6),(7,6),(8,8),(9,10)) for item in range(1,count+1)]

def main() -> int:
    with AUDIT.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    ids = [row["dod_id"] for row in rows]
    assert ids == EXPECTED, {"row_count": len(rows), "first_missing_or_extra": [x for x in ids if x not in EXPECTED][:5]}
    assert all(row["status"] in ALLOWED for row in rows)
    missing = []
    for row in rows:
        for ref in row["evidence"].split(";"):
            path = ROOT / ref.strip()
            if not path.exists():
                missing.append((row["dod_id"], str(path)))
    assert not missing, missing
    by_id = {row["dod_id"]: row for row in rows}
    assert by_id["42.8-05"]["status"] == "PARTIAL"
    assert by_id["42.9-09"]["status"] == "PARTIAL"
    assert by_id["42.9-10"]["status"] == "PENDING"
    assert all(by_id[f"42.9-{i:02d}"]["status"] == "PASS" for i in range(1,9))
    summary = {status: sum(row["status"] == status for row in rows) for status in sorted(ALLOWED)}
    print({"rows": len(rows), "status_counts": summary, "evidence_paths_checked": sum(len(row["evidence"].split(";")) for row in rows)})
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
