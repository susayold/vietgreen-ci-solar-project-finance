"""Block known stale release claims from the public website payload."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
targets = [ROOT / "website" / "index.html", ROOT / "website" / "app.js", ROOT / "website" / "styles.css", *(ROOT / "website" / "data").glob("*.json")]
patterns = {
    "release candidate 1.2.0": "1.2.0",
    "old selected count 13": "selected 13",
    "old selected count 11": "selected 11",
    "old workflow run": "33360401233",
    "old artifact digest": "3396dce1eee9420c8c16532c30e38d7be33d4fbdf0c8da4e317af75b6a4b6f2b",
}
errors = []
for path in targets:
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    for label, pattern in patterns.items():
        if pattern.lower() in text:
            errors.append(f"{label}: {path.relative_to(ROOT)}")
if errors:
    print("Stale V3 claim check FAILED")
    print("\n".join(f"- {item}" for item in errors))
    raise SystemExit(1)
print(f"Stale V3 claim check PASS: scanned {len(targets)} public files")
