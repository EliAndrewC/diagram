# Feature Specification: The Iteration Switches - Remote Off, Scope Locked

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=132-iteration-switches`)

**Created**: 2026-08-25

**Status**: Draft - awaiting `spec-fidelity` review (constitution XVI)

**Input**: [`gm-request.md`](gm-request.md), verbatim and unedited. That file is the authority for
this specification; the session's proposal recorded there is what the GM's *"that sounds like
exactly what I want"* accepted.

## The feature, in one sentence

Two **committed, repository-wide switches** - *remote off* (nothing runs on AWS, and the merge gate
is satisfied locally instead) and *scope locked to the reference settlement* (nothing rolls a map
sweep) - each thrown and released by a make target that records who, when and why, so that during a
period of iterating on the reference hamlet the full test suite and the paid runs are not merely
discouraged but **cannot be run**.

## Why this exists (the GM's words)

- *"I want to make sure that as we iterate, not only do we not run the full test suite, but we
  literally cannot because just telling you, please make sure not to run the full tests. In the
  past has frequently resulted in the full tests getting run, and that costs both time and actual
  money now that we are running on AWS."*
- *"can we perhaps have the first thing that we do to update the tooling to essentially disable AWS?
  That seems like something that would be good as a reusable setting anyway. such that if it is
  disabled, then we do not use it as a gate. and we do not dispatch to it while we are doing
  iteration."*
- *"for the current period, I would like to focus on getting our reference hamlet to be exactly
  right ... and to not bother to run the larger set of tests."*

The project's own record says the same thing about instructions versus tooling: the reference-first
rule was written into the constitution and violated by its own author six hours later; feature 126
ran the full gate three times against a standing instruction; the 2026-08-24 bypass audit found 3
of 5 full sweeps unjustified. *"Just remembering to do the right thing always is much worse than
having good tooling."* This feature is that tooling for the two things the GM named.

## Two axes, deliberately separate

The GM asked for two things and they are independent: one could want local full sweeps with AWS
off (a budget month exhausted, offline), or AWS on with the scope locked (another session landing
engine work while this one iterates). So they are two fields of one setting, thrown and released
separately, and neither implies the other.

| axis | states | what it governs |
|---|---|---|
| **remote** | `on` (default) / `off` | whether anything is dispatched to AWS CodeBuild, and whether the merge gate may depend on it |
| **scope** | `unlocked` (default) / `reference` | whether any target may roll a map other than the reference settlement of its tier |

## User Scenarios & Testing

### User Story 1 - Disable AWS for the iteration period (Priority: P1)

The GM (or a session, on the GM's instruction) runs `make ci-off REASON="..."` once. From that
commit on, in every clone that carries it, no target starts a build, and the push ritual lands
engine work through a local gate instead of refusing.

**Why this priority**: this is the money. The GM's words: *"the first thing that we do"*.

**Independent Test**: throw the switch in a fixture repository; `make ci-check`, `make ci-merge`
and `make ci-image` all exit non-zero before any AWS client is constructed; `make ci-status` shows
the switch as the first condition; `sync-with-main.sh done` on an engine delta with a green local
`make done` on the merged content pushes with no build.

**Acceptance Scenarios**:

1. **Given** remote is `off`, **When** `make ci-check` / `make ci-merge` / `make ci-image` runs,
   **Then** it refuses with the reason and the date the switch was thrown, names `make ci-on`, and
   **no AWS API call is made** (the recorded-response test double records zero calls).
2. **Given** remote is `off` and this clone's delta is GATED, **When** the push ritual runs,
   **Then** the route reports `GATED (local - remote off)`: if a green local `make done` vouches
   for exactly the engine content the merge with the latest main would produce, the clone pushes
   directly; otherwise the ritual refuses and says exactly what to do (`git pull --no-rebase
   origin main`, then `make done`, then push again). Nothing is dispatched either way.
3. **Given** remote is `off`, **When** `make ci-on` runs, **Then** the default behavior returns
   unchanged and the release is recorded (who, when, why) like the throw was.
4. **Given** remote is `off`, **When** any refusal prints, **Then** it names the route that DOES
   the job locally - a guard that blocks a legitimate question without giving the route is a guard
   that gets worked around (CLAUDE.md, feature 127).

---

### User Story 2 - Lock the scope to the reference settlement (Priority: P1)

The GM runs `make scope-lock REASON="..."`. From that commit on, the only map any target rolls is
the reference settlement; every sweep refuses and names `make scope-unlock`.

**Why this priority**: this is the time - and the thing the GM said sessions keep doing when told
not to. Equal priority with Story 1: the GM's *"not only ... but literally cannot"*.

**Independent Test**: throw the lock in a fixture; each sweep target exits non-zero with the reason
before any map rolls; `make reference`, `make quick`, `make done` (reference scope) and
`make map GEN=<the reference gen>` still run.

**Acceptance Scenarios**:

1. **Given** scope is locked, **When** `make cohort`, `make done FULL=1`, `make test-full`,
   `make tripwire`, `make maps SCOPE=all`, `make ci-check FULL=1` or `make ci-check TARGET=<op>`
   runs, **Then** it refuses, before the FULL prompt and before any map rolls, printing the reason
   and date the lock was set and naming `make scope-unlock`.
2. **Given** scope is locked, **When** `make maps` runs, **Then** it rolls the reference map alone
   and does NOT widen to the tier even after a clean run (the adaptive widening is the lock's
   business, not the state machine's).
3. **Given** scope is locked, **When** `make reference`, `make quick`, `make done` (no FULL), or
   `make map` with the tier's reference gen runs, **Then** it runs exactly as before.
4. **Given** scope is locked, **When** `make scope-unlock REASON="..."` runs, **Then** the default
   returns, the release is recorded, and the printout reminds the operator that the pool has not
   been swept since the lock was set (constitution XIII: what accumulated is measured, not
   remembered).

---

### User Story 3 - The switches are visible and auditable (Priority: P2)

Any session can see the switches' state, and the history of every throw and release is in git.

**Independent Test**: `make switches` prints both axes with reason and date; `git log` on the
setting file lists each change as its own commit.

**Acceptance Scenarios**:

1. **Given** any state, **When** `make switches` runs, **Then** both axes print with state, reason,
   who (the committer identity), UTC and the commit they were set at.
2. **Given** a switch is thrown, **When** the target completes, **Then** the setting file is
   COMMITTED by the target itself (`chore: remote off - <reason>` / `chore: scope locked - ...`),
   so the state is never an uncommitted local difference and reaches every clone through the
   normal sync.
3. **Given** `make audit` runs, **Then** its report shows the current switch state and the throws
   and releases in the audited period.

### Edge Cases

- **Both switches thrown at once** (the GM's stated period): every refusal above applies; the
  local-gated push still lands reference-scope work.
- **A throw without a REASON**: refused. A reason someone will READ is a decision you have to
  defend (the bypass-log doctrine); the same bar applies here.
- **The setting file is absent** (a checkout older than this feature, a fixture): both axes are at
  their defaults - remote on, scope unlocked. Absence is never "off".
- **A malformed setting file**: fails CLOSED - treated as remote OFF and scope LOCKED, with the
  parse error printed. A corrupt switch must not silently become "everything is allowed".
- **An environment variable, make variable or command-line flag that says "ignore the switch"**:
  does not exist. The only way past a thrown switch is the release target, which commits. This is
  the GM's *"literally cannot"* and feature 130's *"never through an environment variable"*.
- **Remote off, and main has moved on engine paths since this clone's merge base**: the gated
  route refuses (the green local `make done` vouched for different engine content), and the
  refusal tells the session to merge main in and run `make done` again. Nothing is dispatched.
- **Remote off, `FULL=1` on the push**: refused - `FULL` names a remote sweep (feature 130) and
  there is no remote. With scope also locked it is refused by the lock first.
- **The build side** (`buildspec/run.sh`, the `door`): with remote off no build starts, so nothing
  changes there. A stale queued build from before the throw is not this feature's concern; the
  breaker and the existing detach command remain.
- **A session tries to write the setting file by hand**: nothing stops an edit to a tracked JSON
  file, and the project does not pretend otherwise (the same is true of the bypass log). What the
  feature guarantees is that every path through `make` reads it, and that the guard-file hook
  treats it as a guard file - an edit is a diff someone reviews.
- **A clone that has not synced since the throw**: still has remote on. The switch travels with
  main; the sync-in at the start of every piece of work is what delivers it. Documented, not
  worked around.

## Requirements

### Functional Requirements

**The setting**

- **FR-001**: The switches MUST live in ONE tracked file in the diagram skill's `dev/` area,
  holding both axes, each with `state`, `why`, `who`, `utc` and `commit`. Defaults (file absent):
  remote `on`, scope `unlocked`.
- **FR-002**: A throw or release MUST be done through a make target that REQUIRES a reason,
  writes the file, and COMMITS it in the same target. There is no other supported write path.
- **FR-003**: There MUST be no environment variable, make variable or flag that overrides a thrown
  switch. The release target is the only way back.
- **FR-004**: A malformed file MUST fail closed (remote off, scope locked) and print why.
- **FR-005**: `make switches` MUST print both axes with reason, who, UTC and commit; `make audit`
  MUST include the current state and every throw/release in the audited period.

**Remote off**

- **FR-006**: With remote off, `ci-check`, `ci-merge` and `ci-image` MUST refuse before any AWS
  client is constructed, and MUST name `make ci-on` and the local route that does the job.
- **FR-007**: With remote off, `ci-status` MUST show the switch as the first condition, and the
  dispatch decision MUST carry a `remote-enabled` condition that fails with the reason and date.
- **FR-008**: With remote off, the push ritual's GATED route MUST become LOCAL-GATED: it pushes
  directly when a green local `make done` vouches for exactly the engine content the merge with
  the latest main would produce (the existing local-verified rule of 2026-08-25), and REFUSES
  otherwise with the merge-and-rerun instruction. It MUST NOT fall through to the DIRECT route
  and MUST NOT dispatch.
- **FR-009**: The ritual's route line MUST say which of the three it took: DIRECT, GATED (remote),
  or GATED (local - remote off).

**Scope locked**

- **FR-010**: With scope locked, every target that rolls a map other than the tier's reference
  settlement as part of a SWEEP MUST refuse before any map rolls and before any prompt: `cohort`,
  `done FULL=1`, `test-full`, `tripwire`, `maps SCOPE=all`, `ci-check FULL=1`, `ci-check
  TARGET=<operation>`, `ci-merge FULL=1`. The refusal names the reason, the date and
  `make scope-unlock`.
- **FR-011**: With scope locked, `make maps` (the adaptive command) MUST run the reference map
  alone and MUST NOT widen after a clean run.
- **FR-012**: With scope locked, `make reference`, `make quick`, `make done` (reference scope),
  `make test-file`, and `make map` with the tier's reference gen MUST behave exactly as today.
- **FR-013**: The lock is enforced in BOTH the Makefile (the entry every operator uses) and the
  Python entry points the sweeps run through (`cohort_audit`, `mapcheck`, the `ci` dispatcher), so
  that neither a new make target nor a direct module call can roll a sweep unnoticed. (Everything
  already runs through `make` - feature 127 - so the Python layer is defense in depth, not the
  primary door.)

**The guard treatment (CLAUDE.md "When you add a guard")**

- **FR-014**: Each refusal MUST be proven to FIRE by a test that throws the switch in a fixture
  and watches the target go red, and proven NOT to fire on the allowed targets.
- **FR-015**: The Makefile-level refusals MUST have a `scripts/test-*.sh` companion run by
  `make hooks-test`; the Python-level ones MUST be covered at 100% under `pytest`.
- **FR-016**: The setting file MUST be registered with the guard-file hook so a hand edit is
  flagged like any other guard edit.

**Records**

- **FR-017**: The "why" of every rule above MUST be recorded where the rule lives (CLAUDE.md
  "Record the why", REQUIRED): the setting file's `CLAUDE.md`, a comment at each Makefile
  refusal, and the ci package's `CLAUDE.md` (a sixth condition).
- **FR-018**: The decision NOT to gate single-map targets (`map` with a non-reference gen,
  `hamlet`, `perf`) under the lock MUST be recorded with the alternatives priced (CLAUDE.md
  "Record a decision to ACCEPT a limitation").

### Key Entities

- **Switches**: the two axes and their records; read by every guarded target; written only by the
  four make targets (`ci-off`, `ci-on`, `scope-lock`, `scope-unlock`).
- **Condition `remote-enabled`**: the new first row of the dispatch decision (feature 130's five
  become six).
- **Route `GATED (local - remote off)`**: the push ritual's third route, which exists only while
  remote is off.

## Success Criteria

- **SC-001**: With remote off, a session that attempts every paid target in the repository makes
  zero AWS API calls - proven by the recorded-response double counting calls in the suite.
- **SC-002**: With scope locked, a session that attempts every sweep target rolls zero maps other
  than the reference settlement - proven by the fixture test counting generator invocations.
- **SC-003**: With both thrown, an engine change covered by a green local `make done` lands on main
  through the ritual with no build, in one push.
- **SC-004**: Every refusal message names the release target and the local route that does the job.
- **SC-005**: `make done` (reference scope), `make quick` and `make reference` are unchanged in
  behavior and timing (within noise) whether the switches are thrown or not.
- **SC-006**: `make hooks-test` and `pytest` are green with every new test present; deleting any
  refusal makes at least one test red (proven during implementation, recorded in tasks.md).

## Assumptions

- The GM's proposal-acceptance covers the specifics the session proposed (target names, one tracked
  file, LOCAL-GATED semantics, the two-axes separation). Where this spec goes beyond the proposal
  it is in the direction of MORE refusal (fail-closed on a malformed file, the Python layer, the
  audit rows), never less.
- "The full test suite" in the GM's words means the map SWEEPS - the 48-seed cohort, the pool
  re-gate of `FULL=1`, the tier widening of `make maps`, and any remote operation. Targets that roll
  ONE map are iteration, not the suite, and stay available (FR-018 records this).
- The setting file is one file, not a per-entry directory: it is a SETTING with a current value,
  not an append-only log, so the concurrent-push conflict that drove `perf-log/` and `bypass-log/`
  to directories does not arise (two sessions changing the same switch at once is a real conflict
  that SHOULD be seen).
- The `who` field is the git committer identity `sync-with-main.sh` establishes; the project has no
  other notion of an actor at a terminal (feature 129 research R1).
- Feature 133 (the reference hamlet's acceptance) begins after this feature lands and works with
  both switches thrown for its whole span.
