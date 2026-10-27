# 435-speed-aims-at-time - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-27 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** The checklist and its tools in place, so every later performance task is planned against time
   (D1-D5).
2. **The constraints.** FR-001, FR-002, FR-003, FR-006, FR-007.
3. **Where each comes from.** `spec.md`, `request.md`.
4. **Do they describe the world here?** Yes: `scripts/task-add.py` takes only `--physical` and `--section` today; the
   perf-audit agent is dispatched only for a slowdown investigation.
5. **The order.** First (the GM's order).
6. **The exits.** Green: the doc, the flag, the template line, `make perf-ab` (exit 0 whatever the times), the agent's occasion
   and the guidance sentences landed, each tested.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing (tooling).
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the flag and the template line | `tests/tooling` for task-add |
| `make perf-ab` | its unit tests on recorded snapshots; one real run |

<!-- plan-archive: archived 2026-10-27 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** The earlier call-cutting changes timed group by group, reverted where they bought no time (D6).
2. **The constraints.** FR-004, FR-006; SC-003.
3. **Where each comes from.** `spec.md`; the A/B of the engine before 417's lane against HEAD, measured 2026-10-27 (make perf
   SCALING=1 alternated in two worktrees).
4. **Do they describe the world here?** Yes: the eight commits FR-004's search returns.
5. **The order.** After T01 (it uses `make perf-ab`).
6. **The exits.** Green: every arm's evidence recorded, the reverted arms landed with no pool manifest moved and the cohort
   passing.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a measurement per arm.
8. **The budget.** One landing per feature's set of reverted arms.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| each arm's time | `make perf-ab` against HEAD |
| no map moved | `make maps-moved` |
| no seed regressed | `make cohort-landing` |

<!-- plan-archive: archived 2026-10-27 -->
### T03 Approach (checklist part A)

1. **The goal, in the world.** The three cheap fixes (D7), each its own task filed with `PERF=1`, its checklist answered.
2. **The constraints.** FR-005, FR-006; SC-004.
3. **Where each comes from.** `specs/417-all-seeds-pass/research/t57-analysis.md` items 2, 3, 1.
4. **Do they describe the world here?** Re-measured first (`make phase-calls`, `make perf-profile`) on the engine T02 leaves.
5. **The order.** After T02.
6. **The exits.** Green: each fix landed with its calls and time evidence, the cohort passing.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Each fix removes a search: a screen before a full test, a result kept.
8. **The budget.** One landing per fix.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** Its research claim read first.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| each fix | `make phase-calls`, `make perf-ab` against its parent |
| the maps | `make maps-moved`, the cohort |

<!-- plan-archive: archived 2026-10-27 -->
### T04 Approach (checklist part A)

1. **The goal, in the world.** The new numbers for the GM (D8).
2. **The constraints.** FR-008; SC-006.
3. **Where each comes from.** `request.md` message 3.
4. **Do they describe the world here?** Yes.
5. **The order.** Last.
6. **The exits.** Green: `report-numbers.md` written with both comparisons.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the calls | `make phase-calls` |
| the time | `make perf-ab` |

