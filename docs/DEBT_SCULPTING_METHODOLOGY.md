# DEBT_SCULPTING_METHODOLOGY

Debt sizing applies hard caps in this order:

1. DSCR capacity from forecast CFADS and sizing DSCR;
2. LLCR capacity from discounted CFADS and LLCR floor;
3. leverage capacity from CAPEX and leverage cap.

The binding amount is the minimum of the three. Backward sizing uses:

OpeningDebt_t = (DebtService_t + ClosingDebt_t) / (1 + rate)

Forward rebuild uses:

ClosingDebt_t = max(0, OpeningDebt_t − Principal_t)

and must close to zero at maturity within DEBT_CLOSE_TOL_VND. Interest is included once in debt service; principal is debt service less interest. A pooled facility must be re-sized from aggregate CFADS rather than summing standalone facilities.
