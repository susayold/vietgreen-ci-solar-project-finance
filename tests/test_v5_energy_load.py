from analytics.load_match_8760 import profile
def test_8760_invariants():
 p=profile(100000,90000)
 assert p["hour_count"]==8760
 assert abs(sum(p["load"])-100000)<1e-6
 assert abs(sum(p["solar"])-90000)<1e-6
 assert all(x<=y+1e-9 for x,y in zip(p["self_consumed"],p["load"]))
 assert all(x<=y+1e-9 for x,y in zip(p["self_consumed"],p["solar"]))
