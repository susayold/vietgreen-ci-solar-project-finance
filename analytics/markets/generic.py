"""Generic V5 tariff interface; no default numeric tariff is allowed."""
from __future__ import annotations
from typing import Any, Mapping

def customer_energy_cost(project: Mapping[str, Any], market_data: Mapping[str, Any]) -> dict[str, Any]:
    if market_data.get("status") != "READY_FOR_ECONOMICS":
        raise ValueError("market pack is not ready for economics")
    if not market_data.get("tariff"):
        raise ValueError("validated tariff input is required")
    return {"project_id": project["project_id"], "currency": market_data["currency"], "status": "OBSERVED_OR_RECONSTRUCTED_TARIFF_REQUIRED"}
