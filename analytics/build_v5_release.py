"""Build and validate the V5 public-data migration without fabricating economics."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "public"
EVIDENCE = ROOT / "evidence"
RELEASE = ROOT / "release"
CANDIDATES = ROOT / "research" / "GLOBAL_PROJECT_CANDIDATES.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_evidence(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = {
        "observed_fact_count": 0,
        "derived_fact_count": 0,
        "benchmark_assumption_count": 0,
        "analyst_assumption_count": 0,
        "not_disclosed_count": 0,
    }
    for row in rows:
        kind = row.get("evidence_class", "")
        if kind.startswith("OBSERVED_"):
            counts["observed_fact_count"] += 1
        elif kind == "DERIVED_FROM_OBSERVED":
            counts["derived_fact_count"] += 1
        elif kind == "BENCHMARK_ASSUMPTION":
            counts["benchmark_assumption_count"] += 1
        elif kind == "ANALYST_ASSUMPTION":
            counts["analyst_assumption_count"] += 1
        elif kind == "NOT_DISCLOSED":
            counts["not_disclosed_count"] += 1
    return counts


def build_manifest() -> tuple[dict[str, Any], list[str]]:
    config = json.loads((ROOT / "config" / "v5_global.yml").read_text(encoding="utf-8"))
    source_rows = read_csv(EVIDENCE / "GLOBAL_SOURCE_REGISTER.csv")
    pack_rows = read_csv(EVIDENCE / "COUNTRY_BENCHMARK_PACKS.csv")
    master_rows = read_csv(PUBLIC / "project_master_real.csv")
    overlay_rows = read_csv(PUBLIC / "project_assumption_overlay.csv")
    candidate_rows = read_csv(CANDIDATES)
    blockers: list[str] = []

    source_ids = {row.get("source_id") for row in source_rows}
    if len(source_ids) != len(source_rows) or None in source_ids:
        blockers.append("G0_SOURCE_REGISTER_DUPLICATE_OR_EMPTY_ID")
    pack_ids = {row.get("benchmark_pack_id") for row in pack_rows}
    seen_projects: set[str] = set()
    allowed = set(config["countries"])
    for row in master_rows:
        project_id = row.get("project_id", "")
        if not project_id or project_id in seen_projects:
            blockers.append("G1_PROJECT_ID_DUPLICATE_OR_EMPTY")
        seen_projects.add(project_id)
        if row.get("country") not in allowed:
            blockers.append(f"G1_COUNTRY_NOT_IN_CONTROLLED_UNIVERSE:{project_id}")
        if row.get("benchmark_pack_id") not in pack_ids:
            blockers.append(f"G4_MISSING_BENCHMARK_PACK:{project_id}")
        if row.get("evidence_grade") not in {"GOLD", "STRONG", "ACCEPTABLE"}:
            blockers.append(f"G0_EVIDENCE_GRADE_BELOW_ACCEPTABLE:{project_id}")
        if row.get("model_mode") != "FULL_RECONSTRUCTION":
            blockers.append(f"G5_NOT_FULL_RECONSTRUCTION:{project_id}")
        if row.get("data_quality_status", "").startswith("BLOCKED"):
            blockers.append(f"G0_DATA_QUALITY_BLOCKED:{project_id}")
    minimum = int(config["portfolio"]["minimum_projects"])
    if len(master_rows) < minimum:
        blockers.append(f"G5_MINIMUM_PROJECT_UNIVERSE_NOT_MET:{len(master_rows)}<{minimum}")
    packs_not_ready = [row["benchmark_pack_id"] for row in pack_rows if row.get("status") != "READY_FOR_ECONOMICS"]
    if packs_not_ready:
        blockers.append("G4_BENCHMARK_PACKS_NOT_READY:" + "|".join(packs_not_ready))
    evidence = count_evidence(read_csv(PUBLIC / "raw_project_observations.csv") + overlay_rows)
    grades = {grade: sum(row.get("evidence_grade") == grade for row in master_rows) for grade in ("GOLD", "STRONG", "ACCEPTABLE", "EXCLUDE")}
    countries = sorted({row.get("country") for row in master_rows if row.get("country")})
    status = "READY_FOR_ECONOMICS" if not blockers else "INPUT_DATA_BLOCKED"
    manifest: dict[str, Any] = {
        "release_id": "V5-GLOBAL-REAL-DATA-BASELINE",
        "release_version": "V5.0.0-RESEARCH-BASELINE",
        "release_date": "2026-09-01",
        "git_sha": "RUNTIME_SHA_REQUIRED",
        "input_freeze_id": None,
        "manifest_status": "PRE_FREEZE_CONTROL_SNAPSHOT",
        "release_status": status,
        "project_count": len(master_rows),
        "country_count": len(countries),
        "countries": countries,
        "real_project_count": len(master_rows),
        "frozen_project_count": 0 if blockers else len(master_rows),
        "candidate_count": len(candidate_rows),
        **evidence,
        "coverage_grade_distribution": grades,
        "current_positive_count": None,
        "current_negative_count": None,
        "indeterminate_count": len(master_rows),
        "selected_count": 0,
        "selected_ids": [],
        "selected_countries": [],
        "selected_equity_usd": None,
        "selected_debt_usd": None,
        "base_project_npv_usd": None,
        "base_equity_npv_usd": None,
        "base_dscr": None,
        "recruiter_ready": False,
        "transaction_evidence_status": "OPEN",
        "bankable_transaction_ready": False,
        "claim_boundary": "PUBLIC_DATA_RECONSTRUCTION_ONLY; CONFIDENTIAL_TERMS_ARE_NOT_DISCLOSED; STANDARDIZED_UNDERWRITING_IS_NOT_ACTUAL_LENDER_PRICING; NOT_TRANSACTION_ADVICE",
        "blockers": sorted(set(blockers)),
        "input_hashes": {
            "source_register_sha256": sha256(EVIDENCE / "GLOBAL_SOURCE_REGISTER.csv"),
            "project_master_sha256": sha256(PUBLIC / "project_master_real.csv"),
            "assumption_overlay_sha256": sha256(PUBLIC / "project_assumption_overlay.csv"),
            "benchmark_pack_sha256": sha256(EVIDENCE / "COUNTRY_BENCHMARK_PACKS.csv"),
        },
    }
    return manifest, blockers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    manifest, blockers = build_manifest()
    RELEASE.mkdir(parents=True, exist_ok=True)
    (RELEASE / "V5_BUILD_STATUS.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"release_status": manifest["release_status"], "project_count": manifest["project_count"], "blocker_count": len(blockers), "blockers": blockers}, ensure_ascii=False))
    return 0 if args.allow_incomplete or not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
