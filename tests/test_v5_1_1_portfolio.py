from analytics.portfolio_selection import allocate

def test_portfolio_enforces_common_usd_budget_and_country_cap():
    r=allocate([
        {"project_id":"a","country":"VN","equity_required_usd":60,"equity_npv_usd_at_reference":100},
        {"project_id":"b","country":"VN","equity_required_usd":60,"equity_npv_usd_at_reference":90},
        {"project_id":"c","country":"IN","equity_required_usd":40,"equity_npv_usd_at_reference":80},
    ], equity_budget=100, max_country_share=.6)
    assert r["budget_enforced"] and r["exposure_enforced"]
    assert r["spent_usd"] <= 100
    assert r["shortlist_type"]=="DILIGENCE_PRIORITY_SHORTLIST"
