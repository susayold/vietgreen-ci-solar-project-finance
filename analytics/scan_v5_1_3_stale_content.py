"""Scan V5.1.3 current surfaces and preserve historical references only."""
from __future__ import annotations
import argparse
from pathlib import Path

CURRENT_FILES=("README.md","EXECUTIVE_SUMMARY.md","BUSINESS_CASE.md","ASSUMPTIONS_AND_LIMITATIONS.md","CLAIM_GOVERNANCE.md","SCOPE_MATRIX.md","V5_MIGRATION_STATUS.md","reports/INVESTMENT_COMMITTEE_MEMO.md","reports/LENDER_CREDIT_MEMO.md","reports/RECRUITER_PACKAGE.md","reports/RECRUITER_SURFACE_RECONCILIATION.md","website/index.html","website/app.js","website/data/release-meta.json","website/data/scenarios.json","release/MODEL_RELEASE_MANIFEST.json","release/V5_1_3_STATIC_RELEASE_CONTRACT.json")
STALE=("V5.1.1","v5.1.1-recruiter-final","v5.1.0-recruiter-final","v4.1.3-recruiter-final")
ALLOWED=("HISTORICAL","SUPERSEDED","IMMUTABLE","history","Historical","historical")
def scan(root):
    root=Path(root); errors=[]
    for rel in CURRENT_FILES:
        p=root/rel
        if not p.exists(): errors.append("missing:"+rel); continue
        t=p.read_text(encoding="utf-8",errors="replace")
        for m in STALE:
            if m in t and not any(x in t for x in ALLOWED): errors.append(f"stale:{rel}:{m}")
        if rel not in ("website/data/release-meta.json",) and rel not in ("release/V5_1_3_STATIC_RELEASE_CONTRACT.json",) and "5.1.3" not in t and "V5.1.3" not in t:
            errors.append("not-current:"+rel)
    return errors
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("root"); a=ap.parse_args(); e=scan(a.root)
    if e: raise SystemExit("stale-content validation failed: "+", ".join(e))
    print("V5.1.3 stale-content scan: PASS")
