from analytics.portfolio_selection import allocate
def test_pf001_common_currency_ranking():
    r=allocate([{"project_id":"a","equity_required_usd":10,"equity_npv_usd_at_reference":2},{"project_id":"b","equity_required_usd":10,"equity_npv_usd_at_reference":1}],100)
    assert [x["project_id"] for x in r["selected"]]==["a","b"]
def test_pf002_budget_enforced():
    r=allocate([{"project_id":"a","equity_required_usd":60},{"project_id":"b","equity_required_usd":60}],100); assert r["spent_usd"]<=100
def test_pf003_economic_country_cap():
    r=allocate([{"project_id":"a","country":"VN","equity_required_usd":60},{"project_id":"b","country":"VN","equity_required_usd":60},{"project_id":"c","country":"IN","equity_required_usd":40}],100,.6)
    assert r["exposure_enforced"]
def test_pf004_frontier_boundary():
    r=allocate([{"project_id":"a","equity_required_usd":10}],100); assert r["capital_allocation_status"]=="NOT_INVESTMENT_APPROVAL"
def test_pf005_deterministic():
    p=[{"project_id":"b","equity_required_usd":10,"equity_npv_usd_at_reference":1},{"project_id":"a","equity_required_usd":10,"equity_npv_usd_at_reference":2}]
    assert allocate(p,100)["selected"]==allocate(p,100)["selected"]
