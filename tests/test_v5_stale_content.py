from pathlib import Path
from analytics.scan_stale_v4_content import scan

def test_current_surfaces_are_current_and_fail_closed():
    result=scan(".")
    assert result["status"]=="PASS"
    text="\n".join(Path(p).read_text(encoding="utf-8", errors="ignore") for p in [
        "reports/DATA_ROOM_INDEX.md","reports/RECRUITER_SURFACE_RECONCILIATION.md"
    ])
    assert "V5.1.1" in text
    assert "INDETERMINATE_MISSING_COMMERCIAL_DATA" in text
    assert "BANKABLE_TRANSACTION_READY" in text
