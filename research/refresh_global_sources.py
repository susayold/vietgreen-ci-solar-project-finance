"""Metadata-only source refresh; never stores raw pages or source snapshots."""
from __future__ import annotations

import csv
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "evidence" / "GLOBAL_SOURCE_REGISTER.csv"
OUTPUT = ROOT / "artifacts" / "GLOBAL_SOURCE_REFRESH.csv"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with REGISTER.open(newline="", encoding="utf-8-sig") as handle:
        sources = list(csv.DictReader(handle))
    fields = ["source_id", "source_url", "checked_at_utc", "http_status", "content_saved", "raw_snapshot_path", "note"]
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sources:
            status = "ERROR"
            note = ""
            try:
                request = urllib.request.Request(row["source_url"], method="HEAD", headers={"User-Agent": "vietgreen-v5-metadata-refresh/1.0"})
                with urllib.request.urlopen(request, timeout=20) as response:
                    status = str(response.status)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                note = type(exc).__name__
            writer.writerow({
                "source_id": row["source_id"],
                "source_url": row["source_url"],
                "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "http_status": status,
                "content_saved": "FALSE",
                "raw_snapshot_path": "",
                "note": note,
            })
    print(f"checked={len(sources)} raw_snapshot=FALSE output={OUTPUT}")


if __name__ == "__main__":
    main()
