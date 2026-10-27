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
  real quick A/B with its stage rows; `research/quick-calibration.md`. **X**: PASS - the coverage floor (CONVENTION: constitution X's 100%) on the changed `l7r/` tools.
- **Feature 171** (the GM's 15 s, observed 2026-08-30, method: the GM's words, `research/quick-calibration.md`): the ceiling and baseline unchanged; what is compared changes on the GM's approval (FR-007).

## Decisions

**D1 - The claims stop** (FR-001): `land.claims_route` sends a claims refusal `claims_cure` names (owed with no check in flight
`claims_flight.live`, or introduced) to the preflight's stops; any other to the deferred wait.

**D2 - The verdict line** (FR-002): the template's evidence section ends "THE VERDICT: [the branch of the rule taken] -
because [the measurement that took it ...]" and the branch not taken; the trial form's doc says the review checks it.

**D3 - The seat counters** (FR-003): `profile_stage` writes `meta.seat_search` under the key `meta.seat_search` in
`.placed.json`; `perf_fanout.placed_of` reads its integer counts alone.

**D4 - Every stage** (FR-004): a leg carries `(wall, cpu, {stage: seconds})` - the worker's roll returns the stages, the full
form's `legs` reads them - and `stage_rows` prints every stage, largest move first, `*` past `STAGE_SHARE` (CONVENTION: 1% of A's best roll, a plumbing threshold of ours).

**D5 - The small ones** (FR-005, FR-006, FR-007): `make trial APPROVED=` (`TRIAL_APPROVED`) fills the approval line, the brief
dated today (FR-005); `stale_terms` skips a candidate the diff rewrote from a line already naming its subject
(`rewritten_from`) - FR-006's own condition, as the accepted spec words it ("a line in a replaced block whose old line already
named the candidate's subject; a line the diff inserted, or rewrote to bring the subject in, is still searched");
`ratchet.slowdown` - the loop on `XDIST_WORKERS` processes (fork), best of 5 rounds' slowest (as the pin was taken) over the
pinned 0.12 s (measured 2026-10-27 (the loop on 6 processes, best of 5 rounds, load 1.0)), at least 1 - is asked only for a run
at or over the ceiling and divides it before the verdict, which prints the raw time, the slowdown and the net time; a run under
the ceiling is judged raw as before and prints that its slowdown was not measured (FR-007). Feature 171's other check on quick,
the 60 s budget (CONVENTION: `QUICK_BUDGET` in the Makefile, feature 171), stays raw: no comparison below the ceiling reads load.

## Task approaches

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-27 (feature 375 FR-044) -->
## Project Structure

- `scripts/land.py`, `scripts/trial-start.py`, `scripts/reviews/stale_terms.py`, `scripts/measure/ratchet.py`, `Makefile`.
- `l7r/diagram/tools/perf_profile.py`, `perf_fanout.py`, `perf_ab.py`; `.specify/templates/trial-template.md`.
- `docs/spec-kit-and-reviews.md`, `docs/guards.md`; the tests named above.

## Complexity Tracking

None.
