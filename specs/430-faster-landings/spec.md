# Feature Specification: Faster landings - the gate, the push and the review rounds

**Feature Branch**: `430-faster-landings` (no branch; `main` in the clone)

**Created**: 2026-10-26

**Status**: Draft (spec reviewed FAITHFUL, round 5, 2026-10-26; amendment 1 - SC-001 counted against FR-002)

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
2. **Given** a non-doc, non-module file changed under `tests/x/` (a `conftest.py` or a fixture data file), **Then** the plan selects
   the tests under `tests/x/`, not the suite; **Given** such a file directly under `tests/` (the top-level `conftest.py`), **Then**
   it plans full as today - the top level is the whole suite.

---

### User Story 3 - A coverage gap is caught before the gate (Priority: P1)

Today's six coverage reds were replayed through today's `make cover-changed` (FR-003a, `research.md` R1, `m:coverage-reds-replay`):
every line the five line-naming reds named was an EXISTING line that lost its coverage, none an added line - three in a module
their delta changed, two in a module it did not (a caller changed or deleted) - and the sixth was the floor not counting new tests
marked `tooling`. `cover-changed` asks only added lines, so it saw none of them. The pre-gate check therefore asks every line of
each changed module, with the tests the floor counts, inside `make land` before the gate and faster than it; the two reds in
unchanged modules stay the gate's (FR-009's narrowing, stated in Assumptions).

**Acceptance Scenarios**:

1. **Given** today's coverage reds, **When** each one's delta is replayed, **Then** the pre-gate check names the lines the full
   floor named in the three whose lines lie in a changed module, and counts the floor's tests for the sixth; the two whose lines
   lie in an unchanged module are left to the gate.
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
2. **Given** an approach block that matches the template's shape, changes no rule, tunes no number and moves nothing placed
   earlier (labeled or not), and whose every `D<n>` is defined elsewhere, **Then** it owes no spec-fidelity review, as a part B
   that decides nothing owes none today; a block that only lacks a `D<n>` label still owes one.

---

### User Story 6 - A filed departure lands without an arbiter round (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a DRIFTED claim judged `known (NNN Tnn)` whose task row is open and names the claim's unit, **When** the claims gate
   runs, **Then** it admits the claim, records it, and lists it in `make gm-review` for the GM.
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
- **FR-002**: A `tests/` doc file MUST add no tests; any other non-module file under `tests/<dir>/` (a `conftest.py`, a fixture
  data file) MUST select the tests of that directory; one directly under `tests/` plans full.
- **FR-003a**: Today's six coverage reds MUST first be replayed through today's `make cover-changed`, recording (with an `m:` key)
  whether it named each line the full floor named; FR-003's scope follows from that result.
- **FR-003**: A pre-gate coverage check MUST name every line of each changed module that the full floor would name uncovered,
  measured with the tests the floor counts (the GM's item 3: "on the changed modules, measured the way the full floor measures
  them"), run inside `make land` before the gate, and take less time than the gate.
- **FR-004**: `claims-gate`, `entry-gate` and `cohort-gate` MUST exit at once when the delta holds nothing each judges; their
  verdicts MUST be cached on the delta's content; the push MUST run the gates concurrently and report every refusal together.
- **FR-005**: A mechanical plan-lint MUST run before a plan review is dispatched (labeled figures, the red exit, an approach
  block per task); an approach block MUST owe no review only when it decides nothing in the sense a part B that decides nothing
  does today: it changes no rule, tunes no number and moves nothing placed earlier, labeled or not, and every `D<n>` it names is
  defined elsewhere. The test is asked of the block's own part A answers (the plan names which items carry each property); a
  missing `D<n>` label alone is not enough.
- **FR-006**: The claims gate MUST admit a `known` drift whose open task row names its unit, record it, and list it in `make
  gm-review`; a claims-triage bundle of at most 3 claims is not triaged: impl-drift is dispatched directly and the skip recorded.
- **FR-007**: The decide-first guard MUST let a claims triage be dispatched while the plan review runs.
- **FR-008**: Each change MUST name its cure in its own output and carry a test that fails without it (the project's rule).
- **FR-009**: No change may let a defect through that today's gate catches: each mechanical shortcut is proven against the
  full run on the deltas measured today (a replay), or its narrowing stated and priced.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): of today's 19 full-planned deltas that were full only for a manifest or a `tests/` non-module
  file (`m:full-plan-reasons`: 11 `inashiro.json`, 4 the top-level `tests/conftest.py`, 2 `tests/hooks/`, 1 a `CLAUDE.md`, 1
  `tests/tooling/ci/conftest.py`), the planner, replayed, plans incremental for the 15 that are not the top-level `conftest.py`;
  those 4 plan full, as FR-002 says.
- **SC-002** (FR-003, FR-003a): the pre-gate check names the lines of each of today's 3 coverage reds whose named lines lie in a
  module their delta changed; on the sixth it counts the tests the floor counts (no new `tooling`-marked test the floor leaves
  out); and on those replayed deltas it takes less time than the gate took. The 2 reds whose lines lie in an unchanged module
  are outside "the changed modules" and remain the gate's (`m:coverage-reds-replay`).
- **SC-003** (FR-004): on a records-only delta each of the three gates exits before reading the claims, the record or the
  cohort records (the push observed 2026-10-26, method: each gate timed alone on a records-only delta, `request.md`).
- **SC-004** (FR-005, FR-007): a plan review is never dispatched on a block the plan-lint refuses.
- **SC-005** (FR-006): a known departure lands with no arbiter round, and is listed for the GM.
- **SC-006** (FR-008, FR-009): every change's test fails without it; no replayed delta passes a check today's full run fails.

## Assumptions

- Tooling only: no engine behavior or map changes.
- "A few claims" for skipping triage: at most 3 (a knob, labeled).
- FR-009's narrowing for FR-003, priced: a line that loses its coverage in a module the delta did not change (a caller changed or
  deleted) is not asked before the gate; today that was 2 of 6 coverage reds (`m:coverage-reds-replay`), each still caught by the
  gate as now. Widening the check past "the changed modules" is the GM's to ask for, not this spec's.
