# Implementation Plan: the claims switch

**Branch**: `445-claims-switch` (no branch; `main` in the clone) | **Date**: 2026-10-28 | **Spec**: `spec.md`

**Input**: `spec.md` (the round arbiter's accept at the round cap, ask:445-spec-round-3), `request.md`.

## Summary

A `claims` switch in `dev/switches.json`, `report` (shipped) or `clean`, read by the claims gate: at `report` only an owed claim
and a form problem refuse, and no carried finding or known-drift row is filed; at `clean` every open finding the claims report lists
refuses too. Feature 405 closes, its engine fixes and notes recorded as 444's phase inputs.

## Technical Context

**Language/Version**: Python 3.14, bash. **Testing**: `tests/tooling/test_claims_switch.py` (new), `tests/tooling/test_switches.py`,
the carry and land tests (`tests/tooling/test_claims_carry*.py`, `test_tick_task.py`), `tests/hooks/test-claims-gate.sh` through
`make hooks-test`. **Project Type**: tooling - no engine code.

## Performance bookends

None: no code a roll runs changes.

## Constitution Check

- **I-V, VII-IX, XI, XII, XIX**: N/A - no map, no setting prose.
- **VI**: PASS - the tests above, `make quick`, `make hooks-test`, the landing's `make done`.
- **X**: PASS - 100% coverage on `l7r/diagram/switches.py` and the scripts the tests run.
- **The guard doctrine**: the `clean` refusal (D3) has its test companion, names the command that cures it (`make claims-bundle`),
  and is proven to fire by deleting it; `docs/guards.md` names the switch.

## Decisions

**D1 - The switch** (FR-001, FR-004): `l7r/diagram/switches.py` gains a `claims` axis, `CLAIMS_STATES = ("report", "clean")`,
default `report`; `Switches` carries it, `read` reads it as it reads `remote` (an unknown key ignored; a malformed `claims` entry
closes it to `clean`, the strict state), and `write` keeps the axis it is not setting - today's `write` rewrites the file with
`remote` alone (the round arbiter's note), so it writes both. `make claims-report-only REASON=` and `make claims-clean REASON=`
throw it through `_switch`, which commits. `dev/switches.json` ships with `claims: report` and the GM's words as its reason.

**D2 - At `report`** (FR-002): `scripts/record/claims_carry.py` reads the switch through a stdlib reader of `dev/switches.json`
(`claims_mode(root)`, the scripts importing no engine package, as `codeid.py` does not), defaulting to `report`, failing closed to
`clean` on a malformed file. `gate` at `report` returns as refusals only the owed claims (`classified`'s first list); introduced,
carried and known findings go to the warnings, prefixed as today. `claims.py gate`'s `delta_form_problems` still refuses (it is
added after `claims_carry.gate`, unchanged). `record_known` reads the gate's refusals and so writes nothing at `report`.
`land.py` `file_carries` returns at once at `report`; `carry` (`make claims-carry`) refuses with "the claims switch is at report: a
carried finding is a row of `make claims-report`, filed nowhere (feature 445)". `land.py`'s claims route and wait are unchanged.

**D3 - At `clean`** (FR-003): `gate` at `clean` refuses as today (owed, introduced, unfiled carried, unrecorded known) and also
every open finding the report lists: `claims.py`'s report rows with a verdict of DRIFTED, NEEDS-RESEARCH, MISLABELED, UNCLAIMED,
UNDECIDED or CANNOT-TELL, less the DEFERRED (`load_deferred`) - each named, with `make claims-bundle UNITS="<key>"`. The report's
selection is lifted into one function both read (`open_findings(root)`), so the gate and `make claims-report` cannot disagree.

**D4 - 405 closes** (FR-005): 405's status line opens `Withdrawn 2026-10-28` with the GM's ruling and the evidence (its claims work
deferred to a claims feature after the rewrite; amendment 12, reviewed FAITHFUL, set aside unlanded). `specs/444-work-budget-program/
phase-inputs.md` lists T98 and T101 under `web`, T104 and T106 under `homesteads`, T111 under `track`, T165's three notes under
`homesteads` and `lane_wells`, each with its task text; 444's FR-001 derivation reads them as part of each stage's contract.

**D5 - The docs** (FR-006): `docs/guards.md`'s claims-gate row, the gate's own message in `claims-gate.sh`, and the root
`CLAUDE.md`'s claims line name the switch and its state.

## Task approaches

T01 the switch (D1); T02 the gate at `report` and `clean` (D2, D3); T03 405 closed and its inputs moved (D4); T04 the docs and the
closing report (D5).

### T01 - the switch (D1)

The `claims` axis in `switches.py` (`CLAIMS_STATES`, default `report`, a malformed entry closed to `clean`), `write` keeping the
axis it does not set, the two targets through `_switch`, and `dev/switches.json` thrown to `report` with the GM's words. Exits:
green - `tests/tooling/test_switches.py` throws both axes both ways, reads a malformed `claims` as `clean` and an absent one as
`report`, and finds `remote` kept after a `claims` throw; red - recorded and set down, a claim that it cannot be done to `make
arbiter-ask`.

### T01 Approach (checklist part A)

1. **The goal, in the world.** a claims switch on record, thrown with a reason, shipped at report.
2. **The constraints.** FR-001, FR-004; D1.
3. **Where each comes from.** G: the GM's ruling, 2026-10-28 (`request.md`).
4. **Do they describe the world here?** the switch's tests in a scratch skill directory.
5. **The order.** first.
6. **The exits.** Green: `tests/test_switches.py` green on both axes. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** `dev/switches.json` reads `claims: report` with the GM's words.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

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

## Project Structure

- `l7r/diagram/switches.py`, `dev/switches.json`, `Makefile`; `scripts/record/claims_carry.py`, `scripts/record/claims.py`,
  `scripts/land.py`, `scripts/gates/claims-gate.sh`; `specs/405-engine-findings-from-385/spec.md`,
  `specs/444-work-budget-program/phase-inputs.md`; `docs/guards.md`, `CLAUDE.md`; the tests above.

## Complexity Tracking

None.
