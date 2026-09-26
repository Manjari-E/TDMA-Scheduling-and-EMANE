import json
from pathlib import Path

import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCHEDULE_FILE = PROJECT_ROOT / "results" / "schedule.json"
OUTPUT_FILE = PROJECT_ROOT / "results" / "tdma_schedule.png"


# ---------------------------------------------------------
# Load official generated schedule
# ---------------------------------------------------------
with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
    schedule = json.load(file)


# ---------------------------------------------------------
# Read official schedule data
# ---------------------------------------------------------
node_count = schedule["node_count"]
slot_count = schedule["slot_count"]

slot_to_nodes = {
    int(slot): nodes
    for slot, nodes in schedule["slot_to_nodes"].items()
}

slots = sorted(slot_to_nodes.keys())


# ---------------------------------------------------------
# Create output directory
# ---------------------------------------------------------
OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Create figure
# ---------------------------------------------------------
fig, ax = plt.subplots(
    figsize=(14, 8)
)


# ---------------------------------------------------------
# Draw nodes for every TDMA slot
# ---------------------------------------------------------
for row, slot in enumerate(slots):

    nodes_in_slot = slot_to_nodes[slot]

    for column, node in enumerate(nodes_in_slot):

        ax.scatter(
            column,
            row,
            s=1800,
            facecolors="white",
            edgecolors="black",
            linewidths=2
        )

        ax.text(
            column,
            row,
            node.replace("Node_", ""),
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold"
        )


# ---------------------------------------------------------
# Configure axes
# ---------------------------------------------------------
ax.set_yticks(range(len(slots)))

ax.set_yticklabels(
    [f"Slot {slot}" for slot in slots],
    fontsize=11
)

ax.set_xlabel(
    "Nodes transmitting in the same TDMA slot",
    fontsize=12
)

ax.set_ylabel(
    "TDMA Slot",
    fontsize=12
)

ax.set_title(
    "TDMA Slot Allocation\n"
    f"{node_count} Nodes Scheduled Across {slot_count} Slots",
    fontsize=17,
    fontweight="bold",
    pad=20
)


# ---------------------------------------------------------
# Grid
# ---------------------------------------------------------
ax.grid(
    True,
    linestyle="--",
    alpha=0.3,
    axis="x"
)


# ---------------------------------------------------------
# X-axis range
# ---------------------------------------------------------
max_nodes_per_slot = max(
    len(nodes)
    for nodes in slot_to_nodes.values()
)

ax.set_xlim(
    -1,
    max_nodes_per_slot
)

ax.set_ylim(
    -0.8,
    len(slots) - 0.2
)


# ---------------------------------------------------------
# Summary information
# ---------------------------------------------------------
average_nodes_per_slot = node_count / slot_count

summary = (
    f"Total nodes: {node_count}\n"
    f"TDMA slots: {slot_count}\n"
    f"Average nodes/slot: "
    f"{average_nodes_per_slot:.2f}"
)

ax.text(
    1.02,
    0.5,
    summary,
    transform=ax.transAxes,
    fontsize=10,
    verticalalignment="center",
    bbox=dict(
        boxstyle="round,pad=0.6",
        facecolor="white",
        edgecolor="black"
    )
)


plt.tight_layout()


# ---------------------------------------------------------
# Save visualization
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
print("TDMA SCHEDULE VISUALIZATION")
print("=" * 60)

print(f"Nodes                : {node_count}")
print(f"Slots used           : {slot_count}")

for slot in slots:

    print(
        f"Slot {slot:02d}              : "
        f"{', '.join(slot_to_nodes[slot])}"
    )

print(f"Output               : {OUTPUT_FILE}")

print("=" * 60)