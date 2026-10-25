# 417-all-seeds-pass - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-24 -->
## T02 - the hold made (FR-010)

### T02 Approach (checklist part A)

1. **The goal, in the world.** No engine task of a held claims feature can be started while 417 is open.
2. **The constraints.** `make task-start` is the one place a task becomes active (`plan_gate.task_start`).
3. **Where each comes from.** O: FR-010 and D4.
4. **Do they describe the world here?** Yes: a landing needs the active task, and the active task comes only from task-start.
5. **The order.** Second, small, lands alone (`make land-tooling`).
6. **The exits.** `HOLD_OK` for a non-engine task only.
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** 405, 372 and 384 carry the ON HOLD status (all three marked 2026-10-24); a test starts a 405 engine
   task and is refused, naming 417; a `HOLD_OK` on it is refused; a non-engine
   task with `HOLD_OK` starts; each red without the guard.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D9** A held feature is one whose `**Status**` line holds `ON HOLD` and `until feature NNN`; NNN open by `speckit-todo`'s
  own open/closed rule. An engine task is one whose text names a path under `l7r/` or `pool/`, or whose `research:` line is
  `physical`, or that names a decision whose plan section names such a path; unsure counts as engine. Rendering: none.

