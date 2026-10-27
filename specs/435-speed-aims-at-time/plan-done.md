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

