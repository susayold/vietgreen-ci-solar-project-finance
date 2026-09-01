"""Fail-closed scanner for stale V4/V5.0 claims on current surfaces."""
from pathlib import Path
SURFACES=[
"README.md","EXECUTIVE_SUMMARY.md","BUSINESS_CASE.md","ASSUMPTIONS_AND_LIMITATIONS.md",
"CLAIM_GOVERNANCE.md","SCOPE_MATRIX.md","V5_MIGRATION_STATUS.md",
"reports/INVESTMENT_COMMITTEE_MEMO.md","reports/LENDER_CREDIT_MEMO.md",
"reports/RECRUITER_PACKAGE.md","reports/CV_BULLETS_V5_1_1.md",
"reports/STANDARDIZED_UNDERWRITING_TERMS_V5_1_1.md","website/index.html",
"website/data/shared-summary.json","website/data/release-meta.json","website/data/projects.json",
"website/data/frontier.json","website/data/risk.json","website/data/evidence.json","website/data/scenarios.json",
"artifacts/v5_1_1_surfaces/content_contract.json"
]
BLACKLIST=["V4-FINAL-2026-08-31","V4.0.0","VG-005","VG-010","VG-011","VG-012","30.124825","55.946104","12.003384","5.262393","5.942277","-1.177896","-3.179160","-38.814456","0 / 20 positive Equity NPV","19 / 20 positive Equity NPV","SYNTHETIC_RECRUITER_OUTPUT","VietGreen V4 Project Finance"]
ALLOWED_HISTORICAL=["V5.1.0: SUPERSEDED AFTER POST-RELEASE AUDIT","V5.1.0 — SUPERSEDED AFTER POST-RELEASE AUDIT"]
def scan(root="."):
    root=Path(root); findings=[]
    for name in SURFACES:
        p=root/name
        if not p.exists(): findings.append(f"MISSING:{name}"); continue
        t=p.read_text(encoding="utf-8",errors="ignore")
        for token in BLACKLIST:
            if token in t: findings.append(f"STALE:{name}:{token}")
        if "V5.1.1" not in t and "v5.1.1" not in t: findings.append(f"NOT_CURRENT:{name}")
        if "EXACT_PPA_CONFIRMED" in t or "BANKABLE_TRANSACTION_READY" in t: findings.append(f"UNAUTHORISED_CLAIM:{name}")
    if findings: raise AssertionError(findings)
    return {"status":"PASS","scanned":len(SURFACES)}
if __name__=="__main__":
    print(scan())
