# Implementation Plan: gate and review friction

**Branch**: `442-gate-and-review-friction` (no branch; `main` in the clone) | **Date**: 2026-10-27 | **Spec**: `spec.md`

**Input**: `spec.md` (FAITHFUL, round 2), `request.md`.

## Summary

The four losses trial 441's report measured, each removed where it happens: one reader of a spec's verdict for both gates; a
`sync-in` that takes no lock when the mirror is at the tip; a criterion its rewritten requirement left behind named before a
review round; and a stopped trial's review that checks the outputs its research recorded.

## Technical Context

**Language/Version**: Python 3.14, bash. **Testing**: `tests/tooling/ci/test_features.py`, `tests/tooling/test_stale_terms.py`,
`tests/tooling/test_trial_review.py`, `tests/tooling/test_trial_start.py`; `tests/hooks/test-review-gate.sh`,
`test-sync-with-main.sh` (case_28), `test-review-round-hooks.sh`. **Project Type**: tooling.

## Performance bookends

None: no engine code a roll runs changes.

## Constitution Check

- **I-V, VII-IX, XI**: N/A. **VI**: PASS - the tests above, `make quick`, `make hooks-test`, the landing's `make done`.
- **X**: PASS - the coverage floor (CONVENTION: constitution X) on the changed `l7r/diagram/ci/features.py`.
- **The guard doctrine**: each changed gate's test proves the rule both ways (the agreement cases; the lock held at the tip and
  with main moved; an untouched criterion named and a touched one spared).

## Decisions

**D1 - One verdict reader** (FR-001): `hm_arbiter.spec_verdict(d)` - a FAITHFUL line naming its review (`_FAITHFUL_REVIEW`,
not `_FAITHFUL_NOT`), else `spec_ruled(d)` (a round cap's or an asked ruling, on the spec's body hash); `review-gate.sh` asks
its CLI `spec-verdict`, `ci/features.py` imports it from its own repository's `scripts/`; the merge check's own reader goes.

**D2 - The sync** (FR-002): `sync_in` compares the mirror's HEAD with the fetched `origin/main`; equal, no lock and no refresh;
else `mirror_refresh "$SYNC_LOCK_WAIT"` and the background render, as the prompt hook did; `--background-render` accepted as
before, no foreground flag.

**D3 - A criterion left behind** (FR-003): `stale_terms.criteria_left_behind` reads each `- **FR-NNN**` item and each
`- **SC-NNN** (FR-...)` item of `spec.md` (with its indented continuation), and names an SC citing a rewritten FR whose own
text is unchanged; `make stale-terms` and the review-round hook both add it to their candidates. A rewritten line is judged
against its whole replaced block (found at this feature's own round 2: a 3-line block rewritten as 5 was paired by position).

**D4 - The trial review** (FR-004): `scripts/trial-review.py` (`make trial-review F=`) copies the brief, the request and
`research/*.md` to `/tmp/l7r-check/trial-review-<NNN>/` with a MANIFEST; the check-not-re-run instruction where the Status
opens Done and says set down or stopped at the measurement, the full-review dispatch otherwise; the trial template asks each
measurement's output in a fenced block.

## Task approaches

### T01 Approach (checklist part A)

1. **The goal, in the world.** Each loss trial 441's report measured, removed where it happens.
2. **The constraints.** FR-001 to FR-005; D1-D4.
3. **Where each comes from.** G: the GM 2026-10-27 (`request.md`); O: trial 441's report.
4. **Do they describe the world here?** Yes: each change is in the code the report's row names.
5. **The order.** One task, four parts.
6. **The exits.** Green: landed with its tests. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The tests above pass; `make trial-review F=441` prints the stopped trial's dispatch.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| one verdict reader | `test_features.py`, `test-review-gate.sh` |
| the sync | `test-sync-with-main.sh` case_28 |
| a criterion left behind | `test_stale_terms.py`, `test-review-round-hooks.sh` |
| the trial review | `test_trial_review.py`, `test_trial_start.py` |
| the docs | `docs/guards.md`, `docs/spec-kit-and-reviews.md` read for the four |

**Performance work?** No.

## Project Structure

- `scripts/hooks/lib/hm_arbiter.py`, `scripts/gates/review-gate.sh`, `l7r/diagram/ci/features.py`, `scripts/sync-with-main.sh`,
  `scripts/reviews/stale_terms.py`, `scripts/hooks/lib/hm_review_round.py`, `scripts/trial-review.py`, `Makefile`,
  `.specify/templates/trial-template.md`; the docs and tests above.

## Complexity Tracking

None.
