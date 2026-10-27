# 440-iteration-tooling-five - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-27 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** Each loss trial 439's report measured, removed where it happens.
2. **The constraints.** FR-001 to FR-008; D1-D5.
3. **Where each comes from.** G: the GM 2026-10-27 (`request.md`); O: trial 439's report.
4. **Do they describe the world here?** Yes: each change is in the code the report's row names.
5. **The order.** One task, five parts.
6. **The exits.** Green: landed with its tests and the real runs. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The tests above pass; a quick A/B prints its stage rows; `research/quick-calibration.md` records the
   slowdown tracking (the suite 2.13 times slower under load, the loop 2.24 times, measured 2026-10-27 (make test-file beside
   ratchet.slowdown, quiet and with 16 busy processes)).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the claims stop | `test_land_claims_wait.py` |
| the verdict line, APPROVED= | `test_trial_start.py` |
| the seat counters | `test_perf_profile.py` |
| every stage | `test_perf_ab.py`, a real quick A/B |
| stale terms | `test_stale_terms.py` |
| quick net of load | `test_ratchets.py`, `research/quick-calibration.md` |

**Performance work?** No - it changes tools, not the roll.

