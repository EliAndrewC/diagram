# 436-perf-ab-quick-first - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-27 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** A performance change is compared quickly while it is iterated on, and the slower comparisons
   come only after a quick one of the same engines.
2. **The constraints.** FR-001 to FR-008; D1-D8.
3. **Where each comes from.** G: the GM 2026-10-27 (`request.md`); O: feature 435's A/B runs, 8.2 min each, measured
   2026-10-27 (the file times of feature 435's T04 and T08 A/B logs).
4. **Do they describe the world here?** Yes: `perf_ab.py` as feature 435 landed it.
5. **The order.** One task.
6. **The exits.** Green: landed with its tests, a real quick A/B and an A/A run recorded in `research/t01-evidence.md`.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** A quick A/B of HEAD~ against HEAD at seed 25, 40 households, its wall time stated; the refusal seen
   on a subset run with no record.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the forms, order, refusal, floor | `tests/tools/test_perf_ab.py` |
| the quick form's wall time | a real `make perf-ab A=HEAD~1` |

**Performance work?** No - it times engines; it changes none.

