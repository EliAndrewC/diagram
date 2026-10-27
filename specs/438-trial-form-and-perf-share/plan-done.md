# 438-trial-form-and-perf-share - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-27 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** A module's share of each stage's time, read in one command from the profiles already kept.
2. **The constraints.** FR-001, FR-002, FR-007; D1, D2.
3. **Where each comes from.** G: the GM 2026-10-27 (`request.md`); O: feature 437's `research/share.md`.
4. **Do they describe the world here?** Yes: `dev/perf-raw/` holds the kept profiles; `profile_stage` writes them.
5. **The order.** First.
6. **The exits.** Green: landed with its tests and a real run on 437's profiles. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make perf-share PROFILES=<437's four>` prints 437's shares (3.5% across the four, measured 2026-10-27 (feature 437, research/share.md)).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the reading | `tests/tools/test_perf_share.py` on a synthetic profile |
| the size in the name | `tests/tools/test_perf_profile.py` |

**Performance work?** No - it reads profiles; it changes no engine code a roll runs.

<!-- plan-archive: archived 2026-10-27 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** A trial measured first and reviewed once, its evidence pushed as it is measured.
2. **The constraints.** FR-003, FR-004, FR-006, FR-007; D3-D5.
3. **Where each comes from.** G: the GM 2026-10-27; O: feature 437's three review rounds (`specs/437-array-geometry-trial/report-trial.md`).
4. **Do they describe the world here?** Yes: `review-gate.sh`'s spec loop is the one place a verdict is required at push.
5. **The order.** After T01.
6. **The exits.** Green: landed with the gate's hook tests and `trial-start`'s tests. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make hooks-test` passes the gate's new cases; feature 439 is started with `make trial`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the brief written | `tests/test_trial_start.py` |
| the gate's rule | `tests/hooks/test-review-gate.sh` |

**Performance work?** No.

