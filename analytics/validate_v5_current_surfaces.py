"""Fail-closed current-surface reconciliation for V5.1.1."""
from pathlib import Path
SURFACES=["README.md","EXECUTIVE_SUMMARY.md","BUSINESS_CASE.md","ASSUMPTIONS_AND_LIMITATIONS.md","CLAIM_GOVERNANCE.md","SCOPE_MATRIX.md","V5_MIGRATION_STATUS.md","website/index.html"]
def validate(root="."):
    root=Path(root); text="\n".join((root/p).read_text(encoding="utf-8",errors="ignore") for p in SURFACES)
    required=["V5.1.1","INDETERMINATE_MISSING_COMMERCIAL_DATA","FRONTIER_ONLY"]
    missing=[x for x in required if x not in text]
    prohibited=["EXACT_PPA_CONFIRMED","BANKABLE_TRANSACTION_READY"]
    found=[x for x in prohibited if x in text]
    if missing or found: raise AssertionError({"missing":missing,"prohibited":found})
    return {"status":"PASS","surface_count":len(SURFACES),"version":"V5.1.1"}
if __name__=="__main__":
    print(validate())
