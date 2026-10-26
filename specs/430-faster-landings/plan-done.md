# 430-faster-landings - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-26 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** A landing that moved a pool map runs the tests its code reaches and the tests that read the map.
2. **The constraints.** D1; FR-001, FR-009.
3. **Where each comes from.** The GM 2026-10-26, item 1; `m:full-plan-reasons`.
4. **Do they describe the world here?** Yes: the readers pattern already serves `make quick` (feature 328 wave 54).
5. **The order.** n/a.
6. **The exits.** Green: landed. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled
   through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D1; the 11 replays select every test their run failed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** A doc edit under `tests/` runs nothing; a fixture edit runs the tests that can read it.
2. **The constraints.** D2; FR-002, FR-009.
3. **Where each comes from.** The GM 2026-10-26, item 2; research R3.
4. **Do they describe the world here?** Yes, with D2's superset: fixture data is read across directories (R3).
5. **The order.** n/a.
6. **The exits.** Green: landed. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled
   through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D2; SC-001's 12 replays plan incremental, the 4 and the 3 plan full.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T03 Approach (checklist part A)

1. **The goal, in the world.** A landing that strands a line of a module it changed hears so in seconds, not after the gate.
2. **The constraints.** D3; FR-003, FR-003a, FR-009.
3. **Where each comes from.** The GM 2026-10-26, item 3; research R1, `m:coverage-reds-replay`.
4. **Do they describe the world here?** Yes for 3 of today's 5 line-naming reds and the sixth; the 2 in unchanged modules stay
   the gate's (the spec's Assumptions).
5. **The order.** n/a.
6. **The exits.** Green: landed. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled
   through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D3; the replays of 31f739f5d, d92ff2c90, 39ea51383 name their lines and 9a157cc4b
   counts the floor's tests, each faster than its gate took (SC-002).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T04 Approach (checklist part A)

1. **The goal, in the world.** A push of records alone takes no gate's time; several gates take the longest one's.
2. **The constraints.** D4; FR-004, FR-009.
3. **Where each comes from.** The GM 2026-10-26, item 4 and his question about the push's time.
4. **Do they describe the world here?** Yes: each gate's inputs are read off its own constants, pinned by a test.
5. **The order.** n/a.
6. **The exits.** Green: landed. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled
   through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D4; today's pushes replayed give the same verdicts; a records-only push timed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T05 Approach (checklist part A)

1. **The goal, in the world.** A plan review is never spent on what a script can see, nor on a block that decides nothing.
2. **The constraints.** D5; FR-005, SC-004.
3. **Where each comes from.** The GM 2026-10-26, item 5; `plan_sections.decides_nothing` (feature 385 T75).
4. **Do they describe the world here?** Yes: the three checks are the omissions today's reviews named.
5. **The order.** n/a.
6. **The exits.** Green: landed. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled
   through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D5.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T06 Approach (checklist part A)

1. **The goal, in the world.** A departure already filed for fixing lands without a ruling, and the GM sees it.
2. **The constraints.** D6; FR-006, SC-005.
3. **Where each comes from.** The GM 2026-10-26, item 6; `claims_carry.known_drifts` (feature 417's ruling).
4. **Do they describe the world here?** Yes.
5. **The order.** n/a.
6. **The exits.** Green: landed. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled
   through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D6.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T07 Approach (checklist part A)

1. **The goal, in the world.** The claims triage runs while the plan is reviewed.
2. **The constraints.** D7; FR-007.
3. **Where each comes from.** The GM 2026-10-26, item 7; research R2.
4. **Do they describe the world here?** Yes: R2 found no guard in the way; the prompt to start it is what is missing.
5. **The order.** n/a.
6. **The exits.** Green: landed. Red: the failing tests recorded and the task set down, a claim that it cannot be done ruled
   through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D7.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

