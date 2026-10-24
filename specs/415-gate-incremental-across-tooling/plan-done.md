# 415-gate-incremental-across-tooling - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-24 -->
## T01 - the run record says what ran, why, and where the time went (FR-002, FR-005)

### T01 Approach (checklist part A)

1. **The goal, in the world.** Anyone reading a gate's run record can tell whether it ran everything, why, how many tests it selected, and how long each phase took - without reconstructing it from a log.
2. **The constraints.** The record is written once per gate run by `LOGRUN`; it must not slow the gate or fail it when a figure is missing.
3. **Where each comes from.** O: the GM's items 2 and 5 (request.md).
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: T26's landing log): the run record held seconds and mode but no reason, no selection count and no phases, and the phase table had to be rebuilt by hand.
5. **The order.** Phase marks first (runstats), then the plan fields, then the record.
6. **The exits.** (a) read the log after each run - not taken, the record is what tools read; (b) the fields - taken.
7. **The search smell.** None.
8. **The budget.** 60 min with its landing.
9. **Done, measured.** Unit tests of `runstats.py phase`/`end` and of the record's new fields (red without); a real gate run's record carries `plan_mode`, `plan_reason`, `selected` and `phases`.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** `runstats.py phase <dir> <name> <seconds>` appends a phase mark; `end` returns them as `phases: {name: seconds}`. The `done` recipe marks the preflight, each of static, format and typecheck, the reference step, the hooks suite and the test phase; the `test` recipe marks `pytest` and `floors` (merge, carry, the reports, save-baseline) inside it. Rendering: none.
- **D2** Every run of the gate's test phase writes this run's plan before pytest starts - the planner's, or, for a run that does not go through the planner (`make test-full` by hand, `INCREMENTAL=0`, `FULL=1`, T05's background refresh), its own with its reason - and the selection plugin writes its `result.json` (mode, reason, selected, collected) as today. `LOGRUN` reads only THIS run's result (stamped with the run's start, so an older file is never read) and adds `plan_mode`, `plan_reason`, `selected` and `collected`; the fields are left out only when no test phase ran (the gate stopped before it). Rendering: none.

