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

1. **Given** `make perf-ab` in any form, **Then** below the totals it prints every stage's wall time for both versions and
   the change, marking the stages that moved by more than a share of the roll it states; a leg that records no stages prints
   its total alone.

### User Story 5 - The small snags (Priority: P2)

1. **Given** `make trial SLUG=<slug> APPROVED="<the GM's words>"`, **Then** the brief's `**Approved**:` line carries them, so
   the approval guard passes the brief's first commit.
2. **Given** a later review round's stale-terms search, **Then** a line the same change rewrote (a line in a replaced block,
   rewritten from one already about the subject) is not named as carrying an old value; a line the change inserted is still
   searched.
3. **Given** `make quick` on a loaded host, **Then** its time is read against the GM's 15 s ceiling (feature 171,
   2026-08-30) after dividing out the host's measured slowdown (a calibration loop timed in the same run, on as many processes
   as quick's workers), so load alone does not fail it; the 15 s stays the ceiling for an unloaded host.

## Requirements *(mandatory)*

- **FR-001**: `make land`'s cheap refusals, run before the gate, include the claims gate's "a claim is owed a check and none
  is in flight": it refuses at once with the owed claims named and the bundle command.
- **FR-002**: `.specify/templates/trial-template.md`'s evidence section asks for "the verdict: the branch of the rule taken,
  and the measurement that took it"; `docs/spec-kit-and-reviews.md`'s trial form says the review checks the verdict against
  the rule's branches.
- **FR-003**: `perf_profile.profile_stage` writes `meta.seat_search` (when the roll recorded one) into its `.placed.json`.
- **FR-004**: `make perf-ab` (every form) prints, per seed and size, every stage's best wall time for A and B and the change,
  marking each stage whose times differ by more than 1% of the roll's best time (the threshold printed); the quick and subset
  forms' worker returns each roll's stage times, the full form reads them from its snapshot's legs; a leg with no stage times
  prints its total alone.
- **FR-005**: `make trial` takes `APPROVED="<words>"` and writes it into the brief's `**Approved**:` line, dated today.
- **FR-006**: The stale-terms search (`scripts/reviews/stale_terms.py`) does not name a candidate line the same diff rewrote -
  a line in a replaced block whose old line already named the candidate's subject; a line the diff inserted, or rewrote to
  bring the subject in, is still searched.
- **FR-007**: The quick gate's time check CHANGES what feature 171 compares - from the raw run to the run divided by the
  host's slowdown - on the GM's approval of this item ("quick's 15 s ceiling failing under load", 2026-10-27). The slowdown is
  a fixed calibration loop run at the check on as many processes as quick's workers (`XDIST_WORKERS`), its time against its
  unloaded time - a pinned value with its date, method and reason beside the baseline, as 171 FR-010 asks - and never below
  1. The ceiling and baseline are unchanged; the output prints the raw time, the slowdown and the normalized time. A one-shot
  measurement, dated with its method, records a fixed suite on quick's workers (`tests/hamletgen/`, 6 workers) and the loop
  timed under the same load, showing the slowdown tracks (`research/quick-calibration.md`).
- **FR-008**: `docs/guards.md` and the touched targets' help name each change; nothing added refuses on a time (feature 435
  FR-006).

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): a test of `land`'s preflight refuses on an owed claim with none in flight before any gate step runs.
- **SC-002** (FR-002, FR-005): `make trial ... APPROVED="x y"` writes a brief whose approval line quotes "x y" and whose
  evidence section asks for the branch; a test reads both.
- **SC-003** (FR-003): a test of `profile_stage` finds `seat_search` in the `.placed.json` when the roll recorded it.
- **SC-004** (FR-004): a test of the A/B table prints a row for every stage, only the stage past the threshold marked; reads the
  stage rows from the snapshot's legs in the full form; and prints only the total for a leg that records no stage times; a
  real quick A/B shows the stage rows.
- **SC-005** (FR-006): the stale-terms tests pass a diff whose candidate is a line the same diff rewrote from one about the
  subject, and still name a line the diff inserted carrying the old value.
- **SC-006** (FR-007): the quick ratchet's tests pass a run whose raw time is over the GM's 15 s ceiling (feature 171,
  2026-08-30; observed 2026-08-30, method: the GM's words, its source recorded in `research/quick-calibration.md`)
  but whose normalized time is under it, and fail one whose normalized time is over.
- **SC-007** (FR-008): the docs name the changes; nothing added refuses on a time.

## Edge Cases

- A calibration loop that runs faster than its recorded unloaded time (a quieter host than when recorded): the slowdown is
  taken as no less than 1, so a run is never judged against a tighter ceiling than the GM's.

## Review history

- 2026-10-27, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED - FR-007 states the comparison it changes, the loop on
  quick's workers, the pinned unloaded time and a measurement that the slowdown tracks; FR-004 every stage, every form;
  FR-006 rewritten lines only; SC-006's figure attributed.
- 2026-10-27, round 2 (spec-fidelity-verify): CHANGES REQUIRED - SC-004 to every stage and every form; FR-007 names the
  suite actually timed; SC-006's figure points at its research.

## Assumptions

- The five are the report's rows, in its order; each is a task.
