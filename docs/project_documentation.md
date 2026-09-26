# TDMA Schedule Planner and Optimizer - Project Documentation

## 1. Introduction
A centralised Python program that reads the coordinates of 16 static radios and
computes a collision-free TDMA schedule that reuses slots wherever it is safe.

## 2. Problem statement
Assign each radio a time slot so that no two radios that could interfere share a
slot, while using as few slots as practical. The exact minimum is NP-hard, so a
heuristic is used.

## 3. Objectives
Validated JSON input; NetworkX communication graph; 1-hop and 2-hop conflict
model; distance-2 colouring; Node-to-Slot map and Slot x Node matrix;
automatic independent validation; statistics; modular, tested code.

## 4. Concepts
- **TDMA**: time is divided into repeating slots; a radio transmits only in its own slot.
- **Communication range**: 500 m. Two radios at distance <= range can hear each other (assumption: boundary inclusive).
- **Graph**: nodes = radios, edges = "can hear each other".
- **1-hop**: directly connected. **2-hop**: not connected, but share a neighbour.
- **Hidden terminal**: in A-B-C, A and C cannot hear each other, both transmit, and B hears a collision.
- **Conflict graph**: edge = "must not share a slot" (all 1-hop + 2-hop pairs).
- **Graph colouring**: give every node a colour so conflicting nodes differ. Colour = slot.
- **Spatial reuse**: nodes not in conflict (>= 3 hops apart, or in different components) share a slot.
- **Heuristic optimisation**: a fast rule that usually gives a good, not provably best, answer.

Four ideas kept separate: *physical distance* (metres), *communication graph* (distance <= range),
*hop distance* (edges on the shortest path), *conflict graph* (hop distance 1 or 2).
Two nodes can be 900 m apart physically yet only 2 hops apart in the graph.

## 5. System architecture
```
                +-------------+    +----------+    +-----------------+
 nodes.json --> | input_parser| -> | distance | -> | topology        |
                +-------------+    +----------+    | (comm. graph)   |
                                                    +--------+--------+
                                                             v
 +--------+   +-----------+   +----------+   +------------------+
 | report | <-| validator | <-| scheduler| <-| coloring         | <- conflict_graph
 +--------+   +-----------+   +----+-----+   +------------------+
                                   |
                                   v
                             emane_bridge (bonus) -> schedule.xml
```
`validator` takes only the communication graph and the schedule; it does not import the conflict builder or the colouring code.

## 6. Algorithm
1. Load and validate JSON. 2. Compute all pairwise distances. 3. Build communication graph.
4. Build conflict graph. 5. Run heuristics, keep the best, compact. 6. Convert colours to slots.
7. Build matrix and reuse report. 8. Validate independently. 9. Print report; exit 1 if invalid.

## 7. Distance calculation
`d = sqrt((x2-x1)^2 + (y2-y1)^2)`. The range is configurable (`--range`) so the code is reusable and testable
with other radios; the assignment value 500 m is the default. One function (`is_within_range`) applies `d <= range`
everywhere, so the boundary rule is consistent.

## 8. Communication graph
Every unordered pair is checked once; an edge is added if in range and stores its distance.
No edges are hard-coded. Reported: edges, degree statistics, neighbours, connected components, isolated nodes.

## 9. Conflict graph
- Rule 1: each communication edge becomes a `1-hop` conflict.
- Rule 2: for each node M, every pair of neighbours of M becomes a `2-hop` conflict (unless already 1-hop). This is the hidden-terminal case A-M-C.
- Correctness: within 2 hops <=> adjacent or common neighbour. Tests compare the result with `nx.power(G, 2)` on 25 random topologies.
- Because all constraints are edges, ordinary colouring of the conflict graph = distance-2 colouring of the communication graph.

## 10. Colouring algorithm
Greedy: visit nodes in some order; give each the lowest slot unused by its conflicting neighbours. Orders tried:
input order (baseline), largest conflict degree first, smallest-last, DSATUR (most-constrained next), and 300 seeded random orders.
Each is always valid; quality differs by order. No strategy is claimed to be optimal.

## 11. Optimisation
The best of all strategies is kept, then **compaction** tries to remove the highest slot by moving its nodes into lower slots.
A lower bound is computed as the largest clique in the conflict graph (mutually conflicting nodes need distinct slots).
If slots == bound the result is **proven** minimal for that input; otherwise the report says "not proven" and shows the gap.
Slot reuse comes from colouring itself: nodes with no conflict edge may receive the same colour.

## 12. Validation
For every node, BFS (cutoff 2 hops) on the communication graph finds all 1-hop and 2-hop partners.
Each pair with equal slots is a violation reported with both nodes, conflict type and slot. Missing nodes, unknown nodes and
invalid slot values are structural errors. Any violation -> status INVALID and process exit code 1.

## 13. Input format
```json
{"Node_01": [0.0, 0.0], "Node_02": [420.0, 60.0]}
```
Rejected with a clear message: invalid JSON, non-object top level, blank/duplicate names, non-list or wrong-length coordinates,
non-numeric / boolean / null / NaN values, and node count != 16 (unless `--dev-mode`).

