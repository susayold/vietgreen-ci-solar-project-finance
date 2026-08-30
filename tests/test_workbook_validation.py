import unittest

from analytics.validate_workbook import EXPECTED_SHEETS, run


class WorkbookValidationTests(unittest.TestCase):
    def test_native_workbook_structure_passes(self):
        result = run()
        self.assertEqual(result["failures"], 0)
        self.assertEqual(len(EXPECTED_SHEETS), 22)


if __name__ == "__main__":
    unittest.main()
