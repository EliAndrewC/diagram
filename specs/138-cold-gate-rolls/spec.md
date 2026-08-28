# Feature Specification: The Cold Gate - Faster Rolls, and a Cache Warmed While Idle

**Feature Branch**: none (`SPECIFY_FEATURE=138-cold-gate-rolls`)

**Created**: 2026-08-28

**Status**: APPROVED by `spec-fidelity` - round 1 verdict **FAITHFUL** (2026-08-28). Reviewer asides for the GM: "next inactive gate" read as INTERACTIVE; the 25% / 50% bars are the spec's own numbers; "the cash" read as every cache the gate reads. Implementation may begin.

**Input**: [`gm-request.md`](gm-request.md), verbatim. That file is the authority for this specification.

## The feature, in one sentence

The cold gate - the run in which every cached hamlet roll has to be re-made because engine code they
execute changed - gets faster in both of the ways the GM named: **the rolls themselves get faster**, by
removing the brute-force inner loops the profile found in the lane router and the connector, with every
map byte-identical to what it drew before; and **the cache is warmed while the session is idle after a
sync**, through the idle-tests hook feature 136 landed, so the next interactive gate is warm.

## Why this exists (the GM's words)

- *"speeding up the cold cash runs is our next feature"*
- *"Having the idle tests hook the other session just landed. warm the cash after a sink so that the next
  inactive gate is warm does seem like a really good idea. So I think we should do that. That can be part
  of our next feature."*
- *"one hundred seconds is so long ... are you doing some kind of NP complete problem? ... help me
  understand what's going on here"* - answered by a profile: not NP-hard; a lane router whose clearance
  test walks every fabric segment for every lattice cell (36 million segment-distance calls on one polder),
  and a connector check that compares every pair of water crossings (170 million distance calls).

## User Scenarios & Testing

### User Story 1 - a hamlet rolls in a fraction of the time, drawing the same map (Priority: P1)

A session edits hamletgen and runs the gate. Every hamlet roll re-makes itself, as it must - but the
polder that took ~100 s takes a fraction of that, and every map is **byte-identical** to the map the
previous engine drew for the same spec.

**Independent Test**: the manifest of every gate roll and of every live pool map, generated before and
after the change, compares equal byte for byte; the per-stage timings of the seed-19 polder before and
after are recorded.

**Acceptance Scenarios**:

1. **Given** the seed-19 polder (`stage_web` 57 s, `stage_track` 22 s at the baseline), **When** it rolls
   on the finished engine, **Then** its manifest is byte-identical and its roll time is at most a
   quarter of the baseline.
2. **Given** every live pool map and every gate roll spec, **When** regenerated on the finished engine,
   **Then** each manifest is byte-identical to the baseline's.
3. **Given** the cold gate (every cached roll re-made), **When** it runs, **Then** its wall-clock is at
   most half the baseline's 5 m 42 s.

---

### User Story 2 - the cache is warm when the GM comes back (Priority: P1)

A session syncs main in and the merge changed engine code the rolls execute. The session goes idle. The
idle-tests hook runs the gate unattended; when the GM returns and runs the gate, it is warm.

**Independent Test**: after a sync that moved the rolls' keys, the idle run's log shows the gate ran and
the next interactive gate reports every roll served.

**Acceptance Scenarios**:

1. **Given** a sync-in that changed engine files the rolls execute, **When** the session goes idle,
   **Then** the idle-tests hook's next run re-rolls and stores every gate roll (it is the whole gate, so
   it does), and the following interactive gate is warm.
2. **Given** the GM's feature-136 rulings on when an idle run may start (the staggered 60-120 minute
   wait, the suspend rule, one runner at a time), **Then** this feature changes NONE of them - it only
   makes sure what the idle run does includes warming every cache the interactive gate reads.

---

### User Story 3 - the record says why (Priority: P2)

A future session reads why the polder was slow and what was done. The budget file no longer blames field
bisection; the profile, the mechanism and the fix are recorded where the code is.

**Acceptance Scenarios**:

1. **Given** `GEN_TIME_BUDGETS`'s comment, **Then** it states the measured cause (the router's clearance
   scan and the connector's pairwise crossing check) and the fixed numbers.

### Edge Cases

- A spatial index that prunes a segment the brute-force scan would have measured: the verdict changes
  and the map changes - the byte-identity sweep is what catches it; a prefilter may only drop what
  cannot foul.
- Floating-point order: summing or comparing distances in a different order can move a tie; the
  byte-identity sweep is the arbiter, and a change that moves any manifest is not an optimization.
- The idle run and the cache: two runners never overlap (feature 136 D-rulings); the roll cache's writes
  are atomic (feature 135), so an interrupted idle run leaves either a whole entry or none.

## Requirements

### Functional Requirements

- **FR-001**: The feature MUST record a per-stage BASELINE of the seed-19 polder and of the reference
  hamlet on unmodified code, and the cold gate's wall clock, before any change.
- **FR-002**: The lane router's clearance test MUST NOT measure every fabric segment for every lattice
  cell; it MUST consult a spatial index built once per routing call, and every index lookup MUST return a
  superset of the segments the brute-force scan would have found within the margin.
- **FR-003**: The connector's water-crossing check MUST NOT compare every pair of crossings; it MUST
  find the same pairs within the deck length by a sweep over ordered crossings.
- **FR-004**: Every map MUST be byte-identical after the change: every live pool map's manifest and every
  gate roll's manifest, regenerated with the cache bypassed, MUST equal the baseline's.
- **FR-005**: The cold gate MUST take at most half its baseline wall clock; the seed-19 polder at most a
  quarter of its baseline roll time.
- **FR-006**: The performance bookends (`make perf`) MUST be taken before and after (constitution VI);
  no seed may be slower.
- **FR-007**: The idle-tests run (feature 136's `make idle-tests`) MUST warm every cache the interactive
  gate reads - the roll cache, the reference, the corpus verdicts - and MUST change none of feature 136's
  rulings on when it starts.
- **FR-008**: `GEN_TIME_BUDGETS` and the performance doctrine MUST record the measured cause and the
  fixed figures; the wrong "field bisection" explanation MUST be corrected (constitution XII's
  record-the-why).
- **FR-009**: Any defect found on the way MUST be fixed in this work (constitution XIV).
- **FR-010**: The feature closes when the numbers in FR-005 are met and recorded; the GM's word is
  sought only for a change that would move a map (none is expected).

### Key Entities

- **Fabric index**: a grid over the routing box holding, per cell, the obstacle/tight/line segments whose
  bounds reach that cell; a lookup for a sample point returns the candidates for that point's cell.
- **Crossing sweep**: water crossings along a candidate way, sorted, compared only within the deck length.

## Success Criteria

- **SC-001**: seed-19 polder roll: at most 25% of its baseline (110 s).
- **SC-002**: cold gate: at most 50% of its baseline (5 m 42 s).
- **SC-003**: zero manifests differ across the pool and the gate rolls.
- **SC-004**: `make perf-report` after: no seed slower than at `138-start`.
- **SC-005**: after a sync that moves the rolls' keys and an idle run, the next interactive gate reports
  every roll served.

## Assumptions

- The idle-tests hook already runs the whole gate (`make idle-tests` = `make done`), which stores every
  gate roll; "warming" therefore needs no new mechanism unless measurement shows a cache the gate does
  not fill - then that cache is added to the idle run.
- Remote stays off and scope stays unlocked as the GM set them; the perf bookends run locally.
