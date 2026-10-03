# Tasks: reached across a yard (feature 317)

**Input**: plan.md (D1-D7)

## Occasions

- placement-changed: farmhouse - within the rolled share, a nucleated household with no corridor of its own may be seated against a neighbor's land, reached by passage across its yard (plan D2-D4)
- placement-changed: village lane - such a household draws no lane of its own, and the household it is reached across always keeps its way; the seating judges each corridor as the web will draw it (plan D5, D6)

## Tasks

- [x] T01 the record: brief R1 written and checked (D1, FR-001)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. R1 written (e302788ec) and checked in a page session, five rounds (d522bc76d, 0d705b6e7, 60a124a8b): quote-check, record-format, source-applicability (Wigmore, Morse), entry-drift (CartYard, Farmhouse, VillageLane, ApproachRoad), translation-check; make record-owed UNANSWERED=1: no record check is owed
- [x] T02 the corridor judged as drawn: the door leg found and laid by `lanes_of`, the reproduction refused at seating or drawn lawfully (D6, FR-004)
      research: rendering
      verify: DONE. tree.admits asks needle_loops of the tree with its ends joined as the settle joins them (tree.as_joined, 4dbcf66d1), with an exact box prefilter (ea6bdb56e); the reproduction (/tmp/repro317, seed 13 at 20 households, own parts on) rolls; t06-20.log: all eight seeds at 20 households roll; the cost below the host's noise (research R2: CPU 21.6 -> 20.1 s at 15 households, 15.6 -> 16.1 s at 40)
- [x] T03 the passage, the chain and the share, with unit tests (D2-D4, FR-002)
      research: rendering
      verify: DONE. passage.py (the walk, the adjoining land, the chain, the share, recheck_passages and relay by the whole holding), growth.py tight seats (yard side 90, TIGHT_TREE_FT), place.py landlocked; tests/settlement/test_passage_317.py (24) and tests/hamletgen/homesteads/test_growth.py; R6-R9: 14 passages at 15 households (seeds 1-16), 11 at 40 (seeds 2, 25, 39, 47), passage_unfit 0
- [x] T04 the reach predicate with passages, with unit tests (D5, FR-003)
      research: rendering
      verify: DONE. checks.unreached_houses counts a household reached across a yard reached through its neighbor's chain; tree.passage_anchors keeps the anchor's corridor owed and never pruned; geom.lane_houses keeps no lane for, carries no end to and cuts no web toward such a household; tests in tests/hamletgen/ways (test_checks, test_tree, test_geom, test_sweeps); the village-lane glyph check's F1 resolved (gc-vl-f1-anchor-way)
- [x] T05 the drawing page: brief R2, what the maps draw (D1, FR-001)
      research: rendering
      verify: DONE. the drawing page (0081-village-lanes.drawing.html) says what the maps draw: the passage bullet written in brief R2 and checked in R2-R3 (record-format rounds 1-2, quote-check, entry-drift); make record-owed UNANSWERED=1: no record check is owed
- [x] T06 the route's own parts retried on the fixed judge, kept only if it pays (D6, FR-006)
      research: rendering
      verify: DONE. retried on the fixed judge and WITHDRAWN: the route searched per garden layout round its own parts paid before feature 315 merged and cost the homesteads stage 3-43% more after it (research R4, R8); the corridor's route keeps off the house alone, as on main; the judge defect its cohort run exposed (seed 18) stays closed (tree.laid_run, own_clear)
- [x] T07 timing against main at 15 and 40 households; the cohort and the pool against main (FR-005, FR-006)
      research: rendering
      verify: DONE. the final bookends, three alternated takes on 2ba1f3cf against main 38901e2df: band 2 - 15 households -5.0%, 10 -5.1%, 20 +2.5%, 40 +1.1%; seeds 25 and 47 at 20 households and 47 at 40 cross 10%, explained with a control (perf-317-control-nopass: the passage share at 0 leaves the homesteads stage within 8-10% of main); the cohort (make cohort N=24 JOBS=2, the six pinned seeds included) 30 of 30 on main and on the clone; the pool on the gate, green
- [x] T08 the known bugs listed with their owners and states (D7, FR-007, SC-006)
      research: rendering
      verify: DONE. research R5 lists every bug found with its owner and state: the feature's own fixed (the judge as drawn, seeds 18 and 47, the persimmon reseat, the kura and byre, the passage on the finished seating, four tooling bugs); 315's cohort seeds with the Diagram (Inashiro) session (landed in 315); the lane code's pre-existing figures against its page and the sliver joint, to a follow-up put to the GM
- [x] T09 `make done`, the bookends, the occasions' reviews
      research: rendering
      verify: DONE. make done green on the engine as it lands (5058ad68); the final bookends, three alternated takes against main 38901e2df: band 3 (seed 25 at 40 households +21.6%), explained with its control (perf-317-control-40), confirmed consistent and audited justified by the perf-audit subagent - the GM's sign-off (make perf-signoff) is owed at the push; the occasions' reviews: farmhouse and village lane on Inashiro to their two-round cap (the farmhouse's round-2 fix verified by measurement), homestead bamboo on Kuwabata PASS; the claims checked in eight impl-drift rounds
- [ ] T10 the wood seats reserved clear of the afternoon sun lane, held by a gate test (D7, FR-007)
      research: rendering
      verify:
- [ ] T11 a way of its own asked of straight and round-the-house paths only, the drawing page saying so (D2 amended, FR-002)
      research: rendering
      verify:
- [ ] T12 `make done`, the bookends, the occasions' reviews and the claims on the amended engine (FR-005, FR-006)
      research: rendering
      verify:
