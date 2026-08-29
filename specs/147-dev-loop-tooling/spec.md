# Feature Specification: Dev-loop tooling - the probe, the audit, the profile, and the paired gate

**Feature Branch**: none (this project stays on `main`; `export SPECIFY_FEATURE=147-dev-loop-tooling`)
**Created**: 2026-08-29
**Status**: Draft
**Input**: The GM, 2026-08-29, after a time audit of feature 139 T55: *"Okay, let's do tooling fixes 1-3. And is there some way to make 6 happen automatically instead of reqiring you to remember it? Like is there a scripted way to have them both happen at the same time and that's the only way you can do either of them without some kind of override? We should do that if so."*

## Why this exists (the measurement)

T55 - "one of the vegetable grounds overlaps with the irrigated channels" - took **79.8 minutes** of wall
clock for a geometry fix whose final diff is one function. Measured from the session transcript:

| bucket | time | detail |
|---|---|---|
| waiting on background verification | 33.6 min | 3 gate runs, 2 tier sweeps, and a 17-minute review agent that only started after the gate came back |
| model turns | 25.0 min | 79 turns, ~19 s each - a large share spent re-deriving measurement scripts |
| map rolls | 13.6 min | **19 rolls**, 29-100 s each (median 47 s) |
| edits, lint, quick, shells | 6.6 min | including **42 throwaway measurement scripts** |

The same shape appears in T54 (108.8 min). Three causes, and this feature removes one each: the only
oracle for a geometry question was a full map roll; the only way to ask "does A overlap B" was to write
the point-in-polygon script again; and the independent review, which caught four real defects in T55, ran
last because it is dispatched from memory rather than by the tooling.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Measure a geometry change without drawing a map (Priority: P1)

A session changes how a polder's parcels, channels or banks are laid out and needs to know whether the
change did what it intended - do any parcels still overlap a channel, how much berm is left, what did it
cost in acreage, are the outlines still hand-piled rather than ruled.

**Why this priority**: it is the inner loop. 19 of T55's 80 minutes were map rolls whose only purpose was
to produce numbers that need no houses, no hinterland and no render.

**Independent Test**: change a polder geometry rule, run the probe, read the metrics; no map is drawn.

**Acceptance Scenarios**:

1. **Given** an unmodified engine, **When** the probe runs on the reference polder block, **Then** it
   prints the geometry metrics and exits successfully in a few seconds.
2. **Given** a change that leaves a channel crossing a parcel, **When** the probe runs, **Then** it
   reports the offending parcels with their coordinates and exits non-zero.
3. **Given** a change that shrinks the berm below the fabric's own, **When** the probe runs, **Then** the
   minimum berm it reports falls, without any map being rendered.

### User Story 2 - Ask "does A overlap B" once, not for the twelfth time (Priority: P1)

A session (or a reviewer) needs to know whether a recorded or drawn thing overlaps another: a farmhouse on
marsh, a parcel across a ditch, reed ink on a mulberry bank, a glyph over open water.

**Why this priority**: the same point-in-polygon script was hand-written six times in T55 and six more in
T54, and each rewrite costs a model turn plus the risk of measuring the wrong thing. It is the bucket that
consumes thinking time rather than wall clock, and thinking time is the largest single bucket.

**Independent Test**: run the audit against a finished map and get the same answers the hand-written
scripts produced, without writing one.

**Acceptance Scenarios**:

1. **Given** a map whose farmhouse stands on marsh, **When** the audit runs, **Then** it names the
   offending pair, the coordinates and the count, and exits non-zero.
2. **Given** a map with reed INK drawn over a dike band, **When** the audit runs over the drawn output,
   **Then** it reports the marks - not only the records - because half the questions asked in T54 and T55
   were about ink rather than about the manifest.
3. **Given** a clean map, **When** the audit runs, **Then** it reports zero for every family and exits
   successfully.

### User Story 3 - The gate and the review always run together (Priority: P2)

A session finishes a change that alters what a map draws. The integration gate and the independent
settlement-review are both required; today the gate is a command and the review is a memory.

**Why this priority**: the review caught four real defects in T55 (including a berm the author was about to
ship) and its 17 minutes sat on the critical path because it was dispatched only after the gate returned.
It is also the step that has been silently skipped before (2026-07-27, three city maps).

**Independent Test**: attempt each half alone and observe the refusal; run the pairing command and observe
both start.

**Acceptance Scenarios**:

1. **Given** a clone whose drawn map output has changed, **When** the gate is invoked alone, **Then** it is
   refused with a message naming the pairing command and the override.
2. **Given** no gate running or freshly green for this content, **When** a settlement-review is dispatched,
   **Then** it is refused the same way.
3. **Given** the pairing command, **When** it runs, **Then** the gate starts and the review is dispatched
   for the same content, and the session is told both are running.
4. **Given** a change that alters no drawn map output (docs, tests, a guard script), **When** the gate is
   invoked alone, **Then** it runs normally - the pairing is owed by ink, not by every gate.
5. **Given** an override with a reason, **When** either half is invoked alone, **Then** it runs and the
   reason is recorded where the audit can read it.

### User Story 4 - Find the slow stage in one roll (Priority: P3)

A session notices a roll got slower and needs to know which stage grew.

