"""Export scheduler results to machine-readable and human-readable files."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .conflict_graph import ONE_HOP, TWO_HOP
from .scheduler import ScheduleResult
from .topology import topology_summary


def _conflict_edges(r: ScheduleResult) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for a, b, data in sorted(r.conflict_graph.edges(data=True)):
        item: dict[str, Any] = {"node_a": a, "node_b": b, "type": data["type"]}
        if data["type"] == TWO_HOP:
            item["via"] = data.get("via")
        edges.append(item)
    return edges


def _statistics(r: ScheduleResult) -> dict[str, Any]:
    topology = topology_summary(r.comm_graph)
    one_hop = sum(
        1 for _, _, data in r.conflict_graph.edges(data=True) if data["type"] == ONE_HOP
    )
    two_hop = sum(
        1 for _, _, data in r.conflict_graph.edges(data=True) if data["type"] == TWO_HOP
    )
    slot_sizes = [len(members) for members in r.slot_to_nodes.values()]
    violations = len(r.validation.violations) + len(r.validation.errors)

    return {
        "input": {
            "node_count": len(r.nodes),
            "radio_range_m": r.radio_range,
        },
        "communication_graph": {
            "nodes": topology["nodes"],
            "edges": topology["edges"],
            "degree_min": topology["min_degree"],
            "degree_average": round(topology["avg_degree"], 4),
            "degree_max": topology["max_degree"],
            "connected": topology["connected"],
            "components": topology["components"],
            "isolated_nodes": topology["isolated"],
        },
        "conflict_graph": {
            "one_hop_conflicts": one_hop,
            "two_hop_conflicts": two_hop,
            "total_conflict_edges": r.conflict_graph.number_of_edges(),
            "maximum_conflict_degree": max(dict(r.conflict_graph.degree()).values(), default=0),
        },
        "optimization": {
            "best_heuristic": r.optimization.best_heuristic,
            "heuristic_slots": r.optimization.heuristic_slots,
            "baseline_slots": r.optimization.baseline_slots,
            "slots_before_compaction": r.optimization.slots_before_compaction,
            "slots_used": r.optimization.slots,
            "lower_bound": r.optimization.lower_bound,
            "proven_optimal_for_instance": r.optimization.proven_optimal,
            "random_restarts": r.optimization.restarts,
        },
        "schedule": {
            "slot_count": len(r.slot_to_nodes),
            "nodes_per_slot_min": min(slot_sizes, default=0),
            "nodes_per_slot_average": round(sum(slot_sizes) / len(slot_sizes), 4) if slot_sizes else 0,
            "nodes_per_slot_max": max(slot_sizes, default=0),
            "node_to_slot": r.node_to_slot,
            "slot_to_nodes": {str(slot): members for slot, members in r.slot_to_nodes.items()},
        },
        "validation": {
            "status": "VALID" if r.validation.is_valid else "INVALID",
            "violations": violations,
            "errors": list(r.validation.errors),
        },
        "spatial_reuse": {
            "slots_with_reuse": sum(1 for members in r.slot_to_nodes.values() if len(members) > 1),
            "slots_without_reuse": len(r.node_order),
            "slots_actually_used": len(r.slot_to_nodes),
            "reuse_pair_count": len(r.reuse_pairs),
        },
    }


def export_results(r: ScheduleResult, report: str, output_dir: str | Path = "results") -> Path:
    """Write the complete result package and return its directory."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    schedule_payload = {
        "radio_range_m": r.radio_range,
        "node_count": len(r.nodes),
        "slot_count": r.optimization.slots,
        "node_to_slot": r.node_to_slot,
        "slot_to_nodes": {str(slot): members for slot, members in r.slot_to_nodes.items()},
        "matrix": r.matrix,
        "node_order": r.node_order,
        "validation_status": "VALID" if r.validation.is_valid else "INVALID",
    }
    (out / "schedule.json").write_text(
        json.dumps(schedule_payload, indent=2), encoding="utf-8"
    )

    with (out / "schedule.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["node", "slot"])
        for node in r.node_order:
            writer.writerow([node, r.node_to_slot[node]])

    (out / "statistics.json").write_text(
        json.dumps(_statistics(r), indent=2), encoding="utf-8"
    )

    conflict_payload = {
        "nodes": sorted(r.conflict_graph.nodes()),
        "edges": _conflict_edges(r),
    }
    (out / "conflict_graph.json").write_text(
        json.dumps(conflict_payload, indent=2), encoding="utf-8"
    )

    (out / "final_report.txt").write_text(report, encoding="utf-8")
    return out
