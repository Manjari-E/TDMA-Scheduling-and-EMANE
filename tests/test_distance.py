import unittest

from src.distance import calculate_distance, is_within_range


class TestDistance(unittest.TestCase):
    def test_pythagorean_triple(self):
        self.assertAlmostEqual(calculate_distance((0, 0), (3, 4)), 5.0)

    def test_zero_and_symmetry(self):
        self.assertEqual(calculate_distance((7, 7), (7, 7)), 0.0)
        self.assertAlmostEqual(calculate_distance((1, 2), (9, 5)), calculate_distance((9, 5), (1, 2)))

    def test_range_rule_is_inclusive(self):
        self.assertTrue(is_within_range(499.9, 500.0))
        self.assertTrue(is_within_range(500.0, 500.0))     # boundary => connected
        self.assertFalse(is_within_range(500.1, 500.0))


if __name__ == "__main__":
    unittest.main()
