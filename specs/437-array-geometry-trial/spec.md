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

The GM reads what one caller's geometry, asked of its candidates as arrays, saved in time and calls, and what that suggests the
whole layer would save, and decides whether to go on.

**Acceptance Scenarios**:

1. **Given** the 40-household roll, **Then** the caller whose per-candidate scalar geometry holds the most time is named from a
   measurement, with the share it holds.
2. **Given** that caller vectorized, **Then** the report gives its stage's and the roll's time before and after (`make
   perf-ab`, the quick form, then a subset) and calls (`make phase-calls`), read against the quick form's floor.
3. **Given** the measured saving, **Then** the report states what the whole geometry layer might save, labeled as an
   extrapolation from this one caller.

### User Story 2 - What the trial cost to run (Priority: P1)

The GM reads how long each step of the trial took - specifying, reviews, planning, measuring, building, testing, landing - and
which tooling or process changes those times point at, to make iterating on performance cheaper.

**Acceptance Scenarios**:

1. **Given** the trial done, **Then** the report lists each step's wall-clock time from a log kept as it ran, the waits
   (reviews, gates, cohorts, rolls) apart from the work, and the improvements those times suggest, each with the time it would
   save.

## Requirements *(mandatory)*

- **FR-001**: The target is chosen by measurement: `make perf-profile` of the 40-household roll's largest stages (seed 25),
  read for the caller whose calls into the scalar geometry primitives (`seg_dist`, `seg_closest`, `point_in_poly`, `edge_dist`
  and their kin in `settlement/_geom/primitives.py`) hold the most time; the reading is recorded.
- **FR-002**: That caller asks its candidates' geometry as arrays (the primitives' array forms, `seg_dists`, `points_in_poly`,
  or new ones beside them), each array form held equal to its scalar form by a test on random cases.
- **FR-003**: Maps may move (the GM 2026-10-18: speed work may move maps, held to the research); the landing cohort passes and
  the changed code's research claims are checked.
- **FR-004**: The evidence: `make phase-calls` before and after; `make perf-ab` quick (seed 25, 40 households) with its floor,
  then a subset (seeds 25, 39, 47 at 20 and 40 households) once before landing.
- **FR-005**: The trial lands where the evidence shows time saved beyond the floor, or calls saved with no time lost; otherwise
  it is set down, its evidence recorded.
- **FR-006**: A report (`specs/437-array-geometry-trial/report-trial.md`) gives the measured saving, the labeled extrapolation
  to the whole layer, each step's wall-clock time from a clock log (`process-clock.md`) kept as the trial ran, and the
  tooling and process improvements the times point at.
- **FR-007**: No requirement, test or exit of this feature refuses on a time (feature 435 FR-006 stands).

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): The report names the caller and its measured share of the roll's profiled time.
- **SC-002** (FR-002, FR-003): The array forms' tests pass on random cases and the landing cohort passes (or the trial is set
  down with the reason).
- **SC-003** (FR-004, FR-005): The report shows the quick and subset A/Bs with the floor, and the phase-calls before and after.
- **SC-004** (FR-006): The report's process section lists every step with its time and at least one improvement per step that
  took more than five minutes.
- **SC-005** (FR-007): Nothing added refuses on a time.

## Edge Cases

- The vectorized caller is slower (array setup costs more than it saves on few candidates): that is a finding, recorded, and
  the trial is set down (FR-005).

## Assumptions

- Seed 25 at 40 households is the measured case, as in features 435 and 436.
