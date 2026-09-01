"""Fail-closed stale-claim scan for all declared recruiter and control surfaces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURFACE_PATHS = [
    "README.md",
    "EXECUTIVE_SUMMARY.md",
    "BUSINESS_CASE.md",
    "reports/RECRUITER_PACKAGE.md",
    "reports/CV_BULLETS_V4.md",
    "reports/INVESTMENT_COMMITTEE_MEMO.md",
    "reports/LENDER_CREDIT_MEMO.md",
    "reports/WEBSITE_CONTENT_MAP.md",
    "reports/WEBSITE_QA_REPORT.md",
    "reports/WEBSITE_RELEASE_MANIFEST.json",
    "release/MODEL_RELEASE_MANIFEST.json",
    "validation/OPEN_EXTERNAL_GATES.csv",
    "validation/V4_READINESS_STATE.csv",
    "validation/RECRUITER_SURFACE_RECONCILIATION.csv",
]
SURFACE_PATHS.extend(
    str(path.relative_to(ROOT))
    for path in (ROOT / "website").rglob("*")
    if path.is_file()
)
FORBIDDEN = {
    "legacy selected count": "11 selected",
    "legacy capacity": "13.10 mwp",
    "legacy equity": "138.143294",
    "legacy debt": "152.457008",
    "legacy sponsor npv": "-66.202345",
    "legacy workbook path": "model/vietgreen_core_model.xlsx",
    "unsupported debt response object": "fixedvsresized",
    "unsupported resized value": '"resized"',
}
errors = []
scanned = 0
for relative in sorted(set(SURFACE_PATHS)):
    path = ROOT / relative
    if not path.exists():
        errors.append(f"missing declared surface: {relative}")
        continue
    scanned += 1
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    for label, pattern in FORBIDDEN.items():
        if pattern in text:
            errors.append(f"{label}: {relative}")
if errors:
    print("Stale V3 claim check FAILED")
    print("\n".join(f"- {item}" for item in errors))
    raise SystemExit(1)
print(f"Stale V3 claim check PASS: scanned {scanned} declared recruiter surfaces")
