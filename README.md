# TDMA Schedule Planner and Optimizer

A centralised Python simulator that takes the coordinates of 16 static wireless
radios, builds the communication topology with NetworkX, finds every pair of
radios that could interfere (1-hop and 2-hop), and produces a **collision-free
TDMA schedule** using distance-2 graph colouring with spatial reuse.

## Problem statement
Radios that transmit at the same time can collide at a receiver. In TDMA each
radio gets a time slot. Fewer slots means a shorter frame and more throughput,
but two radios may share a slot only if they cannot interfere: they must be more
than two hops apart (the **hidden-terminal** problem makes 2 hops matter, not
just 1). Finding the minimum number of slots is NP-hard, so this project uses
heuristics and reports honestly what it can and cannot prove.

## Features
- JSON input with strict validation (16 nodes in assignment mode; `--dev-mode` for testing)
- Euclidean distances, configurable radio range (default 500 m, `<=` means connected)
- Communication graph (NetworkX) derived purely from coordinates
- Conflict graph with labelled 1-hop / 2-hop conflicts
- Five colouring strategies + slot compaction, best result kept, lower bound reported
- Node-to-Slot map, Slot x Node 0/1 matrix, spatial-reuse report
- Independent validator (recomputes conflicts by BFS, not from the conflict graph)
- Clean CLI errors (no stack traces for bad input); exit code 1 if a schedule is invalid
- Bonus: EMANE TDMA schedule XML generator (**not tested with EMANE**, see below)

## Architecture
```
nodes.json -> input_parser -> distance -> topology (communication graph)
                                              |
   report <- validator <- scheduler <- coloring <- conflict_graph
                                 \-> emane_bridge (bonus) -> schedule.xml
```

## Algorithm (short)
1. Parse and validate coordinates.
2. Edge between two nodes if `sqrt(dx^2 + dy^2) <= range`.
3. Conflict edge for every communication edge (1-hop) and for every pair of
   neighbours of a common node (2-hop).
4. Colour the conflict graph greedily under several node orderings (input order,
   largest-first, smallest-last, DSATUR, 300 seeded random orders), keep the best,
   then try to eliminate the top slot by moving its nodes to lower slots.
5. Colour = slot. Same colour = spatial reuse.
6. Validate independently. Compute a clique lower bound to say whether the result is provably optimal.

## Requirements and installation
Python 3.9+ (developed on 3.12) and `networkx`.
```bash
cd tdma-scheduler
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```bash
python main.py --input input/nodes.json                 # 16-node assignment mode
python main.py --input input/nodes.json --verbose       # list every conflict / reuse pair
python main.py --input input/nodes.json --range 500 --output report.txt
python main.py --input input/nodes_dense.json           # denser layout: optimiser gives 9 -> 7 slots
python main.py --input input/example_5_nodes.json --dev-mode   # the 5-node hand example
python main.py --input input/nodes.json --emane-xml schedule.xml   # bonus, untested with EMANE
```
Exit codes: `0` valid schedule, `1` schedule failed validation, `2` bad input/arguments.

## JSON input
```json
{
  "Node_01": [0.0, 0.0],
  "Node_02": [420.0, 60.0],
  "Node_03": [850.0, -40.0]
}
```
Assignment mode needs exactly 16 entries. Names must be unique; each value is `[x, y]` in metres.

## Sample output (`input/nodes.json`, real run)
```
Slot \ Node | 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16
------------+-------------------------------------------------
Slot 00     |  1  0  0  1  0  0  0  0  0  1  0  0  0  0  0  1
Slot 01     |  0  1  0  0  0  0  0  1  1  0  0  0  0  0  1  0
Slot 02     |  0  0  1  0  1  0  0  0  0  0  1  0  0  0  0  0
Slot 03     |  0  0  0  0  0  1  0  0  0  0  0  1  1  0  0  0
Slot 04     |  0  0  0  0  0  0  1  0  0  0  0  0  0  1  0  0

TDMA SCHEDULE VALIDATION
Nodes              : 16
Conflicting Pairs  : 55
Slots Used         : 5
Violations         : 0
Status             : VALID
```
16 nodes, 23 communication edges, 55 conflict edges (23 one-hop + 32 two-hop), 5 slots.
A clique of 5 mutually-conflicting nodes exists (Node_06 with its four neighbours),
so 5 is provably the minimum **for this topology**. That is a property of this input, not a general guarantee.

## Testing
```bash
python -m unittest discover -v
```
`unittest` is in the standard library, so no extra dependency is needed.
At the time of writing: 46 tests, all passing (run on Python 3.12, networkx 3.6.1).
`pytest` is not required and has not been run against these tests.

## Project structure
```
tdma-scheduler/
  main.py                 CLI
  requirements.txt
  input/                  nodes.json (16), nodes_dense.json (16), example_5_nodes.json (dev)
  src/                    config, input_parser, distance, topology, conflict_graph,
                          coloring, scheduler, validator, report, emane_bridge
  tests/                  distance, topology, conflicts, coloring, validator,
                          input_parser, scheduler_cli (+ EMANE XML)
  docs/project_documentation.md
  presentation/presentation_outline.md
```

## EMANE status (Part 2 / bonus)
| Item | Status |
|---|---|
| Schedule -> EMANE TDMA schedule XML (`src/emane_bridge.py`) | Implemented; XML shown to be well-formed by unit tests |
| Loading it into a running EMANE emulation | **Not done / not tested** (no EMANE installation used) |
| Packet-delivery validation | **Not done** |

See `docs/project_documentation.md` section 19 for the setup procedure and design.

## Limitations
- Heuristic: optimality is proven only when slots equal the clique lower bound.
- Schedules nodes (one transmit slot per node), not individual links or traffic demands.
- Pure disc model: no fading, obstacles, or interference beyond 2 hops.
- Static topology: if positions change, re-run the scheduler.
- O(n^2) pair checks are fine for tens of nodes, not for very large networks.

## Future work
Link-based scheduling and traffic-aware slot allocation; SINR-based interference;
incremental rescheduling when nodes move; exact solver (ILP/SAT) for small cases;
a tested EMANE run.
