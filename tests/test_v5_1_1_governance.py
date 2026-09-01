from pathlib import Path

def test_current_claim_boundary_and_release_files_exist():
    assert Path("validation/V5_1_1_REMEDIATION_REGISTER.csv").exists()
    assert Path("validation/V5_1_1_CONTENT_MIGRATION_MATRIX.csv").exists()
    assert Path("analytics/build_v5_1_1_release.py").exists()
    for p in ["README.md","EXECUTIVE_SUMMARY.md","BUSINESS_CASE.md","ASSUMPTIONS_AND_LIMITATIONS.md","CLAIM_GOVERNANCE.md","SCOPE_MATRIX.md","V5_MIGRATION_STATUS.md"]:
        assert Path(p).exists()
