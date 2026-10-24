# Feature 415: the gate stays incremental across tooling changes, and a landing waits only on what it must

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-24

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-10-24, "Yes, please file the feature with those 6 items, and then work the entire feature from start to finish. Thank you."

**Input**: `request.md`

## The gap (measured on feature 405 T26's landing, 2026-10-24)

T26's landing took 8.8 minutes: the first pass ~1 min (`cover-changed` 48 s of it), the gate 311 s (preflight 34 s, the
static phases ~30 s, the test phase 280 s over 10,376 tests), the landing cohort 1.4 min past the gate, the ticks and push
~0.5 min. The gate ran the WHOLE suite because `scripts/` had changed since its baseline: `incremental.plan` returns
`full` whenever `state.tooling_hash` moved - a hash over `scripts/`, the Makefile, `pyproject.toml`, `l7r/diagram/ci/`,
`l7r/diagram/pipeline/` and a few more, built to decide when the TOOLING tests rerun. Asked of the gate's own planner, T26's
two engine files reached 143 of 11,890 baseline tests (1%) in 21 test modules. Tooling lands several times a day, so the
rule fires on most landings: of October's green gate runs, 286 were full (median 194 s) and 49 incremental (median 42 s).
A second rule plans `full` when a change reaches more than `FULL_FRACTION` (60%) of the baseline, recorded beside the
constant as "a knob with its reason; not a measured optimum". All observed 2026-10-24; method: the landing's log and commit times, the gate's planner asked offline on its baseline, and a count of `dev/run-log/2026-10/`.

## User Scenarios & Testing

### User Story 1 - A landing runs the tests its change reaches, whatever tooling changed before it (Priority: P1)

**Acceptance Scenarios**:

1. A change under `scripts/` alone (no engine file, no test module) plans `incremental`: it selects the tooling tests (each
   reused, as on a full plan, where its recorded reads are unchanged) and the test modules outside the tooling trees that
   read `scripts/`; no other test runs.
2. An engine change made after a `scripts/` change plans `incremental` over the engine change's reach, plus scenario 1's
   selection for the `scripts/` change.
3. A change to the lines of the Makefile that decide how the gate's tests run (the recipes of the test targets and the
   variables they read), to `pyproject.toml`'s pytest or coverage sections, or to the gate's own machinery
   (`l7r/diagram/ci/`, `l7r/diagram/pipeline/`, `l7r/diagram/switches.py`, `l7r/diagram/_invocation.py`,
   `tests/conftest.py`, `tests/_scope.py`) still plans `full`. Every file under `scripts/` plans `incremental`,
   `scripts/gates/gate-stamp.py` included: where its patterns change which files the gate's manifest covers, those files
   appear in the manifest as added or removed, which the planner already selects on. A change to a pinned lockfile (`requirements.txt`, `requirements-dev.txt`,
   `requirements-ci.txt`) plans `full` - ADDED: no lockfile is in the tooling hash today, so a dependency change plans
   nothing. Any other Makefile or `pyproject.toml` change does not, nor an edit to a `requirements*.in` alone.
4. A landing whose change reaches more than 60% of the baseline runs the tests it reaches, not the whole suite; the
   baseline is refreshed by a full run outside the landing's path (User Story 3).

### User Story 2 - Every gate run says why it ran what it ran, and where its time went (Priority: P1)

**Acceptance Scenarios**:

1. The gate's run record carries the plan's mode and its reason ("the tooling changed: ...", "N engine file(s) ...",
   "no baseline ..."), and the count of tests selected.
2. The run record carries each phase's seconds: the preflight, each static phase, the reference step, the hooks suite, the
   test phase, and the coverage floors where they are a step of their own.

### User Story 3 - The landing waits only on what can refuse it (Priority: P2)

**Acceptance Scenarios**:

1. The landing cohort's fresh block - a rate, never a refusal - runs after the push, outside the landing's path; the fixed
   seeds and pinned rows still run beside the gate and still refuse a regressed seed. The fresh block's record is kept as
   today's (`make cohort-seeds` reads its trend).
2. `cover-changed` runs beside the gate, not before it; where it finds an uncovered added line, the gate is stopped and the
   landing refused with its message, as today.
3. Where a landing ran incremental and the baseline is older than the refresh rule allows, a full gate run is started after
   the push, outside the landing's path, and records a fresh baseline; a later landing never waits on it, and two never run
   at once.

### User Story 4 - The cutoff rests on numbers (Priority: P2)

**Acceptance Scenarios**:

1. Before the 60% cutoff is dropped, the gate's fixed cost (what an incremental run of no tests costs) and its per-test
   cost are measured from the run records of real landings (User Story 2), and recorded in this feature's research with
   the numbers.

## Requirements

### Functional Requirements

