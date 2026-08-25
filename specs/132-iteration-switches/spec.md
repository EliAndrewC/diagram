# Feature Specification: The Iteration Switches - Remote Off, Scope Locked

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=132-iteration-switches`)

**Created**: 2026-08-25

**Status**: APPROVED by `spec-fidelity` - round 3 verdict **FAITHFUL** (2026-08-25), after rounds 1 and 2 returned changes (see Review history). **AMENDED the same day on the GM's second request** (the local `make done` short-circuits on the same rule as the remote gate: FR-019..FR-023) - amendment APPROVED at round 2 (**FAITHFUL**, 2026-08-25); **AMENDED AGAIN on the GM's third message** (the key is the remote key, not wider: Makefile/scripts/config changes do not owe the gate) - second amendment: round 1 NOT FAITHFUL (the tests-only sentence was the session's to ask, not resolve); the GM ruled (FR-024); **round 2 FAITHFUL** (2026-08-25). **FR-025** (ci/ exempt, the GM's words) added after; awaiting its review.

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
   `make map` with exactly one gen runs, **Then** it runs exactly as before.
4. **Given** scope is locked, **When** `make map GEN="a.gen.py b.gen.py"`, `make map
   GEN='pool/*/*.gen.py'`, `make cache-audit` (with or without `--all`), `make regressions` or
   `make perf` runs, **Then** it refuses before any map rolls - the rule is "one map per
   invocation", and the enumeration in FR-010 is not where the guarantee lives.
5. **Given** scope is locked, **When** `make scope-unlock REASON="..."` runs, **Then** the default
   returns, the release is recorded, and the printout reminds the operator that the pool has not
   been swept and no perf bookend taken since the lock was set (constitution XIII: what
   accumulated is measured, not remembered).

---

### User Story 3 - The switches are visible and auditable (Priority: P2)

Any session can see the switches' state, and the history of every throw and release is in git.

**Independent Test**: `make switches` prints both axes with reason and date; `git log` on the
setting file lists each change as its own commit. (Round 1 removed a `make audit` reporting
clause as unrequested.)

**Acceptance Scenarios**:

1. **Given** any state, **When** `make switches` runs, **Then** both axes print with state, reason,
   who (the committer identity) and UTC.
2. **Given** a switch is thrown, **When** the target completes, **Then** the setting file is
   COMMITTED by the target itself (`chore: remote off - <reason>` / `chore: scope locked - ...`),
   so the state is never an uncommitted local difference and reaches every clone through the
   normal sync; the history of throws and releases is that file's git log.

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
  **The existing test seams are inside this rule** (the reviewer's aside): `sync-with-main.sh`
  honors `CI_ROUTE` / `CI_MERGE` today in any tree, and `CI_ROUTE=DIRECT` on a real clone would
  skip the gated route entirely - a pre-existing hole this feature closes under Principle XIV: the
  seams are honored ONLY in a tree with no diagram skill (a fixture), which is the only place the
  tests use them. `mapcheck`'s `SCOPE` environment default is read through the lock like the flag.
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
  holding both axes, each with `state`, `why`, `who` and `utc`. Defaults (file absent): remote
  `on`, scope `unlocked`.
- **FR-002**: A throw or release MUST be done through a make target that REQUIRES a reason,
  writes the file, and COMMITS it in the same target. There is no other supported write path.
- **FR-003**: There MUST be no environment variable, make variable or flag that overrides a thrown
  switch. The release target is the only way back.
- **FR-004**: A malformed file MUST fail closed (remote off, scope locked) and print why.
- **FR-005**: `make switches` MUST print both axes with state, reason, who and UTC. (The history
  of throws and releases is the git log of the file - FR-002 commits each one - and needs no
  second reporting surface; the `spec-fidelity` review of round 1 removed a `make audit` clause
  as unrequested.)

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

- **FR-010**: With scope locked, **no invocation of any target or module may roll a map other
  than the tier's reference settlement, and no invocation may roll more than one map.** This is a
  RULE; the list is its known instances, not its extent: `cohort`, `done FULL=1`, `test-full`,
  `tripwire`, `maps SCOPE=all`, `cache-audit` (any form - its default rolls a subset of the pool
  repeatedly, `--all` the whole pool), `regressions`, `ci-check FULL=1`, `ci-check
  TARGET=<operation>`, `ci-merge FULL=1`, and `map` with more than one gen or a glob in `GEN`
  (`pipeline.regen` takes a list, and `pool/*/*.gen.py` is the documented whole-pool sweep). Each
  refuses before any map rolls and before any prompt, naming the reason, the date and
  `make scope-unlock`. **`perf` and `perf-gate` are in this list**: a snapshot rolls the reference
  settlement at several seeds, which is *"some number of different maps with some number of
  different seeds per map"* - a sweep. Under the lock the performance bookends are not taken; a
  feature that lands while the lock is on records that in its plan, and the bookends are owed when
  the lock is released. (Round 1 of the fidelity review found the enumeration left `cache-audit`
  and a globbed `GEN` open; round 2 found `perf` carved out in FR-018 - the same failure twice.)
- **FR-011**: With scope locked, `make maps` (the adaptive command) MUST run the reference map
  alone and MUST NOT widen after a clean run.
- **FR-012**: THE ONE STATEMENT of what runs under the lock: an invocation that rolls NO map
  (`make quick`, `make test-file`, `make done` in reference scope's non-map phases, `make
  switches`, every `cheap` operation) or exactly ONE map (`make reference`, `make map` with one
  gen, `make hamlet` with one spec, `make perf-profile` - one seed, one stage). Everything else
  refuses (FR-010). No other requirement re-lists the permitted set.
- **FR-013**: The lock is enforced in BOTH the Makefile (the entry every operator uses) and the
  Python entry points the sweeps run through (`cohort_audit`, `mapcheck`, `cache_audit`,
  `make_regressions`, `pipeline.regen` - which refuses a list longer than one - and the `ci`
  dispatcher), so
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
- **FR-018**: The DECISION that one-map invocations (FR-012's set - which this requirement does
  not re-list) stay runnable under the lock MUST be recorded with the alternatives priced
  (CLAUDE.md "Record a decision to ACCEPT a limitation"): the GM's definition of the suite is
  *"forty eight different maps ... some number of different maps with some number of different
  seeds per map"* - a sweep; one map is iteration, and refusing it would make the lock refuse the
  work the lock exists to protect.

**The local gate short-circuits like the remote one (amendment, GM 2026-08-25)**

The GM's words: *"this also seems like the kind of thing which shouldn't even run the normal 5
minute tests, right?! Like it's only documentation. Can we apply the same rules that decide whether
to short circuit and skip AWS tests to these 5 minute tests as well for the make done procedure?"*

- **FR-019**: `make done` (reference scope) MUST check, BEFORE running anything, whether the last
  recorded verification is a green `make done` against exactly the content the gate exercises,
  and if so MUST report `already verified` (naming that run's time and commit), record
  `green-local done`, and exit green - in seconds, rolling no map and running no test. It may
  re-write the `gate-stamp` ONLY because the key (FR-020) includes the stamp's own hash: a
  short-circuit can never stamp content no gate ran on (a test proves it).
- **FR-020**: "The content the gate exercises" is EXACTLY what the remote rule keys on - the GM's
  second amendment: *"I thought we were omitting `make done` results for changes to the hooks or
  scripts or makefile changes, etc."* Two things, both already computed by the dispatcher: the
  content hash of every `*.py` under the skill EXCEPT `tests/` (`gate-stamp`'s `diagram` area -
  the dispatcher's `green-local-since-edit` condition), and the engine key (`l7r/**/*.py`,
  `pool/*.gen.py`, `pool/*.json` - its `tree-not-already-verified` condition). The Makefile,
  `pyproject.toml`, the lockfiles and `scripts/**` are NOT in the key, exactly as they are not in
  the remote one: a change to them does not owe a `make done` (the guard scripts owe `make
  hooks-test`, as before). A documentation-only change leaves both unchanged. (The first draft of
  this amendment widened the key to those paths on the reviewer's containment argument; the GM
  overruled it in their own words, and containment is met by the hash itself.)
- **FR-021**: The short-circuit MUST NOT apply to `FULL=1` (a different scope), and MUST NOT
  apply when the last verification is anything but a green `done` (a green `quick` or `reference`
  vouches for less than the gate does). A red last run never short-circuits.
- **FR-022**: There is no flag to force the short-circuit. (A `FORCE=` re-run flag was in the
  first draft and removed at the amendment's fidelity review as unrequested - the remote rule it
  copies has none.)
- **FR-023**: Proven both ways: a docs-only edit, a Makefile edit, a `scripts/` edit and an edit
  confined to `tests/**` after a green `done` all short-circuit; an edit to a `.py` under the
  skill outside `tests/` (including one outside `l7r/`, e.g. `.explain.py`) or to a pool gen or
  manifest does not, and a test edit combined with one of those does not.
- **FR-024 (the GM's ruling, 2026-08-25)**: *"if the only thing that changed were tests AND the
  previous test run was green then we skipped the lengthy AWS tests - we should do the same thing
  for the expensive 5 minute tests"* - asked which side, the GM chose *"Yes, locally AND on AWS"*.
  So `tests/**` is NOT engine content anywhere: a tests-only delta takes the DIRECT route (no
  build), is outside the engine key, and is outside `gate-stamp`'s `diagram` area (which
  otherwise would refuse the push for want of a green stamp). This deliberately narrows what
  `gate-stamp` hashes, which feature 130's FR-008 forbade a dispatch list from doing on its own -
  here it is the GM's ruling, recorded verbatim above. The cost, stated so it is a decision and
  not an oversight: a test edited after the last green run can land on main without having
  executed; it executes on the next real gate.
- **FR-025 (the GM, 2026-08-25)**: *"isn't it actually test code? Like the engine itself isn't
  using it, right? Isn't it only part of what decides whether the tests need to be run, which
  makes it test code? I suspect the ci/ directory should join the list of exempted things along
  with the tests themselves."* So `l7r/diagram/ci/**` is exempt exactly as `tests/**` is: a
  ci-only delta takes the DIRECT route, is outside the engine key, and is outside `gate-stamp`'s
  `diagram` area. Nothing in `ci/` is imported by a generator or the engine; its tests are in
  `tests/ci/` and run inside `make quick`, which is the check a ci-only change gets. Exactly `ci/`
  - the GM named it; `switches.py`, `_invocation.py` and `tools/` are the same kind of code and
  are left for the GM to add if wanted (recorded here so the question is not reopened blind).

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

## Review history (constitution XVI)

- **Round 1 (2026-08-25): NOT FAITHFUL.** (1) FR-010 was an enumeration that left `cache-audit`
  and a globbed / multi-gen `make map` runnable - two working full-pool routes under a lock whose
  purpose is *"literally cannot"*. Rewritten as a rule (one map per invocation, reference only),
  FR-012/FR-013/FR-018 and Story 2 amended, scenario 5 added. (2) The `make audit` reporting
  clause, Story 3 scenario 3 and the `commit` field were unrequested; removed. The reviewer's
  aside on the `CI_ROUTE`/`CI_MERGE` seams is recorded as an edge case and fixed in this feature.
- **Round 2 (2026-08-25): NOT FAITHFUL.** FR-018 had left `perf` runnable - four seeds is a sweep
  by the GM's own definition - and FR-012/FR-018 stated the permitted set twice with different
  contents. `perf`/`perf-gate` now refuse under the lock (FR-010); FR-012 is the single statement
  of what runs; FR-018 records only the decision. Story 2's scenarios renumbered.
- **Round 3 (2026-08-25): FAITHFUL.** Nothing missing, nothing added; the round-2 changes applied
  without new scope. Reviewer's aside recorded: under remote-off, when main has moved on engine
  paths the ritual refuses with the merge instruction rather than merging itself - the same
  sequence with the session as the driver.
- **Amendment round 1 (2026-08-25): CHANGES REQUIRED.** (1) FR-020 was an enumeration that left
  `.explain.py` and `wip/*.gen.py` - linted by the gate - outside the key; now a rule. (2) FR-019's
  re-stamp made explicit as safe only because the key contains the stamp's areas. (3) `FORCE=`
  removed as unrequested. (4) FR-023 covers the missed case. Applied.
- **Amendment round 2 (2026-08-25): FAITHFUL.** Reviewer's aside checked: `dev/switches.json` is
  outside the gate key on purpose - reference-scope `make done` never reads it (only `FULL=1` does,
  and FULL never short-circuits), so a throw or release cannot change what a reference gate proves.
- **Second amendment (2026-08-25, after landing):** the GM saw the amended gate re-run on a
  Makefile change and overruled the widened key: *"I thought we were omitting `make done` results
  for changes to the hooks or scripts or makefile changes, etc."* FR-020 now keys on exactly what
  the dispatcher keys on. **Round 1: NOT FAITHFUL** - the spec had resolved the GM's second
  sentence (tests-only + previous green -> skip) by declaring its premise false: the AWS rule the GM
  remembered does not exist (feature 130 puts `tests/` in the engine set), but that is authority to
  ASK, not to drop the request. The session asked; the GM ruled "Yes, locally AND on AWS" (FR-024).
- **Second amendment round 2 (2026-08-25): FAITHFUL.** Reviewer's aside recorded for the GM: because
  the route is structural, a tests-only delta after a RED gate still takes the DIRECT route, while
  locally FR-021 would run the gate for the same delta; the engine content is still covered by its
  own green stamp, so nothing unverified but the test lands.
