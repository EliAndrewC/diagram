# 427-call-volume-refactors - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-26 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** A session asks which functions run millions of times and from which loop, and one command
   answers.
2. **The constraints.** D1; FR-001, FR-002, SC-001.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 2 and 5; `tooling-perf-fanout.md`.
4. **Do they describe the world here?** Yes: the reference walk produced `research/fanout-2026-10-26.txt`.
5. **The order.** First: every engine task is scoped against its output (FR-002).
6. **The exits.** Green: its tests red without D1, and `make perf-fanout` on the current engine compared with
   `research/fanout-2026-10-26.txt` (FR-001, SC-001). Red: a red test, or a seed that passes on HEAD failing after (FR-007),
   which a tool that changes no stage cannot cause, recorded and the task set down; a claim that it cannot be done is ruled
   through `make arbiter-ask`. A seed already failing on HEAD is no exit (`request.md` 4 and 5).
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D1; `make perf-fanout` on the current engine lists the chains, compared with
   `research/fanout-2026-10-26.txt`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

<!-- plan-archive: archived 2026-10-26 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** Every snapshot says how many Python calls each stage made, on each seed.
2. **The constraints.** D2; FR-006.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 4; `call-count-flag.md`.
4. **Do they describe the world here?** Yes: counts are deterministic per seed and size.
5. **The order.** After T01; before T03, which compares what it records.
6. **The exits.** Green: its tests red without D2, and a `make perf` snapshot carrying counts. Red: what failed recorded and the
   task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D2; the counting pass's overhead on the reference seeds recorded beside the code.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

<!-- plan-archive: archived 2026-10-26 -->
### T03 Approach (checklist part A)

1. **The goal, in the world.** A landing that makes the engine do more Python work says so, and lands only on the arbiter's
   accept; a slower machine says nothing.
2. **The constraints.** D3; FR-006, SC-005.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 4; `call-count-flag.md`.
4. **Do they describe the world here?** Yes: the counts T02 records.
5. **The order.** After T02.
6. **The exits.** Green: its tests red without D3; a deliberate extra loop refuses the push and an accept clears it (US5's
   test). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D3; US5's independent test run on a scratch change.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

<!-- plan-archive: archived 2026-10-26 -->
### T04 Approach (checklist part A)

1. **The goal, in the world.** The same hamlets, rolled with tenfold fewer Python calls in each chain T04 names.
2. **The constraints.** D4; FR-002, FR-003, FR-004, FR-007, FR-008, US2.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 1 and 5; `research/hotspots-cheap-wins.md`,
   `research/hotspots-recompute.md`, `research/survey-t01.md`.
4. **Do they describe the world here?** Yes: each chain is in the T01 survey of this engine.
5. **The order.** After T03 and the start bookend; before T05 (the wells).
6. **The exits.** Green: each named chain's count down tenfold in `make perf-fanout`, the cohort with no seed regressed. Red: what
   failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Two landings: C1-C3, C5 and R6 first, then R2, R3 and R5 (the dependency).
9. **Done, measured.** Each chain's before and after count from `make perf-fanout`, and the pool reroll's manifest diff.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

<!-- plan-archive: archived 2026-10-26 -->
### T05 Approach (checklist part A)

1. **The goal, in the world.** The same shared wells, seated without re-ranking every seat against every household per well.
2. **The constraints.** D5; FR-003, FR-004, FR-007, US3.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 1 and 5; `research/hotspots-recompute.md` R1,
   `research/survey-t01.md`.
4. **Do they describe the world here?** Yes: lane_wells is the largest stage of the T01 survey of this engine (`research/survey-t01.md`).
5. **The order.** After T04, the order the GM approved (`request.md` 5).
6. **The exits.** Green: the lane_wells chain under US3's bound, the cohort with no seed regressed. Red: what failed recorded and
   the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the sort's own key, computed at once.
8. **The budget.** One landing.
9. **Done, measured.** US3's test: the lane_wells chain's count and the slowest seed's lane_wells time.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

<!-- plan-archive: archived 2026-10-26 -->
### T06 Approach (checklist part A)

1. **The goal, in the world.** `PAIR_LOOK`'s research claim says what the number is: a breadth of ours that decides which first
   well is seated, not only what the search costs.
2. **The constraints.** 385 FR-013 (a carried claims finding is fixed in the code or the claim); constitution XII (every guess
   labeled).
3. **Where each comes from.** impl-drift on T05's claims round 2 (2026-10-26): UNCLAIMED, "PAIR_LOOK = 40: how many first-well
   seats nearest the share's middle are re-ranked ... (search breadth, a GUESS)"; carried into T06 by `make land`.
4. **Do they describe the world here?** Yes: `PAIR_LOOK`'s seats are the only ones the look ahead re-ranks (`wells.py`,
   `pool[:PAIR_LOOK]`), so the number moves which seat the first of two wells takes.
5. **The order.** After T05, before the pairwise families (`request.md` 5).
6. **The exits.** Green: the claim relabeled GUESS and judged IN-STEP by impl-drift. Red: the finding recorded and the task
   set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a label, no search.
