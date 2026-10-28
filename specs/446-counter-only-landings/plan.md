# Implementation Plan: lighter landings for counter-only changes

**Branch**: `446-counter-only-landings` (no branch; `main` in the clone) | **Date**: 2026-10-28 | **Spec**: `spec.md`

**Input**: `spec.md` (the round arbiter's accept at the round cap, ask:446-spec-round-3), `request.md`.

## Summary

One definition of a counter block (`codeid.is_counter_block`) and of counter-only-equal files (`debug_free_bytes`); a delta of
counter-only changes skips the two 48-seed cohorts, the cohort's same-engine test reading such engines as one; the claims triage
clears a claim whose unit only gained counter blocks. The full suite, the reviews and the checklists are unchanged.

## Technical Context

**Language/Version**: Python 3.14. **Testing**: `tests/pipeline/test_codeid.py`, `tests/tooling/test_tick_task.py` (land),
`tests/tooling/test_cohort_known.py` or its existing home, `tests/tooling/test_claims_index.py`; `make hooks-test`. **Project
Type**: tooling - no engine code.

## Performance bookends

None: no code a roll runs changes. The claims scan gains a second, counter-free dump per unit owed a code triage only (D3).

## Constitution Check

- **I-V, VII-IX, XI, XII, XIX**: N/A - no map, no setting prose.
- **VI**: PASS - the tests above, `make quick`, `make hooks-test`, the landing's `make done`.
- **X**: PASS - 100% coverage of the changed scripts' lines the tests reach.
- **The guard doctrine**: each skip is a narrowing of a gate, so each has a test that a non-counter delta still runs what it skips,
  proven red with the skip's condition deleted; `docs/guards.md` names both.

## Decisions

**D1 - The counter block** (FR-001): `scripts/gates/codeid.py` `is_counter_block`, `_counter_value`, `strip_counters`,
`debug_free_bytes`, as FR-001 defines them. Measured 2026-10-28 (a walk of every `if __debug__:` under `l7r/`): 136 blocks, 133
counter blocks, the 3 others the driver's `BY_STAGE` attribution, which stays code.

**D2 - A counter-only delta** (FR-002): `cohort_known.counter_only(root, a, b)` - every engine path that `git diff --name-status
a b` names, by the landing's own list (`land.py`'s `ENGINE`, which becomes `codeid.ENGINE`, the one definition both read - a test
fails if they ever differ), is a modification (not an add or delete) whose two versions are counter-only-equal (`git show <ref>:<path>`
through `debug_free_bytes`). `same_key(root, a, b)` returns True when `counter_only` does, after its two existing tests. `land.py`
asks `cohort_gate.py counter-only` (a new command, exit 0 when the delta against the merge base with origin/main is counter-only):
when it is, it starts no `cohort-landing` beside the gate and no fresh block after the push, and prints "the delta is counter-only
(feature 446): no cohort owed"; the push's cohort gate then finds main's record on the same engine through `same_key`.

**D3 - The claims triage's counter-only clear** (FR-003): where the code-triage owing (`claims_owed` / `claims_triage`) finds a
claim's `code` changed, it reads the unit's file at the merge base, takes the unit's fingerprint there through the same scan
(`l7r/diagram/tools/claims.py`'s units of that source), and when it equals the recorded `code`, compares the base unit's and the
current unit's cores with counter blocks removed (`strip_counters` on each unit's tree) and the counter blocks of the base standing
in the current unit; equal, the claim is recorded cleared ("counter-only (feature 446)") with its current fingerprints and is
bundled nowhere.

**D4 - The docs** (FR-005): `docs/guards.md`'s cohort-gate and claims-gate rows and `make land`'s help name the counter-only skips.

## Task approaches

T01 the counter-only delta and the cohort skip (D1, D2); T02 the claims triage's counter-only clear (D3); T03 the docs and the
report (D4).

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
### T02 - the claims triage's counter-only clear (D3)

The merge base's unit read and fingerprinted; the counter-free cores compared; the claim recorded cleared and bundled nowhere.

### T02 Approach (checklist part A)

1. **The goal, in the world.** A claim whose code only gained counters is cleared without an agent.
2. **The constraints.** FR-003; D3.
3. **Where each comes from.** G: the GM's words, 2026-10-28 (`request.md`).
4. **Do they describe the world here?** 455 claims triaged and two sent on, neither counter-only, measured 2026-10-28 (the `make
   claims-triaged` lines of 443's landings).
5. **The order.** After T01 (it reads `strip_counters`).
6. **The exits.** Green: `tests/tooling/test_claims_index.py` clears a claim whose unit only gained a counter block, and owes one
   changed otherwise, one whose counter block was removed, one whose counter block was rewritten and one whose recorded version is
   not the base's; the clear red with its
   condition deleted. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** A counter-only change's claims are cleared at `make claims-owed` with no bundle.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

### T03 - the docs and the report (D4)

`docs/guards.md` and `make land`'s help name both skips; `make feature-report F=446 WRITE=1`.

### T03 Approach (checklist part A)

1. **The goal, in the world.** A session reading about the cohort and claims gates learns the counter-only skips.
2. **The constraints.** FR-005; D4.
3. **Where each comes from.** G: the GM's words, 2026-10-28 (`request.md`).
4. **Do they describe the world here?** The docs read after the change.
5. **The order.** Last.
6. **The exits.** Green: the docs name the skips; the report written. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** The feature report written.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

## Project Structure

- `scripts/gates/codeid.py`, `scripts/measure/cohort_known.py`, `scripts/gates/cohort_gate.py`, `scripts/land.py`,
  `scripts/record/claims_owed.py`, `scripts/record/claims_triage.py`; `docs/guards.md`, `Makefile`; the tests above.

## Complexity Tracking

None.
