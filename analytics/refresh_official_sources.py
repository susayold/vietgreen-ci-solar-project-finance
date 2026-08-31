"""Remote official-source live check.

The runner reads response bodies only in memory. It writes metadata (status,
content type, byte count and SHA-256) but never stores a raw source snapshot.
"""
from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "SOURCE_REFRESH_MANIFEST.csv"
REGISTER = ROOT / "evidence" / "SOURCE_REGISTER.csv"
OUTPUT = ROOT / "evidence" / "REMOTE_SOURCE_LIVE_CHECK.csv"
MAX_BYTES = 12_000_000


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def registered_ids() -> set[str]:
    with REGISTER.open(newline="", encoding="utf-8") as handle:
        return {row["source_id"] for row in csv.DictReader(handle)}


def fetch(row: dict[str, str]) -> dict[str, str]:
    checked_at = utc_now()
    digest = hashlib.sha256()
    bytes_read = 0
    status = ""
    content_type = ""
    final_url = row["url"]
    note = ""
    fetch_status = "WARN"
    try:
        request = Request(row["url"], headers={"User-Agent": "VietGreen-remote-source-refresh/1.0"})
        with urlopen(request, timeout=30) as response:
            status = str(getattr(response, "status", response.getcode()))
            content_type = response.headers.get("Content-Type", "")
            final_url = response.geturl()
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                bytes_read += len(chunk)
                digest.update(chunk)
                if bytes_read > MAX_BYTES:
                    note = f"response exceeded {MAX_BYTES} bytes; hash is truncated at the safety cap"
                    break
            fetch_status = "PASS" if status.startswith("2") else "WARN"
            if not note:
                note = "response body hashed in memory; raw snapshot not stored"
    except HTTPError as exc:
        status = str(exc.code)
        content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
        final_url = exc.geturl()
        note = f"HTTP error; raw response not stored: {exc.reason}"
    except (URLError, TimeoutError, OSError) as exc:
        note = f"fetch error; raw response not stored: {exc}"
    return {
        "source_id": row["source_id"],
        "url": row["url"],
        "checked_at_utc": checked_at,
        "http_status": status,
        "content_type": content_type,
        "bytes_read_in_memory": str(bytes_read),
        "content_sha256": digest.hexdigest() if bytes_read else "",
        "final_url": final_url,
        "fetch_status": fetch_status,
        "raw_snapshot_stored": "FALSE",
        "storage_boundary": "REMOTE_RUNNER_EPHEMERAL",
        "notes": note,
    }


def main() -> int:
    known = registered_ids()
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        sources = list(csv.DictReader(handle))
    unknown = sorted({row["source_id"] for row in sources} - known)
    if unknown:
        raise SystemExit(f"Unregistered source IDs: {unknown}")
    results = [fetch(row) for row in sources]
    fields = list(results[0])
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    print({
        "checked_sources": len(results),
        "pass": sum(row["fetch_status"] == "PASS" for row in results),
        "warn": sum(row["fetch_status"] == "WARN" for row in results),
        "raw_snapshot_stored": False,
        "output": str(OUTPUT.relative_to(ROOT)),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