- The GM approved items 5 and 6's fidelity trade by approving all seven.

## Review history

- spec-fidelity round 1 (2026-10-26): CHANGES REQUIRED - (1) item 3's "after confirming whether today's `cover-changed`
  actually missed those lines" is carried nowhere, and FR-003's "(not only the mirrored directory)" presumes its answer; the
  confirmation must come first and decide FR-003's scope, "fast" must be a criterion, and SC-002's "or the plan says which it
  cannot" escape goes to the plan review rather than being pre-approved. (2) FR-002 reads item 2's "a fixture change" as
  `conftest.py` only; fixture data files under `tests/<dir>/` are unaddressed (SC-001's 8 may need them). (3) FR-006's "on
  changed code" condition is not in item 6 (NOT LEGITIMATE as a condition; "task row names the unit" and "open" are
  LEGITIMATE); its "MAY be skipped" softens item 6's "skip". (4) FR-005's "decides nothing" must be the part B test, not the
  absence of a `D<n>` label alone.
- spec-fidelity round 2 (2026-10-26, VERIFY): CHANGES REQUIRED - (1) RESOLVED: FR-003a puts the `cover-changed` replay first
  and FR-003's scope follows it; "(not only the mirrored directory)" is gone; SC-002 makes "fast" a criterion; the US3.1 and
  SC-002 escapes are deleted. (2) RESOLVED: FR-002 and US2.2 cover any non-doc, non-module file under `tests/<dir>/`; the top
  level plans full. (3) RESOLVED: "on code the landing changed" is gone from FR-006, US6.1 and SC-005; FR-006 says small bundles
  are not triaged, and the skip is recorded. (4) PARTLY RESOLVED, two defects: (a) FR-005's parenthetical ("item 4 answered
  "No", item 5 "Neither"") copies `plan_sections.decides_nothing`, which only runs on `### Txx part B` blocks. Those item
  numbers belong to the checklist's part B (B4 "moving something placed earlier?", B5 "Tuning or changing?"). An approach block
  answers part A (`approach_gate.py` D8, `docs/approach-checklist.md`), and there A4 and A5 are different questions with no
  No/Neither answer, so no approach block can take the test as written. FR-005 must define "decides nothing" for an approach
  block in its own terms: the property part B's test checks, that no rule is changed, no number tuned and no earlier placement
  moved (labeled or not), and that every `D<n>` it names is defined elsewhere. A missing label alone is still not enough.
  (b) US5.2 still gives the label-only test that FR-005 now rejects. It must state the same test as the corrected FR-005.
