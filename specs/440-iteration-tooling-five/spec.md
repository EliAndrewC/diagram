# Feature Specification: five iteration tooling improvements

**Feature Branch**: `440-iteration-tooling-five` (no branch; work on `main` in the clone)

**Created**: 2026-10-27

**Status**: Draft

**Affects**: tooling, performance

**Approved**: the GM, 2026-10-27, "I think you should make all 5 of those tooling improvements"

**Input**: `request.md` (the GM's words, verbatim, and the five improvements of trial 439's report).

## Why

Trial 439's report (`specs/439-fewer-envelope-probes/report-trial.md`, "What the times point at") measured where features 438
and 439 lost time: a landing that ran its whole gate (about 19 min) before refusing on a claim never dispatched; a review
round spent on a verdict that misread its own rule; a counting spike and two dead ends to read a 40-household roll's seat
counters; two call-count fanouts to find which stage a +17% came from; and three small snags.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A landing refuses at once what waiting cannot cure (Priority: P1)

1. **Given** a claim owed a check with none in flight, **When** `make land` runs, **Then** it refuses before the gate runs,
   naming the claim and the command that bundles it, instead of after the gate.

### User Story 2 - The trial's verdict states its branch (Priority: P1)

1. **Given** a new trial brief, **Then** its evidence section asks for the verdict as the branch of the rule taken and the
   measurement that took it.

### User Story 3 - A seating trial's counters on record (Priority: P2)

1. **Given** `make perf-profile` of a stage at or after the homesteads, **Then** the `.placed.json` beside its raw profile
   holds the roll's seat-search counters (`meta.seat_search`) as well as the counts it holds now.

### User Story 4 - The stage that moved, in the A/B's own table (Priority: P1)

1. **Given** `make perf-ab` in the quick or subset form, **Then** below the totals it prints each stage's wall time for both
   versions and the change, for every stage whose time differs by more than a share of the roll it states.

### User Story 5 - The small snags (Priority: P2)

1. **Given** `make trial SLUG=<slug> APPROVED="<the GM's words>"`, **Then** the brief's `**Approved**:` line carries them, so
   the approval guard passes the brief's first commit.
2. **Given** a later review round's stale-terms search, **Then** a line the same change rewrote is not named as carrying an
   old value.
3. **Given** `make quick` on a loaded host, **Then** its time is read against the GM's 15 s ceiling after dividing out the
   host's measured slowdown (a calibration loop timed in the same run), so load alone does not fail it; the 15 s stays the
   ceiling for an unloaded host.

## Requirements *(mandatory)*

- **FR-001**: `make land`'s cheap refusals, run before the gate, include the claims gate's "a claim is owed a check and none
  is in flight": it refuses at once with the owed claims named and the bundle command.
- **FR-002**: `.specify/templates/trial-template.md`'s evidence section asks for "the verdict: the branch of the rule taken,
  and the measurement that took it"; `docs/spec-kit-and-reviews.md`'s trial form says the review checks the verdict against
  the rule's branches.
- **FR-003**: `perf_profile.profile_stage` writes `meta.seat_search` (when the roll recorded one) into its `.placed.json`.
- **FR-004**: `make perf-ab` (quick and subset forms) prints, per seed and size, each stage's best wall time for A and B and
  the change, for every stage whose times differ by more than 1% of the roll's best time (the threshold printed); the worker
  returns each roll's stage times.
- **FR-005**: `make trial` takes `APPROVED="<words>"` and writes it into the brief's `**Approved**:` line, dated today.
- **FR-006**: The stale-terms search (`scripts/reviews/stale_terms.py`) does not name a candidate line the same diff added or
  rewrote.
- **FR-007**: The quick gate's time check divides the run's time by the host's slowdown - a fixed calibration loop timed at
  the run, against its unloaded time recorded beside the pinned baseline - before comparing it with the 15 s ceiling; the
  ceiling and baseline are unchanged; the output prints both the raw and the normalized time.
- **FR-008**: `docs/guards.md` and the touched targets' help name each change; nothing added refuses on a time (feature 435
  FR-006).

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): a test of `land`'s preflight refuses on an owed claim with none in flight before any gate step runs.
- **SC-002** (FR-002, FR-005): `make trial ... APPROVED="x y"` writes a brief whose approval line quotes "x y" and whose
  evidence section asks for the branch; a test reads both.
- **SC-003** (FR-003): a test of `profile_stage` finds `seat_search` in the `.placed.json` when the roll recorded it.
- **SC-004** (FR-004): a test of the A/B table prints a stage row for a stage that moved past the threshold and none for one
  that did not; a real quick A/B shows the stage rows.
- **SC-005** (FR-006): the stale-terms tests pass a diff whose candidate line is itself added by the diff.
- **SC-006** (FR-007): the quick ratchet's tests pass a run whose raw time is over 15 s but whose normalized time is under it,
  and fail one whose normalized time is over.
- **SC-007** (FR-008): the docs name the changes; nothing added refuses on a time.

## Edge Cases

- A calibration loop that runs faster than its recorded unloaded time (a quieter host than when recorded): the slowdown is
  taken as no less than 1, so a run is never judged against a tighter ceiling than the GM's.

## Assumptions

- The five are the report's rows, in its order; each is a task.
