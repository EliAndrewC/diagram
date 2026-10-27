# Implementation Plan: five iteration tooling improvements

**Branch**: `440-iteration-tooling-five` (no branch; `main` in the clone) | **Date**: 2026-10-27 | **Spec**: `spec.md`

**Input**: `spec.md`, `request.md`.

## Summary

The five improvements trial 439's report measured, each where the time was lost: the landing's claims stop before the gate,
the trial verdict's branch line, the seat counters beside a profile, every stage in the A/B's table, and three small ones
(`make trial APPROVED=`, stale-terms sparing rewritten lines, quick judged net of the host's load).

## Technical Context

**Language/Version**: Python 3.14. **Testing**: `tests/tooling/test_land_claims_wait.py`, `test_trial_start.py`,
`test_stale_terms.py`, `test_ratchets.py`; `tests/tools/test_perf_profile.py`, `test_perf_ab.py`. **Project Type**: tooling.

## Performance bookends

None: no engine code a roll runs changes (the tools read and time rolls; `perf_fanout` reads its sidecar's counts alone).

## Constitution Check

- **I-V, VII-IX, XI**: N/A. **VI**: PASS - the tests above, `make quick`, `make cover-changed`, the landing's `make done`; a
  real quick A/B with its stage rows; `research/quick-calibration.md`. **X**: PASS - 100% on the changed `l7r/` tools.
- **Feature 171** (the GM's 15 s): the ceiling and baseline unchanged; what is compared changes on the GM's approval (FR-007).

## Decisions

**D1 - The claims stop** (FR-001): `land.claims_route` sends a claims refusal `claims_cure` names (owed with no check in flight
`claims_flight.live`, or introduced) to the preflight's stops; any other to the deferred wait.

**D2 - The verdict line** (FR-002): the template's evidence section ends "THE VERDICT: [the branch of the rule taken] -
because [the measurement that took it ...]" and the branch not taken; the trial form's doc says the review checks it.

**D3 - The seat counters** (FR-003): `profile_stage` writes `meta.seat_search` under the key `meta.seat_search` in
`.placed.json`; `perf_fanout.placed_of` reads its integer counts alone.

**D4 - Every stage** (FR-004): a leg carries `(wall, cpu, {stage: seconds})` - the worker's roll returns the stages, the full
form's `legs` reads them - and `stage_rows` prints every stage, largest move first, `*` past 1% of A's best roll.

**D5 - The small ones** (FR-005-FR-007): `make trial APPROVED=` (`TRIAL_APPROVED`) fills the approval line; `stale_terms`
skips a candidate the diff rewrote from a line already naming its subject (`rewritten_from`); `ratchet.slowdown` - the loop
on `XDIST_WORKERS` processes (fork), best of 3 rounds' slowest over the pinned 0.12 s, at least 1, asked only for a run at or
over the ceiling - divides quick's run before the verdict, which prints both.

## Task approaches

### T01 Approach (checklist part A)

1. **The goal, in the world.** Each loss trial 439's report measured, removed where it happens.
2. **The constraints.** FR-001 to FR-008; D1-D5.
3. **Where each comes from.** G: the GM 2026-10-27 (`request.md`); O: trial 439's report.
4. **Do they describe the world here?** Yes: each change is in the code the report's row names.
5. **The order.** One task, five parts.
6. **The exits.** Green: landed with its tests and the real runs. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The tests above pass; a quick A/B prints its stage rows; `research/quick-calibration.md` records the
   slowdown tracking (the suite 2.13 times slower under load, the loop 2.24 times, measured 2026-10-27 (make test-file beside
   ratchet.slowdown, quiet and with 16 busy processes)).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the claims stop | `test_land_claims_wait.py` |
| the verdict line, APPROVED= | `test_trial_start.py` |
| the seat counters | `test_perf_profile.py` |
| every stage | `test_perf_ab.py`, a real quick A/B |
| stale terms | `test_stale_terms.py` |
| quick net of load | `test_ratchets.py`, `research/quick-calibration.md` |

**Performance work?** No - it changes tools, not the roll.

## Project Structure

- `scripts/land.py`, `scripts/trial-start.py`, `scripts/reviews/stale_terms.py`, `scripts/measure/ratchet.py`, `Makefile`.
- `l7r/diagram/tools/perf_profile.py`, `perf_fanout.py`, `perf_ab.py`; `.specify/templates/trial-template.md`.
- `docs/spec-kit-and-reviews.md`, `docs/guards.md`; the tests named above.

## Complexity Tracking

None.
