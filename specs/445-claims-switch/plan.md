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

## Project Structure

- `l7r/diagram/switches.py`, `dev/switches.json`, `Makefile`; `scripts/record/claims_carry.py`, `scripts/record/claims.py`,
  `scripts/land.py`, `scripts/gates/claims-gate.sh`; `specs/405-engine-findings-from-385/spec.md`,
  `specs/444-work-budget-program/phase-inputs.md`; `docs/guards.md`, `CLAUDE.md`; the tests above.

## Complexity Tracking

None.
