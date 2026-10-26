# 426-faster-iteration - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-26 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** `make land` never waits for a claims round nothing can deliver.
2. **The constraints.** D1; FR-001, FR-002, FR-011.
3. **Where each comes from.** the GM 2026-10-26 (fix 1); measured: T50's two full waits (research R1).
4. **Do they describe the world here?** Measured by: the wait loop re-runs the gate each poll; the marker is the one new state.
5. **The order.** first: the cheapest, the largest measured waste.
6. **The exits.** green: landed by `make land` with T02-T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T03 Approach (checklist part A)

1. **The goal, in the world.** A docstring-, comment- or claims-only edit re-rolls and re-renders nothing; content docstrings still count.
2. **The constraints.** D3; FR-003, FR-005, FR-006, FR-012.
3. **Where each comes from.** the GM 2026-10-26; R2, R3; measured R5 (11 of 16 re-rolled before, 0 after).
4. **Do they describe the world here?** Measured by: `make cache-audit` (3 audited, 0 FAILED) and the before/after cohort count.
5. **The order.** after T02.
6. **The exits.** green: landed with T01, T02, T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: archived 2026-10-26 -->
### T04 Approach (checklist part A)

1. **The goal, in the world.** The other code-hashing keys follow the same rule where they should.
2. **The constraints.** the audit table; FR-004.
3. **Where each comes from.** the GM 2026-10-26 ("look for any other places"); R3b.
4. **Do they describe the world here?** Measured by: each site's test: a function docstring keeps it, code moves it, usage text and the Makefile still count for `tooling_hash`.
5. **The order.** after T02.
6. **The exits.** green: landed with T01-T03; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

