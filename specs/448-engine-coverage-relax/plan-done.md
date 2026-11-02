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

<!-- plan-archive: archived 2026-11-02 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** Every doc that states the one floor says the exemption, with the GM's words.
2. **The constraints.** FR-006, SC-003; D5.
3. **Where each comes from.** G: the GM's ruling, 2026-11-02 (`request.md`).
4. **Do they describe the world here?** The floor tests read the Makefile the gate runs.
5. **The order.** After T01 (the docs name its record and reader).
6. **The exits.** Green: `test_coverage_floor.py` and `test_docs_match_the_mechanism.py` green. Red: recorded, ruled through
   `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** The same landing as T01.
9. **Done, measured.** Every doc D5 lists - `l7r/diagram/CLAUDE.md` among them - names `dev/coverage-exempt.json` and carries the
   GM's 2026-11-02 words, checked by `git grep -l coverage-exempt` and `git grep -l "going away"` over that list.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - docs.
