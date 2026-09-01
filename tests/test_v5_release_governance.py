import json
from pathlib import Path
def test_release_governance_files():
    m=json.loads(Path("release/MODEL_RELEASE_MANIFEST.json").read_text())
    assert m["release_version"]=="5.1.1" and m["ppa_mode"]=="FRONTIER_ONLY"
    assert Path("release/V5_RUNTIME_RELEASE_MANIFEST.json").exists()
    assert Path("artifacts/v5_1_1_surfaces/content_contract.json").exists()
    assert "v5.1.1-recruiter-final" in Path("README.md").read_text()
