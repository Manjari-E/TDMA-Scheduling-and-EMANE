import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "input" / "nodes.json"
OUTPUT_FILE = PROJECT_ROOT / "results" / "network_topology.png"

RADIO_RANGE = 500.0


# ---------------------------------------------------------
# Load project input
# Format:
# {
#     "Node_01": [x, y],
#     "Node_02": [x, y],
#     ...
# }
# ---------------------------------------------------------
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    nodes = json.load(file)


# ---------------------------------------------------------
# Create communication graph
# ---------------------------------------------------------
graph = nx.Graph()

positions = {}

for node_name, coordinates in nodes.items():

    x = float(coordinates[0])
    y = float(coordinates[1])

    graph.add_node(node_name)

    positions[node_name] = (x, y)


# ---------------------------------------------------------
# Calculate communication links
#
# Two nodes communicate when:
#
# distance <= 500 metres
# ---------------------------------------------------------
node_names = list(nodes.keys())

for i in range(len(node_names)):

    for j in range(i + 1, len(node_names)):

        node_a = node_names[i]
        node_b = node_names[j]

        x1, y1 = positions[node_a]
        x2, y2 = positions[node_b]

        distance = math.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2
        )

        if distance <= RADIO_RANGE:

            graph.add_edge(
                node_a,
                node_b,
                distance=distance
            )


# ---------------------------------------------------------
# Create results directory
# ---------------------------------------------------------
OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Create visualization
# ---------------------------------------------------------
plt.figure(figsize=(13, 10))


# Communication links
nx.draw_networkx_edges(
    graph,
    positions,
    width=1.8,
    alpha=0.65
)


# Nodes
nx.draw_networkx_nodes(
    graph,
    positions,
    node_size=950,
    node_color="white",
    edgecolors="black",
    linewidths=1.8
)


# Node labels
nx.draw_networkx_labels(
    graph,
    positions,
    font_size=9,
    font_weight="bold"
)


# ---------------------------------------------------------
# Title
# ---------------------------------------------------------
plt.title(
    "TDMA Network Topology\n"
    "16 Nodes | Communication Range = 500 m",
    fontsize=17,
    fontweight="bold",
    pad=20
)


plt.xlabel(
    "X Coordinate (metres)",
    fontsize=12
)

plt.ylabel(
    "Y Coordinate (metres)",
    fontsize=12
)


# Grid
plt.grid(
    True,
    linestyle="--",
    alpha=0.3
)


# Keep coordinate proportions correct
plt.axis("equal")


# ---------------------------------------------------------
# Information box
# ---------------------------------------------------------
information = (
    f"Nodes: {graph.number_of_nodes()}\n"
    f"Communication edges: {graph.number_of_edges()}\n"
    f"Radio range: {RADIO_RANGE:.0f} m\n"
    f"Connected: {'Yes' if nx.is_connected(graph) else 'No'}"
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
print("NETWORK TOPOLOGY VISUALIZATION")
print("=" * 60)

print(f"Nodes                : {graph.number_of_nodes()}")
print(f"Communication edges  : {graph.number_of_edges()}")
print(f"Radio range          : {RADIO_RANGE:.1f} m")
print(
    f"Connected            : "
    f"{'yes' if nx.is_connected(graph) else 'no'}"
)

print(f"Output               : {OUTPUT_FILE}")

print("=" * 60)