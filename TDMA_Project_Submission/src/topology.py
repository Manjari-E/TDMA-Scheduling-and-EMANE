"""Communication graph: radios are nodes, "can hear each other" is an edge."""
from __future__ import annotations

from itertools import combinations
from typing import Dict, List

import networkx as nx

from .distance import calculate_distance, is_within_range
from .input_parser import Nodes


def build_communication_graph(nodes: Nodes, radio_range: float) -> nx.Graph:
    """Build the graph purely from coordinates (no hard-coded edges).

    Every unordered pair is tested once (O(n^2), fine for 16 nodes).
    Node attribute 'pos' = (x, y); edge attribute 'distance' = metres.
    """
    graph = nx.Graph()
    for name, position in nodes.items():
        graph.add_node(name, pos=position)
    for a, b in combinations(nodes, 2):
        d = calculate_distance(nodes[a], nodes[b])
        if is_within_range(d, radio_range):
            graph.add_edge(a, b, distance=d)
    return graph


def topology_summary(graph: nx.Graph) -> Dict[str, object]:
    """Numbers used by the report."""
    degrees = dict(graph.degree())
    components: List[List[str]] = [sorted(c) for c in nx.connected_components(graph)]
    n = graph.number_of_nodes()
    return {
        "nodes": n,
        "edges": graph.number_of_edges(),
        "degrees": degrees,
        "min_degree": min(degrees.values()) if degrees else 0,
        "max_degree": max(degrees.values()) if degrees else 0,
        "avg_degree": (sum(degrees.values()) / n) if n else 0.0,
        "components": components,
        "connected": len(components) <= 1,
        "isolated": sorted(node for node, d in degrees.items() if d == 0),
    }