**Why this priority**: real but smaller - it cost ~3 minutes and four rolls in T55, twice in one session.

**Independent Test**: roll a map with the flag and read the per-stage table; roll without it and see the
output unchanged.

**Acceptance Scenarios**:

1. **Given** the flag, **When** a map rolls, **Then** each stage's elapsed time, the total, and the slowest
   stage are printed.
2. **Given** no flag, **When** a map rolls, **Then** the output is exactly what it is today.

### Edge Cases

- A guard must fire on an INVOCATION and stay silent on a MENTION: during the T55 audit a guard blocked an
  analysis script because the script's *text* contained the words `make quick` and `make done`. Every guard
  in this feature is tested against that shape.
- Two maps' ink changes in one clone: the pairing is satisfied when a review is pending for each changed
  map, not by one review of one of them.
- A review of a map whose gate is already green for exactly this content is allowed - the pairing is
  satisfied by the record, not by a second gate run.
- The probe must not become a second implementation of the geometry: it reports what the engine builds, so
  it cannot pass while the map fails.
- The audit is a diagnostic, not a gate: it never decides what ships, and a family it cannot measure is
  reported as unmeasured rather than as zero.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A make target MUST build a polder block alone - no houses, no hinterland, no render - and
  print its geometry metrics.
- **FR-002**: The metrics MUST include, at minimum: parcels overlapping a channel (count and coordinates),
  the minimum berm between a parcel and water, the block's acreage, and the per-parcel vertex and
  square-corner counts that `polder_parcels_are_organic` is judged on.
- **FR-003**: The probe MUST accept the knobs that shape a block (at least the seed and the fabric or
  archetype) so a change can be measured across several blocks in one run.
- **FR-004**: The probe MUST exit non-zero when a metric it reports would fail the gate, so it can be
  chained ahead of an expensive run.
- **FR-005**: A make target MUST report overlaps between named families on a finished map, taking the map
  as an argument.
- **FR-006**: The audit MUST cover both RECORDED geometry (footprints, parcels, channels, banks, marsh) and
  DRAWN ink (the marks in the rendered output), because half the questions asked in T54 and T55 were about
  ink rather than the manifest.
- **FR-007**: The audit MUST name each offender with its family, coordinates and count, and exit non-zero
  when any overlap is found.
- **FR-008**: A map roll MUST print per-stage timings when a flag is given, and MUST be byte-identical in
  output and behavior when it is not.
- **FR-009**: The timing output MUST name the slowest stage and the roll's total.
- **FR-010**: One command MUST start the integration gate and dispatch the independent settlement-review
  for the same content, together.
- **FR-011**: The integration gate MUST be refused when the clone's drawn map output has changed and no
  settlement-review is pending or freshly complete for that content.
- **FR-012**: A settlement-review dispatch MUST be refused when no gate is running, or freshly green, for
  that content.
- **FR-013**: Each refusal MUST name a single override token that carries a reason, MUST run the command
  when it is present, and MUST record the reason where the bypass audit reads it.
- **FR-014**: Every guard added by this feature MUST have a test companion proving it fires and proving it
  stays silent on a mention of the commands it guards (constitution XVIII).
- **FR-015**: Every new capability MUST be reachable only through `make` (feature 127), and MUST refuse a
  bare interpreter the way the rest of the engine does.
- **FR-016**: The new targets MUST be listed in the skill's command map with their measured times, so the
  next session finds them where it looks for the others.

### Key Entities

- **Polder block**: the parcels, channels, banks and envelope the polder builder produces, independent of
  any settlement drawn on it.
- **Overlap family**: a named pair of things that may not intersect (footprint vs water, parcel vs channel,
  ink vs mound), each with its own measure.
- **Pairing record**: the evidence that a gate and a review are running, or have run, against the same
  drawn content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A polder geometry change is measured in under 5 seconds, against the 47-second median map
  roll it replaces.
- **SC-002**: Every overlap question asked during T54 and T55 is answerable by one command with no script
  written - demonstrated by re-asking them on the shipped maps.
- **SC-003**: A slow stage in a roll is identified from a single roll, with no edit to engine code.
- **SC-004**: The gate and the review start within one minute of each other for the same content, so the
  review is no longer the last thing to finish.
- **SC-005**: Neither the gate nor a settlement-review can be run alone, for content whose ink changed,
  without an override that leaves a reason behind.
- **SC-006**: A repeat of a T55-shaped fix takes at most two thirds of its 79.8 minutes, with the map-roll
  count down from 19 to 5 or fewer.

## Assumptions

- The probe covers the POLDER archetypes. The comb field has its own diagnostics (`crop_map`,
  `site_justice`, `why_placed`) and is out of scope; the probe's shape should not preclude a comb sibling.
- "Freshly green" means the project's existing verified-tree record for the same engine content - the same
  key the gate already uses to short-circuit itself.
- The pairing governs Mode B settlement maps and the `settlement-review` agent. Mode A plans and
  `building-review` are out of scope for this feature.
- The override follows the project's existing convention: a token in the command plus a stated reason,
  logged for the audit - the same shape as `GATE_OK`, `DISCARD_OK` and `MEASURE_OK`.
- The audit reads a map that already exists; producing one is the roll's job, not the audit's.
- No map's drawn output changes as a result of this feature: it adds diagnostics and guards only.
