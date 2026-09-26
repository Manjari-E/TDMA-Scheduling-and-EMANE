"""Turns a ScheduleResult into readable terminal text (no computation here)."""
from __future__ import annotations

from typing import List

from .conflict_graph import ONE_HOP, TWO_HOP
from .scheduler import ScheduleResult
from .topology import topology_summary

BAR = "=" * 64


def _title(text: str) -> str:
    return f"\n{BAR}\n{text}\n{BAR}"


def _short(name: str) -> str:
    """'Node_07' -> '07' so the matrix stays narrow; other names unchanged."""
    return name[5:] if name.startswith("Node_") else name


def format_inputs(r: ScheduleResult) -> str:
    lines = [_title("1. INPUT COORDINATES (metres)")]
    lines.append(f"{'Node':<12}{'X':>10}{'Y':>10}")
    for name, (x, y) in r.nodes.items():
        lines.append(f"{name:<12}{x:>10.1f}{y:>10.1f}")
    return "\n".join(lines)


def format_topology(r: ScheduleResult, verbose: bool) -> str:
    s = topology_summary(r.comm_graph)
    lines = [_title("2. COMMUNICATION GRAPH")]
    lines.append(f"Radio range        : {r.radio_range:.1f} m (connected when distance <= range)")
    lines.append(f"Nodes              : {s['nodes']}")
    lines.append(f"Communication edges: {s['edges']}")
    lines.append(f"Degree min/avg/max : {s['min_degree']} / {s['avg_degree']:.2f} / {s['max_degree']}")
    lines.append(f"Connected          : {'yes' if s['connected'] else 'NO - ' + str(len(s['components'])) + ' components'}")
    if s["isolated"]:
        lines.append(f"Isolated nodes     : {', '.join(s['isolated'])}")
    lines.append("\nEdges (derived from coordinates):")
    for a, b, data in sorted(r.comm_graph.edges(data=True)):
        lines.append(f"  {a} -- {b}   ({data['distance']:.1f} m)")
    lines.append("\nNeighbours:")
    for node in sorted(r.comm_graph.nodes()):
        neigh = ", ".join(_short(n) for n in sorted(r.comm_graph[node])) or "(none)"
        lines.append(f"  {node} [deg {r.comm_graph.degree(node)}]: {neigh}")
    return "\n".join(lines)


def format_conflicts(r: ScheduleResult, verbose: bool) -> str:
    cg = r.conflict_graph
    one = sum(1 for *_, d in cg.edges(data=True) if d["type"] == ONE_HOP)
    two = sum(1 for *_, d in cg.edges(data=True) if d["type"] == TWO_HOP)
    degrees = dict(cg.degree())
    lines = [_title("3. CONFLICT GRAPH (pairs that must NOT share a slot)")]
    lines.append(f"1-hop conflicts    : {one}")
    lines.append(f"2-hop conflicts    : {two}")
    lines.append(f"Total conflict edges: {cg.number_of_edges()}")
    if degrees:
        worst = max(degrees, key=lambda n: (degrees[n], n))
        lines.append(f"Max conflict degree: {degrees[worst]} ({worst})")
    if verbose:
        lines.append("\nAll conflicting pairs:")
        for a, b, d in sorted(cg.edges(data=True)):
            via = f" via {d['via']}" if d["type"] == TWO_HOP else ""
            lines.append(f"  {a} <-> {b}   [{d['type']}{via}]")
    else:
        lines.append("(use --verbose to list every conflicting pair)")
    return "\n".join(lines)


def format_coloring(r: ScheduleResult) -> str:
    o = r.optimization
    lines = [_title("4. DISTANCE-2 COLOURING (colour = TDMA slot)")]
    lines.append(f"{'Heuristic':<32}{'Slots':>6}")
    for name, slots in o.heuristic_slots.items():
        lines.append(f"{name:<32}{slots:>6}")
    lines.append("")
    lines.append(f"Baseline (greedy, JSON order): {o.baseline_slots} slots")
    lines.append(f"Best found                   : {o.slots} slots  <- {o.best_heuristic}")
    lines.append(f"Improvement over baseline    : {o.baseline_slots - o.slots} slot(s)")
    lines.append(f"Lower bound (largest clique) : {o.lower_bound} slots")
    if o.proven_optimal:
        lines.append("Optimality                   : PROVEN optimal (slots == lower bound)")
    else:
        lines.append("Optimality                   : NOT proven (best is between "
                     f"{o.lower_bound} and {o.slots} slots)")
    return "\n".join(lines)


