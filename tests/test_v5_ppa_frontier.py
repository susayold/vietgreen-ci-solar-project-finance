from analytics.ppa_engine import negotiation_zone,solve_floor
def test_frontier_zone_is_deterministic():
 z=negotiation_zone(10,7,8)
 assert z["lower_bound_local_per_kwh"]==8 and z["upper_bound_local_per_kwh"]==10
 assert z["status"]=="FEASIBLE_ZONE"
 assert solve_floor(0,10,lambda x:x,5)==5
