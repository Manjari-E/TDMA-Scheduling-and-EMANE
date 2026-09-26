"""Independent schedule validator.

Deliberately does NOT use conflict_graph.py or coloring.py.  It re-derives
every 1-hop / 2-hop pair straight from the communication graph using BFS
(hop distances), so a bug in the conflict builder cannot hide itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import networkx as nx


@dataclass
class Violation:
    node_a: str
    node_b: str
    conflict_type: str      # "1-hop" or "2-hop"
    slot: int


@dataclass
class ValidationResult:
    nodes: int
    conflicting_pairs: int
    slots_used: int
    violations: List[Violation] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)   # structural problems

    @property
    def is_valid(self) -> bool:
        return not self.violations and not self.errors


def validate_schedule(comm_graph: nx.Graph, node_to_slot: Dict[str, int]) -> ValidationResult:
    errors: List[str] = []
    graph_nodes = set(comm_graph.nodes())

    for name in sorted(graph_nodes - set(node_to_slot)):
        errors.append(f"Node '{name}' has no slot assigned.")
    for name in sorted(set(node_to_slot) - graph_nodes):
        errors.append(f"Schedule contains unknown node '{name}'.")
    for name, slot in node_to_slot.items():
        if isinstance(slot, bool) or not isinstance(slot, int) or slot < 0:
            errors.append(f"Node '{name}' has an invalid slot value {slot!r}.")

    violations: List[Violation] = []
    pairs = 0
    if not errors:
        for a in sorted(graph_nodes):
            hops = nx.single_source_shortest_path_length(comm_graph, a, cutoff=2)
            for b, distance in hops.items():
                if a < b and distance in (1, 2):      # a<b counts each pair once
                    pairs += 1
                    if node_to_slot[a] == node_to_slot[b]:
                        violations.append(
                            Violation(a, b, "1-hop" if distance == 1 else "2-hop",
                                      node_to_slot[a])
                        )
    slots_used = len(set(node_to_slot.values()))
    return ValidationResult(len(graph_nodes), pairs, slots_used, violations, errors)
