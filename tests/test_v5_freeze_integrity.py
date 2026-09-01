import json, re
from pathlib import Path

def test_ci_freeze_contains_real_hashes_and_timestamp():
    freeze=json.loads(Path("release/V5_1_1_INPUT_FREEZE_MANIFEST.json").read_text(encoding="utf-8"))
    assert freeze["manifest_version"]=="V5.1.1"
    assert re.fullmatch(r"[0-9a-f]{40}", freeze["code_sha"])
    assert re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", freeze["freeze_date_utc"])
    assert len(freeze["input_sha256"])>=6
    assert all(re.fullmatch(r"[0-9a-f]{64}", value) for value in freeze["input_sha256"].values())
    runtime=json.loads(Path("release/V5_RUNTIME_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    assert re.fullmatch(r"[0-9a-f]{40}", runtime["source_sha"])
    assert all(re.fullmatch(r"[0-9a-f]{64}", value) for value in runtime["input_hashes"].values())
    assert "RUNTIME_SHA_REQUIRED" not in json.dumps(runtime)
