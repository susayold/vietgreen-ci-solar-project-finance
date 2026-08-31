"""Locked-input hash and seed verification for GitHub Actions."""
from __future__ import annotations
import csv,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/"config/SYNTHETIC_INPUT_HASHES.csv"
INPUTS=[ROOT/"config/synthetic_seed.yml"]+sorted((ROOT/"data/synthetic").glob("*.csv"))

def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rows():
    return [{"path":str(path.relative_to(ROOT)).replace("\\","/"),"sha256":sha256(path),"bytes":path.stat().st_size} for path in INPUTS]
def write_baseline(items):
    BASELINE.parent.mkdir(parents=True,exist_ok=True)
    with BASELINE.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=["path","sha256","bytes"]); writer.writeheader(); writer.writerows(items)
def verify_or_write():
    current=rows()
    if not BASELINE.exists(): write_baseline(current); return "BASELINE_CREATED"
    with BASELINE.open(newline="",encoding="utf-8") as handle: expected=list(csv.DictReader(handle))
    normalized=[{key:str(item[key]) for key in ("path","sha256","bytes")} for item in current]
    if expected!=normalized: raise ValueError("synthetic input hash drift detected")
    return "HASHES_LOCKED"
if __name__=="__main__": print(verify_or_write())
