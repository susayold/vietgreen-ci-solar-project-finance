"""Single V5 public-data model boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
MODES={"FULL_RECONSTRUCTION","PARTIAL_RECONSTRUCTION","FRONTIER_ONLY","SCREENING_ONLY"}
@dataclass(frozen=True)
class ProjectModelInput:
    project: Mapping[str,Any]
    benchmark_pack: Mapping[str,Any]
    assumptions: Sequence[Mapping[str,Any]]
    market_module: Any
    model_mode: str
    local_currency: str
    operating_life_years: int
    ppa_tenor_years: int|None
    debt_tenor_years: int|None
    terminal_branch: str
def require_model_eligible(project:Mapping[str,Any], assumptions:Sequence[Mapping[str,Any]]|None=None)->None:
    missing=[k for k in ("project_id","country","benchmark_pack_id","model_mode") if not project.get(k)]
    if missing: raise ValueError("V5 identity fields missing: "+", ".join(missing))
    mode=project["model_mode"]
    if mode not in MODES: raise ValueError("unsupported V5 model mode")
    if mode=="FULL_RECONSTRUCTION":
        missing=[k for k in ("installed_capacity_kwp","annual_generation_kwh","currency") if not project.get(k)]
        if missing: raise ValueError("FULL_RECONSTRUCTION requires observed core fields: "+", ".join(missing))
    if mode=="PARTIAL_RECONSTRUCTION":
        got={a.get("parameter") for a in (assumptions or [])}
        missing=[k for k in ("annual_generation_kwh","ppa_price_local_per_kwh","project_cost_local","financing_amount_local","operating_horizon_years") if k not in got]
        if missing: raise ValueError("PARTIAL_RECONSTRUCTION missing overlay parameters: "+", ".join(missing))
def build_project_cash_flow(project,benchmark_pack,assumptions,market_module):
    require_model_eligible(project,assumptions)
    mode=project["model_mode"]
    return {"project_id":project["project_id"],"status":"ECONOMICS_ALLOWED" if mode in {"FULL_RECONSTRUCTION","PARTIAL_RECONSTRUCTION"} else "FRONTIER_OR_SCREENING_ONLY","model_mode":mode,"currency":project.get("currency"),"evidence_boundary":"PUBLIC_DATA_RECONSTRUCTION_ONLY"}
