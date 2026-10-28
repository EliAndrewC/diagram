# Tasks - feature 443, the work-budget tooling

## Occasions

- none for a map: the counters change no manifest (FR-004 proves it); no glyph, placement or record change. The `work-budget`
  agent's first dispatches are T05's two fixtures.

## Tasks

- [x] T01 The shared counters and their attribution: `l7r/diagram/work_counts.py`, the sites in `_geom/primitives.py`, `_geom/indexes.py` and `overlap/registry.py`, `driver._run_stages`' per-stage copy; no Python call added, the overhead measured (D1-D3; FR-001, FR-002, SC-001); the stages' candidate loops are T09-T12
      research: rendering
      verify: DONE. landed: the shared counters landed: Python calls unmoved (-0.005% at 40 households), +1% wall inside the -4% floor, inert under -O (research/overhead.md)
- [x] T02 (after T09-T12) `make work-budget` and the standing record `dev/work-budget.md` with today's figures for every stage at 10, 20, 40 and 80 households; `make counters-inert` in `make done` (D4, D5; FR-003, FR-004, SC-001, SC-002, SC-004)
      research: rendering
      verify: DONE. landed: make work-budget writes the standing record (dev/work-budget.md, every stage at 10/20/40/80, research/first-record.md: no roll at 80, the hinterland 77% of the counted work); make counters-inert passes on seed 25 and runs in make done
- [x] T03 The budget table `dev/work-budget.json`, `make budget-set` and `make budget-change`, the WORDS hook `budget-change-hooks.sh`, the table a guard file (D6; FR-005, SC-003)
      research: rendering
      verify: DONE. landed: landed: dev/work-budget.json (every STAGES stage, unbudgeted; a guard file), scripts/budget_change.py (budget-set from a SOUND verdict only; budget-change and budget-program need WORDS and are logged in dev/work-budget-changes.jsonl), budget-change-hooks.sh checking WORDS against the GM's messages; each refusal red with its condition deleted
- [x] T04 The ratchet `make work-budget-review` in the push, and the standing record printed by `make land` and `make speckit-todo` (D7, D8; FR-006, FR-007, SC-003, SC-004)
      research: rendering
      verify: DONE. landed: landed: make work-budget-review in the push beside perf-review (accepted stages held at 40 and 80 households to the accepted figure and the budget, from a run at the pushed engine; seam CI_WORK_BUDGET_REVIEW; no arbiter accept), the standing record printed by make land on engine code and make speckit-todo under 444; each red with its condition deleted
- [x] T05 The `work-budget` agent, `docs/work-budget-rubric.md`, `make work-budget-bundle MODE=budget|audit`, the two fixtures dispatched and their rulings held by a test (D9-D11; FR-008, FR-009, SC-005)
      research: rendering
      verify: DONE. landed: landed: the work-budget agent and rubric, make work-budget-bundle (MODE BUDGET refuses code and today's counts, red with the refusal deleted), the ledger check; FR-009 held by the typed agent's rulings - the funnel OVER (MODE AUDIT against the rubric's reference; MODE 1 ruled UNDERIVED's acceptance NOT LEGITIMATE), the grid placer SOUND at round 4 (the arbiter's continues on rounds 3 and 4). Departure from D9: work-budget is not added to the WAVE JOBS list - that list is the GM's authorization and a new fan-out is his to grant
- [x] T06 `.specify/templates/phase-checklist.md` and `make land`'s refusal of a feature-444 `phase:` task with its checklist absent, short or unticked (D12; FR-010, SC-006)
      research: rendering
      verify: DONE. landed: landed: the phase checklist template (eight boxes) and land's refusal of a 444 phase task with its checklist absent, short or unticked, asked among the cheap refusals; red with the call and with each condition deleted
- [x] T07 `dev/rust-tooling.md` and `make rust-tooling` in `make hooks-test`, over every tracked file and the Makefile's recipes (D13; FR-011, SC-007)
      research: rendering
      verify: DONE. landed: landed: dev/rust-tooling.md with a row for each of the 43 readers and 14 make targets the check finds (check-file-scale.py among them), make rust-tooling in hooks-test, failing on a scratch reader of every D13 kind with no row; red with its condition deleted. The design's rule that every one-for-one, partial and rewritten row is proven on a Rust fixture before the first Rust phase lands is carried to 444's step 5 in the inventory's header
- [x] T08 `docs/guards.md`, `docs/reviews.md` and each target's help name every change; each guard proven to fire with it deleted; the 443-end bookend; `make feature-report F=443 WRITE=1` (FR-012, SC-008)
      research: rendering
      verify: DONE. landed: landed: docs/guards.md rows for each refusal 443 added (the budget hook and budget-set, the push ratchet, counters-inert, the bundle's refusals with the derivation form, the phase checklist, rust-tooling, land's tooling tests), each proven red with it deleted in its task; the root CLAUDE.md's work-budget line; the 443-end bookend; the feature report
- [x] T09 The candidate-loop counters of the water and fields stages (water_frame, field, sink, waterward, pond_stock, pond_bank): the walk's loops filtered and hand-read, each loop that tries a site given its candidate@<function> increment, the excluded loops listed with why (D2; FR-001, research/candidate-loops.md)
      research: rendering
      verify: DONE. landed: the water and fields stages' candidate loops counted (research/candidate-loops.md, T09 section); Python calls +0.031% at 40 households; comb.py split at the 1,000-line bar
- [x] T10 The candidate-loop counters of the homesteads family (seat, homesteads, appurtenances, burial, lane_wells, sties, washing): the walk's loops filtered and hand-read - the getattr-dispatched seat region, free ground, access and site corridors and homesteads/stages.py included - each given its increment, the excluded listed with why (D2; FR-001)
      research: rendering
      verify: DONE. landed: the homesteads family's candidate loops counted (research/candidate-loops.md, T10 section, three misses of the walk added); Python calls -0.03% at 40 households; stages.py split at the 1,000-line bar; the rank step's drift carried to 405 T166
- [x] T11 The candidate-loop counters of the ways (track, web, crossings): the walk's loops filtered and hand-read - the cross-check's misses gap_ways way_out and trace, meet near_misses and web_lines included - each given its increment, the measuring loops excluded with why (D2; FR-001)
      research: rendering
      verify: DONE. landed: the ways' candidate loops counted (research/candidate-loops.md, T11 section; no miss in the cross-check); Python calls -0.15% at 40 households
- [x] T12 The candidate-loop counters of ground cover, the frame, the notice board and the labels (hinterland, woodland, windbreak, bamboo, frame, notice, labels): the walk's loops filtered and hand-read, each given its increment, the excluded listed with why (D2; FR-001)
      research: rendering
      verify: DONE. landed: ground cover, frame, notice and labels' candidate loops counted (research/candidate-loops.md, T12 section; one miss of the walk added); Python calls +0.0001% at 40 households
- [x] T13 A derivation's form checked before any dispatch: .specify/templates/derivation.md (each factor's scope, value, reason and worst case; the cheaper algorithms considered), make work-budget-bundle MODE=budget refusing a derivation short of a field, the phase checklist's box 2 naming the template (the GM 2026-10-28)
      research: rendering
      verify: DONE. landed: landed: the derivation template and the bundle's refusal of a derivation short of a field (a factor's scope, worst case, every column; each standard cheaper algorithm considered), naming the field; box 2 names the template; both fixtures in the form, the grid placer SOUND again on it; red with the check deleted
