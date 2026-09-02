#!/usr/bin/env python3
import json, os
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"website"/"public"/"data"/"release.json"
d=json.loads(p.read_text(encoding="utf-8"))
assert d["modelSha"]=="ff69e15d211ff1abc88200574242ed2f1db49074"
assert d["modelTag"]=="v5.1.3-recruiter-final" and d["modelFrozen"] is True
expected=os.getenv("GITHUB_SHA") or os.getenv("WEBSITE_SOURCE_SHA")
if expected and expected!="CI_PENDING": assert d["websiteSourceSha"]==expected,(d["websiteSourceSha"],expected)
assert d["websiteType"]=="CV_FROM_SCRATCH" and d["remoteOnly"] is True and len(d["routes"])==8
print("release identity PASS:",d["modelSha"],d["websiteSourceSha"])
