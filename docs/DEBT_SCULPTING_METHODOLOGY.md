# Debt sculpting methodology

## Standalone sizing

For each eligible project, debt capacity is bounded by:

- DSCR capacity from annual CFADS;
- LLCR capacity from discounted CFADS;
- PLCR capacity from discounted CFADS including the modeled tail;
- leverage cap;
- minimum debt and tail rules.

The minimum binding capacity is selected, then a forward debt schedule is rebuilt and checked for debt close, coverage and tail.

## Pooled facility

The pooled facility is sized from aggregate selected-project CFADS and the same coverage and leverage concepts. A feedback loop rebuilds project cash flows with the pooled allocations, recalculates CFADS and debt service, and repeats until convergence. The latest run converged in 2 iterations.

The pooled amount equals the displayed standalone sum in this candidate because the current synthetic terms and linear aggregation make the independent capacity sum binding. This equality is an observed output, not a hard-coded pooled-debt assumption.

## Limitations

Annual screening debt service does not substitute for lender-specific covenant, reserve, hedge, default, intercreditor or security documentation. P90 debt sizing and final lender sizing remain open diligence gates.

