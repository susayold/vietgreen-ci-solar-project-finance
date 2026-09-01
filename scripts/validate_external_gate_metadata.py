#!/usr/bin/env python3
"""Fail-closed validation for remote-only external gate submission metadata."""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "validation" / "OPEN_EXTERNAL_GATES.csv"
REGISTER_PATH = ROOT / "validation" / "EXTERNAL_GATE_INTAKE.csv"
SUBMISSION_PATH = ROOT / "validation" / "EXTERNAL_GATE_SUBMISSIONS.csv"
MANIFEST_PATH = ROOT / "release" / "MODEL_RELEASE_MANIFEST.json"

EXPECTED = {f"EXT-{i:03d}" for i in range(1, 9)}
ALLOWED_STATUS = {"OPEN", "SUBMITTED", "UNDER_REVIEW", "CLOSED", "REJECTED"}
REQUIRED_SUBMISSION_COLUMNS = [
    "gate_id", "document_type", "issuer_or_counterparty", "document_date",
    "effective_date", "applicability_scope", "redaction_status",
    "drive_file_id_or_controlled_link", "github_metadata_commit", "sha256",
    "verifier", "verification_date", "model_update_required", "status", "notes",
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
PRIVATE_DRIVE_RE = re.compile(r"^(https://drive\.google\.com/|https://docs\.google\.com/|[A-Za-z0-9_-]{10,})")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames or []
        return fields, list(reader)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ERROR: {message}")


_, gate_rows = load_rows(GATE_PATH)
_, register_rows = load_rows(REGISTER_PATH)
submission_fields, submission_rows = load_rows(SUBMISSION_PATH)
require({row.get("gate_id") for row in gate_rows} == EXPECTED, "gate tracker must contain exactly EXT-001..EXT-008")
require({row.get("gate_id") for row in register_rows} == EXPECTED, "intake register must contain exactly EXT-001..EXT-008")
require(submission_fields == REQUIRED_SUBMISSION_COLUMNS, "submission header does not match the remote-only schema")
require(len({row.get("gate_id") for row in submission_rows}) == len(submission_rows), "one submission bundle row per gate is required")
require({row.get("gate_id") for row in submission_rows} <= EXPECTED, "submission contains an unknown gate")

for row in gate_rows + register_rows:
    require(row.get("status", row.get("current_status")) in ALLOWED_STATUS, f"unsupported status for {row.get('gate_id')}")

for row in submission_rows:
    gate_id = row["gate_id"]
    status = row["status"]
    require(status in ALLOWED_STATUS, f"unsupported submission status for {gate_id}")
    if status == "CLOSED":
        for field in REQUIRED_SUBMISSION_COLUMNS:
            require(row.get(field, "").strip() != "", f"{gate_id} CLOSED but {field} is empty")
        for field in ("document_date", "effective_date", "verification_date"):
            require(ISO_DATE_RE.fullmatch(row[field]), f"{gate_id} {field} must be ISO")
            date.fromisoformat(row[field])
        require(SHA256_RE.fullmatch(row["sha256"]), f"{gate_id} sha256 must be 64 lowercase hex characters")
        require(COMMIT_RE.fullmatch(row["github_metadata_commit"]), f"{gate_id} github_metadata_commit is invalid")
        require(PRIVATE_DRIVE_RE.match(row["drive_file_id_or_controlled_link"]), f"{gate_id} needs a controlled Drive reference")
        require(row["redaction_status"] in {"REDACTED_METADATA_ONLY", "PRIVATE_DOCUMENT_RETAINED_IN_DRIVE"}, f"{gate_id} has unsafe redaction_status")
        require(row["model_update_required"] in {"YES", "NO", "REVIEWED_NO_CHANGE"}, f"{gate_id} model_update_required is invalid")

tracker_by_id = {row["gate_id"]: row for row in gate_rows}
for row in submission_rows:
    tracker_status = tracker_by_id[row["gate_id"]]["status"]
    if row["status"] == "CLOSED":
        require(tracker_status == "CLOSED", f"{row['gate_id']} submission CLOSED but gate tracker is {tracker_status}")
    if tracker_status == "CLOSED":
        require(row["status"] == "CLOSED", f"{row['gate_id']} gate tracker CLOSED without a CLOSED submission")

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
open_gate_count = sum(row["status"] != "CLOSED" for row in gate_rows)
require(
    manifest.get("external_gate_count_open") == open_gate_count,
    "manifest external_gate_count_open does not match the gate tracker",
)
if manifest.get("recruiter_ready") is True:
    require(
        manifest.get("transaction_evidence_status") == "OPEN",
        "recruiter_ready boundary changed: transaction evidence must remain OPEN",
    )
    require(
        manifest.get("bankable_transaction_ready") is False,
        "recruiter_ready cannot imply bankable transaction readiness",
    )

print(json.dumps({
    "gate_rows": len(gate_rows),
    "submission_rows": len(submission_rows),
    "closed_submissions": sum(row["status"] == "CLOSED" for row in submission_rows),
    "gate_statuses": {row["gate_id"]: row["status"] for row in gate_rows},
    "recruiter_ready": manifest.get("recruiter_ready"),
    "result": "PASS",
}, sort_keys=True))
