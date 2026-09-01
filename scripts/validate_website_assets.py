#!/usr/bin/env python3
"""Fail-closed validation of website local links, hash routes and required assets."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
INDEX = WEBSITE / "index.html"
EXPECTED_ROUTES = ("overview", "case", "economics", "debt", "portfolio", "risk", "model", "evidence")
REQUIRED_FILES = (
    INDEX,
    WEBSITE / "app.js",
    WEBSITE / "styles.css",
    WEBSITE / "model_preview" / "index.html",
)
errors: list[str] = []


def add_error(message: str) -> None:
    errors.append(message)


def check_local_reference(source: Path, reference: str) -> None:
    value = reference.strip()
    if not value or value.startswith(("#", "http://", "https://", "//", "data:", "$" + "{")):
        return
    value = value.split("#", 1)[0].split("?", 1)[0]
    if not value:
        return
    target = (source.parent / value).resolve()
    try:
        target.relative_to(WEBSITE.resolve())
    except ValueError:
        add_error(f"reference escapes website: {source.relative_to(ROOT)} -> {reference}")
        return
    if not target.exists():
        add_error(f"missing local asset: {source.relative_to(ROOT)} -> {reference}")


def check_hash_routes(text: str, source: Path) -> None:
    for route in re.findall(r'href\s*=\s*["\']#/?([^"\']*)', text):
        route = route.split("?", 1)[0].strip("/")
        if route and route not in EXPECTED_ROUTES:
            add_error(f"unknown hash route in {source.relative_to(ROOT)}: {route}")


for required in REQUIRED_FILES:
    if not required.exists():
        add_error(f"missing required website file: {required.relative_to(ROOT)}")

for source in WEBSITE.rglob("*"):
    if not source.is_file():
        continue
    if source.suffix.lower() in {".html", ".js", ".css"}:
        text = source.read_text(encoding="utf-8", errors="ignore")
        check_hash_routes(text, source)
    if source.suffix.lower() == ".html":
        text = source.read_text(encoding="utf-8", errors="ignore")
        for reference in re.findall(r'\b(?:href|src)\s*=\s*["\']([^"\']+)["\']', text):
            check_local_reference(source, reference)
    if source.suffix.lower() == ".css":
        text = source.read_text(encoding="utf-8", errors="ignore")
        for reference in re.findall(r'url\(\s*["\']?([^)"\']+)', text):
            check_local_reference(source, reference)

for route in EXPECTED_ROUTES:
    path = WEBSITE / "data" / f"{route}.json"
    if not path.exists():
        add_error(f"missing route data: {path.relative_to(ROOT)}")
    else:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            add_error(f"invalid route JSON {path.relative_to(ROOT)}: {exc}")

for path in (WEBSITE / "data").glob("*.json"):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add_error(f"invalid data JSON {path.relative_to(ROOT)}: {exc}")

if errors:
    print("Website link/asset validation FAILED")
    print("\n".join(f"- {error}" for error in errors))
    raise SystemExit(1)

print(f"Website link/asset validation PASS: {len(EXPECTED_ROUTES)} routes, local HTML/CSS references and data JSON checked")
