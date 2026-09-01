"""Fail-closed governance checks for public claims and unsupported finance outputs."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
errors = []
for path in WEBSITE.rglob("*"):
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    for token in ("private_validation", "hidden_truth", "localhost", "password", "secret"):
        if token in text:
            errors.append(f"{token}: {path.relative_to(ROOT)}")
    for token in ("fixedvsresized", '"resized"', "0.85", "1.55"):
        if token in text:
            errors.append(f"unsupported illustrative token {token}: {path.relative_to(ROOT)}")
risk = (WEBSITE / "data" / "risk.json").read_text(encoding="utf-8")
if "fixedVsResized" in risk:
    errors.append("risk contract exposes fixedVsResized")
if errors:
    print("Public claim governance FAILED")
    print("\n".join(f"- {item}" for item in errors))
    raise SystemExit(1)
print("Public claim governance PASS: no unsupported public finance output detected")
