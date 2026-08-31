"""Deterministic annual XNPV/XIRR helpers for the V4 remote runner."""
from __future__ import annotations

from math import isfinite


def xnpv(rate, cashflows):
    rate = float(rate)
    if rate <= -1.0:
        raise ValueError("discount rate must be greater than -100%")
    return sum(float(value) / ((1.0 + rate) ** index) for index, value in enumerate(cashflows))


def xirr(cashflows, low=-0.9999, high=10.0, iterations=120):
    """Return an annual IRR or None when the cash-flow signs do not bracket a root."""
    values = [float(value) for value in cashflows]
    if not any(value < 0 for value in values) or not any(value > 0 for value in values):
        return None
    low_value = xnpv(low, values)
    high_value = xnpv(high, values)
    expansions = 0
    while low_value * high_value > 0 and expansions < 12:
        high = high * 2.0 + 1.0
        high_value = xnpv(high, values)
        expansions += 1
    if low_value * high_value > 0:
        return None
    for _ in range(iterations):
        mid = (low + high) / 2.0
        mid_value = xnpv(mid, values)
        if abs(mid_value) <= 1e-7:
            return mid
        if low_value * mid_value <= 0:
            high, high_value = mid, mid_value
        else:
            low, low_value = mid, mid_value
    result = (low + high) / 2.0
    return result if isfinite(result) else None
