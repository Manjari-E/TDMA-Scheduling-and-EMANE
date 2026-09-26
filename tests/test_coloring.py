import random
import unittest

import networkx as nx

from src.coloring import (clique_lower_bound, dsatur_coloring, greedy_coloring,
                          num_colors, optimize_coloring, order_input,
                          order_largest_first, order_smallest_last, reduce_slots)
from src.conflict_graph import build_conflict_graph
from src.scheduler import build_schedule
from src.topology import build_communication_graph


def is_proper(graph, coloring):
    return all(coloring[a] != coloring[b] for a, b in graph.edges())


def random_conflict_graph(seed, n=16):
    rng = random.Random(seed)
    nodes = {f"N{i:02d}": (rng.uniform(0, 1500), rng.uniform(0, 1500)) for i in range(n)}
    return build_conflict_graph(build_communication_graph(nodes, 500.0))


class TestColoring(unittest.TestCase):
    def test_every_strategy_is_proper_on_many_random_graphs(self):
        for seed in range(40):
            g = random_conflict_graph(seed)
            for order in (order_input, order_largest_first, order_smallest_last):
                self.assertTrue(is_proper(g, greedy_coloring(g, order(g))))
            self.assertTrue(is_proper(g, dsatur_coloring(g)))

    def test_optimizer_result_is_proper_and_complete(self):
        for seed in range(20):
            g = random_conflict_graph(seed)
            res = optimize_coloring(g, restarts=50)
            self.assertEqual(set(res.coloring), set(g.nodes))
            self.assertTrue(is_proper(g, res.coloring))
            self.assertLessEqual(res.slots, res.baseline_slots)
            self.assertGreaterEqual(res.slots, res.lower_bound)

    def test_compaction_never_breaks_validity(self):
        for seed in range(20):
            g = random_conflict_graph(seed)
            wasteful = {n: i for i, n in enumerate(g.nodes)}     # one slot per node
            reduced = reduce_slots(g, wasteful)
            self.assertTrue(is_proper(g, reduced))
            self.assertLess(num_colors(reduced), num_colors(wasteful))

    def test4_spatial_reuse_on_chain(self):
        nodes = {c: (i * 400.0, 0.0) for i, c in enumerate("ABCDE")}
        r = build_schedule(nodes, 500.0)
        self.assertFalse(r.conflict_graph.has_edge("A", "D"))   # 3 hops => allowed to share
        self.assertEqual(r.optimization.slots, 3)               # hand-solved result
        self.assertTrue(r.optimization.proven_optimal)          # clique A,B,C forces >= 3
        self.assertTrue(any(len(m) > 1 for m in r.slot_to_nodes.values()))
        self.assertTrue(all(p.hop_distance is None or p.hop_distance >= 3 for p in r.reuse_pairs))

    def test_disconnected_components_can_share_slots(self):
        nodes = {"A": (0, 0), "B": (300, 0), "C": (9000, 0), "D": (9300, 0)}
        r = build_schedule(nodes, 500.0)
        self.assertEqual(r.optimization.slots, 2)
        self.assertEqual(r.node_to_slot["A"], r.node_to_slot["C"])

    def test_clique_lower_bound(self):
        self.assertEqual(clique_lower_bound(nx.complete_graph(4)), 4)
        self.assertEqual(clique_lower_bound(nx.path_graph(5)), 2)

    def test_same_seed_gives_same_result(self):
        g = random_conflict_graph(3)
        self.assertEqual(optimize_coloring(g, 60, seed=7).coloring,
                         optimize_coloring(g, 60, seed=7).coloring)

    def test_no_conflicts_needs_one_slot(self):
        g = nx.empty_graph(["A", "B", "C"])
        self.assertEqual(optimize_coloring(g, 5).slots, 1)


if __name__ == "__main__":
    unittest.main()
