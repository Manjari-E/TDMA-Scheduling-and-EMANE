import json
import math
from pathlib import Path

import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "input" / "nodes.json"
SCHEDULE_FILE = PROJECT_ROOT / "results" / "schedule.json"
OUTPUT_FILE = PROJECT_ROOT / "results" / "spatial_reuse.png"

RADIO_RANGE = 500.0


# ---------------------------------------------------------
# Load node coordinates
# ---------------------------------------------------------
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    nodes = json.load(file)


# ---------------------------------------------------------
# Load official schedule
# ---------------------------------------------------------
with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
    schedule = json.load(file)


slot_to_nodes = {
    int(slot): node_list
    for slot, node_list in schedule["slot_to_nodes"].items()
}


# ---------------------------------------------------------
# Calculate Euclidean distance
# ---------------------------------------------------------
def distance(node_a, node_b):
    x1, y1 = nodes[node_a]
    x2, y2 = nodes[node_b]

    return math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2
    )


# ---------------------------------------------------------
# Create output directory
# ---------------------------------------------------------
OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Create one visualization for all slots
# ---------------------------------------------------------
fig, axes = plt.subplots(
    1,
    len(slot_to_nodes),
    figsize=(20, 6)
)

if len(slot_to_nodes) == 1:
    axes = [axes]


# ---------------------------------------------------------
# Draw each slot
# ---------------------------------------------------------
for ax, (slot, nodes_in_slot) in zip(
    axes,
    sorted(slot_to_nodes.items())
):

    # Plot all network nodes in light background
    for node_name, (x, y) in nodes.items():

        ax.scatter(
            x,
            y,
            s=250,
            facecolors="white",
            edgecolors="gray",
            linewidths=1
        )

        ax.text(
            x,
            y + 35,
            node_name.replace("Node_", ""),
            ha="center",
            va="bottom",
            fontsize=7
        )


    # Plot nodes using this slot
    for node_name in nodes_in_slot:

        x, y = nodes[node_name]

        ax.scatter(
            x,
            y,
            s=700,
            facecolors="white",
            edgecolors="black",
            linewidths=2.5
        )

        ax.text(
            x,
            y,
            node_name.replace("Node_", ""),
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold"
        )


    # Connect nodes sharing the same slot
    for i in range(len(nodes_in_slot)):

        for j in range(i + 1, len(nodes_in_slot)):

            node_a = nodes_in_slot[i]
            node_b = nodes_in_slot[j]

            x1, y1 = nodes[node_a]
            x2, y2 = nodes[node_b]

            d = distance(node_a, node_b)

            ax.plot(
                [x1, x2],
                [y1, y2],
                linestyle="--",
                linewidth=1.5
            )

            # Distance label
            midpoint_x = (x1 + x2) / 2
            midpoint_y = (y1 + y2) / 2

            ax.text(
                midpoint_x,
                midpoint_y,
                f"{d:.0f} m",
                fontsize=7,
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor="white",
                    edgecolor="black",
                    alpha=0.8
                )
            )


    # Slot title
    ax.set_title(
        f"Slot {slot}\n"
        f"{len(nodes_in_slot)} nodes",
        fontsize=11,
        fontweight="bold"
    )

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")

    ax.grid(
        True,
        linestyle="--",
        alpha=0.25
    )

    ax.set_aspect("equal")


# ---------------------------------------------------------
# Overall title
# ---------------------------------------------------------
fig.suptitle(
    "TDMA Spatial Reuse Analysis\n"
    "Nodes sharing a slot are spatially separated",
    fontsize=17,
    fontweight="bold"
)


plt.tight_layout(
    rect=[0, 0, 1, 0.90]
)


# ---------------------------------------------------------
# Save
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
print("SPATIAL REUSE VISUALIZATION")
print("=" * 60)

print(
    f"Total nodes          : "
    f"{schedule['node_count']}"
)

print(
    f"TDMA slots            : "
    f"{schedule['slot_count']}"
)

print(
    f"Radio range           : "
    f"{RADIO_RANGE:.1f} m"
)

print()

for slot, nodes_in_slot in sorted(slot_to_nodes.items()):

    print(
        f"Slot {slot:02d}              : "
        f"{', '.join(nodes_in_slot)}"
    )

    # Find closest pair in this slot
    if len(nodes_in_slot) >= 2:

        closest_distance = float("inf")
        closest_pair = None

        for i in range(len(nodes_in_slot)):

            for j in range(i + 1, len(nodes_in_slot)):

                node_a = nodes_in_slot[i]
                node_b = nodes_in_slot[j]

                d = distance(node_a, node_b)

                if d < closest_distance:
                    closest_distance = d
                    closest_pair = (node_a, node_b)

        print(
            f"  Closest pair        : "
            f"{closest_pair[0]} & {closest_pair[1]}"
        )

        print(
            f"  Distance            : "
            f"{closest_distance:.1f} m"
        )

        print(
            f"  Reuse allowed       : "
            f"{'YES' if closest_distance > RADIO_RANGE else 'NO'}"
        )


print()
print(f"Output               : {OUTPUT_FILE}")
print("=" * 60)