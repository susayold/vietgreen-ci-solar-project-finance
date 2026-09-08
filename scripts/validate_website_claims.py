"""Catch forbidden browser data sources and over-claims in the website source."""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app"
FORBIDDEN = (
    "raw.githubusercontent.com",
    'href="/model"',
    "BANKABLE: YES",
    "LENDER APPROVED: YES",
    "IC APPROVED: YES",
    "SCREENING_ADAPTER",
    "NO POSITIVE IRR",
    "Raw frozen value: -0.99",
    "pending-build-sha",
    "pending-run-id",
    "101.182",
    "P19-0057",
    "P19-0155",
    "P19-0118",
    "P19-0176",
    "INPUT ASSUMPTION</span>",
    "REMOTE ONLY",
    "REMOTE-ONLY POLICY",
    "Frozen Release",
    "recruiter-final",
    "26 / 26",
    "26/26",
)


def main():
    failures = []
    physical = json.loads((ROOT / 'public/data/physical.json').read_text(encoding='utf-8'))
    # Frozen analytics/physical_sanity.py: upper 1600 * extreme multiplier 2.
    if physical['screeningBand'] != {'minKwhKwp': 900, 'maxKwhKwp': 1600, 'extremeUpperKwhKwp': 3200}:
        failures.append('Physical screening policy differs from frozen model policy')
    for path in SOURCE.rglob("*.tsx"):
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token in text:
                failures.append(f"{path.relative_to(ROOT)} contains {token!r}")
    if failures:
        raise SystemExit("\n".join(failures))
    print("website claim/source validation: PASS")


if __name__ == "__main__":
    main()

