import unittest

from src.scheduler import build_schedule
from src.topology import build_communication_graph
from src.validator import validate_schedule

CHAIN = {c: (i * 400.0, 0.0) for i, c in enumerate("ABCDE")}


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.graph = build_communication_graph(CHAIN, 500.0)

    def test7_valid_schedule_has_zero_violations(self):
        v = validate_schedule(self.graph, {"A": 0, "B": 1, "C": 2, "D": 0, "E": 1})
        self.assertTrue(v.is_valid)
        self.assertEqual(v.violations, [])
        self.assertEqual(v.conflicting_pairs, 7)     # AB BC CD DE AC BD CE

    def test_generated_schedule_passes_independent_validation(self):
        self.assertTrue(build_schedule(CHAIN, 500.0).validation.is_valid)

    def test8_detects_one_hop_violation(self):
        v = validate_schedule(self.graph, {"A": 0, "B": 0, "C": 2, "D": 0, "E": 1})
        self.assertFalse(v.is_valid)
        found = [(x.node_a, x.node_b, x.conflict_type, x.slot) for x in v.violations]
        self.assertIn(("A", "B", "1-hop", 0), found)

    def test8_detects_two_hop_violation(self):
        # A and C share slot 0 but only via hidden-terminal interference at B
        v = validate_schedule(self.graph, {"A": 0, "B": 1, "C": 0, "D": 2, "E": 1})
        self.assertEqual([(x.node_a, x.node_b, x.conflict_type) for x in v.violations],
                         [("A", "C", "2-hop")])

    def test_three_hop_reuse_is_not_flagged(self):
        v = validate_schedule(self.graph, {"A": 0, "B": 1, "C": 2, "D": 0, "E": 1})
        self.assertEqual(len(v.violations), 0)

    def test_structural_errors(self):
        self.assertTrue(validate_schedule(self.graph, {"A": 0}).errors)                       # missing
        full = {"A": 0, "B": 1, "C": 2, "D": 0, "E": 1}
        self.assertTrue(validate_schedule(self.graph, {**full, "Z": 3}).errors)               # unknown
        self.assertTrue(validate_schedule(self.graph, {**full, "E": -1}).errors)              # negative
        self.assertFalse(validate_schedule(self.graph, {**full, "E": -1}).is_valid)


if __name__ == "__main__":
    unittest.main()