## 14. Output format
```
Node_01 -> Slot 0 ...
Slot \ Node | 01 02 03 ...
Slot 00     |  1  0  0 ...
```
Every column has exactly one `1` (each node transmits in one slot).

## 15. Testing
Framework: `unittest` (standard library, no extra dependency). Run `python -m unittest discover -v`.

| Required test | Where | Result (real run) |
|---|---|---|
| 1 within 500 m -> edge | test_topology | pass |
| 2 beyond 500 m -> no edge | test_topology | pass |
| 3 chain A-B-C: A,C two-hop | test_conflicts | pass |
| 4 spatial reuse | test_coloring | pass |
| 5 invalid JSON | test_input_parser | pass |
| 6 invalid coordinates | test_input_parser | pass |
| 7 valid schedule, 0 violations | test_validator | pass |
| 8 invalid schedule detected (1-hop and 2-hop) | test_validator | pass |

Total: 46 tests, all passing on Python 3.12 / networkx 3.6.1. Extra tests cover the 500 m boundary, the `nx.power` cross-check,
compaction validity, determinism by seed, disconnected components, matrix properties, CLI exit codes, and EMANE XML well-formedness.

## 16. Results (from real runs)
| Input | Nodes | Comm. edges | Conflict edges (1-hop + 2-hop) | Baseline slots | Slots used | Lower bound | Status |
|---|---|---|---|---|---|---|---|
| input/nodes.json | 16 | 23 | 55 (23 + 32) | 5 | 5 | 5 | VALID |
| input/nodes_dense.json | 16 | 35 | 67 (35 + 32) | 9 | 7 | 7 | VALID |

Observations:
- `nodes.json`: without reuse 16 slots would be needed; 5 are used. Closest pair sharing a slot is 3 hops apart. Baseline already reached the bound, so optimisation had nothing to improve. Comparing heuristics: largest-first gave 6, the others 5.
- `nodes_dense.json` (a randomly generated, seeded layout chosen because it is denser): baseline 9 -> 7 slots via smallest-last ordering; 7 equals the clique bound, so 7 is minimal for that input.
- These proofs are per-input; the algorithm is not guaranteed optimal in general.

## 17. Limitations
Heuristic; node (not link) scheduling; ideal disc radio model; only 1- and 2-hop interference; static positions; no traffic demand or
fairness; O(n^2) construction.

## 18. Future improvements (not implemented)
Link scheduling; traffic-weighted slots; SINR interference model; incremental rescheduling on mobility; exact ILP/SAT for small inputs; local search (e.g. tabu).

## 19. EMANE (Part 2, bonus)
**What EMANE is.** The Extendable Mobile Ad-hoc Network Emulator: it emulates radio behaviour (propagation, MAC) between virtual nodes
(NEMs) so real applications can run over an emulated wireless network.
**Why use it.** It would let the schedule be checked with real packets rather than only by graph logic.
**TDMA Radio Model.** Per the EMANE Guide, time is a repeating multiframe of frames of slots; a slot can be transmit, receive or idle for each NEM.
A schedule is XML; one with a `<structure>` element is a full schedule. In a full schedule, slots not listed for an NEM are receive slots
(as documented at emane.io/tdma-radio-model). Schedules are published as events, e.g. `emaneevent-tdmaschedule schedule.xml -i <iface>` (EMANE tutorial).
**Mapping implemented** (`src/emane_bridge.py`): NEM id = 1-based rank of the node name; one frame; our slot k = EMANE slot index k;
`<slot index="k" nodes="...">` lists the transmitters of slot k. Default 1500 us slots, 2.4G, 1M are placeholders to tune.
Example generated from `input/nodes.json`:
```xml
<emane-tdma-schedule>
  <structure frames="1" slots="5" slotoverhead="0" slotduration="1500" bandwidth="1M"/>
  <multiframe frequency="2.4G" power="0" class="0" datarate="1M">
    <frame index="0">
      <slot index="0" nodes="1,4,10,16"/>
      ...
```
**Planned validation.** Run 16 NEMs with the TDMA model and a propagation model whose connectivity matches the 500 m graph; load the schedule; send traffic
and check that transmissions occur only in assigned slots and that frames are not lost to collisions.
**Setup procedure (to be followed on a Linux machine; steps not executed here).** Install EMANE from the packages/instructions on emane.io, write a platform XML
for 16 NEMs, a TDMA radio-model XML, and a transport/event-service configuration; start the emulation; publish the schedule with `emaneevent-tdmaschedule`.
**Implementation status.** Only the schedule-to-XML generator exists. Not verified: (a) EMANE accepting the file, (b) the multi-NEM `nodes="1,4,10,16"` list syntax
against the schema shipped with your EMANE version (the tutorial shows single-NEM examples), (c) any packet behaviour. **Blocker:** no EMANE installation/testbed was available.
Nothing in Part 2 should be described as "working" until it has been run.
