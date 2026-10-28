# Tasks - feature 443, the work-budget tooling

## Occasions

- none for a map: the counters change no manifest (FR-004 proves it); no glyph, placement or record change. The `work-budget`
  agent's first dispatches are T05's two fixtures.

## Tasks

- [x] T01 The shared counters and their attribution: `l7r/diagram/work_counts.py`, the sites in `_geom/primitives.py`, `_geom/indexes.py` and `overlap/registry.py`, `driver._run_stages`' per-stage copy; no Python call added, the overhead measured (D1-D3; FR-001, FR-002, SC-001); the stages' candidate loops are T09-T12
      research: rendering
      verify: DONE. landed: the shared counters landed: Python calls unmoved (-0.005% at 40 households), +1% wall inside the -4% floor, inert under -O (research/overhead.md)
- [ ] T02 (after T09-T12) `make work-budget` and the standing record `dev/work-budget.md` with today's figures for every stage at 10, 20, 40 and 80 households; `make counters-inert` in `make done` (D4, D5; FR-003, FR-004, SC-001, SC-002, SC-004)
      research: rendering
- [ ] T03 The budget table `dev/work-budget.json`, `make budget-set` and `make budget-change`, the WORDS hook `budget-change-hooks.sh`, the table a guard file (D6; FR-005, SC-003)
      research: rendering
- [ ] T04 The ratchet `make work-budget-review` in the push, and the standing record printed by `make land` and `make speckit-todo` (D7, D8; FR-006, FR-007, SC-003, SC-004)
      research: rendering
- [ ] T05 The `work-budget` agent, `docs/work-budget-rubric.md`, `make work-budget-bundle MODE=budget|audit`, the two fixtures dispatched and their rulings held by a test (D9-D11; FR-008, FR-009, SC-005)
      research: rendering
- [ ] T06 `.specify/templates/phase-checklist.md` and `make land`'s refusal of a feature-444 `phase:` task with its checklist absent, short or unticked (D12; FR-010, SC-006)
      research: rendering
- [ ] T07 `dev/rust-tooling.md` and `make rust-tooling` in `make hooks-test`, over every tracked file and the Makefile's recipes (D13; FR-011, SC-007)
      research: rendering
- [ ] T08 `docs/guards.md`, `docs/reviews.md` and each target's help name every change; each guard proven to fire with it deleted; the 443-end bookend; `make feature-report F=443 WRITE=1` (FR-012, SC-008)
      research: rendering
- [ ] T09 The candidate-loop counters of the water and fields stages (water_frame, field, sink, waterward, pond_stock, pond_bank): the walk's loops filtered and hand-read, each loop that tries a site given its candidate@<function> increment, the excluded loops listed with why (D2; FR-001, research/candidate-loops.md)
      research: rendering
- [ ] T10 The candidate-loop counters of the homesteads family (seat, homesteads, appurtenances, burial, lane_wells, sties, washing): the walk's loops filtered and hand-read - the getattr-dispatched seat region, free ground, access and site corridors and homesteads/stages.py included - each given its increment, the excluded listed with why (D2; FR-001)
      research: rendering
- [ ] T11 The candidate-loop counters of the ways (track, web, crossings): the walk's loops filtered and hand-read - the cross-check's misses gap_ways way_out and trace, meet near_misses and web_lines included - each given its increment, the measuring loops excluded with why (D2; FR-001)
      research: rendering
- [ ] T12 The candidate-loop counters of ground cover, the frame, the notice board and the labels (hinterland, woodland, windbreak, bamboo, frame, notice, labels): the walk's loops filtered and hand-read, each given its increment, the excluded listed with why (D2; FR-001)
      research: rendering
