# Feature Specification: Cut the Cost of the Hamlet-Tier Test Suite

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=158-hamlet-test-cost`)

**Created**: 2026-08-29

**Status**: **APPROVED** - `spec-fidelity` round 3 verdict **FAITHFUL** (2026-08-29). Rounds 1 and 2
each returned CHANGES REQUIRED with four items; all eight were applied and the history is at the
bottom of this file. Implementation proceeds.

**Input**: [`request.md`](request.md), verbatim and unedited. That file is the authority for this
specification.

## The feature, in one sentence

Every test that runs for a HAMLET in any of the three tiers - `make quick`, `make done`, and the
full run - is audited one by one; every automated check whose guarantee the placement algorithm
already makes is retired together with the unit tests that exist only to prove it; every frozen
bad-map fixture that no generator can produce any more is deleted; and the tests that remain are
made cheaper by the techniques this project has already proved (a cached roll instead of a fresh
generation, fewer random seeds, a smaller subject) - with code coverage held exactly where it is.

## Why this exists (the GM's words - `request.md` is the authority)

- *"looking at the sum total of all of the tests that we have, which run for hamlets under any
  circumstances, which I believe is three different tiers of tests, the quick tests, the make done
  tests, and then the completely full test suite, I would like for you to look at where we can make
  further performance improvements."*
- *"if we are Running unit tests for an automated check. Then let's see whether that automated check
  is even still actually needed. In fact, I would guess that we need extremely few automated checks
  at this point because our placement algorithm is the thing which is doing the actual correctness
  guarantees. And in almost every case, there should be no reason for an automated check to even be
  run."*
- *"I think we have gotten rid of most or all of the stored maps from past failures because those
  maps were all from a period of time when the maps were manually generated. And, therefore, there
  is no reason to see what would happen if we encountered a type of map, which is literally
  impossible to produce any longer."*
- *"eliminate any automated checks, which do not comport to this new standard along with the unit
  tests associated with them, and then make whatever refactors you are able to make to increase the
  performance of the unit tests which remain"*
- *"It is okay if the tests become slightly less rigorous so long as we maintain our code coverage
  standards. For example, reducing the number of random seeds that we test against is okay but
  reducing our unit test code coverage is not. reducing the size of a test fixture settlement, which
  a unit test runs against in order to make it run more efficiently is fine, but making the test
  unable to validate the behavior, which we are checking for, is not fine."*
- *"At this time, I am only interested in the tests that are run while we are still developing on
  hamlets because we are still not yet done with our hamlet generation, which means we have not yet
  moved on to villages."*
- *"when you are done, push your results back to main. I will review what you have done after the
  fact and decide what to focus on next."*

## Scope, stated exactly

**IN scope**: every test that runs for hamlets under any circumstances, in all three tiers -
`make quick` (the unit tier), `make done` (the merge tier: `tests/` + `tests/gate/` +
`tests/tooling/`), and `make done FULL=1` / `make test-full` (the full tier, which adds
`tests/full/` and the three coverage floors). The gate's automated CHECKS
(`l7r/diagram/check_village/`) and the frozen bad-map corpus (`pool/regressions/`) are in scope
because unit tests exist to prove them.

**Also IN scope, stated plainly**: `tests/tier_town/` and `tests/tier_city/` are collected by
`make done` and by the full run (`tests/CLAUDE.md`, the tier table), so their tests are time paid
while developing hamlets and they are in scope for elimination and for cheapening exactly like any
other test the three tiers run. A check that only a town or a city map executes is judged like every
other check; where it is nonetheless kept, the unit tests that exist only to prove it are still
candidates for cutting, because they run in the tiers the GM is paying for.

**OUT of scope**: the drawing and placement behavior of the ENGINE. This feature does not change
what a map looks like; a retirement that would change a rendered map is not a retirement, it is an
engine change. Adding new map features, new tiers or new checks is likewise out of scope.

**NOT a scope reduction**: the GM's acceptance is explicitly *after the fact* - *"push your results
back to main. I will review what you have done after the fact"* - so unlike features 133, 135, 141
and 147 this feature does NOT close on a GM acceptance task. It closes when the work is pushed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - the audit, measured before anything moves (Priority: P1)

The GM asks for *"an extensive audit"* before any cut. A session that starts deleting before it has
measured cannot say afterwards what the deletion bought.

**Independent Test**: the audit is a ledger file; it is complete when every test the three tiers run
for a hamlet has a row, and every row carries a cost, what it proves, and a verdict.

**Acceptance Scenarios**:

1. **Given** a warm clone at the feature's merge base, **When** each of the three tiers is timed,
   **Then** a baseline table records wall time and test count for `make quick ALL=1`, the merge tier
   and the full tier, and the same three numbers are re-measured at the end for comparison.
2. **Given** the check battery, **When** the census runs, **Then** every check that executes on a
   scripted hamlet carries the stage its inputs are placed at, the stage they last change at, and a
   verdict of RETIRE (the placer's guarantee is final) or KEEP (a later stage can undo it).
3. **Given** `pool/regressions/`, **When** each fixture is classified, **Then** every fixture is
   marked as either producible by a generator that exists today or a relic of the hand-placement
   era, with the tier it belongs to.

---

### User Story 2 - the checks the placer already guarantees are retired (Priority: P1)

**Independent Test**: after the cut, the check-name roster is smaller, the gate is still green, and
every retirement's disposition is written down in the ledger.

**Acceptance Scenarios**:

1. **Given** a check whose every input is written by one placer stage and never changed by a later
   stage on any scripted hamlet, **When** the audit judges it, **Then** it is retired, its segment
   function deleted, its unit tests deleted, and its frozen fixtures deleted.
2. **Given** a retired check, **When** the retirement lands, **Then** the ledger records what
   carries its invariant afterwards - a named placer unit test, the placer's own construction, or an
   accepted loss of rigor - so a later reader can tell a deliberate cut from a lost guarantee. A
   replacement test is written only where a coverage floor would otherwise fall.
3. **Given** a check that measures a fact a LATER stage can still change - a caption placed before
   the frame, a lane web clipped after it is drawn - **When** the audit judges it, **Then** it is
   kept, and the ledger says which stage can still undo it.
4. **Given** the retirement, **When** the gate runs, **Then** every remaining check that HAS a firing
   proof still fires on a deliberate break of a real scripted roll, and the check-name fixture
   matches the registry.

---

### User Story 3 - the hand-era bad-map corpus is deleted (Priority: P2)

**Independent Test**: the corpus contains no manifest that no generator alive can produce; the
replay test is correspondingly cheaper and still green.

**Acceptance Scenarios**:

1. **Given** a frozen fixture whose manifest is a hand-authored legacy-tier map (town, city, capital,
   village), **When** the audit judges it, **Then** it is deleted - a map that is *"literally
   impossible to produce any longer"* pins nothing.
2. **Given** a frozen fixture whose only `fires` entries are checks retired by this feature,
   **When** the retirement lands, **Then** the fixture is deleted with them.
3. **Given** a kept check that only a frozen fixture proved, **When** its fixture is deleted,
   **Then** a scripted negative fixture replaces it where FR-010 requires it, and otherwise the loss
   of the proof is recorded in the ledger.

---

### User Story 4 - the tests that remain are made cheaper (Priority: P2)

**Independent Test**: each cheapened test still fails when its subject behavior is broken, and each
of the three tiers is measurably faster than the baseline.

**Acceptance Scenarios**:

1. **Given** a test that generates a settlement in order to ask one question, **When** it is
   cheapened, **Then** it reads a cached roll or a small hand-built manifest instead, and it still
   fails when the behavior it names is broken.
2. **Given** a test that sweeps N random seeds, **When** it is cheapened, **Then** it runs fewer
   seeds - in EVERY tier that runs it, the full tier included, since the full run is one of the
   three the GM asked to make faster - and the reduction is recorded with the number of seeds before
   and after. A sweep is retained at its old width in the full tier only if the ledger says what
   that width buys.
3. **Given** a test whose subject is larger than the behavior needs (household count, canvas size,
   feature count), **When** it is cheapened, **Then** the subject is the smallest one that still
   exercises the branch, and the test still fails on a deliberate break.
4. **Given** the whole change, **When** coverage is measured, **Then** the global 100% floor, the
   `settlement/` ratchet floor and the derived hamlet-path 100% floor all hold at or above their
   pre-feature values.

---

### Edge Cases

- A check that reads no manifest key the census can see (it derives everything) cannot be judged
  mechanically; it is judged by hand and the ledger says so.
- A segment function that carries BOTH a retired check and a kept one is split or kept whole with the
  reason recorded - it is never retired by half.
- A check that the reference hamlet and the gate polders never execute has no MEASURED verdict, so
  it is judged by hand against the same standard and the hand reason is recorded. Whatever the
  verdict, its unit tests are still weighed for cost, because they run in the tiers being paid for.
- Deleting a test deletes its coverage. Any module that falls below a floor because its only
  exerciser was deleted needs a direct unit test of the module, not a restored sweep.
- A cheapened test that no longer fails on a deliberate break has been broken, not cheapened; the
  break must be demonstrated for every test whose subject shrinks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The audit MUST cover every test that runs for a hamlet in all three tiers, and MUST
  record for each the tier it runs in, its measured cost, what it proves, and its verdict.
- **FR-002**: A baseline MUST be measured before any change and re-measured after, for all three
  tiers, reporting wall time and test count for each.
- **FR-003**: Every automated check MUST be judged against the standard the GM states: a check whose
  guarantee the placement algorithm already makes is retired. The mechanical test is whether any
  stage after the check's placer changes an input the check reads, measured on the scripted hamlet
  rolls; a hand judgment may override the mechanical verdict in either direction, with its reason
  recorded.
- **FR-004**: A retired check MUST take with it its segment function, every unit test that exists
  only to prove it, and every frozen fixture whose only purpose was to fire it.
- **FR-005**: Each retirement MUST be RECORDED with what carries the invariant afterwards - an
  existing placer unit test, the construction of the placer itself, or an accepted reduction in
  rigor (*"It is okay if the tests become slightly less rigorous"*). A NEW test is written only
  where a coverage floor named in FR-010 would otherwise fall. FR-010 is the only hard bar.
- **FR-006**: Every frozen bad-map fixture that no generator alive can produce MUST be deleted.
- **FR-007**: A kept check whose only proof was a deleted fixture MAY be given a scripted negative
  fixture (a cached roll with one deliberate break); one MUST be written only where a coverage floor
  named in FR-010 would otherwise fall. Every kept check left without a firing proof is named in the
  ledger.
- **FR-008**: *"make whatever refactors you are able to make to increase the performance of the unit
  tests which remain"*. The three techniques the GM names - a cached roll instead of a fresh
  generation, fewer random seeds, a smaller test subject - are EXAMPLES (*"things like that"*), not
  the list. ANY refactor that measurably speeds a remaining test, in any tier including the full
  one, is in scope so long as it breaks neither FR-009 nor FR-010. Each cheapening MUST be recorded
  with its before and after cost.
- **FR-009**: A cheapened test MUST still fail when the behavior it names is broken; this MUST be
  demonstrated, not asserted, for every test whose subject or seed count shrinks.
- **FR-010**: Code coverage MUST NOT fall. The global 100% floor, the `settlement/` ratchet and the
  derived hamlet-path 100% floor MUST all hold at or above their pre-feature values.
- **FR-011**: The engine's drawing and placement behavior MUST NOT change: every pool map's manifest
  is byte-identical after the feature, apart from any change the GM approves separately.
- **FR-012**: The work MUST be pushed to main when it is done. The GM reviews it after the fact;
  there is no acceptance task to wait on.
- **FR-013**: Every deletion MUST be recorded in a ledger that says what was deleted and why, so a
  later session can tell a deliberate cut from a lost test.
- **FR-014**: The three tiers' selection contract MUST be preserved: the directory a test lives in
  is what decides when it runs (feature 135). A test moved between tiers is recorded as a move.
- **FR-015**: A test the audit finds no longer relevant or useful - obsolete, duplicated, or
  superseded by a placer unit test - MUST be deleted with its reason recorded in the ledger, subject
  to FR-009 and FR-010. This is INDEPENDENT of FR-004: a test need not belong to a retired check to
  be cut. It is the second of the two patterns the GM named - *"eliminating tests ... which are no
  longer relevant or useful ... see where these patterns ... can be applied"*.

### Key Entities

- **Tier**: one of the three collections the GM names - `make quick` (unit), `make done` (merge),
  the full run. Membership is decided by the directory a test sits in.
- **Check**: a named automated verdict in `check_village`, produced by a segment function, listed in
  the check-name fixture, proved by at least one negative fixture.
- **Frozen fixture**: a stored manifest in `pool/regressions/` with a `_regression.fires` list, replayed
  to prove the named checks still fire.
- **Scripted negative fixture**: a cached roll of a real hamlet with one deliberate break applied in
  the test body - the post-141 replacement for a frozen fixture.
- **Ledger**: the audit's per-test and per-check record, with the verdict and its reason.

## Success Criteria *(mandatory)*

- **SC-001**: Each of the three tiers is measurably faster than its recorded baseline, and the three
  before/after pairs are published in the ledger.
- **SC-002**: The number of automated checks that run on a hamlet is lower than before the feature,
  and every one that remains has a stated reason a later stage can still undo it.
- **SC-003**: No stored bad map remains that no generator can produce.
- **SC-004**: No check that remains is proved only by a stored manifest that no generator can
  produce, and the ledger names every kept check left without a firing proof.
- **SC-005**: All three coverage floors hold at or above their pre-feature values.
- **SC-006**: Every pool map's manifest is unchanged, so no map moved.
- **SC-007**: A reader of the ledger can say, for any deleted test or check, why it went and what
  carries its guarantee afterwards - including tests cut on their own merits under FR-015.

## Assumptions

- "The completely full test suite" means `make done FULL=1` / `make test-full` - the tier that adds
  `tests/full/`, rolls every pool map and enforces the coverage floors. The remote AWS run executes
  the same target; the switch is `remote off`, so the measurements are local.
- "Maintain our code coverage standards" means the three floors the Makefile enforces, at their
  current values. Raising a floor is out of scope; lowering one is forbidden.
- The reference hamlet (Inashiro seed 4) and the gate polders are the scripted hamlets the census
  measures against, as in feature 141 - they are the maps the project currently iterates on.
- A check that no scripted hamlet executes gets no MECHANICAL verdict, because the census measures
  against the rolls. It is judged BY HAND against the same standard, with the reason recorded - it
  is not exempt. The GM's standard applies to every check; only the method of judging it changes.
- "Push your results back to main" follows the project's usual routing: the delta decides DIRECT vs
  GATED, and with `remote off` the gated route lands on a green local `make done`.

## Review history

- **Round 1** (`spec-fidelity`, 2026-08-29): **CHANGES REQUIRED**, four items. (1) The blanket
  exemption for checks that no scripted hamlet executes was an "X except where Y" carve-out against
  FR-003's own "every automated check MUST be judged", and it sheltered exactly the cost the GM
  asked to attack - `tests/tier_town/` and `tests/tier_city/` ARE collected by `make done` and the
  full run. (2) FR-005's "no retired invariant may become unwatched" turned every elimination into a
  1:1 replacement, adding tests to a feature whose purpose is to remove them, and silently overrode
  *"It is okay if the tests become slightly less rigorous"*. (3) US4-2 mandated that the full tier
  keep its seed sweep, when the full tier is one of the three the GM asked to make faster. (4)
  FR-008 narrowed *"whatever refactors you are able to make"* to the three techniques the GM offered
  as examples. All four applied. The review also confirmed as FAITHFUL the reading that the GM's
  *"push your results back to main. I will review what you have done after the fact"* removes the
  closing GM-acceptance task features 133/135/141/147 carried - and noted the consequence that
  `tasks.md` must therefore carry no open task at push time, or `sync-with-main.sh` refuses the
  landing.

- **Round 2** (`spec-fidelity`, 2026-08-29): **CHANGES REQUIRED**, four items, after confirming all
  four round-1 changes were correctly applied and that no new "X except where Y" had appeared.
  (1) FR-007, SC-004, US2-4 and US3-3 re-imposed the 1:1 replacement bar round 1 struck out of
  FR-005, moved from unit tests to FIRING proofs - which contradicted FR-005's own "FR-010 is the
  only hard bar" and would have made a feature whose purpose is to remove tests write scores of new
  ones. (2) SC-004 asserted, as an exit criterion, a property the tree already misses: the reviewer
  counted 154 registered check names against 35 proved by scripted fixtures and 97 proved only by the
  frozen corpus - **42 registered checks have no firing proof of any kind today**, and 77 more would
  lose their only proof if the corpus went. (3) US2-4 and US3-3 had to be restated to match. (4) No
  requirement carried the GM's second named pattern - *"eliminating tests ... which are no longer
  relevant or useful"* - on its own merits, only as an appendage of a retired check; FR-015 now does.
  All four applied.

  The reviewer also left an observation that is not a fidelity finding and is worth acting on: those
  **42 checks with no firing proof at all are, on the GM's own standard, prime retirement
  candidates** - a check nothing has ever shown to fire is a check nothing has shown to be needed.

- **Round 3** (`spec-fidelity`, 2026-08-29): **FAITHFUL**. All four round-2 changes applied with no
  new problem introduced, no requirement missing against the request, no "X except where Y" anywhere,
  and no scope inflation - "the only artifact created is the audit ledger the GM's own *do an
  extensive audit* asks for, and the before/after measurement pair that *further performance
  improvements* needs to be demonstrable". Two asides carried forward into implementation: FR-015 was
  listed out of order (fixed), and FR-005's "FR-010 is the only hard bar" is scoped to RETIREMENTS -
  where the test is deleted so FR-009 cannot apply. For a CHEAPENED test FR-009 still binds: it must
  still fail on a deliberate break. Implementation proceeds.
