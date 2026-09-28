# Feature 278 - the second hotspot pass

**Feature Branch**: none (main, in the clone `diagram-inashiro`)
**Created**: 2026-09-28
**Status**: Draft
**Request**: [`request.md`](request.md) - the GM's words verbatim: run feature 276's exercise again - measure, find, make faster.
**Predecessors**: 276 (the first pass: placement indexes, batched seam closing, the track's `PathChecker`, the shared
test parses; `dev/performance.md` "Three more shapes"), 218 (the index-once doctrine), 138 (the router's one index per
box).

## Summary

The same exercise as feature 276, on the code as it stands after 276 and 261 landed (main `ac01ffe2d`). The measurement
(research R1) rolled every pool hamlet with each stage timed and every mechanism counted, profiled a full regeneration
with rendering, and timed the whole test suite. It found three kinds of cost:

- **Per-candidate scans that an index or a hoist removes exactly** - the router evaluating its whole search box before
  searching, a doorstep search rebuilding one index's key per candidate, the footbridge widening testing every water
  segment per deck, and the hamlet's well placer re-sorting its whole pool on every iteration. These change no map.
- **A roll done twice** - Sawada strands a farmhouse on its first attempt every time, so every Sawada roll is two.
- **Tooling** - `make map` rolls the reference hamlet twice, a test fails in every clone after a sync-in because a
  gitignored page it reads is re-plated only at landing, and one of feature 276's own equality tests costs 4.6 s of
  `make quick` (observed 2026-09-28, method: `make durations`).

And a fourth, which this feature measures and records rather than changes: the remaining costs are the algorithms'
own densities (the comb carve's per-row geometry, the windbreak's candidate clumps, the commons scatter, the notice
board's verge probes), each already indexed - the point the GM anticipated where "we've optimized as much as can be
expected" begins to show.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The ways are routed without evaluating ground the search never reaches (Priority: P1)

The lane router marks every cell of its search box free or fouled, and in or out of the brook's band, before Dijkstra
starts - up to 90,000 cells, most of which the search never reaches. On Kashikawa and Sawada this is the largest single
cost of the ways stage.

**Why this priority**: the largest shared engine cost the measurement found, on every map with lanes.

**Independent Test**: count the router's cell tests on Kashikawa and Sawada before and after; route the same
start/goal pairs through the old and new router and compare the paths.

**Acceptance Scenarios**:

1. **Given** any start, goal and ground, **When** the router runs, **Then** it returns exactly the path the eager router
   returned.
2. **Given** the pool hamlets, **When** they roll, **Then** the router tests far fewer cells.

### User Story 2 - Three placers stop re-deriving what does not change (Priority: P1)

A doorstep search asks for the same fabric index once per candidate standing-place (and builds its memo key each
time); the footbridge widening tests every segment of every other watercourse for every deck candidate; the hamlet's
well placer re-sorts its whole candidate pool, with a key that sorts every house's distance, on every iteration -
including the iterations that placed nothing.

**Why this priority**: each is the per-candidate-scan shape the doctrine names, and each removal is exact.

**Independent Test**: count each mechanism on the pool hamlets before and after; the pool manifests are unchanged.

**Acceptance Scenarios**:

1. **Given** the pool hamlets, **When** they roll, **Then** each named mechanism runs a fraction as often and every
   manifest is what it was.

### User Story 3 - Sawada is rolled once (Priority: P2)

Sawada's first attempt strands a farmhouse every time, so the driver re-rolls it; each Sawada roll is two builds.

**Why this priority**: it doubles the most expensive pool hamlet, and a stranded farmhouse is itself a defect in
whichever pass should have reached it.

**Independent Test**: roll Sawada and count its builds.

**Acceptance Scenarios**:

1. **Given** Sawada's spec, **When** it rolls, **Then** it is built once, seats all 19 households, and every farmhouse
   reaches a way.

### User Story 4 - The tooling stops paying for work nobody asked for (Priority: P2)

`make map` on the reference hamlet rolls it once for the gate's check and again to draw the render; a clone fails
`test_every_clickable_class_is_named_somewhere_on_the_committed_page` after any sync-in that brings a new class, until
someone re-plates a gitignored page by hand; and the `md_tokens` equality test costs 4.6 s of `make quick`.

**Why this priority**: seconds on every iteration, and a false red on every sync-in that adds a class.

**Independent Test**: time and count each.

**Acceptance Scenarios**:

1. **Given** the reference hamlet, **When** `make map` runs on it, **Then** it is rolled once.
2. **Given** a clone synced in after a class was added, **When** `make quick` runs, **Then** the placement-stages page
   test is not red for a page the landing re-plates.
3. **Given** the quick tree, **When** it runs, **Then** the `md_tokens` equality test proves the same equality in a
   fraction of the time.

### Edge Cases

- A route with no path: the lazy router explores every reachable cell, as the eager one did, and returns [].
- A deck whose box meets no other watercourse: the widening returns the span unchanged, as before.
- A well pool iteration that places nothing: the order it leaves is the order the next iteration reads.
- The placement-stages page absent in a fresh clone: the test's existing skip.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 The router evaluates only the cells its search reaches.** A cell's free/fouled state and its brook-band
  membership are computed the first time Dijkstra touches the cell, and the returned path is exactly the eager
  router's.
- **FR-002 The doorstep search builds its index once per search.** The fabric index a straggler's doorstep candidates
  are tested against is obtained once for the candidates of one house, not once per candidate.
- **FR-003 The footbridge widening asks an index of the other watercourses' segments.** Built once per footbridge
  pass, asked with the deck's box widened by the test's own reach, the exact test deciding as before.
- **FR-004 The hamlet's well placer re-sorts only when a well lands.** The parts of the sort key that do not depend
  on the wells already placed are computed once per candidate; the pool is re-sorted only after a well is placed.
- **FR-005 Sawada seats every farmhouse on its first roll.** The pass that leaves a farmhouse unreached on Sawada's
  first attempt is found and fixed where it is (constitution XIV), under the rules the engine already holds.
- **FR-006 `make map` rolls a map once.** The reference hamlet's gate check and its render come from one roll.
- **FR-007 The placement-stages page a test reads is current in a synced clone.** The tooling that brings a new class
  into a clone re-plates the page, or the test reads what the clone can derive - never a red that only a landing clears.
- **FR-008 The `md_tokens` equality test keeps its corpus and loses its cost.** Every tracked text is still checked.
- **FR-009 The pool does not move except where FR-005 moves it.** FR-001 to FR-004 and FR-006 to FR-008 change no
  manifest; FR-005 changes Sawada's alone, every gate rule holding.
- **FR-010 What is left is measured and written down.** `dev/performance.md` records the costs this pass measured and
  did not change - the field carve, the windbreak's candidates, the commons scatter, the notice board's probes - with
  their counts and why each is the algorithm's density rather than a scan.

### Key Entities

- **The harness** (`harness.py`): per pool hamlet, stage seconds from unprofiled rolls and mechanism counts from a
  profiled one; before-figures from a detached worktree of `ac01ffe2d`, after-figures from the clone, back to back.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001): the router's cell tests (fouled plus brook-band) are at least `2x` fewer on Kashikawa (358398 and
  174118, m:before-kashikawa-cell-fouled, m:before-kashikawa-brook-band) and on Sawada (1013133 and 460131,
  m:before-sawada-cell-fouled, m:before-sawada-brook-band), and an equality test over recorded route requests returns
  the eager router's paths.
