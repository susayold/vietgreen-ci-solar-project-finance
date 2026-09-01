"""Generate V5 recruiter surfaces from the V5 manifest only."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "V5_BUILD_STATUS.json"
STATIC_MANIFEST = ROOT / "release" / "MODEL_RELEASE_MANIFEST_V5.json"
OUT = ROOT / "artifacts" / "v5_surfaces"


def load_manifest() -> dict:
    path = MANIFEST if MANIFEST.exists() else STATIC_MANIFEST
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    manifest = load_manifest()
    count = manifest.get("project_count", 0)
    countries = manifest.get("country_count", 0)
    status = manifest.get("release_status", "INPUT_DATA_BLOCKED")
    headline = f"{count} real C&I solar project records across {countries} markets — reconstructed from public evidence."
    if status != "READY_FOR_ECONOMICS":
        headline += " Economics are blocked pending input freeze and evidence gates."
    OUT.mkdir(parents=True, exist_ok=True)
    surfaces = {
        "README.md": f"# VietGreen V5 Global Real-Data Migration\n\n{headline}\n\nRelease status: {status}\n\nThis is a public-data reconstruction control surface. It does not claim confidential PPA terms, actual lender pricing, transaction approval or bankability.\n",
        "EXECUTIVE_SUMMARY.md": f"# V5 Executive Summary\n\n{headline}\n\nNo independent economic figures are published until the real project universe is selected, frozen and reconciled.\n",
        "BUSINESS_CASE.md": f"# V5 Business Case\n\nStatus: {status}.\n\nObserved facts, benchmark reconstructions and standardized underwriting outputs must remain separate.\n",
        "IC_MEMO.md": f"# V5 Investment Committee Memo\n\nDecision status: INDETERMINATE_MISSING_COMMERCIAL_DATA.\n\nThe public evidence set is not sufficient to approve investment or to create a synthetic base case.\n",
        "LENDER_MEMO.md": f"# V5 Lender Memo\n\nStatus: SCREENING_ONLY.\n\nActual lender terms, covenants, reserves and debt schedules are NOT_DISCLOSED.\n",
        "CV_BULLETS.md": "# V5 CV Bullets\n\n- Built a governed framework for reconstructing real C&I solar project-finance data from public evidence across multiple markets.\n- Separated observed transaction facts from benchmark assumptions and standardized underwriting outputs.\n- Implemented outcome-blind freeze and failed-closed release controls; no confidential lender terms were fabricated.\n",
    }
    for name, content in surfaces.items():
        (OUT / name).write_text(content, encoding="utf-8")
    (OUT / "website_headline.txt").write_text(headline + "\n", encoding="utf-8")
    print(f"generated={len(surfaces)+1} status={status} output={OUT}")


if __name__ == "__main__":
    main()
