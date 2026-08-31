"""Debt sizing and forward roll-forward helpers."""

from __future__ import annotations


def annuity_factor(rate, periods):
    if periods <= 0:
        return 0.0
    if abs(rate) < 1e-12:
        return float(periods)
    return (1.0 - (1.0 + rate) ** (-periods)) / rate


def backward_capacity(cfads, rate, sculpting_dscr):
    """Size debt by reverse-solving DSCR-constrained debt service."""
    closing = 0.0
    openings = []
    services = []
    for cash in reversed([max(0.0, float(value)) for value in cfads]):
        service = cash / sculpting_dscr if sculpting_dscr else 0.0
        opening = (closing + service) / (1.0 + rate)
        openings.append(opening)
        services.append(service)
        closing = opening
    openings.reverse()
    services.reverse()
    return (openings[0] if openings else 0.0), services


def forward_rebuild(initial_debt, cfads, rate, sculpting_dscr):
    """Rebuild interest, principal and closing balance period by period."""
    debt = max(0.0, float(initial_debt))
    rows = []
    for cash in cfads:
        cash = max(0.0, float(cash))
        if debt <= 1e-8:
            rows.append(
                {"opening": 0.0, "interest": 0.0, "principal": 0.0, "debt_service": 0.0, "closing": 0.0, "dscr": None}
            )
            continue
        max_service = debt * (1.0 + rate)
        target_service = cash / sculpting_dscr if sculpting_dscr else 0.0
        debt_service = min(target_service, max_service)
        interest = debt * rate
        principal = max(0.0, min(debt, debt_service - interest))
        closing = max(0.0, debt - principal)
        rows.append(
            {
                "opening": debt,
                "interest": interest,
                "principal": principal,
                "debt_service": interest + principal,
                "closing": closing,
                "dscr": cash / (interest + principal) if interest + principal else None,
            }
        )
        debt = closing
    return rows


def discounted_value(values, rate):
    return sum(float(value) / ((1.0 + rate) ** index) for index, value in enumerate(values, start=1))


def coverage_ratio(cfads, debt_service):
    values = [float(value) for value in cfads]
    services = [float(value) for value in debt_service]
    return min((cash / service for cash, service in zip(values, services) if service > 0), default=0.0)
