"""Scan the current surface for stale superseded claims."""
from pathlib import Path
SURFACES=["README.md","EXECUTIVE_SUMMARY.md","BUSINESS_CASE.md","ASSUMPTIONS_AND_LIMITATIONS.md","CLAIM_GOVERNANCE.md","SCOPE_MATRIX.md","V5_MIGRATION_STATUS.md","website/index.html","reports/v5_1_1_recruiter_summary.md"]
def scan(root="."):
    root=Path(root); findings=[]
    for name in SURFACES:
        p=root/name
        if not p.exists(): findings.append(f"MISSING:{name}"); continue
        t=p.read_text(encoding="utf-8",errors="ignore")
        if "V5.0" in t or "V4.0" in t: findings.append(f"STALE_VERSION:{name}")
        if "EXACT_PPA_CONFIRMED" in t or "BANKABLE_TRANSACTION_READY" in t: findings.append(f"UNAUTHORISED_CLAIM:{name}")
    if findings: raise AssertionError(findings)
    return {"status":"PASS","scanned":len(SURFACES)}
if __name__=="__main__":
    print(scan())
