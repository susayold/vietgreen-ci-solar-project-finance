"""Generate recruiter surfaces from the authoritative V5.1 economics output."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"outputs";DEST=ROOT/"artifacts"/"v5_surfaces"
def rows(p):
 with p.open(newline="",encoding="utf-8-sig") as h:return list(csv.DictReader(h))
def build():
 DEST.mkdir(parents=True,exist_ok=True);econ=rows(OUT/"v5_project_economics.csv");n=len(econ)
 intro="Reconstructed and underwrote a portfolio of real C&I/distributed-solar projects from public project and transaction evidence, using country-specific solar, tariff, tax, financing and FX benchmarks; integrated 8,760 load matching, PPA frontier analysis, CFADS-based debt sizing, DSCR/LLCR/PLCR, sponsor returns and downside stress testing with evidence-level governance."
 boundary="V5.1 is a standardized public-data reconstruction. Confidential PPA, lender, tax, technical and site terms are not represented as actual unless explicitly disclosed. Recruiter-ready does not mean investment approval, lender approval, legal/tax opinion or technical certification. It is not a bankable transaction."
 (DEST/"README.md").write_text("# VietGreen V5.1\n\n"+intro+"\n\n"+boundary+"\n",encoding="utf-8")
 (DEST/"Executive_Summary.md").write_text("# Executive Summary\n\nProjects under full-engine public-data reconstruction: "+str(n)+". Every project is outcome-blind selected before economics. PPA mode is FRONTIER_ONLY when exact price is not public; displayed reference economics is not a confidential PPA.\n\n"+boundary+"\n",encoding="utf-8")
 (DEST/"Business_Case.md").write_text("# Business Case\n\nThe customer ceiling, sponsor floor and lender floor are shown as a negotiation frontier. Local currency cash flows are translated to USD only for reporting. No manual NPV/IRR edits are permitted.\n\n"+boundary+"\n",encoding="utf-8")
 (DEST/"IC_memo.md").write_text("# IC Memo\n\nDecision status is INDETERMINATE_MISSING_COMMERCIAL_DATA unless confidential PPA, site, technical, tax and financing diligence closes the missing evidence. No IC approval is claimed.\n\n"+boundary+"\n",encoding="utf-8")
 (DEST/"Lender_memo.md").write_text("# Lender Memo\n\nDebt is capacity-sized using DSCR/LLCR/PLCR/leverage constraints and a forward schedule. Financing inputs are standardized underwriting assumptions, not lender terms; transaction evidence remains OPEN.\n\n"+boundary+"\n",encoding="utf-8")
 (DEST/"recruiter_package.md").write_text("# Recruiter Package\n\n"+intro+"\n\nEvidence labels: OBSERVED PUBLIC FACT; DERIVED PUBLIC FACT; BENCHMARK RECONSTRUCTION; ANALYST ASSUMPTION; STANDARDIZED UNDERWRITING; SCENARIO; NOT DISCLOSED.\n\n"+boundary+"\n",encoding="utf-8")
 (DEST/"CV_bullets.md").write_text("# CV Bullets\n\n- "+intro+"\n- Built reproducible remote CI controls for units, FX, source lineage, 8,760 load matching, PPA frontier, CFADS/debt sizing, DSCR/LLCR/PLCR, returns and downside scenarios.\n\n"+boundary+"\n",encoding="utf-8")
if __name__=="__main__":build()
