"""Inject cached formula results into the recruiter workbook OOXML.

openpyxl intentionally writes formula cells without cached <v> results. That is
fine for desktop Excel, which recalculates on open, but Office web preview and
some browser viewers can render those cells as blank. This post-processor keeps
the formulas intact and adds deterministic cached values for the default
VG-001 presentation view.
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path, PurePosixPath
from tempfile import NamedTemporaryFile
from xml.etree import ElementTree as ET

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN, "r": OFFICE_REL, "pr": PACKAGE_REL}
ET.register_namespace("", MAIN)
ET.register_namespace("r", OFFICE_REL)


def _load_cache(paths: list[Path]) -> dict[str, dict[str, object]]:
    merged: dict[str, dict[str, object]] = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for sheet, cells in payload.items():
            merged.setdefault(sheet, {}).update(cells)
    return merged


def _sheet_targets(files: dict[str, bytes]) -> tuple[dict[str, str], ET.Element]:
    workbook = ET.fromstring(files["xl/workbook.xml"])
    rels = ET.fromstring(files["xl/_rels/workbook.xml.rels"])
    rel_by_id = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall("pr:Relationship", NS)
    }
    targets: dict[str, str] = {}
    for sheet in workbook.findall("m:sheets/m:sheet", NS):
        name = sheet.attrib["name"]
        rid = sheet.attrib[f"{{{OFFICE_REL}}}id"]
        target = rel_by_id[rid]
        if target.startswith("/"):
            target = target.lstrip("/")
        elif not target.startswith("xl/"):
            target = str(PurePosixPath("xl") / target)
        targets[name] = target
    return targets, workbook


def _set_cached_value(cell: ET.Element, value: object) -> None:
    formula = cell.find("m:f", NS)
    if formula is None:
        raise ValueError(f"Cached-value target {cell.attrib.get('r')} is not a formula cell")
    value_node = cell.find("m:v", NS)
    if value_node is None:
        value_node = ET.SubElement(cell, f"{{{MAIN}}}v")

    if isinstance(value, bool):
        cell.set("t", "b")
        value_node.text = "1" if value else "0"
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        cell.attrib.pop("t", None)
        value_node.text = repr(value)
    elif value is None:
        cell.attrib.pop("t", None)
        value_node.text = None
    else:
        cell.set("t", "str")
        value_node.text = str(value)


def inject_cached_values(workbook_path: Path, cache_paths: list[Path]) -> None:
    cache = _load_cache(cache_paths)
    with zipfile.ZipFile(workbook_path, "r") as src:
        infos = src.infolist()
        files = {info.filename: src.read(info.filename) for info in infos}

    targets, workbook = _sheet_targets(files)
    patched = 0
    for sheet_name, cells in cache.items():
        target = targets.get(sheet_name)
        if target is None:
            raise KeyError(f"Workbook is missing cached-value sheet: {sheet_name}")
        root = ET.fromstring(files[target])
        index = {
            cell.attrib.get("r"): cell
            for cell in root.findall(".//m:c", NS)
            if cell.attrib.get("r")
        }
        for address, value in cells.items():
            cell = index.get(address)
            if cell is None:
                raise KeyError(f"Workbook is missing cached-value cell: {sheet_name}!{address}")
            _set_cached_value(cell, value)
            patched += 1
        files[target] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    calc_pr = workbook.find("m:calcPr", NS)
    if calc_pr is None:
        calc_pr = ET.SubElement(workbook, f"{{{MAIN}}}calcPr")
    calc_pr.set("calcMode", "auto")
    calc_pr.set("fullCalcOnLoad", "1")
    calc_pr.set("forceFullCalc", "1")
    files["xl/workbook.xml"] = ET.tostring(workbook, encoding="utf-8", xml_declaration=True)

    with NamedTemporaryFile(delete=False, suffix=".xlsx", dir=workbook_path.parent) as tmp:
        tmp_path = Path(tmp.name)
    try:
        with zipfile.ZipFile(tmp_path, "w") as dst:
            for info in infos:
                dst.writestr(info, files[info.filename])
        tmp_path.replace(workbook_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    print(f"Injected cached results into {patched} recruiter workbook formula cells")


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(
            "usage: inject_recruiter_workbook_cache.py WORKBOOK.xlsx CACHE1.json [CACHE2.json ...]"
        )
    workbook_path = Path(sys.argv[1]).resolve()
    cache_paths = [Path(p).resolve() for p in sys.argv[2:]]
    inject_cached_values(workbook_path, cache_paths)


if __name__ == "__main__":
    main()
