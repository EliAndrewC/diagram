# Feature Specification: array geometry trial

**Feature Branch**: `437-array-geometry-trial` (no branch; work on `main` in the clone)

**Created**: 2026-10-27

**Status**: Draft

**Affects**: tooling, performance, hamlet

**Approved**: the GM, 2026-10-27, "Sounds good, let's go with trialing the array-based geometry."

**Input**: `request.md` (the GM's words, verbatim).

## Why

Feature 417 T57 found that about two thirds of a 40-household roll's calls are a candidate's coordinates compared one number at
a time against the map's geometry (`specs/417-all-seeds-pass/research/t57-analysis.md`, section 3), and ranked item 10 - the
shared geometry layer asked on arrays of candidates - as the only candidate with a large expected effect, recommending a short
spike first: one predicate vectorized in its hottest caller and measured, to put a number on the large item before committing
to it. Feature 435's closing report found time unchanged by call counts alone, so the spike is measured in time.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A measured number on the large item (Priority: P1)

The GM reads what one predicate's calls in its hottest caller, asked as arrays, saved in time and calls, and what that suggests
the whole layer would save, and decides whether to go on.

**Acceptance Scenarios**:

1. **Given** the 40-household roll, **Then** the predicate and its hottest caller are named from a measurement (FR-001), with
   the share they hold.
2. **Given** that predicate's calls in that caller asked as arrays, **Then** the report gives its stage's and the roll's time before and after (`make
   perf-ab`, the quick form, then a subset) and calls (`make phase-calls`), read against the quick form's floor.
3. **Given** the measured saving, **Then** the report states what the whole geometry layer might save, labeled as an
   extrapolation from this one caller.

### User Story 2 - What the trial cost to run (Priority: P1)

The GM reads how long each step of the trial took - specifying, reviews, planning, measuring, building, testing, landing - and
which tooling or process changes those times point at, to make iterating on performance cheaper.

**Acceptance Scenarios**:

1. **Given** the trial done, **Then** the report lists each step's wall-clock time from the clock log (FR-006), the waits
   (reviews, gates, cohorts, rolls) apart from the work, and the improvements those times suggest, each with the time it would
   save.

## Requirements *(mandatory)*

- **FR-001**: One predicate and its hottest caller are chosen by measurement: `make perf-profile` of the 40-household roll's
  largest stages (seed 25), read for every scalar function in `l7r/diagram/settlement/_geom/primitives.py` taking a single
  point, and for the caller under which the chosen predicate's time is largest; the reading is recorded
  (`research/share.md`), with the whole module's share of each stage's time beside it.
- **FR-002**: That caller's calls to that one predicate go through its array form (asked of the caller's candidates at once),
  which a test on random cases holds equal to the scalar form; the caller's other primitives stay as they are.
- **FR-003**: Maps may move (the GM 2026-10-18: speed work may move maps, held to the research); the landing cohort passes and
  the changed code's research claims are checked.
- **FR-004**: The evidence: `make phase-calls` before and after; `make perf-ab` quick (seed 25, 40 households) with its floor,
  then a subset (seeds 25, 39, 47 at 20 and 40 households) once before landing.
- **FR-005**: The trial lands only where the evidence shows time saved beyond the quick form's floor; otherwise it is set down
  (the engine change not landed), its evidence recorded, and the report says plainly that no time saving was measured.
- **FR-006**: A report (`specs/437-array-geometry-trial/report-trial.md`) gives the measured saving, the labeled extrapolation
  to the whole layer, each step's wall-clock time from a clock log (`process-clock.md`), and the tooling and process
  improvements the times point at. The log is kept as the trial runs from its opening; the steps before its first entry are
  entered from commit timestamps and the review dispatches' times, labeled reconstructed with their source. The trial starts
  at the GM's request and ends at the report, which states the total, split into the session's work and its waits (reviews,
  gates, cohorts, rolls).
- **FR-007**: No requirement, test or exit of this feature refuses on a time (feature 435 FR-006 stands).

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): The report names the predicate and its hottest caller, and their measured share of the profiled time.
- **SC-002** (FR-002, FR-003): The array form's test passes on random cases and the landing cohort passes (or the trial is set
  down with the reason).
- **SC-003** (FR-004, FR-005): The report shows the quick A/B with the floor and the phase-calls before and after, and the
  subset A/B where the trial lands (a trial set down by FR-005 runs no subset).
- **SC-004** (FR-006): The report's process section lists every step with its time and the total split into work and waits;
  every step over five minutes names an improvement with the time it would save, or says why none is seen.
- **SC-005** (FR-007): Nothing added refuses on a time.

## Edge Cases

- The vectorized caller is slower (array setup costs more than it saves on few candidates): that is a finding, recorded, and
  the trial is set down (FR-005).

## Review history

- 2026-10-27, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED - one predicate, not the whole caller; the clock's
  earlier steps reconstructed and labeled, the total split into work and waits; SC-004's quota replaced; the calls-only
  landing dropped.
- 2026-10-27, round 2 (spec-fidelity-verify): CHANGES REQUIRED - the caller reading taken over FR-001's search space and the
  predicate named; User Story 1 and SC-001/SC-002 worded for one predicate; the clock's rows sourced or marked not recorded.

## Assumptions

- Seed 25 at 40 households is the measured case, as in features 435 and 436.
