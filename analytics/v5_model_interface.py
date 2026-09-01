"""V5 model boundary.

V4 synthetic engines remain historical on main and are not reused as V5 facts.
This module defines the only input contract permitted for future V5 economics.
It deliberately fails closed when an asset-level public-data record is incomplete.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class ProjectModelInput:
    project: Mapping[str, Any]
    benchmark_pack: Mapping[str, Any]
    assumptions: Sequence[Mapping[str, Any]]
    market_module: Any
    model_mode: str
    local_currency: str
    operating_life_years: int
    ppa_tenor_years: int | None
    debt_tenor_years: int | None
    terminal_branch: str


def require_model_eligible(project: Mapping[str, Any]) -> None:
    required = ("project_id", "country", "benchmark_pack_id", "model_mode")
    missing = [key for key in required if not project.get(key)]
    if missing:
        raise ValueError("V5 project missing required identity fields: " + ", ".join(missing))
    if project.get("model_mode") not in {"FULL_RECONSTRUCTION", "PARTIAL_RECONSTRUCTION", "FRONTIER_ONLY", "SCREENING_ONLY"}:
        raise ValueError("unsupported V5 model mode")
    if project.get("model_mode") != "FULL_RECONSTRUCTION":
        raise ValueError("asset-level economics are blocked unless model_mode=FULL_RECONSTRUCTION")
    for key in ("installed_capacity_kwp", "annual_generation_kwh", "currency"):
        if not project.get(key):
            raise ValueError(f"asset-level V5 field not disclosed: {key}")


def build_project_cash_flow(project: Mapping[str, Any], benchmark_pack: Mapping[str, Any], assumptions: Sequence[Mapping[str, Any]], market_module: Any) -> dict[str, Any]:
    """Reserved V5 entry point; no economics before input freeze and eligibility."""
    require_model_eligible(project)
    years = int(project.get("model_horizon_years") or project.get("operating_life_years") or 0)
    if not 1 <= years <= 30:
        raise ValueError("V5 horizon must be project-specific and within 1..30 years")
    return {
        "project_id": project["project_id"],
        "status": "READY_FOR_ECONOMICS_AFTER_FREEZE",
        "currency": project["currency"],
        "years": years,
        "evidence_boundary": "PUBLIC_DATA_RECONSTRUCTION_ONLY",
    }
