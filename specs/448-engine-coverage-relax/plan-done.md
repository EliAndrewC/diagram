# 448-engine-coverage-relax - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-11-02 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** A session changing the engine code the Rust port replaces is not held to the full floor on it; every other
   file still is.
2. **The constraints.** FR-001 to FR-005; D1-D4.
3. **Where each comes from.** G: the GM's ruling, 2026-11-02 (`request.md`); 444 FR-010 for what stays Python.
4. **Do they describe the world here?** The record's 90 entries, 0 stale, measured 2026-11-02 (`make coverage-exempt`, the
   reader's own reachability over `stage_files` and `closure.py`'s entries).
5. **The order.** First.
6. **The exits.** Green: `tests/tooling/ci/test_coverage_exempt.py`, the hamlet floor's, cover-changed's and land's tests green,
   and the landing's gate floor green. Red: what failed recorded, a claim it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** The landing's `make done` floor green with the record's omission, every kept file at the full floor (SC-002).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

