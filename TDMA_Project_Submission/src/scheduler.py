"""Glue: coordinates -> graphs -> colouring -> schedule -> validation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import networkx as nx

from .coloring import OptimizationResult, optimize_coloring
from .config import RANDOM_RESTARTS, RANDOM_SEED
from .conflict_graph import build_conflict_graph
from .distance import calculate_distance
from .input_parser import Nodes
from .topology import build_communication_graph
from .validator import ValidationResult, validate_schedule


@dataclass
class ReusePair:
    slot: int
    node_a: str
    node_b: str
    physical_distance: float
    hop_distance: Optional[int]      # None = different connected components


@dataclass
class ScheduleResult:
    nodes: Nodes
    radio_range: float
    comm_graph: nx.Graph
    conflict_graph: nx.Graph
    optimization: OptimizationResult
    node_to_slot: Dict[str, int]
    slot_to_nodes: Dict[int, List[str]]
    matrix: List[List[int]]              # rows = slots, columns = node_order
    node_order: List[str]
    reuse_pairs: List[ReusePair]
    validation: ValidationResult


def group_by_slot(node_to_slot: Dict[str, int]) -> Dict[int, List[str]]:
    slots: Dict[int, List[str]] = {}
    for node, slot in sorted(node_to_slot.items()):
        slots.setdefault(slot, []).append(node)
    return dict(sorted(slots.items()))


def build_matrix(node_to_slot: Dict[str, int], node_order: List[str]) -> List[List[int]]:
    """matrix[s][j] == 1  <=>  node_order[j] transmits in slot s."""
    total = (max(node_to_slot.values()) + 1) if node_to_slot else 0
    return [[1 if node_to_slot[n] == s else 0 for n in node_order] for s in range(total)]


def find_spatial_reuse(comm_graph: nx.Graph, nodes: Nodes,
                       node_to_slot: Dict[str, int]) -> List[ReusePair]:
    """Every pair of nodes that share a slot, with physical and hop distance.
    Reuse is legitimate because hop distance >= 3 (or no path at all);
    physical distance alone is NOT what decides it."""
    pairs: List[ReusePair] = []
    for slot, members in group_by_slot(node_to_slot).items():
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                try:
                    hops: Optional[int] = nx.shortest_path_length(comm_graph, a, b)
                except nx.NetworkXNoPath:
                    hops = None
                pairs.append(ReusePair(slot, a, b,
                                       calculate_distance(nodes[a], nodes[b]), hops))
    return pairs


def build_schedule(nodes: Nodes, radio_range: float,
                   restarts: int = RANDOM_RESTARTS, seed: int = RANDOM_SEED) -> ScheduleResult:
    comm = build_communication_graph(nodes, radio_range)
    conflicts = build_conflict_graph(comm)
    optimization = optimize_coloring(conflicts, restarts=restarts, seed=seed)
    node_to_slot = dict(sorted(optimization.coloring.items()))
    node_order = sorted(nodes)
    return ScheduleResult(
        nodes=nodes,
        radio_range=radio_range,
        comm_graph=comm,
        conflict_graph=conflicts,
        optimization=optimization,
        node_to_slot=node_to_slot,
        slot_to_nodes=group_by_slot(node_to_slot),
        matrix=build_matrix(node_to_slot, node_order),
        node_order=node_order,
        reuse_pairs=find_spatial_reuse(comm, nodes, node_to_slot),
        validation=validate_schedule(comm, node_to_slot),   # independent check
    )
