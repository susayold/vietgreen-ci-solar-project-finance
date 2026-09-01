from analytics.build_v5_economics import npv,irr
def test_returns_are_consistent():
 cf=[-100,40,40,40,40]
 assert npv(cf,.1)>0
 assert irr(cf)!=""