- **FR-001**: Of the paths the tooling hash covers, `incremental.plan` MUST plan `full` only for the gate's own machinery
  and test configuration (US1 scenario 3), and MUST plan `full` for a change to a pinned lockfile; its other fallbacks (no
  baseline, a non-Python engine file, a non-module file under `tests/`, an import-time line) are unchanged. A `scripts/`
  change MUST select the tooling tests (reused on their recorded reads) and every test module outside `tests/tooling/`
  and `tests/hooks/` that reads `scripts/` - decided by a STATIC rule, since nothing records those modules' reads: the
  module's own source, or the source of a module under `tests/` it imports (transitively), names `scripts/` or imports
  `tests._scripts` - read LOOSELY: any source line of the module, or of such a helper, that mentions the word `scripts`
  (`tests/test_building_types.py` reaches it as `os.path.join(REPO, "scripts")`) - over-selecting costs a module, missing
  one makes a `scripts/` change unsafe.
- **FR-002**: The gate's run record MUST carry the plan's mode, its reason and the count of tests selected.
- **FR-003**: The landing (`scripts/land.py`) MUST run the cohort's fresh block after the push, outside its path; the fixed
  seeds and pinned rows MUST stay beside the gate with their refusal.
- **FR-004**: The landing MUST run `cover-changed` beside the gate, stop the gate when it refuses, and refuse the landing
  with its message.
- **FR-005**: The gate's run record MUST carry each phase's seconds.
- **FR-006**: A landing's gate MUST run the tests its change reaches however many there are; the baseline MUST be refreshed
  by a full run started after a push when the refresh rule calls for one, never on a landing's path, one at a time. The
  rule and the dropped cutoff MUST rest on the costs FR-007 measures.
- **FR-007**: The gate's fixed cost and per-test cost MUST be measured from real landings' run records before FR-006's
  rule is set, and recorded with the numbers.
- **FR-008**: Each behavior has a unit test that fails with the change removed.

## Success Criteria

- **SC-001** (FR-001): In a fixture repository, a `scripts/` edit after a baseline plans `incremental` and selects the
  tooling tests and the test modules that read `scripts/`, among them a module outside `tests/tooling/` that reaches
  `scripts/` only through a `tests/` helper it imports, and one that reaches it only as `os.path.join(ROOT, "scripts")`;
  an edit to `l7r/diagram/ci/`, a test target's recipe,
  `pyproject.toml`'s `[tool.coverage.run]` or `requirements.txt` plans `full`; an edit to a Makefile help line or a
  `requirements*.in` plans `incremental`.
- **SC-002** (FR-002, FR-005): A gate run's record carries `plan_mode`, `plan_reason`, `selected` and `phases` with a
  number of seconds for each phase that ran.
- **SC-003** (FR-003, FR-004): A landing's log shows the fresh block started after the push and `cover-changed` beside the
  gate; a fixture landing with an uncovered added line is refused and its gate stopped.
- **SC-004** (FR-006, FR-007): This feature's research records the measured fixed and per-test costs; a landing reaching
  more than `FULL_FRACTION` (the constant, 0.6) runs incremental; a full gate is started after the push when the refresh rule calls for one, and none
  while another runs.
- **SC-005** (FR-008): `make test-file FILE="tests/tooling/ci/ tests/tooling/test_tick_task.py"` and `make hooks-test` pass,
  each new test red without its change.
- **SC-006** (FR-001, FR-003, FR-004, FR-006): A real engine landing after a tooling change is measured end to end and
  reported against T26's 8.8 minutes (observed 2026-10-24; method: the landing's log and commit times).

## Assumptions

- The tooling tests' own reuse (feature 383 amendment 5) stays as it is; this feature only stops a tooling change from
  forcing the engine tests to run.
- The fixed seeds and pinned rows keep refusing a regressed seed at the landing; only the fresh block moves.
- The lockfiles the GM's item names are the pinned `requirements*.txt` (`requirements.txt`: "Locked ... Re-lock:
  pip-compile"); a `requirements*.in` is their source and changes nothing the tests run on until re-locked.

## Review history

- spec-fidelity round 1 (2026-10-24): CHANGES REQUIRED - the lockfile rule was new, not existing, and named the `.in`
  sources too (narrowed to the pinned files, marked ADDED); "reads `scripts/`" had nothing to decide it from (a static rule
  stated, with a fixture through a helper); "only" dropped the planner's other fallbacks (kept, stated). Its aside taken:
  `scripts/gates/gate-stamp.py` stays a full trigger.
- spec-fidelity round 2 (2026-10-24): CHANGES REQUIRED - the static rule missed a bare `"scripts"` path component
  (`tests/test_building_types.py`; read loosely now, any mention of the word); `gate-stamp.py` as a full trigger was an
  unmarked exception to the GM's item 1 (dropped: a change to the files it covers shows in the manifest as added or removed).
