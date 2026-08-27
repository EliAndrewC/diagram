# Feature Specification: The `make done` Tests Are Audited and Accepted by the GM

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=134-done-test-audit`)

**Created**: 2026-08-27

**Status**: APPROVED by `spec-fidelity` - round 2 verdict **FAITHFUL** (2026-08-27), after round 1 returned two changes (the ledger covers every phase the gate runs; the unlocked measurement's precondition is stated). Implementation may begin.

**Input**: [`gm-request.md`](gm-request.md), verbatim and unedited. That file is the authority for
this specification.

## The feature, in one sentence

Every test that `make done` runs - the check that decides whether a clone may merge back into
main - is audited one by one for a cheaper form that keeps ninety percent or more of its value,
the suite is reorganized so that the DIRECTORY a test lives in is what decides when it runs
(quick / done / the lengthy AWS run), the improvements are implemented, and the feature closes only
when **the GM accepts the current state of the tests** - with further tasks added as the audit's
findings and the GM's own improvements arrive.

## Why this exists (the GM's words)

- *"we did an extensive audit of our quick tests ... I think it is worth doing a pass on this
  where we do a similar type of audit of the tests which are our make done tests. that is
  currently, I think, something like four or five minutes. I feel like It should probably only be
  a fraction of that."*
- *"I suspect that we are doing things similar to what we were doing on those original quick
  tests, things like recomputing things that could be cached, thus wasting millions of operations
  on every test run, and running tests against many random seeds on the same map when, in fact,
  that is something either more suited to a EXAUSTIVE=1 Test run or better yet best farmed out to
  the AWS tests."*
- *"For each test, I want you to examine whether there is a more efficient version of that same
  test that would get us ninety percent or more of the benefit. while taking a tiny fraction of
  the time to run."*
- *"If there are cases where you think that there is some value in running the full version of
  the test, then that's fine, and we can kick it off to the full AWS tests."*
- *"if we have one directory for our quick tests, one directory for our done tests, and one
  directory for our lengthy AWS tests, then that is probably both a useful efficiency improvement
  and also something that helps from an organizational perspective because when we are deciding
  whether a new test should be added, then the directory into which we added is the thing that
  inherently determines When and under what circumstance that test is run"*
- *"the final task of the new spec kit feature should be me taking acceptance of the current
  state of the tests. And I plan on adding other tasks to the feature as we go"*

## The shape of the feature

The same shape as feature 133: an audit with a measured baseline, a first batch of implemented
improvements, and an **open-ended task list** whose last task - the GM's acceptance - cannot be
ticked by a session. The feature therefore stays in the clone until the GM accepts (feature 130
FR-011's feature-complete condition refuses to land engine work while a task is open); the
`specs/` number claim is pushed once, as the project requires, and every later push is routed by
its delta as always.

The audit is a per-test LEDGER, not a summary: for every test the gate runs, what it costs, what
it proves, and which of four verdicts it received - **keep** (already cheap or already earning its
time), **cheapen** (the same assertion on a smaller or cached subject), **move to the full run**
(its full form is worth having, at AWS/`FULL=1` time, not at merge time), or **re-home** (it was
in the wrong tree: a test marked as a map-roller that rolls nothing, a test that only exists to
carry coverage the merge check does not enforce). Nothing is deleted: a test's assertion survives
every verdict; only its size, its subject, or the time it runs changes.

## User Scenarios & Testing

### User Story 1 - The merge check answers in a fraction of today's time (Priority: P1)

A session has changed engine code and runs `make done` with the scope UNLOCKED - the real merge
check, map-rolling tests included. It finishes in a fraction of the four-to-five minutes it takes
today, and the verdict is as trustworthy: every assertion the gate made before, it still makes,
on a subject that is either the same or a documented cheaper stand-in.

**Why this priority**: it is the request. Iteration wall-clock is the project goal every guard
serves (constitution v2.3.0), and the gate is the largest fixed cost of every engine change.

**Independent Test**: the baseline ledger (FR-001) and the after-measurement, taken the same
way, both green, and the second is at most a quarter of the first; the end-to-end unlocked `make
done` confirming it lands in the run-log at the GM's unlock.

**Acceptance Scenarios**:

1. **Given** the baseline measurement is recorded (FR-001, per-test durations kept), **When** the
   audited suite is measured the same way on the same code, **Then** its total is at most 25% of
   the baseline's and no test that passed at the baseline fails.
2. **Given** an engine change that alters what a rolled map draws, **When** `make done` runs,
   **Then** every test whose subject that change reaches is re-rolled for real - a cached subject
   is served only when nothing it depends on changed.
3. **Given** a test whose FULL form was moved to the lengthy run, **When** the full run executes
   (`make done FULL=1` locally, or the AWS check), **Then** that full form runs there, unchanged.

---

### User Story 2 - Where a test lives is when it runs (Priority: P1)

A session is about to add a test. It looks at the tree and sees three places - the quick tests,
the done tests, the lengthy tests - and the choice of directory IS the choice of when the test
runs. No marker, no deselect list, no Makefile edit is needed to make that true.

**Why this priority**: the GM named it as both an efficiency and an organizational improvement,
and it is what keeps the audit from rotting - a test added to the wrong place is visible by its
path.

**Independent Test**: the three targets each collect exactly their tree(s) and nothing else, and
a test dropped into each tree runs under exactly the target(s) that tree belongs to.

**Acceptance Scenarios**:

1. **Given** the reorganized tree, **When** `make quick` runs, **Then** it collects only the quick
   tree; **When** `make done` runs, the quick and done trees; **When** the full run executes, all
   three.
2. **Given** a new test file placed in the done tree, **When** `make quick` runs, **Then** the
   file is not even collected; **When** `make done` runs, it is.
3. **Given** the tree index (`tests/CLAUDE.md`), **When** a session reads it, **Then** the rule
   "directory = when it runs" and the criteria for each tree are stated in one place.

---

### User Story 3 - Every gate test carries an audited verdict (Priority: P2)

A future session wonders why a gate test is small, or cached, or absent from `make done`. The
audit ledger names the test, its measured cost before and after, what it proves, and the verdict
it received - so the decision is recorded, not rediscovered.

**Why this priority**: constitution Principle XII's "record the decision and the alternatives" -
without the ledger a cheapened test is indistinguishable from a weakened one.

**Independent Test**: the ledger lists every test the baseline `make done` collected, with a
verdict and a measured before/after cost for each one that changed.

**Acceptance Scenarios**:

1. **Given** the ledger, **When** it is checked against the baseline's collected test list,
   **Then** no test is missing from it.
2. **Given** a test with the verdict "cheapen", **When** its entry is read, **Then** it states
   what was made smaller or cached and why the assertion still holds.

---

### User Story 4 - The GM accepts the state of the tests (Priority: P1)

The GM, having added whatever further tasks the findings and their own ideas call for, declares
the current state of the tests accepted. Only then is the feature complete.

**Why this priority**: it is the feature's closing condition, in the GM's own words.

**Independent Test**: the acceptance task is ticked with the GM's words recorded verbatim, and
the feature-complete condition then permits the gated push.

**Acceptance Scenarios**:

1. **Given** the acceptance task is open, **When** a session tries to land engine work from this
   feature, **Then** the push is refused as an incomplete feature.
2. **Given** the GM's explicit acceptance, **When** it is recorded in the task list, **Then** the
   feature is complete and the ordinary route applies.

### Edge Cases

- A test marked as rolling a map that in fact rolls nothing (its generator is stubbed): it is
  re-homed to the quick tree, and the guard that demands the marker must understand why it no
  longer needs one.
- A cached subject whose cache entry is stale in a way the key cannot see (the same class of
  hole the pool cache closed for deleted modules): any doubt regenerates, never serves.
- A test that exists only to carry line coverage: the merge check does not enforce coverage
  floors, so it proves nothing there and runs only where the floors are enforced.
- Two tests that roll the same map: the second must not pay for the roll again in the same run.
- The scope lock is on (as it is today): the reorganization must leave the locked gate at least
  as fast as it is now, and the deferred tests owed at unlock must still be owed.
- A test whose full form and cheap form disagree: the full run is the authority; the cheap form
  is fixed or the test is moved, never the other way round.

## Requirements

### Functional Requirements

- **FR-001**: The feature MUST record a measured BASELINE before any change, on unmodified code:
  every phase `make done` runs (the reference step, lint / format / typecheck, the guard-script
  suites of `hooks-test`, and the test phase), with per-test durations for the test phase, plus
  the time spent collecting the suite. The scope lock is a TRACKED file the GM set, so the
  map-rolling tests it defers are measured by running them by name (`make durations
  MARK=rolls_map`, which the lock does not refuse) rather than by flipping the switch; the one
  figure that needs the lock released - an end-to-end unlocked `make done` - is taken at the
  GM's unlock, and the spec says so rather than leaving it to the implementer.
- **FR-002**: Every test the baseline `make done` RUNS - the pytest-collected list, the
  `hooks-test` guard suites, and the reference step - MUST appear in the audit ledger with a
  verdict - keep, cheapen, move to the full run, or re-home - and, for every test that changed,
  its measured cost before and after.
- **FR-003**: A test given the "cheapen" verdict MUST keep its assertion; what changes is the
  size of its subject, the number of repetitions, or whether an unchanged subject is recomputed.
- **FR-004**: A subject that is expensive to produce (a rolled map) and is produced by the same
  inputs on every run MUST NOT be produced again while nothing it depends on has changed; the
  decision MUST be keyed on what the production actually executed and read, in the way the pool's
  own cache already is, and any doubt MUST regenerate.
- **FR-005**: Running a test against many seeds of the same map MUST NOT happen at merge time;
  the sweep runs in the full form (`EXHAUSTIVE=1` / `make done FULL=1` / the AWS check) and the
  merge check runs one representative seed.
- **FR-006**: The suite MUST be organized into three trees - quick, done, full - such that `make
  quick` collects the quick tree, `make done` the quick and done trees, and the full run all
  three; a test's tree is the only thing that decides which targets run it.
- **FR-007**: A test that only carries coverage MUST live in the full tree, because the merge
  check does not enforce the coverage floors.
- **FR-008**: The whole pool sweep and the multi-seed cohort ratchet MUST live in the full tree.
- **FR-009**: A test marked as a map-roller that stubs its generator MUST be re-homed to the
  quick tree, and the marker guard MUST accept it there.
- **FR-010**: Nothing MUST be deleted from the suite by this feature: every assertion the baseline
  made is still made somewhere, in a form the ledger names.
- **FR-011**: The tree index MUST state the rule "the directory decides when a test runs" and the
  admission criteria for each tree.
- **FR-012**: The constitution and the dev-loop docs MUST be brought into agreement with the
  three-tree rule where they currently describe the two-level (quick / gate) arrangement, quoting
  the GM's request.
- **FR-013**: Any defect found during the audit (a stale deselect path, a mis-marked test, a
  guard that would not fire) MUST be fixed in this work (constitution XIV), and each is a task.
- **FR-014**: The feature's task list MUST end with the GM's acceptance of the current state of
  the tests, tickable only on the GM's explicit word recorded verbatim, and MUST accept further
  tasks as findings and the GM's improvements arrive.
- **FR-015**: The locked-scope `make done` MUST be no slower after this work than before it.

### Key Entities

- **Audit ledger**: one row per gate test - path, what it proves, cost before, verdict, cost
  after, what changed.
- **Test tree**: quick / done / full - a directory whose membership decides which make targets
  collect it.
- **Rolled-subject cache**: an entry per fixed roll spec, keyed on the code and data the roll
  executed and read; serves the finished manifest and plan on a hit.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The gate's unlocked cost on unchanged code - the sum of its phases as FR-001
  measures them, the map-rolling tests included - is at most 25% of the baseline's, green; the
  end-to-end unlocked `make done` confirming it is recorded in the run-log when the GM releases
  the lock.
- **SC-002**: Every test the baseline ran (FR-002's three groups) has a ledger row; zero assertions are
  dropped (every baseline test is either present, cheapened, moved, or re-homed - never absent).
- **SC-003**: A test placed in each of the three trees runs under exactly the targets that tree
  belongs to (three placements, three observations).
- **SC-004**: The locked-scope `make done` is no slower than its baseline.
- **SC-005**: Suite collection time is measured before and after, and the after figure is no
  larger for any target.
- **SC-006**: The acceptance task is ticked only with the GM's verbatim words.

## Assumptions

- The scope lock and remote-off switches stay as the GM set them (the lock is a tracked file, so
  a worktree is locked too); the map-rolling tests are measured by name under the lock (FR-001),
  and the end-to-end unlocked figure waits for the GM's unlock.
- `EXHAUSTIVE=1` remains the name of the full form; the full run is `make done FULL=1` locally
  and the AWS check remotely, and feature 134's successor (the idle background run) will consume
  the full tree.
- "A tiny fraction" is read as the SC-001 target of 25% or less; the GM may tighten it.
