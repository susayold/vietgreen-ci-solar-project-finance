"""Write deployment identity into the public website payload during CI."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "release" / "MODEL_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
payload = {
    "releaseId": manifest["release_id"],
    "modelVersion": "V4.0.0",
    "dataContractVersion": "V4.1-RECRUITER-CLOSURE",
    "gitSha": os.environ.get("GITHUB_SHA", "local-not-deployed"),
    "builtAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "workflowRunId": os.environ.get("GITHUB_RUN_ID", "local"),
    "sourceManifestPath": "release/MODEL_RELEASE_MANIFEST.json",
    "status": "DEPLOYMENT_CANDIDATE",
    "claimBoundary": manifest["claim_boundary"],
}
path = ROOT / "website" / "data" / "release-meta.json"
path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(payload, sort_keys=True))
