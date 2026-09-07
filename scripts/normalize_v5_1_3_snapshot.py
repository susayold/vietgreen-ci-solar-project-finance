"""Normalize the checked-in website snapshot to the frozen V5.1.3 contract."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"
MODEL_SHA = "ff69e15d211ff1abc88200574242ed2f1db49074"
MODEL_TAG = "v5.1.3-recruiter-final"


def read(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def write(name: str, value) -> None:
    (DATA / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    diligence = read("diligence.json")
    technical_id = "IN-FPEL-ARISUDHANA"
    technical = [row for row in diligence["rows"] if row["projectId"] == technical_id]
    diligence["rows"] = [row for row in diligence["rows"] if row["projectId"] != technical_id]
    if technical:
        diligence["technicalValidationTrack"] = technical
    write("diligence.json", diligence)

    release = read("website-release.json")
    release.update(
        {
            "websiteSha": os.getenv("WEBSITE_SOURCE_SHA") or os.getenv("GITHUB_SHA") or "local-source",
            "websiteRunId": os.getenv("WEBSITE_WORKFLOW_RUN_ID") or os.getenv("GITHUB_RUN_ID") or "local-build",
            "builtAtUtc": os.getenv("WEBSITE_BUILD_TIME_UTC") or "local-build",
            "modelSha": MODEL_SHA,
            "modelTag": MODEL_TAG,
        }
    )
    write("website-release.json", release)


if __name__ == "__main__":
    main()
