"""Unit tests for the data-driven PPA frontier geometry."""

import unittest


def marker_percent(value: float, lower: float, upper: float) -> float:
    if upper <= lower:
        raise ValueError("upper bound must be greater than lower bound")
    return min(100.0, max(0.0, (value - lower) / (upper - lower) * 100.0))


def ticks(lower: float, upper: float) -> list[float]:
    if upper <= lower:
        raise ValueError("upper bound must be greater than lower bound")
    span = upper - lower
    return [lower, lower + span / 3, lower + span * 2 / 3, upper]


class PPAZoneMathTest(unittest.TestCase):
    def test_bounds_and_midpoint(self):
        self.assertEqual(marker_percent(100.0, 100.0, 200.0), 0.0)
        self.assertEqual(marker_percent(200.0, 100.0, 200.0), 100.0)
        self.assertEqual(marker_percent(150.0, 100.0, 200.0), 50.0)

    def test_clamps_out_of_range(self):
        self.assertEqual(marker_percent(50.0, 100.0, 200.0), 0.0)
        self.assertEqual(marker_percent(250.0, 100.0, 200.0), 100.0)

    def test_ticks_share_same_bounds(self):
        values = ticks(2100.0, 2400.0)
        self.assertEqual(values[0], 2100.0)
        self.assertEqual(values[-1], 2400.0)
        self.assertAlmostEqual(values[1], 2200.0)
        self.assertAlmostEqual(values[2], 2300.0)

    def test_invalid_axis_is_rejected(self):
        with self.assertRaises(ValueError):
            marker_percent(100.0, 100.0, 100.0)
        with self.assertRaises(ValueError):
            ticks(200.0, 100.0)


if __name__ == "__main__":
    unittest.main()
