"""Reject stale predecessor content from the public website surface."""
from pathlib import Path
BAD=("V4-FINAL-2026-08-31","V4.0.0","V4.1-RECRUITER-CLOSURE","current V5.1.1","model/vietgreen_v4_formula_model.xlsx","VG-005","VG-010","VG-011","VG-012","Selected portfolio (four projects)","NO DEPLOYMENT","Synthetic V4 outputs","Synthetic model output only")
ROOT=Path(__file__).resolve().parents[1]/"website"
def main():
 found=[]
 for p in ROOT.rglob("*"):
  if p.is_file() and p.suffix.lower() in {".html",".js",".json",".md",".css"}:
   t=p.read_text(encoding="utf-8",errors="ignore")
   for b in BAD:
    if b in t: found.append((str(p),b))
 if found: raise AssertionError(found)
 print("website stale-content scan PASS")
if __name__=="__main__": main()
