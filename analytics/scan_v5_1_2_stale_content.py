"""Scan current release surfaces for stale identity or prohibited claims."""
from __future__ import annotations
import argparse
from pathlib import Path

CURRENT_FILES=(
 "README.md","EXECUTIVE_SUMMARY.md","BUSINESS_CASE.md","ASSUMPTIONS_AND_LIMITATIONS.md",
 "CLAIM_GOVERNANCE.md","SCOPE_MATRIX.md","V5_MIGRATION_STATUS.md",
 "reports/INVESTMENT_COMMITTEE_MEMO.md","reports/LENDER_CREDIT_MEMO.md",
 "reports/RECRUITER_PACKAGE.md","reports/DATA_ROOM_INDEX.md",
 "reports/RECRUITER_SURFACE_RECONCILIATION.md","website/index.html",
 "website/data/release-meta.json","release/MODEL_RELEASE_MANIFEST.json",
)
STALE=("V5.1.1","v5.1.1-recruiter-final","v5.1.1-data-model-content-rebuild","v5.1.0-recruiter-final","v4.1.3-recruiter-final")
ALLOWED=("HISTORICAL","SUPERSEDED","IMMUTABLE","legacy","history","Historical","historical")

def scan(root: str|Path) -> list[str]:
    root=Path(root); errors=[]
    for rel in CURRENT_FILES:
        path=root/rel
        if not path.exists(): errors.append(f"missing:{rel}"); continue
        text=path.read_text(encoding="utf-8",errors="replace")
        for marker in STALE:
            if marker in text and not any(word in text for word in ALLOWED):
                errors.append(f"stale:{rel}:{marker}")
    for rel in ("README.md","EXECUTIVE_SUMMARY.md","BUSINESS_CASE.md","reports/INVESTMENT_COMMITTEE_MEMO.md","reports/LENDER_CREDIT_MEMO.md","reports/RECRUITER_PACKAGE.md","website/index.html"):
        text=(root/rel).read_text(encoding="utf-8",errors="replace")
        if "5.1.2" not in text: errors.append(f"not-current:{rel}")
    return errors

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("root"); args=ap.parse_args()
    problems=scan(args.root)
    if problems: raise SystemExit("stale-content validation failed: "+", ".join(problems))
    print("V5.1.2 stale-content scan: PASS")
