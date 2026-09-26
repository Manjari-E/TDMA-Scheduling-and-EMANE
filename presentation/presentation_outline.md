# Presentation outline (15 slides)

Numbers below come from real runs of `input/nodes.json` (5 slots, 23 edges, 55 conflicts) and `input/nodes_dense.json` (9 -> 7 slots). Re-run and update before presenting.

**1. Title** - TDMA Schedule Planner and Optimizer. *Show:* title, your name. *Say:* one-sentence goal. *Q:* What does the project do?

**2. Problem** - 16 radios, shared channel, collisions. *Show:* nodes scattered on a map. *Say:* we must decide who transmits when. *Q:* Why not let everyone transmit?

**3. Motivation** - fewer slots = shorter frame = more throughput. *Show:* 16 slots vs 5 slots bars. *Q:* Why reduce slots?

**4. TDMA concept** - repeating slots, one owner each. *Show:* timeline strip. *Say:* classroom "your turn" analogy. *Q:* TDMA vs CSMA?

**5. Network topology** - nodes/edges from coordinates, 500 m. *Show:* the 16-node graph. *Q:* Why 500 m? Is exactly 500 connected? (our rule: yes, `<=`)

**6. 1-hop and 2-hop interference** - hidden terminal A-B-C. *Show:* 3-node diagram with B hearing both. *Q:* Why do A and C need different slots?

**7. Conflict graph** - 23 one-hop + 32 two-hop = 55 edges. *Show:* conflict graph beside topology. *Q:* Difference between communication graph, conflict graph, hop distance, physical distance?

**8. Distance-2 coloring** - colour = slot. *Show:* coloured nodes. *Q:* Why not ordinary colouring? Why is it NP-hard?

**9. Optimization and spatial reuse** - orderings, DSATUR, restarts, compaction, clique bound. *Show:* heuristic comparison table (nodes.json: 5/6/5/5/5; dense: 9/8/7/7/7). *Q:* Is your answer optimal? (proven only when it equals the clique bound; true for both demo inputs, not in general)

**10. System architecture** - pipeline diagram from the README. *Q:* Why modular?

**11. Implementation** - Python + NetworkX; the conflict builder and validator are written by hand. *Show:* module list. *Q:* Why NetworkX? What did you write yourself?

**12. Results** - 5 slots for 16 nodes; slot table; matrix. *Show:* the Slot x Node matrix. *Q:* Show me a reused slot and justify it (e.g. Node_01 & Node_04, 3 hops).

**13. Validation** - independent BFS validator; 0 violations; demo of an injected violation. *Show:* VALID box and INVALID box. *Q:* How do you know the validator is right? (independent code path, tests with deliberate violations, cross-check with `nx.power`)

**14. EMANE integration** - what EMANE is, TDMA model, XML generator. *Say clearly:* XML generation implemented; NOT tested in EMANE. *Q:* Did it run in EMANE? (No - state the blocker.)

**15. Limitations and future work** - heuristic, node-based, disc model, static. *Q:* What if nodes move? Network disconnected? 100 nodes?
