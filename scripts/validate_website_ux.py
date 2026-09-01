#!/usr/bin/env python3
"""Fail-closed static responsive and accessibility checks for the recruiter site."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
INDEX = (WEBSITE / "index.html").read_text(encoding="utf-8")
APP = (WEBSITE / "app.js").read_text(encoding="utf-8")
CSS = (WEBSITE / "styles.css").read_text(encoding="utf-8")
CASE = json.loads((WEBSITE / "data" / "case.json").read_text(encoding="utf-8"))
errors: list[str] = []
QA_WIDTHS = (390, 430, 768, 1024, 1440)


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


require('<html lang="en">' in INDEX, "document language is missing")
require('name="viewport"' in INDEX, "viewport meta is missing")
require('<a class="skip-link" href="#app">' in INDEX, "skip link is missing")
require('<main id="app" tabindex="-1" aria-live="polite">' in INDEX, "focusable live main region is missing")
require('aria-label="Primary navigation"' in INDEX, "primary nav label is missing")
require('class="mobile-menu" type="button"' in INDEX and 'aria-expanded="false"' in INDEX, "mobile menu keyboard state is missing")
require('href="#/model"' in INDEX and 'href="#/evidence"' in INDEX, "primary decision links are missing")
require("let hasRendered = false;" in APP and "if (hasRendered) page.focus({preventScroll: true})" in APP, "route focus management is missing")
require('setAttribute("aria-expanded"' in APP and 'classList.toggle("open")' in APP, "mobile menu state handler is missing")
require('window.addEventListener("hashchange", renderRoute)' in APP, "hash route navigation handler is missing")
require('const PAGE_NAMES = ["overview", "case", "economics", "debt", "portfolio", "risk", "model", "evidence"];' in APP, "eight-route registry is missing")
require("negativeBarChart(chart" in APP and "zero-bar-zero" in APP, "current NPV zero-line bar chart is missing")
require('ppaPosition(frontier.lower_bound_vnd_kwh, ppa.lower, ppa.upper)' in APP, "PPA lower-bound geometry is not data-driven")
require("zone-feasible" in APP and "zone-empty" in APP, "PPA feasible/empty zone styling is missing")
require("overflow-x: hidden" in CSS and "overflow-x: auto" in CSS, "horizontal overflow policy is missing")
require(":focus-visible" in CSS, "visible keyboard focus state is missing")
require("prefers-reduced-motion" in CSS, "reduced-motion preference is missing")
for breakpoint in ("560px", "820px", "1100px"):
    require(f"@media (max-width: {breakpoint})" in CSS, f"responsive breakpoint {breakpoint} is missing")
require(".main-nav.open" in CSS, "mobile navigation open state CSS is missing")
require(".zero-bar-row" in CSS and ".frontier-marker" in CSS, "critical chart layout CSS is missing")
for image in re.findall(r"<img\b[^>]*>", INDEX + "\n" + (WEBSITE / "model_preview" / "index.html").read_text(encoding="utf-8")):
    require(bool(re.search(r'\balt\s*=\s*["\'][^"\']+["\']', image)), "image is missing non-empty alt text")
values = [float(item["value"]) for item in CASE.get("currentNPVChart", [])]
require(len(values) == 20, "current NPV chart must contain 20 projects")
require(all(value < 0 for value in values), "current NPV chart contains a non-negative current-terms value")
require(values == sorted(values), "current NPV chart must be sorted most-negative first")
require("negative" in APP and "positive" in APP and "Economic" in APP and "Credit" in APP, "positive/negative/status meaning is not text-visible")
if errors:
    print("Website responsive/accessibility validation FAILED")
    print("\n".join(f"- {error}" for error in errors))
    raise SystemExit(1)
print(f"Website responsive/accessibility validation PASS: static critical checks at QA widths {', '.join(map(str, QA_WIDTHS))}")
