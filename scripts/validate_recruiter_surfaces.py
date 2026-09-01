"""Reconcile declared recruiter-facing documents and JSON to the released V4 manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "release" / "MODEL_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
SURFACES = [
    ROOT / "README.md",
    ROOT / "EXECUTIVE_SUMMARY.md",
    ROOT / "BUSINESS_CASE.md",
    ROOT / "reports" / "RECRUITER_PACKAGE.md",
    ROOT / "reports" / "WEBSITE_CONTENT_MAP.md",
    ROOT / "reports" / "WEBSITE_QA_REPORT.md",
    ROOT / "reports" / "WEBSITE_RELEASE_MANIFEST.json",
    ROOT / "release" / "MODEL_RELEASE_MANIFEST.json",
    ROOT / "validation" / "OPEN_EXTERNAL_GATES.csv",
    ROOT / "validation" / "V4_READINESS_STATE.csv",
]
SURFACES.extend(path for path in (ROOT / "website").rglob("*") if path.is_file())
OLD_CLAIMS = ("11 selected", "13.10 mwp", "138.143294", "152.457008", "-66.202345", "model/vietgreen_core_model.xlsx")
required_fragments = {
    ROOT / "EXECUTIVE_SUMMARY.md": ("0 / 20", "30.124825", "55.946104", "5.942277", "NO_DEPLOYMENT"),
    ROOT / "BUSINESS_CASE.md": ("0 / 20", "VG-005", "VG-010", "VG-011", "VG-012", "30.124825"),
}
errors = []
for path in SURFACES:
    if not path.exists():
        errors.append(f"missing surface: {path.relative_to(ROOT)}")
        continue
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    for claim in OLD_CLAIMS:
        if claim.lower() in text:
            errors.append(f"stale claim {claim}: {path.relative_to(ROOT)}")
for path, fragments in required_fragments.items():
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        if fragment.lower() not in text.lower():
            errors.append(f"{path.relative_to(ROOT)} missing required fragment {fragment}")
shared = json.loads((ROOT / "website" / "data" / "shared-summary.json").read_text(encoding="utf-8"))
if shared.get("selectedProjectIds") != MANIFEST["selected_ids"]:
    errors.append("shared selected IDs mismatch")
if shared.get("selectedProjects") != MANIFEST["selected_count"]:
    errors.append("shared selected count mismatch")
if errors:
    print("Recruiter surface reconciliation FAILED")
    print("\n".join(f"- {item}" for item in errors))
    raise SystemExit(1)
print(f"Recruiter surface reconciliation PASS: {len(SURFACES)} surfaces; release {MANIFEST['release_id']}")
