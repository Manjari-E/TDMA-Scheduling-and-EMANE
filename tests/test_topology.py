import unittest

from src.topology import build_communication_graph, topology_summary


class TestTopology(unittest.TestCase):
    def test1_nodes_within_range_have_edge(self):
        g = build_communication_graph({"A": (0, 0), "B": (300, 0)}, 500.0)
        self.assertTrue(g.has_edge("A", "B"))
        self.assertAlmostEqual(g["A"]["B"]["distance"], 300.0)

    def test2_nodes_beyond_range_have_no_edge(self):
        g = build_communication_graph({"A": (0, 0), "B": (600, 0)}, 500.0)
        self.assertFalse(g.has_edge("A", "B"))

    def test_exactly_500_is_connected(self):
        g = build_communication_graph({"A": (0, 0), "B": (500, 0)}, 500.0)
        self.assertTrue(g.has_edge("A", "B"))

    def test_range_is_configurable(self):
        nodes = {"A": (0, 0), "B": (300, 0)}
        self.assertFalse(build_communication_graph(nodes, 200.0).has_edge("A", "B"))

    def test_summary_components_and_isolated(self):
        g = build_communication_graph({"A": (0, 0), "B": (100, 0), "C": (5000, 0)}, 500.0)
        s = topology_summary(g)
        self.assertEqual(s["edges"], 1)
        self.assertFalse(s["connected"])
        self.assertEqual(s["isolated"], ["C"])
        self.assertEqual(len(s["components"]), 2)


if __name__ == "__main__":
    unittest.main()
