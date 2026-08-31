"""Period-by-period FX translation and break-even stress solving."""

from __future__ import annotations


def fx_path(base_fx, depreciation, periods):
    values = []
    fx = float(base_fx)
    for _ in range(periods):
        fx *= 1.0 + float(depreciation)
        values.append(fx)
    return values


def translate_usd_debt_service(usd_service, base_fx, depreciation):
    return [
        float(service) * fx
        for service, fx in zip(usd_service, fx_path(base_fx, depreciation, len(usd_service)))
    ]


def break_even_depreciation(
    npv_vnd,
    usd_service,
    cfads,
    base_fx,
    discount_rate=0.14,
    low=0.0,
    high=0.20,
    iterations=60,
):
    """Solve the VND/USD depreciation where the discounted equity value is zero."""
    del npv_vnd
    def value(depreciation):
        translated = translate_usd_debt_service(usd_service, base_fx, depreciation)
        return sum(
            (float(cash) - float(service))
            / ((1.0 + discount_rate) ** index)
            for index, (cash, service) in enumerate(zip(cfads, translated), start=1)
        )
    low_value = value(low)
    high_value = value(high)
    if low_value < 0.0:
        return low
    if high_value > 0.0:
        return high
    for _ in range(iterations):
        mid = (low + high) / 2.0
        if value(mid) > 0.0:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0
