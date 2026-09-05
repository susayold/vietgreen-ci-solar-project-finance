"""Catch forbidden browser data sources and over-claims in the website source."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app"
FORBIDDEN = (
    "raw.githubusercontent.com",
    'href="/model"',
    "BANKABLE: YES",
    "LENDER APPROVED: YES",
    "IC APPROVED: YES",
)


def main():
    failures = []
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


