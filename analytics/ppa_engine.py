"""PPA frontier primitives; exact PPA is optional for FRONTIER_ONLY."""
def negotiation_zone(customer_ceiling,sponsor_floor,lender_floor,tolerance=1e-9):
    lower=max(float(sponsor_floor),float(lender_floor));upper=float(customer_ceiling);feasible=lower<=upper+float(tolerance)
    return {"lower_bound_local_per_kwh":lower,"upper_bound_local_per_kwh":upper,"status":"FEASIBLE_ZONE" if feasible else "EMPTY_ZONE","action":"PROCEED" if feasible else "RENEGOTIATE_OR_REJECT"}
def solve_floor(low,high,fn,target=0.0,iterations=80):
    for _ in range(iterations):
        mid=(float(low)+float(high))/2
        if fn(mid)>=target: high=mid
        else: low=mid
    return (float(low)+float(high))/2
