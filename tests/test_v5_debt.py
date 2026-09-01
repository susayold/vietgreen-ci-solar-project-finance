from analytics.debt_sculpting import capacity_constraints,forward_rebuild
def test_debt_capacity_and_schedule_close():
 cap,binding,choices=capacity_constraints([30,30,30],.08,1.35,1.3,1.2,.7,100)
 rows=forward_rebuild(cap,[30,30,30],.08,1.35)
 assert cap>0 and binding in choices
 assert rows[-1]["closing"]>=-1e-6
 assert all(r["principal"]<=r["opening"]+1e-6 for r in rows)
