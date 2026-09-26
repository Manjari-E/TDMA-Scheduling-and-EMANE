"""Greedy graph-colouring heuristics applied to the CONFLICT graph.

Because the conflict graph already contains every 1-hop and 2-hop pair, a
normal ("distance-1") colouring of it IS a distance-2 colouring of the
communication graph.  Colour k  ==  TDMA slot k.

Finding the minimum number of colours is NP-hard, so everything here is a
heuristic: fast, always valid, but not guaranteed minimal.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List

import networkx as nx

from .config import RANDOM_RESTARTS, RANDOM_SEED

Coloring = Dict[str, int]


def num_colors(coloring: Coloring) -> int:
    return (max(coloring.values()) + 1) if coloring else 0


# ---------------------------------------------------------------- core greedy
def greedy_coloring(graph: nx.Graph, order: List[str]) -> Coloring:
    """Colour nodes in the given order; each gets the LOWEST colour not already
    used by a conflicting neighbour.  Different orders give different results.
    """
    coloring: Coloring = {}
    for node in order:
        forbidden = {coloring[nb] for nb in graph[node] if nb in coloring}
        color = 0
        while color in forbidden:
            color += 1
        coloring[node] = color
    return coloring


# ------------------------------------------------------------------ orderings
def order_input(graph: nx.Graph) -> List[str]:
    """Baseline: nodes in the order they appear in the JSON file."""
    return list(graph.nodes())


def order_largest_first(graph: nx.Graph) -> List[str]:
    """Most-conflicted nodes first (Welsh-Powell). Ties broken by name."""
    return sorted(graph.nodes(), key=lambda n: (-graph.degree(n), n))


def order_smallest_last(graph: nx.Graph) -> List[str]:
    """Repeatedly remove the node with the fewest remaining conflicts, then
    colour in reverse removal order (degeneracy ordering)."""
    remaining = {n: set(graph[n]) for n in graph.nodes()}
    removed: List[str] = []
    while remaining:
        node = min(remaining, key=lambda n: (len(remaining[n]), n))
        removed.append(node)
        for nb in remaining[node]:
            remaining[nb].discard(node)
        del remaining[node]
    return removed[::-1]


def dsatur_coloring(graph: nx.Graph) -> Coloring:
    """DSATUR: always colour next the node whose neighbours already use the
    MOST different colours ("saturation"); ties -> higher degree, then name.
    The order is decided while colouring, so it is its own function."""
    coloring: Coloring = {}
    uncolored = set(graph.nodes())
    while uncolored:
        def priority(n: str):
            saturation = len({coloring[nb] for nb in graph[n] if nb in coloring})
            return (-saturation, -graph.degree(n), n)
        node = min(uncolored, key=priority)
        forbidden = {coloring[nb] for nb in graph[node] if nb in coloring}
        color = 0
        while color in forbidden:
            color += 1
        coloring[node] = color
        uncolored.remove(node)
    return coloring


# ------------------------------------------------------------- slot compaction
def reduce_slots(graph: nx.Graph, coloring: Coloring) -> Coloring:
    """Try to delete the highest slot by moving its nodes into lower slots.
    Repeats until no further slot can be removed. Never breaks validity."""
    current = dict(coloring)
    while num_colors(current) > 1:
        top = num_colors(current) - 1
        trial = dict(current)
        for node in [n for n, c in current.items() if c == top]:
            used = {trial[nb] for nb in graph[node]}
            free = [c for c in range(top) if c not in used]
            if not free:
                break
            trial[node] = free[0]
        else:                       # loop finished without 'break' -> success
            current = trial
            continue
        break
    return current


# ------------------------------------------------------------------ optimiser
@dataclass
class OptimizationResult:
    coloring: Coloring
    best_heuristic: str
    baseline_slots: int                      # greedy in JSON order
    heuristic_slots: Dict[str, int] = field(default_factory=dict)
    slots_before_compaction: int = 0
    lower_bound: int = 0                     # size of largest clique
    restarts: int = 0

    @property
    def slots(self) -> int:
        return num_colors(self.coloring)

    @property
    def proven_optimal(self) -> bool:
        """True only when slots == a proven lower bound."""
        return self.slots == self.lower_bound


def clique_lower_bound(graph: nx.Graph) -> int:
    """Nodes of a clique all conflict pairwise, so they need distinct slots.
    Hence  slots needed >= size of the largest clique."""
    return max((len(c) for c in nx.find_cliques(graph)), default=0)


def optimize_coloring(
    graph: nx.Graph,
    restarts: int = RANDOM_RESTARTS,
    seed: int = RANDOM_SEED,
) -> OptimizationResult:
    """Run several heuristics, keep the best, then try slot compaction."""
    named: Dict[str, Callable[[], Coloring]] = {
        "greedy (input order)": lambda: greedy_coloring(graph, order_input(graph)),
        "greedy (largest-first)": lambda: greedy_coloring(graph, order_largest_first(graph)),
        "greedy (smallest-last)": lambda: greedy_coloring(graph, order_smallest_last(graph)),
        "DSATUR": lambda: dsatur_coloring(graph),
    }
    results: Dict[str, Coloring] = {name: fn() for name, fn in named.items()}

    rng = random.Random(seed)                 # seeded => reproducible
    nodes = list(graph.nodes())
    best_random: Coloring = {}
    for _ in range(restarts):
        rng.shuffle(nodes)
        candidate = greedy_coloring(graph, nodes)
        if not best_random or num_colors(candidate) < num_colors(best_random):
            best_random = candidate
    if best_random:
        results[f"random restarts (x{restarts})"] = best_random

    heuristic_slots = {name: num_colors(c) for name, c in results.items()}
    best_name = min(results, key=lambda name: num_colors(results[name]))  # first wins ties
    best = results[best_name]
    compacted = reduce_slots(graph, best)

    return OptimizationResult(
        coloring=compacted,
        best_heuristic=best_name if compacted == best else f"{best_name} + slot compaction",
        baseline_slots=heuristic_slots["greedy (input order)"],
        heuristic_slots=heuristic_slots,
        slots_before_compaction=num_colors(best),
        lower_bound=clique_lower_bound(graph),
        restarts=restarts,
    )
