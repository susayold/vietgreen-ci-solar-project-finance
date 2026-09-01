"""Generate governed V5 recruiter surfaces from the final V5 manifest."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; M=ROOT/"release"/"V5_BUILD_STATUS.json"; OUT=ROOT/"artifacts"/"v5_surfaces"
def main():
    m=json.loads(M.read_text(encoding="utf-8"));OUT.mkdir(parents=True,exist_ok=True);status=m.get("release_status","INPUT_DATA_BLOCKED");ready=status.startswith("READY")
    headline=f"{m.get('project_count',0)} selected real C&I solar records across {m.get('candidate_count',0)} public candidates."
    if not ready:headline+=" Release is blocked pending V5 input/evidence gates."
    common="This is a public-data reconstruction. It does not claim confidential PPA terms, actual lender pricing, transaction approval, legal/tax certification or bankability."
    docs={"README.md":f"# VietGreen V5\n\n{headline}\n\nStatus: {status}\n\n{common}\n","EXECUTIVE_SUMMARY.md":f"# V5 Executive Summary\n\n{headline}\n\n{common}\n","BUSINESS_CASE.md":f"# V5 Business Case\n\nSelected real records are modeled with observed facts separated from explicit benchmark assumptions.\n\nStatus: {status}\n","IC_MEMO.md":f"# V5 Investment Committee Memo\n\nDecision boundary: standardized public-data screening only.\n\n{common}\n","LENDER_MEMO.md":f"# V5 Lender Memo\n\nStatus: SCREENING_ONLY; actual debt terms remain undisclosed.\n\n{common}\n","CV_BULLETS.md":"# V5 CV Bullets\n\n- Built a governed real-data migration across 50+ public C&I solar candidates.\n- Implemented outcome-blind selection, country benchmark packs, source lineage, conflict controls and remote CI reproducibility.\n- Separated observed facts from standardized underwriting assumptions and claim boundaries.\n"}
    for n,c in docs.items():(OUT/n).write_text(c,encoding="utf-8")
    (OUT/"website_headline.txt").write_text(headline+"\n",encoding="utf-8")
if __name__=="__main__":main()
