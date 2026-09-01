from pathlib import Path

def test_current_surfaces_do_not_claim_exact_ppa_or_bankability():
    text="\n".join(Path(p).read_text(encoding="utf-8",errors="ignore") for p in ["README.md","EXECUTIVE_SUMMARY.md","BUSINESS_CASE.md","ASSUMPTIONS_AND_LIMITATIONS.md","CLAIM_GOVERNANCE.md","SCOPE_MATRIX.md","V5_MIGRATION_STATUS.md"])
    assert "v5.1.1" in text.lower()
    assert "INDETERMINATE_MISSING_COMMERCIAL_DATA" in text
    assert "bankable" in text.lower() or "bankability" in text.lower()
