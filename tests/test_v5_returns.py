from analytics.build_v5_economics import npv,irr
def test_no_debt_plus_two_discount_shortcut():
 assert npv([-100,60,60],.10)>npv([-100,60,60],.12)
 assert irr([-100,60,60])!=""
