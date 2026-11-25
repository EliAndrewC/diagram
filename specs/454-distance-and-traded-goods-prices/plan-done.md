# 454-distance-and-traded-goods-prices - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-11-24 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** n/a
2. **The constraints.** D1; FR-001, FR-002, FR-005, FR-006, FR-007.
3. **Where each comes from.** The FRs above, from `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** n/a
6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** SC-001, SC-002, SC-003.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

### T01 part B (2026-11-24T18:05Z)

The trigger `red-gate@2` was two red gates on feature 453's landing of its T01, in this clone; `make arbiter-ruled` filed it under this
feature because `.specify/feature.json` pointed here (the last number claimed). It is answered here because the tool asks it here.

1. **What exactly is refusing?** Nothing now. Red one was the house-style check on British spellings in the saved search-pass reports;
   red two was clippy's doc lint on a test comment in `rust/guard/shared/src/checks/reply.rs`. Not the same rule twice.
2. **A3 again, for that rule, freshly checked.** Both are the project's own standing rules (house style; the lint set), from `CLAUDE.md`.
3. **A4 again.** Yes: each named a real fault in what was written.
4. **Is the next fix moving something placed earlier to suit something placed later?** No.
5. **Tuning or changing?** Neither: two one-line corrections, each made once.
6. **The one-sentence test.** No such question arises.
7. **The next step is a measurement.** `make quick` after the first fix and `make static` after the second, each run before another gate:
   both clean, observed 2026-11-24, method: the two make runs in this clone; the landing that followed was green.
8. **Before offering routes.** No route was offered; the arbiter was asked only whether the next landing may run.
9. **After a ruling.** The ruling was accept, naming the next `make land F=453 T=T01`; that was the step taken, and it landed.
   For this feature's own tasks: a search-pass report is run through `make quick` when it is saved, before any landing.
<!-- plan-archive: archived 2026-11-25 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** n/a
2. **The constraints.** D2; FR-001, FR-002, FR-005, FR-006, FR-007.
3. **Where each comes from.** The FRs above, from `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** n/a
6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** SC-001, SC-002, SC-003.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