- **SC-002** (FR-002): fabric-index requests on Sawada are at least `3x` fewer than 7071 (m:before-sawada-fabric-index-calls).
- **SC-003** (FR-003): `quad_hits_seg` calls on Inashiro are at least `10x` fewer than 63674
  (m:before-inashiro-quad-hits-seg).
- **SC-004** (FR-004): Kuwabata's appurtenance stage is at least `3x` faster back to back against the base worktree.
- **SC-005** (FR-005): Sawada is built once (2 builds before, m:before-sawada-builds), seating all 19 households.
- **SC-006** (FR-006, FR-007, FR-008): `make map` on the reference rolls it once; a synced clone's `make quick` is not
  red on the placement-stages page; the `md_tokens` equality test takes under `1 s`.
- **SC-007** (FR-009): the four pool manifests other than Sawada's are byte-identical before and after; Sawada passes
  every gate rule and seats its 19 households.
- **SC-008** (FR-010): `dev/performance.md` holds the measured residue; every before- and after-figure named here is in
  `measurements.json`, the after-figures with the command that re-runs them.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

FR-001 to FR-004 and FR-006 to FR-008 change nothing a map draws. FR-005 changes Sawada: the class of that change is
recorded here when its cause is known (the plan), before the fix lands.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The windbreak's clumps, the commons scatter, the comb carve and the notice board's probes are measured and left as they are | map drawing convention (their cost is their sampling density, which is what they draw) | each is already indexed (218, 276); fewer samples is a different drawing, and 218's research R2 already holds those levers for the GM | `dev/performance.md`; research R1 |

## Assumptions

- The seconds are taken back to back against a detached worktree of the base at a low load; the counts are
  load-independent and are the primary targets.
- Sawada's re-roll comes from a defect in a pass rather than from a hamlet whose ground genuinely cannot serve a house;
  if the plan finds the latter, the spec is amended with the measurement.

## Review history
