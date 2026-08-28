# Feature Specification: the hamlet floor's residue - all three classes, until the floor is green

**Feature Branch**: none - `specs/146-the-hamlet-floor-residue` (`SPECIFY_FEATURE=146-the-hamlet-floor-residue`)
**Created**: 2026-08-28
**Status**: DRAFT - awaiting `spec-fidelity`
**Input**: [`gm-request.md`](gm-request.md), the GM's words verbatim (2026-08-28, accepting feature 145)

## What the GM asked for

One feature covering **all three** residue classes feature 145 left, not the biggest one alone; taken to
completion and merged **without a further acceptance**; and - the GM's explicit worry - the hamlet
coverage floor must **no longer be red** by the time this lands on main. The GM asked whether the floor's
red state is captured here or needs separate tasks: it is captured, because the 373 lines the floor
reports ARE the three classes and nothing else, so a green floor is this feature's closing condition
rather than a fourth errand. Where a class turns out to need work the floor does not measure, that work
is a task here too.

**Which floor turns green**: the HAMLET-PATH floor - the one that reports the residue the GM called *"that
three hundred and seventy four line residue"* (measured 373; the GM's number is recorded verbatim in
`gm-request.md` and the small discrepancy is arithmetic, not drift). The separate GLOBAL floor's ~30
pre-existing subprocess-side misses (145 research R3d) stay ledgered, out of scope by constitution XIII,
and are reported to the GM again at this feature's landing so the distinction is never silent.

## User Scenarios & Testing

### US1 - the floor is green (Priority: P1)

`make done FULL=1` runs the hamlet-path floor and it passes: every module the scripted rolls execute is at
100%. Nothing is exempted to achieve it, no `# pragma: no cover` is written, and no engine code is deleted
merely to make a number - the rules feature 145's FR-002 set, which the GM ruled on then and has not changed.

**Acceptance**: `make hamlet-floor-check` exits 0 on the FULL run's coverage data (the make-only guard refuses
the bare module invocation).

### US2 - a check that can fire is proved to fire (Priority: P1)

Class 2 is the largest and is not really a coverage errand: a check whose failure branch no test reaches is
a check nobody has proved fires. Each kept check that a hamlet enters gets a scripted negative fixture in
`tests/gate/test_scripted_fixtures.py` - a cached roll plus one deliberate break, targeted - which both
proves the check fires and covers the branch.

**Acceptance**: every hamlet-entered check with a reachable failure branch has a scripted fixture proving
it fires; a census names any that cannot be broken and says why.

### US3 - the dike-pond check is exercised (Priority: P2)

Class 1 is 56 lines behind one archetype guard. Either a scripted map rolls `mulberry_dike_fishpond` (the
peer session's feature 139 is scripting Kuwabata as exactly that) or this feature exercises the check
another way. The choice is made on the state of 139 when this task is reached, and recorded.

### US4 - the placer's refusals are unit-tested (Priority: P2)

Class 3: one `return True` per reason a seat is refused. A unit test builds the manifest that trips it and
asserts the predicate, the way feature 145 closed sixteen of them.

## Requirements

- **FR-001** Every line the hamlet-path floor reports as uncovered is either covered by a new test, or -
  where it is genuinely unreachable - removed with its reason recorded at the point of change. A line is
  never exempted, pragma'd, or excluded from the floor's module set to make the floor pass.
- **FR-002** Class 2's coverage comes from SCRIPTED negative fixtures (`tests/gate/test_scripted_fixtures.py`),
  not from hand-built manifests frozen into a corpus - feature 141's ruling stands.
- **FR-003** A check whose failure branch cannot be tripped by any legal break of a scripted map is named
  with its reason in this feature's record and DISPOSED OF HERE under FR-001 - covered, or removed with the
  reason recorded at the point of change - so the floor is green at landing. The census is reported to the
  GM as information, never as a gate on the landing: the GM ruled this feature needs no acceptance
  (*"without needing any acceptance from me"*), so it may not invent one.
- **FR-004** Class 1: the dike-pond check is exercised by a scripted map rolling the archetype where that
  is available; the decision and its date are recorded.
- **FR-005** Class 3: each refusal branch gets a unit test that trips exactly that reason.
- **FR-006** No regression: the HAMLET-PATH floor green, `make done` green, and `make done FULL=1` showing no
  failure other than the ledgered pre-existing GLOBAL-floor misses (145 research R3d - ~30 subprocess-side
  lines in `ci/`, `switches.py` and three tools, present in the pre-145 baseline), whose count is unchanged
  or lower. The pool stays clean, every gate check that passed at 145's landing still passes, and a moved
  map is settlement-reviewed before it ships.
- **FR-007** The feature lands on main when it is green, with NO acceptance task - the GM's instruction.

## Success Criteria

- **SC-001** The hamlet-path coverage floor is GREEN in `make done FULL=1`.
- **SC-002** Every hamlet-entered check with a reachable failure branch has a scripted fixture proving it fires.
- **SC-003** `make done` green; `make done FULL=1` red on nothing but the ledgered global-floor misses; no new
  regression against 145's landing.
- **SC-004** The count of uncovered hamlet-path lines is recorded before and after (373 at 145's landing).

## Assumptions

- "The residue in three named classes" = the classes as feature 145 named them, quoted in `gm-request.md`.
- The pre-existing GLOBAL floor misses (~30 lines in `ci/`, `switches.py` and three tools, all
  subprocess-side, present in the pre-145 baseline - 145's research R3d) are NOT this feature's residue and
  are out of scope unless the GM says otherwise; this feature's floor is the hamlet-path one.
