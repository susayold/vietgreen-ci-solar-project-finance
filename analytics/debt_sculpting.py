def backward_capacity(cfads, rate, sculpting_dscr):
    closing = 0.0
    opening = []
    service = []
    for cash in reversed(cfads):
        ds = cash / sculpting_dscr
        op = (closing + ds) / (1.0 + rate)
        opening.append(op)
        service.append(ds)
        closing = op
    opening.reverse()
    service.reverse()
    return opening[0] if opening else 0.0, service

def forward_rebuild(initial_debt, cfads, rate, sculpting_dscr):
    debt = initial_debt
    rows = []
    for cash in cfads:
        debt_service = min(cash / sculpting_dscr, debt * (1 + rate))
        interest = debt * rate
        principal = max(0.0, debt_service - interest)
        closing = max(0.0, debt - principal)
        rows.append({
            "opening": debt,
            "interest": interest,
            "principal": principal,
            "debt_service": interest + principal,
            "closing": closing,
            "dscr": cash / debt_service if debt_service else None,
        })
        debt = closing
    return rows
