from analytics.tax_engine_v5 import apply_tax_loss
def test_tl001_no_loss():
    r=apply_tax_loss(100,0,.25); assert r["tax"]==25
def test_tl002_partial_use():
    r=apply_tax_loss(50,100,.25); assert r["tax"]==0 and r["closing_loss"]==50
def test_tl003_full_use():
    r=apply_tax_loss(150,100,.25); assert r["tax"]==12.5 and r["closing_loss"]==0
def test_tl004_current_loss_adds():
    r=apply_tax_loss(-30,20,.25); assert r["tax"]==0 and r["closing_loss"]==50
def test_tl005_opening_loss_never_increases_tax():
    assert apply_tax_loss(100,50,.25)["tax"] < apply_tax_loss(100,0,.25)["tax"]
def test_tl006_closing_loss_nonnegative():
    assert apply_tax_loss(1,0,.25)["closing_loss"] >= 0
def test_tl007_cfads_tax_is_zero_in_loss_year():
    assert apply_tax_loss(-100,0,.25)["tax"]==0
