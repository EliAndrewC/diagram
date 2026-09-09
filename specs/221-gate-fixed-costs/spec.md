# Feature 221 - the gate's fixed costs

**Status**: DRAFT 2026-09-09.
**Request**: [`request.md`](request.md) - the session's profile and four-item proposal the GM approved,
and the approval. **Research**: [`research.md`](research.md) - the profile before (R1), each item's
measurement (R2-R5), the gate after (R6). **Predecessors**: 213 (the worker cap's measurement and rule),
207 (the incremental gate and its coverage contexts), 208 (the raster out of the workers; the memory
method), 216/217 (a roll earns its lines; `make roll-audit`).

## Summary

Features 218 and 220 took a hamlet roll from 24 s to 7 s and the gate barely moved, because the gate's
time is set by what runs around the rolls. The GM asked for a profile of the gate's phases and the tests'
time and for the low-hanging fruit in it; the profile (R1) found four items and the GM approved all four:
the worker count, capped at 6 by a measurement taken when the gate was roll-bound; the per-test coverage
contexts every gated run records; the three coverage tables the bookkeeping prints; and two village-tier
roll tests in `tests/full` whose lines may no longer be theirs alone. This feature measures each,
changes what the measurement supports, and records what it does not.

## Functional requirements

- **FR-001 The worker count is re-measured and set by the rule.** The gate's test phase is timed on the
  gate as it is now at 6, 8, 10 and 12 workers on identical content, each with its peak memory measured
  by feature 208's method (a pytest plugin sampling per-test RSS, plus the container's `memory.current`),
  with the box otherwise quiet (checked; a concurrent gate voids the measurement). The cap becomes the
  smallest count within 10% of the fastest - feature 213's own rule - PROVIDED two such gates at once fit
  under the container's 8 GiB with headroom (the GM's standing goal of concurrent gates on a stable
  foundation). The numbers, the rule and the choice are recorded at the point of change (the `XDIST_WORKERS`
  comment) and in R2; a cap that stays at 6 because the measurement says so is a result, recorded the
  same way. CodeBuild's `auto` is untouched. The expected outcome the GM approved - the 47 s test phase
  near 30 s - is the yardstick, and the measured number is reported against it.
- **FR-002 The coverage contexts' share is measured, and the arrangement follows the number.** The full
  tree is timed under the gate's coverage with per-test contexts and without them, on identical content,
  three runs each. If the contexts cost more than 10 s of the phase, the feature answers the question the
  GM posed - does an incremental run need them, or only the run that records the baseline? - from
  `l7r/diagram/ci/incremental.py`'s merge (which contexts it reads from the new run) and implements the
  cheapest arrangement that keeps the incremental gate exact; if the merge needs every run's contexts,
  that is recorded with the measured cost and nothing changes. If the contexts cost 10 s or less, the
  number is recorded and nothing changes. Either way R3 carries the runs.
- **FR-003 One coverage table.** pytest-cov's own terminal report - the first `TOTAL` on a gated run's
  screen, the SELECTION's coverage on an incremental run and not the verdict - is no longer printed by
  default: `--cov-report=term` leaves `addopts`, and each target that wants a table asks for one
  (`cov-file` already does; the gate's verdict is the merged `coverage report` it already prints; the
  hamlet-floor table stays, it is a different floor). The saving is measured (R4) and the Makefile's
  note that `--cov-report=` "does not" silence it is corrected to say how it is silenced.
- **FR-004 The two village rolls answer to the audit.** `make roll-audit` on the landed baseline (R1)
  says: `test_pinned_knob_is_byte_identical_across_regens_and_rejects_incompatible_pins` reaches 15 lines
  of `settlement/rolling/roll.py` nothing else reaches - it earns its roll and stays;
  `test_roll_village_is_deterministic_and_seed_varies_the_combination` reaches ONE line
  (`settlement/_geom/water_index.py`) nothing else reaches, for two 6.7 s village rolls. Under feature
  216's clause that line becomes a unit test of the index, and the determinism test moves to
  `tests/soak/` with its reason (a real-map behavior no coverage line requires). `make roll-audit` after
  landing shows no roll with an empty set among the rolls the gate makes.
- **FR-005 Measured throughout.** R1 the profile before (the phase table, the three test-suite timings,
  the audit); R2-R5 each item's measurement; R6 a green `make done` after, phase by phase, beside R1; the
  numbers reported to the GM, a change that buys less than expected reported as such.
- **FR-006 Tests, under the floor.** The lifted water-index line has its unit test; any Makefile or
  `ci/` change has its `tests/tooling/` companion (the coverage floor measures `ci/`); 100% over
  everything added; `make done` green.

## Success criteria

- **SC-001** The worker cap is set by the measured rule with its numbers recorded; the test phase's time
  reported against the GM's yardstick (near 30 s from 47 s).
- **SC-002** The contexts' cost is a measured number in R3 and the arrangement matches it.
- **SC-003** A gated run prints one coverage verdict table (plus the hamlet floor's), and the saving is
  measured.
- **SC-004** `make roll-audit` shows every gate roll with a non-empty set; the determinism test is in the
  soak tier; the water-index line is a unit test; `make done` green at 100%.

## Decisions Recorded

- **D1 - no performance bookends.** Constitution VI bookends a feature that touches the diagram
  GENERATORS; this feature touches the Makefile, the test trees, `pyproject.toml` and possibly `ci/`,
  and changes no map. The gate's own time (R1 vs R6) is the measurement.
- **D2 - the worker rule is feature 213's, re-run.** The request's premise that the cap came from
  feature 208's memory ceiling was wrong (request.md's correction); the rule that set it - the smallest
  count within 10% of the fastest, with other sessions' memory as the tie-break - is kept, and the memory
  bar is made explicit: two concurrent gates under 8 GiB.
- **D3 - the pinned-knob roll stays.** The audit says it carries 15 lines of the village roller nothing
  else reaches; a roll with a unique set is what feature 216 keeps.
