"""Compare two GitHub Actions artifacts without persisting their contents.

Only per-file sizes and SHA-256 metadata are written. Artifact bytes are held
in memory on the ephemeral GitHub Actions runner and are discarded afterwards.
"""
from __future__ import annotations

import csv
import hashlib
import io
import os
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "validation" / "REPRODUCIBILITY_COMPARISON.csv"
TARGETS = (
    "model/vietgreen_core_model.xlsx",
    "validation/REMOTE_8760_INDEX.csv",
    "remote_derived/load_8760.csv.gz",
    "remote_derived/solar_8760.csv.gz",
    "remote_derived/load_8760.parquet",
    "remote_derived/solar_8760.parquet",
)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, new_url):
        return None


def download_artifact(artifact_id: str) -> dict[str, tuple[str, int]]:
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact_id}/zip"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "VietGreen-remote-reproducibility-check/1.1",
        },
    )
    opener = urllib.request.build_opener(NoRedirect)
    try:
        response = opener.open(request, timeout=120)
    except urllib.error.HTTPError as error:
        if error.code not in {301, 302, 303, 307, 308}:
            raise
        location = error.headers.get("Location")
        if not location:
            raise RuntimeError(f"artifact {artifact_id} redirect missing Location header")
        # The signed storage URL must not receive the GitHub bearer token.
        response = urllib.request.urlopen(
            urllib.request.Request(
                location,
                headers={"User-Agent": "VietGreen-remote-reproducibility-check/1.1"},
            ),
            timeout=120,
        )
    with response:
        archive_bytes = response.read()
    result: dict[str, tuple[str, int]] = {}
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        names = set(archive.namelist())
        missing = [target for target in TARGETS if target not in names]
        if missing:
            raise RuntimeError(f"artifact {artifact_id} missing: {missing}")
        for target in TARGETS:
            body = archive.read(target)
            result[target] = (hashlib.sha256(body).hexdigest(), len(body))
    return result


def main() -> int:
    baseline_id = os.environ["BASELINE_ARTIFACT_ID"]
    repeat_id = os.environ["REPEAT_ARTIFACT_ID"]
    baseline = download_artifact(baseline_id)
    repeat = download_artifact(repeat_id)
    rows = []
    for target in TARGETS:
        base_hash, base_size = baseline[target]
        repeat_hash, repeat_size = repeat[target]
        rows.append(
            {
                "path": target,
                "baseline_artifact_id": baseline_id,
                "repeat_artifact_id": repeat_id,
                "baseline_sha256": base_hash,
                "repeat_sha256": repeat_hash,
                "baseline_bytes": base_size,
                "repeat_bytes": repeat_size,
                "match": str(base_hash == repeat_hash and base_size == repeat_size).upper(),
                "raw_artifact_contents_stored": "FALSE",
            }
        )
    fields = list(rows[0])
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    matches = sum(row["match"] == "TRUE" for row in rows)
    print({"baseline_artifact_id": baseline_id, "repeat_artifact_id": repeat_id, "file_matches": matches, "file_count": len(rows)})
    if matches != len(rows):
        raise SystemExit("reproducibility comparison failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
