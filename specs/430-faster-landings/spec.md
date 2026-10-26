# Feature Specification: Faster landings - the gate, the push and the review rounds

**Feature Branch**: `430-faster-landings` (no branch; `main` in the clone)

**Created**: 2026-10-26

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-10-26, "Please file all 7 as one feature and then work all of them start to finish. Thank you."

**Input**: `request.md` (the GM's words verbatim, the seven proposals in order, and the measurements behind them).

## Why

A landing's cost is mostly the ceremony around the change, not the change (observed 2026-10-26, method: `dev/run-log` and
`dev/review-ledger.md`, see `request.md`): most gates ran FULL for reasons that do not need a full run, most red gates were
coverage gaps found only after a 4-5 minute gate, the push re-runs checks with nothing to judge, and review rounds spent
themselves on mechanical omissions or re-confirmed a departure already filed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A map-moving landing runs an incremental gate (Priority: P1)

A change regenerates a pool map. The gate runs the tests the change's code selects plus every test that reads the moved
manifests, instead of the whole suite.

**Independent Test**: a delta whose only non-Python change is `pool/hamlets/<m>/<m>.json` plans `incremental`, selecting the
manifest readers; a delta that changes an engine data file the readers do not cover still plans `full`.

**Acceptance Scenarios**:

1. **Given** a delta changing a pool manifest and engine Python, **When** the gate plans, **Then** it plans incremental with the
   manifest's readers added, and names them.
2. **Given** a delta changing a non-manifest engine data file, **Then** it plans full as today.

---

### User Story 2 - A test-tree doc or fixture change runs what it can affect (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a delta whose only `tests/` non-module change is a doc file (`*.md`), **Then** that change adds no tests.
2. **Given** a `conftest.py` changed under `tests/x/`, **Then** the plan selects the tests under `tests/x/`, not the suite;
   **Given** the top-level `tests/conftest.py`, **Then** it plans full as today.

---

### User Story 3 - A coverage gap is caught before the gate (Priority: P1)

Before the gate, one command measures the changed modules' coverage the way the full floor does, on the tests that reach them,
and names each uncovered changed line in under a few minutes.

**Acceptance Scenarios**:

1. **Given** today's six coverage reds, **When** each one's delta is replayed, **Then** the pre-landing check names the lines the
   full floor named (or the plan records which it cannot and why).
2. **Given** `make land`, **Then** it runs this check first and refuses before the gate on a named uncovered line (escape as
   today's `COVER_OK`).

---

### User Story 4 - A push checks only what its delta holds (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a delta of records only (no engine, claims or record-entry file), **When** the push runs, **Then** `claims-gate`,
   `entry-gate` and `cohort-gate` each exit at once, saying why.
2. **Given** the same delta checked twice, **Then** the second check reads the first's answer.
3. **Given** a delta several gates judge, **Then** they run concurrently and the push reports every refusal together.

---

### User Story 5 - Plan reviews spend themselves on decisions (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a plan block with an unlabeled figure, no red exit through `make arbiter-ask`, or a task with no approach block,
   **When** a plan review is dispatched, **Then** a mechanical plan-lint refuses first, naming each, and no round is spent.
2. **Given** an approach block that matches the template's shape and names no decision (`D<n>`) not defined in a reviewed block,
   **Then** it owes no spec-fidelity review, as a part B that decides nothing owes none today.

---

### User Story 6 - A filed departure lands without an arbiter round (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a DRIFTED claim judged `known (NNN Tnn)` whose task row is open and names the claim's unit, on code the landing
   changed, **When** the claims gate runs, **Then** it admits the claim, records it, and lists it in `make gm-review` for the GM.
2. **Given** a claims-triage bundle of at most a few claims, **Then** the session dispatches impl-drift directly and the
   triage is recorded as skipped for size.

---

### User Story 7 - The claims triage runs beside the plan review (Priority: P3)

**Acceptance Scenarios**:

1. **Given** a task whose plan blocks are under review, **When** the session dispatches the claims triage, **Then** the guard
   allows it (impl-drift still waits for the plan's verdict, as today).

### Edge Cases

- A pool manifest no reader names: the plan stays incremental and says no reader reads it.
- A landing's own records committed during the push: the push checks' cache keys on the delta's content, so a record-only commit
  is answered from the cache.
- An approach block that a later edit gives a new decision: it owes a review again (the template-match is re-asked each time).
- A known drift whose task row is closed or does not name the unit: still introduced, as today.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The gate's planner MUST plan incremental when the delta's only non-Python engine files are pool manifests, adding
  the manifests' reader tests (the readers `pool-readers.py` finds, extended to the gate's own trees).
- **FR-002**: A `tests/` doc file MUST add no tests; a non-top-level `conftest.py` MUST select the tests of its directory.
- **FR-003**: A pre-gate coverage check MUST measure the changed modules' lines with the tests that reach them (not only the
  mirrored directory), name each uncovered changed line, and run inside `make land` before the gate.
- **FR-004**: `claims-gate`, `entry-gate` and `cohort-gate` MUST exit at once when the delta holds nothing each judges; their
  verdicts MUST be cached on the delta's content; the push MUST run the gates concurrently and report every refusal together.
- **FR-005**: A mechanical plan-lint MUST run before a plan review is dispatched (labeled figures, the red exit, an approach
  block per task); an approach block matching the template and naming no new decision MUST owe no review.
- **FR-006**: The claims gate MUST admit a `known` drift on changed code whose open task row names its unit, record it, and list
  it in `make gm-review`; a claims-triage bundle of at most a few claims MAY be skipped for impl-drift, recorded.
- **FR-007**: The decide-first guard MUST let a claims triage be dispatched while the plan review runs.
- **FR-008**: Each change MUST name its cure in its own output and carry a test that fails without it (the project's rule).
- **FR-009**: No change may let a defect through that today's gate catches: each mechanical shortcut is proven against the
  full run on the deltas measured today (a replay), or its narrowing stated and priced.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): replaying today's 19 full-planned deltas that were full only for a manifest or a `tests/`
  non-module file, the planner plans incremental for each.
- **SC-002** (FR-003): the pre-gate check names the lines in each of today's 6 coverage reds (or the plan says which it cannot).
- **SC-003** (FR-004): on a records-only delta each of the three gates exits before reading the claims, the record or the
  cohort records (the push observed 2026-10-26, method: each gate timed alone on a records-only delta, `request.md`).
- **SC-004** (FR-005, FR-007): a plan review is never dispatched on a block the plan-lint refuses.
- **SC-005** (FR-006): a known departure on changed code lands with no arbiter round, and is listed for the GM.
- **SC-006** (FR-008, FR-009): every change's test fails without it; no replayed delta passes a check today's full run fails.

## Assumptions

- Tooling only: no engine behavior or map changes.
- "A few claims" for skipping triage: at most 3 (a knob, labeled).
- The GM approved items 5 and 6's fidelity trade by approving all seven.
