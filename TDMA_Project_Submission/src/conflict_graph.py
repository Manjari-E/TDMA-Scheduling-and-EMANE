"""Conflict graph: an edge means "these two nodes must NOT share a slot".

Four different ideas (do not mix them up):
  * physical distance   - metres between coordinates
  * communication graph - edge if physical distance <= range
  * hop distance        - fewest communication-graph edges between two nodes
  * conflict graph      - edge if hop distance is 1 or 2
"""
from __future__ import annotations

from itertools import combinations

import networkx as nx

ONE_HOP = "1-hop"
TWO_HOP = "2-hop"


def build_conflict_graph(comm_graph: nx.Graph) -> nx.Graph:
    """Build the conflict graph from the communication graph.

    Rule 1 (1-hop / direct interference): every communication edge is a conflict.
    Rule 2 (2-hop / hidden terminal):     any two neighbours of the same node
                                          are a conflict, because both would be
                                          heard at that shared neighbour.

    Correctness: a pair is within 2 hops  <=>  they are adjacent, or they have
    a common neighbour. Rule 1 covers the first case, Rule 2 the second.
    Isolated nodes stay in the graph (with no conflicts) so they get a slot.
    """
    conflicts = nx.Graph()
    conflicts.add_nodes_from(comm_graph.nodes(data=True))

    for a, b in comm_graph.edges():                       # Rule 1
        conflicts.add_edge(a, b, type=ONE_HOP)

    for middle in comm_graph.nodes():                     # Rule 2
        for a, c in combinations(comm_graph.neighbors(middle), 2):
            if not conflicts.has_edge(a, c):              # keep "1-hop" if already direct
                conflicts.add_edge(a, c, type=TWO_HOP, via=middle)
    return conflicts
