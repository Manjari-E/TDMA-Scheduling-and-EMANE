import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "input" / "nodes.json"
OUTPUT_FILE = PROJECT_ROOT / "results" / "conflict_graph.png"

RADIO_RANGE = 500.0


# ---------------------------------------------------------
# Load node coordinates
# ---------------------------------------------------------
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    nodes = json.load(file)


# ---------------------------------------------------------
# Build communication graph
# ---------------------------------------------------------
communication_graph = nx.Graph()

for node_name in nodes:
    communication_graph.add_node(node_name)


node_names = list(nodes.keys())

for i in range(len(node_names)):
    for j in range(i + 1, len(node_names)):

        node_a = node_names[i]
        node_b = node_names[j]

        x1, y1 = nodes[node_a]
        x2, y2 = nodes[node_b]

        distance = (
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2
        ) ** 0.5

        if distance <= RADIO_RANGE:
            communication_graph.add_edge(
                node_a,
                node_b
            )


# ---------------------------------------------------------
# Build distance-2 conflict graph
#
# Two nodes conflict if their shortest-path distance
# in the communication graph is <= 2.
# ---------------------------------------------------------
conflict_graph = nx.Graph()

conflict_graph.add_nodes_from(node_names)

for node_a in node_names:

    shortest_paths = nx.single_source_shortest_path_length(
        communication_graph,
        node_a,
        cutoff=2
    )

    for node_b, hops in shortest_paths.items():

        if node_a == node_b:
            continue

        if hops <= 2:
            conflict_graph.add_edge(
                node_a,
                node_b
            )


# ---------------------------------------------------------
# Create output directory
# ---------------------------------------------------------
OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Use a deterministic layout
# ---------------------------------------------------------
positions = nx.spring_layout(
    conflict_graph,
    seed=42,
    k=1.2
)


# ---------------------------------------------------------
# Create figure
# ---------------------------------------------------------
plt.figure(figsize=(14, 11))


# Conflict edges
nx.draw_networkx_edges(
    conflict_graph,
    positions,
    width=1.0,
    alpha=0.45
)


# Nodes
nx.draw_networkx_nodes(
    conflict_graph,
    positions,
    node_size=1000,
    node_color="white",
    edgecolors="black",
    linewidths=1.8
)


# Labels
nx.draw_networkx_labels(
    conflict_graph,
    positions,
    font_size=9,
    font_weight="bold"
)


# ---------------------------------------------------------
# Title
# ---------------------------------------------------------
plt.title(
    "TDMA Distance-2 Conflict Graph\n"
    "55 Conflict Edges",
    fontsize=17,
    fontweight="bold",
    pad=20
)


plt.axis("off")


# ---------------------------------------------------------
# Information box
# ---------------------------------------------------------
information = (
    f"Nodes: {conflict_graph.number_of_nodes()}\n"
    f"Communication edges: "
    f"{communication_graph.number_of_edges()}\n"
    f"Conflict edges: "
    f"{conflict_graph.number_of_edges()}\n"
    f"Maximum conflict degree: "
    f"{max(dict(conflict_graph.degree()).values())}"
)

plt.text(
    0.02,
    0.02,
    information,
    transform=plt.gca().transAxes,
    fontsize=10,
    verticalalignment="bottom",
    bbox=dict(
        boxstyle="round,pad=0.5",
        facecolor="white",
        edgecolor="black",
        alpha=0.9
    )
)


plt.tight_layout()


# ---------------------------------------------------------
# Save image
# ---------------------------------------------------------
plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ---------------------------------------------------------
# Terminal summary
# ---------------------------------------------------------
print("=" * 60)
print("CONFLICT GRAPH VISUALIZATION")
print("=" * 60)

print(
    f"Nodes                : "
    f"{conflict_graph.number_of_nodes()}"
)

print(
    f"Communication edges  : "
    f"{communication_graph.number_of_edges()}"
)

print(
    f"Conflict edges       : "
    f"{conflict_graph.number_of_edges()}"
)

print(
    f"Max conflict degree  : "
    f"{max(dict(conflict_graph.degree()).values())}"
)

print(f"Output               : {OUTPUT_FILE}")

print("=" * 60)