"""Validate CI-sealed release identity without persisting project data locally."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path

def validate(manifest_path: str|Path, expected_sha: str|None=None, expected_run: str|None=None) -> list[str]:
    p=Path(manifest_path)
    data=json.loads(p.read_text(encoding="utf-8"))
    errors=[]
    expected_sha=expected_sha or os.getenv("GITHUB_SHA")
    expected_run=expected_run or os.getenv("GITHUB_RUN_ID")
    if data.get("release_version")!="5.1.2": errors.append("release_version")
    if data.get("release_tag")!="v5.1.2-recruiter-final": errors.append("release_tag")
    if expected_sha and data.get("source_sha")!=expected_sha: errors.append("source_sha")
    if expected_run and str(data.get("workflow_run_id"))!=str(expected_run): errors.append("workflow_run_id")
    forbidden={"CI_RUNTIME_ID_REQUIRED","CI_RUNTIME_TIMESTAMP_REQUIRED","PAGES_BUILD_SHA_INJECTED","PAGES_BUILD_RUN_ID_INJECTED"}
    for key in ("source_sha","workflow_run_id","workflow_run_attempt","primary_artifact_id","primary_artifact_digest","runtime_manifest_artifact_id","runtime_manifest_artifact_digest","build_timestamp_utc"):
        if str(data.get(key,"")) in forbidden: errors.append(f"placeholder:{key}")
    if data.get("gate_status")!="G0-G9_CLEARED_G2_PASS_WITH_NONBLOCKING_REVIEW": errors.append("gate_status")
    if data.get("remote_only") is not True: errors.append("remote_only")
    if data.get("runtime_manifest_artifact_id") in (None,""): errors.append("runtime_manifest_artifact_id")
    return errors

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("manifest"); ap.add_argument("--sha"); ap.add_argument("--run")
    args=ap.parse_args(); errors=validate(args.manifest,args.sha,args.run)
    if errors: raise SystemExit("runtime identity validation failed: "+", ".join(errors))
    print("V5.1.2 runtime identity: PASS")
    return 0
if __name__=="__main__": raise SystemExit(main())
