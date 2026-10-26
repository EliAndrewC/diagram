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

