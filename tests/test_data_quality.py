import unittest
from analytics.data_quality import run

class DataQualityTests(unittest.TestCase):
    def test_remote_quality_checks_pass(self):
        result = run()
        self.assertEqual(result["failures"], 0)
        self.assertGreaterEqual(result["checks"], 10)

if __name__ == "__main__":
    unittest.main()
