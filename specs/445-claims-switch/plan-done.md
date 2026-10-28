# 445-claims-switch - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-28 -->
### T02 - the gate at `report` and `clean` (D2, D3)

`claims_carry.claims_mode`, `gate`'s two modes, `open_findings` lifted from the report and read by both, `file_carries` and
`carry` at `report`. Exits: green - `tests/tooling/test_claims_switch.py` lands a fixture with an introduced, a carried and a known
finding at `report` with no task filed and no `gm-review.jsonl` row, refuses one with an owed claim, refuses `make claims-carry` at
`report` (the refusal's own test, proven to fire with it deleted), refuses at `clean` a fixture whose report lists an open finding
and passes one whose only findings are DEFERRED, a DEFERRED carried one among them; red as T01.

### T02 Approach (checklist part A)

1. **The goal, in the world.** claims findings recorded, not refused, at report; every open finding refused at clean.
2. **The constraints.** FR-002, FR-003; D2, D3.
3. **Where each comes from.** G: the GM's ruling, 2026-10-28 (`request.md`).
4. **Do they describe the world here?** the gate's tests on fixture repositories with each kind of finding.
5. **The order.** after T01.
6. **The exits.** Green: `tests/tooling/test_claims_switch.py` green, each refusal red with it deleted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** a landing at report passes with findings warned and none filed.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

<!-- plan-archive: archived 2026-10-28 -->
### T03 - 405 closed (D4)

405's status line `Withdrawn` with its evidence; `specs/444-work-budget-program/phase-inputs.md` holding the six tasks' texts under
their stages, any measured figure in them marked as today's count so 444's budget bundles leave it out (443 FR-008's refusal holds).
Exits: green - `make speckit-todo` lists 405 closed and `phase-inputs.md` names each task once; red as T01.

### T03 Approach (checklist part A)

1. **The goal, in the world.** 405 closed and its engine work handed to the phases that rebuild it.
2. **The constraints.** FR-005; D4.
3. **Where each comes from.** G: the GM's ruling, 2026-10-28 (`request.md`).
4. **Do they describe the world here?** the open tasks of feature 405 read against `STAGES`, observed 2026-10-28 (method: `make speckit-todo` and `grep -n "STAGES = (" -A60`).
5. **The order.** after T02.
6. **The exits.** Green: `make speckit-todo` lists 405 closed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** `phase-inputs.md` names each of the six tasks once.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

<!-- plan-archive: archived 2026-10-28 -->
### T04 - the docs and the report (D5)

`docs/guards.md`, `claims-gate.sh`'s message and the root `CLAUDE.md` name the switch and its state; `make feature-report F=445
WRITE=1`. Exits: green - the docs read the switch; red as T01.

### T04 Approach (checklist part A)

1. **The goal, in the world.** the switch and its state named where a session reads about the claims gate.
2. **The constraints.** FR-006; D5.
3. **Where each comes from.** G: the GM's ruling, 2026-10-28 (`request.md`).
4. **Do they describe the world here?** the docs read after the change.
5. **The order.** last.
6. **The exits.** Green: the docs name the switch. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** the feature report written.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

