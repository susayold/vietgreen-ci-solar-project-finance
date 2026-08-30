from math import sqrt

def p50_p90(capacity_kwp, pvout_kwh_kwp, uncertainty_pct):
    p50 = capacity_kwp * pvout_kwh_kwp
    p90 = p50 * (1.0 - 1.2816 * uncertainty_pct)
    if p90 > p50: raise ValueError('P90 must not exceed P50')
    return p50, max(0.0, p90)

def degradation(generation_y1, rate, year):
    return generation_y1 * (1.0 - rate) ** max(0, year - 1)
