from analytics.tax_engine_v5 import apply_tax_loss, validate_tax_row

def test_loss_year_creates_positive_carryforward_without_tax():
    r=apply_tax_loss(-100,0,.25)
    assert r["tax"] == 0
    assert r["closing_loss"] == 100
    validate_tax_row(r)

def test_profit_year_uses_carryforward_before_tax():
    r=apply_tax_loss(150,100,.25)
    assert r["loss_used"] == 100
    assert r["taxable_after_loss"] == 50
    assert r["tax"] == 12.5
    assert r["closing_loss"] == 0
