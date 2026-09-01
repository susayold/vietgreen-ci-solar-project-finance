from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]


def test_v5_config_is_dynamic():
    config = json.loads((ROOT / "config" / "v5_global.yml").read_text(encoding="utf-8"))
    portfolio = config["portfolio"]
    assert portfolio["minimum_projects"] == 15
    assert portfolio["target_projects"] == 20
    assert portfolio["maximum_projects"] == 25


def test_v5_master_has_no_v4_ids():
    with (ROOT / "data" / "public" / "project_master_real.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert all(not row["project_id"].startswith("VG-") for row in rows)


def test_v5_candidate_sources_are_registered():
    with (ROOT / "research" / "GLOBAL_PROJECT_CANDIDATES.csv").open(newline="", encoding="utf-8") as handle:
        candidates = list(csv.DictReader(handle))
    with (ROOT / "evidence" / "GLOBAL_SOURCE_REGISTER.csv").open(newline="", encoding="utf-8") as handle:
        sources = {row["source_id"] for row in csv.DictReader(handle)}
    assert candidates
    assert all(set(row["source_ids"].split("|")).issubset(sources) for row in candidates)


def test_v5_release_is_blocked_before_freeze():
    manifest = json.loads((ROOT / "release" / "MODEL_RELEASE_MANIFEST_V5.json").read_text(encoding="utf-8"))
    assert manifest["release_status"] == "INPUT_DATA_BLOCKED"
    assert manifest["recruiter_ready"] is False
    assert manifest["base_project_npv_usd"] is None
