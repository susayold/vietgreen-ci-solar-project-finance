"""Three-sided PPA negotiation-zone calculations."""
from __future__ import annotations


def negotiation_zone(customer_ceiling, sponsor_floor, lender_floor, tolerance=0.01):
    lower = max(float(sponsor_floor), float(lender_floor))
    upper = float(customer_ceiling)
    feasible = lower <= upper + float(tolerance)
    return {
        "lower_bound_vnd_kwh": lower, "upper_bound_vnd_kwh": upper,
        "status": "FEASIBLE_ZONE" if feasible else "EMPTY_ZONE",
        "action": "PROCEED" if feasible else "RENEGOTIATE_OR_REJECT",
        "tolerance_vnd_kwh": float(tolerance),
    }