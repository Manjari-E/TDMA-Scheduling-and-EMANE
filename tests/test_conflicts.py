import random
import unittest

import networkx as nx

from src.conflict_graph import ONE_HOP, TWO_HOP, build_conflict_graph
from src.topology import build_communication_graph


def chain(n, spacing=400.0):
    nodes = {chr(65 + i): (i * spacing, 0.0) for i in range(n)}
    return build_communication_graph(nodes, 500.0)


class TestConflicts(unittest.TestCase):
    def test3_chain_A_C_is_two_hop_conflict(self):
        cg = build_conflict_graph(chain(3))          # A -- B -- C, A-C is 800 m
        self.assertTrue(cg.has_edge("A", "B"))
        self.assertTrue(cg.has_edge("A", "C"))
        self.assertEqual(cg["A"]["B"]["type"], ONE_HOP)
        self.assertEqual(cg["A"]["C"]["type"], TWO_HOP)
        self.assertEqual(cg["A"]["C"]["via"], "B")

    def test_three_hops_apart_is_not_a_conflict(self):
        cg = build_conflict_graph(chain(4))          # A B C D
        self.assertFalse(cg.has_edge("A", "D"))

    def test_direct_neighbours_keep_one_hop_label(self):
        # triangle: A-C are direct neighbours AND share neighbour B
        g = build_communication_graph({"A": (0, 0), "B": (200, 0), "C": (100, 150)}, 500.0)
        self.assertEqual(build_conflict_graph(g)["A"]["C"]["type"], ONE_HOP)

    def test_matches_networkx_square_of_graph_on_random_topologies(self):
        """Cross-check against nx.power(G, 2) (all pairs within 2 hops)."""
        for seed in range(25):
            rng = random.Random(seed)
            nodes = {f"N{i}": (rng.uniform(0, 1500), rng.uniform(0, 1500)) for i in range(14)}
            comm = build_communication_graph(nodes, 500.0)
            ours = {frozenset(e) for e in build_conflict_graph(comm).edges()}
            reference = {frozenset(e) for e in nx.power(comm, 2).edges()}
            self.assertEqual(ours, reference, f"mismatch for seed {seed}")

    def test_isolated_node_is_kept_without_conflicts(self):
        g = build_communication_graph({"A": (0, 0), "B": (100, 0), "Z": (9000, 0)}, 500.0)
        cg = build_conflict_graph(g)
        self.assertIn("Z", cg.nodes)
        self.assertEqual(cg.degree("Z"), 0)


if __name__ == "__main__":
    unittest.main()
