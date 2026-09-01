from analytics.debt_sculpting import capacity_constraints

def test_llcr_is_loan_life_and_plcr_is_project_life():
    debt,binding,choices=capacity_constraints(
        [100,100],0.08,1.35,1.30,1.20,0.70,1000,
        project_life_cfads=[100,100,100,100,100]
    )
    assert choices["PLCR"] > choices["LLCR"]
    assert debt > 0
    assert binding in {"DSCR","LLCR","PLCR","LEVERAGE"}
