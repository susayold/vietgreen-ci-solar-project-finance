import unittest
from analytics.energy_yield import p50_p90
from analytics.load_match_8760 import profile
from analytics.debt_sculpting import backward_capacity, forward_rebuild

class CoreTests(unittest.TestCase):
    def test_p90(self):
        p50,p90=p50_p90(1000,1400,.08); self.assertGreaterEqual(p50,p90)
    def test_hourly_reconciliation(self):
        p=profile(1000000,1200000); self.assertAlmostEqual(sum(p['load']),1000000,places=5); self.assertAlmostEqual(sum(p['solar']),1200000,places=5)
    def test_debt_closes(self):
        initial,service=backward_capacity([100,100,100],.08,1.3); rows=forward_rebuild(initial,[100,100,100],.08,1.3); self.assertLessEqual(rows[-1]['closing'],1e-6)

if __name__=='__main__': unittest.main()
