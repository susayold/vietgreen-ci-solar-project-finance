from analytics.debt_sculpting import capacity_constraints, forward_rebuild

def test_plcr_uses_project_life_not_loan_life():
    debt,binding,c=capacity_constraints([100,100],.08,1.35,1.30,1.20,.7,1000,project_life_cfads=[100,100,100,100,100])
    assert c["PLCR"] > c["LLCR"]
    assert debt > 0

def test_forward_schedule_reduces_debt():
    rows=forward_rebuild(100,[100,100,100],.08,1.35)
    assert rows[0]["opening"] == 100
    assert rows[-1]["closing"] < 100
