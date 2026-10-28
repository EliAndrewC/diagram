# 442-gate-and-review-friction - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-27 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** Each loss trial 441's report measured, removed where it happens.
2. **The constraints.** FR-001 to FR-005; D1-D4.
3. **Where each comes from.** G: the GM 2026-10-27 (`request.md`); O: trial 441's report.
4. **Do they describe the world here?** Yes: each change is in the code the report's row names.
5. **The order.** One task, four parts.
6. **The exits.** Green: landed with its tests. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The tests above pass; `make trial-review F=441` prints the stopped trial's dispatch.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| one verdict reader | `test_features.py`, `test-review-gate.sh` |
| the sync | `test-sync-with-main.sh` case_28 |
| a criterion left behind | `test_stale_terms.py`, `test-review-round-hooks.sh` |
| the trial review | `test_trial_review.py`, `test_trial_start.py` |
| the docs | `docs/guards.md`, `docs/spec-kit-and-reviews.md` read for the four |

**Performance work?** No.