- spec-fidelity round 3 (2026-10-26, VERIFY): CHANGES REQUIRED - (1) RESOLVED: FR-005 states the decides-nothing property (no
  rule changed, no number tuned, nothing placed earlier moved, labeled or not; every `D<n>` defined elsewhere) asked of part
  A's answers, with the item mapping left to the plan; a missing label alone is still not enough. (2) RESOLVED: US5.2 states the
  same test. New, from research.md R1 (added since round 2): (3) FR-003a's result is in and FR-003 did not follow it. R1 finds
  all 8 named lines were EXISTING lines that lost coverage, none added, and concludes the check asks every line of each changed
  module with the floor's own test selection; FR-003 still says "each uncovered changed line", which reaches none of the lines
  SC-002 requires it to name, and US3's description still carries the unresolved "if ... if not" branch. FR-003 must say: the
  check names every line of each changed module that the full floor would name uncovered, measured with the tests the floor
  counts (the GM's item 3: "on the changed modules, measured the way the full floor measures them"); US3 must state R1's result
  instead of the branch. (4) SC-002's "names the lines in each of today's 6" cannot hold for the sixth (9a157cc4b), which names
  no line - the floor and `cover-changed` selected different tests. SC-002 must name the lines of the five and, for the sixth,
  require the check to count the tests the floor counts. Figures: `m:coverage-reds-replay`'s command is prose, so `make
  figures` reported it NOT RE-MEASURED; spot-checked by `git diff -U0` on 31f739f5d, d92ff2c90 and 39ea51383 (12 line numbers
  sampled from their named lines, none added), agreeing with it.
- spec-fidelity round 4 (2026-10-26, VERIFY): CHANGES REQUIRED - (1) RESOLVED as asked: FR-003 names every line of each
  changed module the floor would name uncovered, with the tests the floor counts, quoting item 3; US3 states R1's result in
  place of the branch. (2) RESOLVED as asked: SC-002 names the 5 line-naming reds and, for the sixth, the floor's tests. New,
  introduced by those changes: (3) US3's "every line the five line-naming reds named was an EXISTING line of a changed module"
  is false by the replay's own method (base = the last `ticked (make land)` / `Tooling from` commit before the red):
  7f209090b names `law.py:933` and `b1713222b..7f209090b` does not touch law.py; 449e7df7b names `checks.py:141` and
  `144a0e102..449e7df7b` does not touch checks.py (both lost coverage through a caller changed elsewhere). The key US3 cites
  (`m:coverage-reds-replay`) records only added-versus-existing, not module-in-delta. So FR-003 as worded (the GM's "on the
  changed modules") cannot name those two, and SC-002 requires it to; US3.1 ("six coverage reds ... names the lines the full
  floor named") also no longer matches SC-002. It must say: US3 and R1 state the measured split (31f739f5d, d92ff2c90,
  39ea51383 name lines in modules their delta changed; 7f209090b and 449e7df7b name lines in modules it did not), with a
  module-in-delta field per red in the key; SC-002 and US3.1 require the check to name the lines of the three, the sixth's
  floor-counted tests, and state the two as outside the GM's "changed modules" scope, still caught by the gate (FR-009's
  narrowing stated). Reaching those two before the gate would widen item 3 beyond the GM's words and is the GM's call, not a
  spec edit. Round 3 prescribed FR-003's wording from R1's "So", which took a step the replay did not measure. Figures:
  `make figures` again NOT RE-MEASURED (prose command); the split checked by `git diff --name-only` on each red's range.
- spec-fidelity round 5 (2026-10-26, VERIFY): NOT-REVIEWABLE - no round consumed. The one figure with a unit in the changed
  passages, research.md R1's "So" bullet ("at a price of 2 of today's 6 reds (one 4-5 minute gate each)"), carries no
  `m:<key>` (`m:coverage-reds-replay` records lines, not minutes), no one-shot label and no round label; the Why paragraph
  labels the same figure, R1's new use does not. Label it there (e.g. "observed 2026-10-26, method: `dev/run-log`, the GM's
  figure in `request.md` item 3") and re-dispatch. Pending that, nothing else in the diff is in question: round 4's item reads
  as resolved on every point (the 3/2 split in US3, R1 and the key; SC-002 and US3.1 require the three plus the sixth and
  leave the two to the gate; the narrowing stated and priced in Assumptions; FR-003 unchanged, not widened). Figures:
  `make figures` 0 moved, 0 outside band, 0 not re-measured; `bash replay-reds.sh` matches `per_red` row for row (on round 5's
  own run).
- spec-fidelity round 5, re-dispatch (2026-10-26, VERIFY): FAITHFUL. The NOT-REVIEWABLE item is resolved: research.md R1's
  "So" now labels its figure ("one gate each, 4-5 minutes - observed 2026-10-26, method: `dev/run-log`, the GM's figure in
  `request.md` item 3"), matching request.md item 3's "4-5 minute gate". The spans-vs-lines aside was applied: R1's Finding
  and the key now say 8 spans, 20 lines (`unit: spans`, `lines_in_spans: 20`), and no passage in the feature directory still
  says "8 lines". Round 4's item stays resolved (none of its passages changed). The new wording adds no scope and contradicts
  nothing. Figures: `make figures` 0 moved, 0 outside band, 0 not re-measured; `bash replay-reds.sh` prints 8 EXISTING spans
  covering 1+7+1+3+1+1+2+4 = 20 lines, with law.py:933 and checks.py:141 not in their deltas (on round 5's own run).
