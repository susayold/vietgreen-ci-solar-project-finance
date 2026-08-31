import unittest
from analytics.capex_engine import build_capex_schedule
from analytics.debt_sculpting import backward_capacity, forward_rebuild
from analytics.energy_yield import p50_p90
from analytics.load_match_8760 import profile
from analytics.ppa_engine import negotiation_zone


class CoreTests(unittest.TestCase):
    def test_p90(self):
        p50, p90 = p50_p90(1000, 1400, 0.08)
        self.assertGreaterEqual(p50, p90)

    def test_hourly_reconciliation(self):
        p = profile(1000000, 1200000)
        self.assertAlmostEqual(sum(p["load"]), 1000000, places=5)
        self.assertAlmostEqual(sum(p["solar"]), 1200000, places=5)

    def test_debt_closes(self):
        initial, service = backward_capacity([100, 100, 100], 0.08, 1.3)
        rows = forward_rebuild(initial, [100, 100, 100], 0.08, 1.3)
        self.assertLessEqual(rows[-1]["closing"], 1e-6)

    def test_empty_ppa_zone_rejects_or_renegotiates(self):
        zone = negotiation_zone(100, 110, 120)
        self.assertEqual(zone["status"], "EMPTY_ZONE")
        self.assertEqual(zone["action"], "RENEGOTIATE_OR_REJECT")

    def test_capex_vat_idc_reconciles(self):
        capex_rows = [
            {"project_id": "TEST", "amount_local": "108", "vat_rate": "0.08"},
        ]
        construction_rows = [
            {"project_id": "TEST", "construction_month": str(month), "construction_share": str(1 / 12), "source_or_assumption_id": "TEST"}
            for month in range(1, 13)
        ]
        rows, summary = build_capex_schedule(capex_rows, construction_rows, "TEST", idc_rate=0.085)
        self.assertEqual(len(rows), 12)
        self.assertAlmostEqual(summary["construction_capex_net_vnd"] + summary["vat_vnd"], 108, places=8)
        self.assertAlmostEqual(summary["total_uses_vnd"], summary["construction_capex_gross_vnd"] + summary["idc_vnd"], places=8)


if __name__ == "__main__":
    unittest.main()