8. **The budget.** One landing, riding with the next engine task if one is ready.
9. **Done, measured.** impl-drift's verdict on `wells.py::PAIR_LOOK`; no map moves (a docstring).
10. **Before moving a constant.** n/a: the constant keeps its value.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the claim relabeled | `make claims-owed` names it, impl-drift IN-STEP |
| no map moved | `make maps-moved` (a docstring: the roll cache keeps every seed) |
<!-- plan-archive: archived 2026-10-26 -->
### T07 Approach (checklist part A)

1. **The goal, in the world.** The same homesteads seated, their parts asked of their neighbors per candidate set, not one Python
   call per pair.
2. **The constraints.** US4, FR-003, FR-004, FR-007; the GM's order (`request.md` 5): homestead parts first of the families
   outside the lanes.
3. **Where each comes from.** `research/hotspots-pairwise.md` "Homestead seating" (yards' `_filled_lattice`, `gap_ways.way_out`
   and `trace`, `wood_share`); `research/hotspots-recompute.md` R8 (`capacity.field_distances` for every free grid point), which
   US4 sends with this family. R4 (`household_reach`), which US4 also sends here, is its own task (T12): its research's direction
   is the household-keyed roll feature 297 withdrew, so it needs a design of its own (`research/t07-homestead-parts.md`).
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage, so a chain of the family outside `homesteads` is not dropped) on the then-current engine scopes
   the task to the chains that still stand (FR-002).
5. **The order.** After T06, before the ground cover family.
6. **The exits.** Green: each chain named falls at least tenfold (US4's test), the cohort with no seed regressed, the claims
   round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the same predicates asked of a candidate set (STRtree query or numpy broadcast), no new search.
8. **The budget.** One landing per chain group that changes no map, the cohort judging any that does.
9. **Done, measured.** Each chain's count before and after from `make perf-fanout`, recorded in `research/`; R8, which no chain
   shows, by its own test (US2, FR-003): the homesteads stage and `field_distances`' share at seed 47, 40 households, before and
   after, as a seed-by-seed A/B against HEAD, and a pool reroll diffed against HEAD's manifests - reported, gating nothing
   (FR-006).
10. **Before moving a constant.** n/a: no constant moves.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the chains re-scoped | `make perf-fanout` (every stage) |
| each chain converted | its count in `make perf-fanout`, `make maps-moved` |
| R8 | the homesteads stage at seed 47, 40 households, A/B of HEAD against the change in two detached worktrees, back to back, alternated; `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |


<!-- plan-archive: archived 2026-10-26 -->
### T12 Approach (checklist part A)

1. **The goal, in the world.** The same homesteads seated, the reach a candidate seat's homestead takes measured without laying
   its four garden sides' whole homesteads, fixtures included, at every candidate.
2. **The constraints.** US4 (R4 goes with the homestead family), FR-003, FR-004, FR-007; feature 297's plan C and research R9:
   a homestead's parts are rolled at the seat offered, never once per household (keyed on the household, seed 3 seated 9 of 10
   and its site was refused).
3. **Where each comes from.** `research/hotspots-recompute.md` R4; `research/t07-homestead-parts.md` (why its direction, one
   envelope per lot and size, is the withdrawn household-keyed roll).
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage) on the then-current engine scopes the
   task to R4's chains as they stand after T07 (FR-002).
5. **The order.** After T07, before the ground cover family.
6. **The exits.** Green: R4's chain at least tenfold down with the per-seat rolls kept, the cohort with no seed regressed, the
   claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the same layout, asked less often or more cheaply, not a new search.
8. **The budget.** One landing.
9. **Done, measured.** R4's chain count before and after from `make perf-fanout`, recorded in `research/`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the chain re-scoped | `make perf-fanout` (every stage) |
| R4's chain | its count in `make perf-fanout`, `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |

<!-- plan-archive: archived 2026-10-26 -->
### T08 Approach (checklist part A)

1. **The goal, in the world.** The same ground cover drawn, its keep-out and gap tests asked per candidate set.
2. **The constraints.** US4, FR-003, FR-004, FR-007; the GM's order (`request.md` 5): ground cover after the homestead parts.
3. **Where each comes from.** `research/hotspots-pairwise.md` "Ground cover" (`close_belt_gaps`, `household_bamboo` ->
   `stand_spares_seats`, `belt.fouled`, `convex_hull`, `belt_law`, `_crown_seat_clear`, the grove and hinterland genexprs).
4. **Do they describe the world here?** Re-measured first: `make perf-fanout` (every stage, so a chain in another stage is not
   dropped) scopes the task to the chains that still stand after T04 and T07 (FR-002).
5. **The order.** After the homestead parts family, before the water family.
6. **The exits.** Green: each chain named falls at least tenfold, the cohort with no seed regressed, the claims round clean.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the same tests over a candidate set.
8. **The budget.** One landing per chain group.
9. **Done, measured.** Each chain's count before and after from `make perf-fanout`, recorded in `research/`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the chains re-scoped | `make perf-fanout` (every stage) |
| each chain converted | its count in `make perf-fanout`, `make maps-moved` |
| no seed regressed | `make cohort-landing` (in `make land`) |


