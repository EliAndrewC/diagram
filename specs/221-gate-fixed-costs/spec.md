# Feature 221 - the gate's fixed costs

**Status**: IMPLEMENTED 2026-09-09 (workers 6 -> 10 by the measured rule, two gates 5.9 GiB; contexts ~2 s, left; one coverage table; the determinism roll to the soak tier with its line as a unit test; pytest under the gate 47 s -> 32 s, `make done` 65 s -> 55 s - research R2-R6). `spec-fidelity` round 1 required three changes, applied: FR-001 raises the cap when the GM's memory condition holds at a count above 6, with feature 213's rule choosing AMONG 8, 10 and 12 rather than re-opening the raise, and no longer pre-authorizes staying at 6 (a measurement that shows no faster count goes to the GM with the numbers); the memory bar is the GM's exactly - two concurrent gates under 8 GiB, no unstated headroom (the container's cap, measured, is 10 GiB; 8 is the GM's figure and the stricter one); FR-003 delivers ONE table by also suppressing the hamlet floor's on a passing run.
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

- **FR-001 The worker cap is raised when the GM's condition holds.** The gate's test phase is timed on
  the gate as it is now at 8, 10 and 12 workers (6 as the control) on identical content, each with its
  peak memory measured by feature 208's method (a pytest plugin sampling per-test RSS, plus the
  container's `memory.current`), with the box otherwise quiet (checked; a concurrent gate voids the
  measurement). The GM's condition, as written: *"if two concurrent gates still fit under 8 GiB, raise
  the cap"* - two of the measured peaks, added, under 8 GiB (the container's cap is 10 GiB, measured; 8
  is the GM's figure and the stricter one, and no headroom is added to it). Where it holds at a count
  above 6 the cap IS raised, to the count feature 213's selection rule picks FROM AMONG 8, 10 and 12 - the
  smallest of them within 10% of the fastest; the rule chooses the number, it does not re-open the
  raise. If the timing shows no count above 6 faster than 6, or the memory condition fails at every
  count above 6, that result and the corrected premise (request.md) go to the GM with a recommendation,
  and the cap is not changed by this feature on the session's own authority. The numbers, the rule and
  the choice are recorded at the point of change (the `XDIST_WORKERS` comment) and in R2. CodeBuild's
  `auto` is untouched. The expected outcome the GM approved - the 47 s test phase near 30 s - is the
  yardstick, and the measured number is reported against it.
- **FR-002 The coverage contexts' share is measured, and the arrangement follows the number.** The full
  tree is timed under the gate's coverage with per-test contexts and without them, on identical content,
  three runs each. If the contexts cost more than 10 s of the phase, the feature answers the question the
  GM posed - does an incremental run need them, or only the run that records the baseline? - from
  `l7r/diagram/ci/incremental.py`'s merge (which contexts it reads from the new run) and implements the
  cheapest arrangement that keeps the incremental gate exact; if the merge needs every run's contexts,
  that is recorded with the measured cost and nothing changes. If the contexts cost 10 s or less, the
  number is recorded and nothing changes. Either way R3 carries the runs.
- **FR-003 One coverage table.** A gated run prints ONE coverage table - the merged `coverage report`
  that is the verdict. pytest-cov's own terminal report (the first `TOTAL` on the screen, the SELECTION's
  coverage on an incremental run and not the verdict) is no longer printed by default: `--cov-report=term`
  leaves `addopts`, and each target that wants a table asks for one (`cov-file` already does). The hamlet
  floor's table (`hamlet_floor.check`, which takes its verdict per line from `cov.analysis2` and uses
  the report only for a percentage) is printed only when a module is under 100%, where its missing lines
  are the point; a passing floor prints its one-line result. The saving is measured (R4) and the
  Makefile's note that `--cov-report=` "does not" silence pytest-cov's table is corrected to say how it
  is silenced.
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

- **SC-001** The worker cap is raised to the count the rule picks among 8, 10 and 12 where the GM's memory
  condition holds, with its numbers recorded; the test phase's time reported against the GM's yardstick
  (near 30 s from 47 s); a result that does not support a raise goes to the GM with the numbers.
- **SC-002** The contexts' cost is a measured number in R3 and the arrangement matches it.
- **SC-003** A gated run that passes prints one coverage table, and the saving is measured.
- **SC-004** `make roll-audit` no longer lists the determinism roll (the two village rolls the GM named are
  answered: one stays with its 15 lines, one moved); the water-index line is a unit test; `make done` green
  at 100%. Two other village-tier contexts with empty sets, outside the GM's item, are recorded in R5.


## Decisions Recorded

- **D1 - no performance bookends.** Constitution VI bookends a feature that touches the diagram
  GENERATORS; this feature touches the Makefile, the test trees, `pyproject.toml` and possibly `ci/`,
  and changes no map. The gate's own time (R1 vs R6) is the measurement.
- **D2 - feature 213's rule chooses AMONG the GM's candidates; the GM's condition decides the raise.**
  The request's premise that the cap came from feature 208's memory ceiling was the session's error
  (request.md's correction, the session's own and not yet the GM's); it changes why 6 was chosen, not
  what the GM asked. So the raise is governed by the GM's condition as written, and feature 213's
  selection rule - the smallest count within 10% of the fastest - only picks which of 8, 10 or 12.
- **D3 - the pinned-knob roll stays.** The audit says it carries 15 lines of the village roller nothing
  else reaches; a roll with a unique set is what feature 216 keeps.

## Review history

- **Round 1** (`spec-fidelity`, Mode 2, the GM's request verbatim, 2026-09-09): CHANGES REQUIRED, three - the
  raise is the GM's condition's to decide, feature 213's rule only chooses among 8, 10 and 12, and the spec may
  not pre-authorize keeping 6; the memory bar is the GM's 8 GiB as written, no headroom; "Print one" means one
  table, so the hamlet floor's prints only on a miss. All three applied.
- **Round 2** (`spec-fidelity`, Mode 2, 2026-09-09): **FAITHFUL**.

