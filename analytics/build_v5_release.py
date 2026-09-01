"""Build and validate the V5 public-data migration without fabricating economics."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "public"
EVIDENCE = ROOT / "evidence"
RELEASE = ROOT / "release"
CANDIDATES = ROOT / "research" / "GLOBAL_PROJECT_CANDIDATES.csv"
SCORING = ROOT / "research" / "CANDIDATE_SCORING.csv"

EVIDENCE_CLASSES = {
    "OBSERVED_PROJECT_FACT",
    "OBSERVED_TRANSACTION_FACT",
    "OBSERVED_REGULATORY_FACT",
    "OBSERVED_MARKET_FACT",
    "DERIVED_FROM_OBSERVED",
    "BENCHMARK_ASSUMPTION",
    "ANALYST_ASSUMPTION",
    "SCENARIO_ONLY",
    "NOT_DISCLOSED",
    "NOT_APPLICABLE",
}
SOURCE_TIERS = {"A1", "A2", "B1", "B2", "B3", "C", "D", "E"}
GRADE_BANDS = (
    ("GOLD", 85, 100),
    ("STRONG", 75, 84),
    ("ACCEPTABLE", 65, 74),
    ("EXCLUDE", 0, 64),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def validate_columns(path: Path, required: set[str], blockers: list[str]) -> None:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        fields = set(csv.DictReader(handle).fieldnames or [])
    missing = sorted(required - fields)
    if missing:
        blockers.append(f"G2_SCHEMA_MISSING:{path.name}:" + "|".join(missing))


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


def expected_grade(score: int) -> str:
    for grade, lower, upper in GRADE_BANDS:
        if lower <= score <= upper:
            return grade
    return "EXCLUDE"


def validate_candidate_register(
    candidates: list[dict[str, str]],
    scoring: list[dict[str, str]],
    source_ids: set[str],
    blockers: list[str],
) -> dict[str, Any]:
    candidate_ids = [row.get("candidate_id", "") for row in candidates]
    if len(candidate_ids) != len(set(candidate_ids)) or any(not item for item in candidate_ids):
        blockers.append("G3_CANDIDATE_ID_DUPLICATE_OR_EMPTY")
    scoring_map: dict[str, dict[str, str]] = {}
    for row in scoring:
        candidate_id = row.get("candidate_id", "")
        if not candidate_id or candidate_id in scoring_map:
            blockers.append("G3_SCORING_ID_DUPLICATE_OR_EMPTY")
        scoring_map[candidate_id] = row
    candidate_set = set(candidate_ids)
    if set(scoring_map) != candidate_set:
        missing = sorted(candidate_set - set(scoring_map))
        extra = sorted(set(scoring_map) - candidate_set)
        if missing:
            blockers.append("G3_SCORING_MISSING:" + "|".join(missing))
        if extra:
            blockers.append("G3_SCORING_EXTRA:" + "|".join(extra))
    gold_strong = 0
    below_acceptable = 0
    for row in candidates:
        source_refs = [ref for ref in row.get("source_ids", "").split("|") if ref]
        if not source_refs or not set(source_refs).issubset(source_ids):
            blockers.append(f"G3_CANDIDATE_SOURCE_UNREGISTERED:{row.get('candidate_id', '')}")
        score_row = scoring_map.get(row.get("candidate_id", ""))
        if not score_row:
            continue
        try:
            score = int(score_row.get("total_score", ""))
        except ValueError:
            blockers.append(f"G3_SCORING_NOT_INTEGER:{row.get('candidate_id', '')}")
            continue
        grade = score_row.get("evidence_grade", "")
        if not 0 <= score <= 100:
            blockers.append(f"G3_SCORING_OUT_OF_RANGE:{row.get('candidate_id', '')}")
        if grade != expected_grade(score):
            blockers.append(f"G3_SCORING_GRADE_MISMATCH:{row.get('candidate_id', '')}")
        if score >= 75:
            gold_strong += 1
        if score < 65:
            below_acceptable += 1
    total = len(candidates)
    return {
        "candidate_count": total,
        "gold_strong_count": gold_strong,
        "gold_strong_share": round(gold_strong / total, 4) if total else 0,
        "below_acceptable_count": below_acceptable,
        "candidate_quality_status": (
            "PASS_FOR_RESEARCH_REGISTER"
            if total and below_acceptable == 0
            else "BLOCKED"
        ),
    }


def validate_observations(
    raw_rows: list[dict[str, str]],
    known_project_ids: set[str],
    source_ids: set[str],
    blockers: list[str],
) -> dict[str, int]:
    conflicts: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in raw_rows:
        project_id = row.get("project_id", "")
        source_id = row.get("source_id", "")
        evidence_class = row.get("evidence_class", "")
        if project_id not in known_project_ids:
            blockers.append(f"G3_OBSERVATION_PROJECT_UNREGISTERED:{project_id}")
        if source_id not in source_ids:
            blockers.append(f"G3_OBSERVATION_SOURCE_UNREGISTERED:{row.get('observation_id', '')}")
        if evidence_class not in EVIDENCE_CLASSES:
            blockers.append(f"G2_EVIDENCE_CLASS_INVALID:{row.get('observation_id', '')}")
        key = (project_id, row.get("entity_id", ""), row.get("parameter", ""))
        conflicts[key].add(row.get("value", ""))
    unresolved = sum(len(values) > 1 for values in conflicts.values())
    if unresolved:
        blockers.append(f"G7_UNRESOLVED_OBSERVATION_CONFLICTS:{unresolved}")
    return {"observation_count": len(raw_rows), "conflict_key_count": unresolved}


def selected_country_share(rows: list[dict[str, str]]) -> dict[str, float]:
    selected = [row for row in rows if "SELECTED" in row.get("selection_status", "")]
    if not selected:
        return {}
    counts: dict[str, int] = defaultdict(int)
    for row in selected:
        counts[row.get("country", "")] += 1
    total = len(selected)
    return {country: round(count / total, 4) for country, count in counts.items()}


def gate_status(blockers: list[str]) -> dict[str, str]:
    status = {f"G{i}": "PASS" for i in range(10)}
    for blocker in blockers:
        gate = blocker[:2]
        if gate in status:
            status[gate] = "BLOCKED"
    return status


def build_manifest() -> tuple[dict[str, Any], list[str]]:
    config = json.loads((ROOT / "config" / "v5_global.yml").read_text(encoding="utf-8"))
    source_rows = read_csv(EVIDENCE / "GLOBAL_SOURCE_REGISTER.csv")
    pack_rows = read_csv(EVIDENCE / "COUNTRY_BENCHMARK_PACKS.csv")
    master_rows = read_csv(PUBLIC / "project_master_real.csv")
    overlay_rows = read_csv(PUBLIC / "project_assumption_overlay.csv")
    raw_rows = read_csv(PUBLIC / "raw_project_observations.csv")
    candidate_rows = read_csv(CANDIDATES)
    scoring_rows = read_csv(SCORING)
    blockers: list[str] = []

    validate_columns(
        EVIDENCE / "GLOBAL_SOURCE_REGISTER.csv",
        {"source_id", "source_url", "source_tier", "access_status"},
        blockers,
    )
    validate_columns(
        PUBLIC / "project_master_real.csv",
        {"project_id", "country", "benchmark_pack_id", "evidence_grade", "model_mode", "data_quality_status"},
        blockers,
    )
    validate_columns(
        PUBLIC / "project_assumption_overlay.csv",
        {"project_id", "parameter", "evidence_class", "review_status"},
        blockers,
    )
    validate_columns(
        PUBLIC / "raw_project_observations.csv",
        {"observation_id", "project_id", "entity_id", "parameter", "evidence_class", "source_id"},
        blockers,
    )
    validate_columns(
        CANDIDATES,
        {"candidate_id", "project_id", "source_ids", "coverage_score", "evidence_grade"},
        blockers,
    )
    validate_columns(
        SCORING,
        {"candidate_id", "total_score", "evidence_grade"},
        blockers,
    )

    source_ids = {row.get("source_id") for row in source_rows}
    if len(source_ids) != len(source_rows) or None in source_ids or "" in source_ids:
        blockers.append("G0_SOURCE_REGISTER_DUPLICATE_OR_EMPTY_ID")
    for row in source_rows:
        if row.get("source_tier") not in SOURCE_TIERS:
            blockers.append(f"G2_SOURCE_TIER_INVALID:{row.get('source_id', '')}")
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
        if row.get("primary_source_id") not in source_ids:
            blockers.append(f"G3_PRIMARY_SOURCE_UNREGISTERED:{project_id}")
        if row.get("evidence_grade") not in {"GOLD", "STRONG", "ACCEPTABLE"}:
            blockers.append(f"G0_EVIDENCE_GRADE_BELOW_ACCEPTABLE:{project_id}")
        if row.get("model_mode") != "FULL_RECONSTRUCTION":
            blockers.append(f"G5_NOT_FULL_RECONSTRUCTION:{project_id}")
        if row.get("data_quality_status", "").startswith("BLOCKED"):
            blockers.append(f"G0_DATA_QUALITY_BLOCKED:{project_id}")
        if row.get("evidence_class") not in EVIDENCE_CLASSES:
            blockers.append(f"G2_EVIDENCE_CLASS_INVALID:{project_id}")

    candidate_metrics = validate_candidate_register(candidate_rows, scoring_rows, source_ids, blockers)
    known_ids = set(row.get("project_id", "") for row in master_rows) | set(row.get("project_id", "") for row in candidate_rows)
    observation_metrics = validate_observations(raw_rows, known_ids, source_ids, blockers)

    minimum = int(config["portfolio"]["minimum_projects"])
    if len(master_rows) < minimum:
        blockers.append(f"G5_MINIMUM_PROJECT_UNIVERSE_NOT_MET:{len(master_rows)}<{minimum}")
    packs_not_ready = [row["benchmark_pack_id"] for row in pack_rows if row.get("status") != "READY_FOR_ECONOMICS"]
    if packs_not_ready:
        blockers.append("G4_BENCHMARK_PACKS_NOT_READY:" + "|".join(packs_not_ready))

    selected_share = selected_country_share(master_rows)
    hard_max = float(config["portfolio"]["hard_max_country_share"])
    if selected_share and max(selected_share.values()) > hard_max:
        blockers.append("G6_COUNTRY_CONCENTRATION_HARD_MAX:" + json.dumps(selected_share, sort_keys=True))
    if any("BANKABLE" in row.get("selection_status", "").upper() for row in master_rows):
        blockers.append("G8_CLAIM_BOUNDARY_BANKABLE_STATUS_FORBIDDEN")
    if any("SELECTED" in row.get("selection_status", "") for row in master_rows) and candidate_metrics["gold_strong_share"] < 0.70:
        blockers.append("G5_SELECTED_UNIVERSE_GOLD_STRONG_SHARE_BELOW_70_PCT")
    if not config["release"]["recruiter_ready_when_blocked"]:
        pass
    else:
        blockers.append("G9_RELEASE_CONTROL_CONFIG_INVALID")

    evidence = count_evidence(raw_rows + overlay_rows)
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
        "candidate_quality": candidate_metrics,
        "observation_validation": observation_metrics,
        "selected_country_share": selected_share,
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
        "gate_status": gate_status(sorted(set(blockers))),
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
    print(json.dumps({"release_status": manifest["release_status"], "project_count": manifest["project_count"], "candidate_count": manifest["candidate_count"], "blocker_count": len(blockers), "blockers": blockers}, ensure_ascii=False))
    return 0 if args.allow_incomplete or not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
