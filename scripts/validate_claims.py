#!/usr/bin/env python3
"""Fail positive transaction claims while allowing explicit boundary disclaimers."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
paths=[ROOT/"website"/"src",ROOT/"website"/"public"/"data"]
negative=re.compile(r"\b(?:not|no|never|does not|do not|without|disabled|false|missing|open|indeterminate|≠)\b",re.I)
for base in paths:
    if not base.exists(): continue
    for path in base.rglob("*"):
        if path.suffix not in {".tsx",".json"}: continue
        text=path.read_text(encoding="utf-8")
        for phrase in ["executed PPA","bankable PPA","actual PPA","transaction-ready","transaction ready","lender approval","IC approval","approved loan","realized return"]:
            for match in re.finditer(re.escape(phrase),text,re.I):
                context=text[max(0,match.start()-70):match.start()]\n                if not negative.search(context) and "≠" not in context:
                    raise SystemExit(f"positive claim boundary violation: {phrase} in {path}")
print("claim boundary validation PASS")