def format_schedule(r: ScheduleResult) -> str:
    lines = [_title("5. NODE -> SLOT MAPPING")]
    for node, slot in r.node_to_slot.items():
        lines.append(f"  {node} -> Slot {slot}")
    lines.append("\nSlot -> Nodes:")
    for slot, members in r.slot_to_nodes.items():
        lines.append(f"  Slot {slot:02d}: {', '.join(members)}")
    return "\n".join(lines)


def format_matrix(r: ScheduleResult) -> str:
    labels = [_short(n) for n in r.node_order]
    width = max(len(x) for x in labels)
    header_label = "Slot \\ Node"
    lines = [_title("6. SLOT x NODE MATRIX (1 = node transmits in that slot)")]
    lines.append(f"{header_label:<12}| " + " ".join(f"{x:>{width}}" for x in labels))
    lines.append("-" * 12 + "+" + "-" * (1 + (width + 1) * len(labels)))
    for slot, row in enumerate(r.matrix):
        cells = " ".join(f"{v:>{width}}" for v in row)
        lines.append(f"{'Slot ' + format(slot, '02d'):<12}| {cells}")
    return "\n".join(lines)


def format_reuse(r: ScheduleResult, verbose: bool) -> str:
    lines = [_title("7. SPATIAL REUSE")]
    if not r.reuse_pairs:
        lines.append("No slot is shared: every node has its own slot.")
        return "\n".join(lines)
    multi = [s for s, m in r.slot_to_nodes.items() if len(m) > 1]
    lines.append(f"Slots used by more than one node: {len(multi)} of {len(r.slot_to_nodes)}")
    lines.append(f"Slots without reuse would be     : {len(r.node_order)} (one per node)")
    lines.append(f"Slots actually used              : {len(r.slot_to_nodes)}")
    hops = [p.hop_distance for p in r.reuse_pairs if p.hop_distance is not None]
    if hops:
        lines.append(f"Closest reusing pair (hops)      : {min(hops)}  (must be >= 3)")
    limit = None if verbose else 8
    lines.append("\nExamples (same slot, why it is allowed):")
    for p in r.reuse_pairs[:limit]:
        hop = "no path (different components)" if p.hop_distance is None else f"{p.hop_distance} hops apart"
        lines.append(f"  Slot {p.slot}: {p.node_a} & {p.node_b}  -> {p.physical_distance:7.1f} m, {hop}")
    if limit and len(r.reuse_pairs) > limit:
        lines.append(f"  ... {len(r.reuse_pairs) - limit} more (use --verbose)")
    return "\n".join(lines)


def format_validation(r: ScheduleResult) -> str:
    v = r.validation
    lines = ["", "=" * 40, "TDMA SCHEDULE VALIDATION", "=" * 40]
    lines.append(f"Nodes              : {v.nodes}")
    lines.append(f"Conflicting Pairs  : {v.conflicting_pairs}")
    lines.append(f"Slots Used         : {v.slots_used}")
    lines.append(f"Violations         : {len(v.violations) + len(v.errors)}")
    lines.append(f"Status             : {'VALID' if v.is_valid else 'INVALID'}")
    lines.append("=" * 40)
    for err in v.errors:
        lines.append(f"ERROR: {err}")
    for x in v.violations:
        lines.append(f"VIOLATION: {x.node_a} and {x.node_b} [{x.conflict_type}] "
                     f"both use Slot {x.slot}")
    return "\n".join(lines)


def format_statistics(r: ScheduleResult) -> str:
    s = topology_summary(r.comm_graph)
    sizes = [len(m) for m in r.slot_to_nodes.values()]
    lines = [_title("8. FINAL STATISTICS")]
    lines.append(f"Nodes                 : {s['nodes']}")
    lines.append(f"Communication edges   : {s['edges']}")
    lines.append(f"Conflict edges        : {r.conflict_graph.number_of_edges()}")
    lines.append(f"Heuristic used        : {r.optimization.best_heuristic}")
    lines.append(f"Slots used            : {r.optimization.slots}")
    lines.append(f"Lower bound           : {r.optimization.lower_bound}")
    lines.append(f"Nodes per slot (min/avg/max): {min(sizes)} / {sum(sizes)/len(sizes):.2f} / {max(sizes)}")
    lines.append(f"Validation            : {'VALID' if r.validation.is_valid else 'INVALID'}")
    return "\n".join(lines)


def build_report(r: ScheduleResult, verbose: bool = False) -> str:
    parts: List[str] = [
        format_inputs(r),
        format_topology(r, verbose),
        format_conflicts(r, verbose),
        format_coloring(r),
        format_schedule(r),
        format_matrix(r),
        format_reuse(r, verbose),
        format_validation(r),
        format_statistics(r),
    ]
    return "\n".join(parts) + "\n"
