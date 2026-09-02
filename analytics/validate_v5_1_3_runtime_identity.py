"""Validate the CI-sealed V5.1.3 runtime manifest."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path

def validate(path, expected_sha=None, expected_run=None):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    errors=[]
    if d.get("release_version")!="5.1.3": errors.append("release_version")
    if d.get("release_tag")!="v5.1.3-recruiter-final": errors.append("release_tag")
    expected_sha=expected_sha or os.getenv("GITHUB_SHA")
    expected_run=expected_run or os.getenv("GITHUB_RUN_ID")
    if expected_sha and d.get("source_sha")!=expected_sha: errors.append("source_sha")
    if expected_run and str(d.get("workflow_run_id"))!=str(expected_run): errors.append("workflow_run_id")
    if d.get("gate_status")!="G0-G9_CLEARED_G2_PASS_WITH_NONBLOCKING_REVIEW": errors.append("gate_status")
    if d.get("remote_only") is not True: errors.append("remote_only")
    for k in ("source_sha","workflow_run_id","workflow_run_attempt","primary_artifact_id","primary_artifact_digest","runtime_manifest_artifact_id","runtime_manifest_artifact_digest","build_timestamp_utc"):
        if str(d.get(k,"")).startswith("CI_") or str(d.get(k,"")).endswith("_REQUIRED"): errors.append("placeholder:"+k)
    if not d.get("runtime_manifest_artifact_id"): errors.append("runtime_manifest_artifact_id")
    return errors

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("manifest"); ap.add_argument("--sha"); ap.add_argument("--run")
    e=validate(ap.parse_args().manifest,ap.parse_args().sha,ap.parse_args().run)
    if e: raise SystemExit("runtime identity validation failed: "+", ".join(e))
    print("V5.1.3 runtime identity: PASS")
