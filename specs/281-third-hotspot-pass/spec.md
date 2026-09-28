# Feature 281 - the third hotspot pass

**Feature Branch**: none (main, in the clone `diagram-inashiro`)
**Created**: 2026-09-28
**Status**: Draft
**Request**: [`request.md`](request.md) - the GM's words verbatim: run the exercise again - measure, find what is slow,
improve it "without any loss in accuracy"; the maps may change a little "as long as the ... invariants ... hold ... things
that aren't supposed to overlap don't overlap".
**Predecessors**: 278 (the second pass; its residue table in `dev/performance.md` priced the grove and marsh levers), 276
(the first), 218 (index once, ask per candidate), 138 (the fabric index).

## Summary

The same exercise as features 276 and 278, on main as this work began (`c13a6ebe6`: both landed, 279's woodland crowns merged). The five pool hamlets roll in 32.9 s
between them (m:before-pool-roll-s). Research R1 profiled a full generation of each and traced every hot primitive to
its caller. It found:

- **Scans the index doctrine missed**: the lane clip walks every obstacle edge per sample while its sibling asks the
  fabric index; the notice board walks every way and every route per candidate; the home-bank join and the homestead
  fit walk every brook segment; the caption probe walks every lane segment; the brook-band toll reads up to 25 grid cells
  per ask.
- **Work done twice**: every fabric-index miss rebuilds the ring index of polygons already indexed; the carve computes
  each bund vertex once per plot sharing it, and walks each shared plot edge once per plot.
- **Static tests asked one at a time in Python** where 278 priced the array form: the windbreak's fill and the marsh
  scatter.

What the after-profile shows is left is written down with its levers priced (FR-011).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The pool rolls faster, and every map is still the place it was (Priority: P1)

The GM waits on hamlet rolls in every iteration. After this feature the five pool hamlets roll faster between them; a
change that asks the same questions of an index leaves its maps byte-identical, and a change that moves marks keeps every
invariant - nothing that may not overlap overlaps.

**Why this priority**: it is the whole point of the exercise.

**Independent Test**: the harness, the base worktree and the clone back to back.

**Acceptance Scenarios**:

1. **Given** the five pool hamlets, **When** they roll, **Then** their summed roll time is well under the base's.
2. **Given** an exact change, **When** the pool regenerates, **Then** the manifests it touches are byte-identical.
3. **Given** a moving change, **When** the pool regenerates, **Then** `make done` is green with every gate rule passing and
   every map keeps its households, forms and kinds.

### User Story 2 - The ways, the board and the captions ask indexes (Priority: P1)

The lane clip, the notice board's handover walk and departure count, the home-bank join, the homestead fit's stream
test, the caption probe and the router's toll each re-read static geometry per candidate.

**Why this priority**: each is the per-candidate-scan shape the doctrine names, each removal is exact, and together they
are most of the distance primitives' calls.

**Independent Test**: count each mechanism before and after; the manifests are unchanged.

**Acceptance Scenarios**:

1. **Given** the pool hamlets, **When** they roll, **Then** each named mechanism runs a fraction as often and every
   manifest is what it was.

### User Story 3 - What was computed once is not computed again (Priority: P1)

A fabric-index miss rebuilds ring indexes it already built; the carve computes a shared bund vertex, and walks a shared
plot edge, once per plot.

**Independent Test**: count ring-index builds, bund vertices and supply-bank tests before and after.

**Acceptance Scenarios**:

1. **Given** any roll, **When** the fabric index misses its memo, **Then** each polygon's ring index is reused.
2. **Given** a carve, **When** its plots are laid, **Then** each bund vertex is computed once per sector.

### User Story 4 - The windbreak stops re-asking, and the marsh asks as arrays (Priority: P2)

The windbreak's gap fill offers every unfilled gap the same candidate points round after round, asking the outline,
the hard ground, the local keep-outs and the lanes of each again; the marsh scatter tests its marks one at a time, and
278 priced its array form.

**Independent Test**: count the scalar tests before and after; the grove's clumps are the same, the marsh keeps its
density and keep-outs.

**Acceptance Scenarios**:

1. **Given** a grove fill, **When** it runs, **Then** its clumps are today's, and a gap that took no seat is not offered
   its points again.
2. **Given** a marsh, **When** it is scattered, **Then** its marks keep every keep-out and its density.

### Edge Cases

- A clip with no obstacles and no lines: returns the polyline, as now.
- A roll with no brook: the toll and the home-bank join do nothing, as now.
- A gap whose neighbors change (a clump lands between them): it is a new gap between new neighbors, offered its own points.
- A fill that stops after one round: nothing is skipped.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 The lane clip asks the fabric index.** `clip_to_clear` decides a sample with `FabricIndex.fouled` over the
  same obstacles, margin, lines and line margin - the index `clear_runs` already asks - so every clip returns what it
  returns today.
- **FR-002 A polygon's ring index is built once per roll** and shared by every fabric index that files it; a memo miss
  builds only the polygons it has not seen. A ring index is reused only for a ring with the SAME POINTS - the reuse is
  keyed on the ring's content, never on its identity, length or ends (`dev/performance.md`: such a key is "a guess about
  content") - and the store is cleared with the fabric-index memo at the start of every roll.
- **FR-003 The brook-band toll reads a grid sized to the band**, so an ask reads at most nine cells; the verdict is the
  same distance test.
- **FR-004 The notice board asks indexes**: `outermost_join` a segment index of the other ways; `routes_missed` an index
  of the routes' points, counting the routes that come within reach - the same counts.
- **FR-005 The home-bank join and the homestead fit's stream test ask a segment index of the watercourse**, the exact
  crossing and distance tests deciding as before.
- **FR-006 The caption seat probe asks an index of the lane segments**, built once per caption pass while the lanes do
  not change.
- **FR-007 The carve computes each bund vertex once per sector**, and walks each shared plot edge against the supply banks
  once. A vertex depends on its fall, its column, its column count AND the row wander, which is off while the sector's
  fall limit is probed and live after; so the vertices are remembered only once the wander is live, keyed on (fall,
  column, count), and the probe's are never reused for plots. The shared edge is walked in one direction for both plots,
  so a sample point can differ from today's in its last floating-point bits: a plot at the bank's exact threshold may
  flip, which this spec accepts as a map change under the GM's ruling, with SC-011's condition.
- **FR-008 The windbreak's gap fill does not re-ask what it already knows.** The fill offers each gap between two seated
  clumps the same candidate points in every round (5 fractions x 33 depths), and nothing it asks of them changes during the
  fill except the spacing test, whose refusals only grow as clumps land. So a gap that took no seat in a round cannot take
  one in a later round, and is not offered again; and a point's static verdict - the outline, the hard ground, the local
  keep-outs, the lanes - is remembered per point, as the outline's already is (278). The spacing test and the `near` reach
  still run for every point offered, in today's order, so the clumps are today's.
- **FR-009 The marsh scatter is vectorized** as the grass was (278, FR-008): throws and keep-out tests as array
  operations, the same density and the same keep-outs; its marks move.
- **FR-010 Every map keeps its invariants.** A change that moves a map (FR-007, FR-009) is held to SC-011; nothing that
  may not overlap overlaps.
- **FR-011 What is left is measured and written down.** `dev/performance.md` records what the after-profile shows
  remaining - per stage, where the seconds go - with each remaining lever priced.

### Key Entities

- **The harness** (`harness.py`, `counts.py`, `measure.py`): stage seconds from unprofiled rolls, mechanism counts from
  a saved profile; `measure.py before` recorded the base in the clone at `c13a6ebe6`, `measure.py after` runs a detached
  worktree of it and the clone back to back.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (spec-wide): the five pool hamlets' summed roll time is at least `1.25x` less than the base's, measured back to
  back (32.902 s at the start, m:before-pool-roll-s; research R1).
- **SC-002** (FR-001): `seg_dist` calls from the clip's test are at least `10x` fewer on Kashikawa (535389,
  m:before-kashikawa-clip-seg-dist) and Kuwabata (413895, m:before-kuwabata-clip-seg-dist).
- **SC-003** (FR-002): ring-index builds by the fabric index are at least `5x` fewer on Sawada (9098,
  m:before-sawada-ring-index-builds) and Kashikawa (7020, m:before-kashikawa-ring-index-builds).
- **SC-004** (FR-003): the toll's grid-cell lookups are at least `2x` fewer on Kashikawa (1638800,
  m:before-kashikawa-brook-band-tests) and Mizuguchi (548823, m:before-mizuguchi-brook-band-tests).
- **SC-005** (FR-004): the handover walk's `seg_dist` calls are at least `10x` fewer on Sawada (209131,
  m:before-sawada-handover-seg-dist); the departure count's distance tests at least `10x` fewer on Sawada (724209,
  m:before-sawada-routes-missed-dist) and Inashiro (631718, m:before-inashiro-routes-missed-dist).
- **SC-006** (FR-005): the home-bank join's crossing tests are at least `10x` fewer on Kashikawa (531766,
  m:before-kashikawa-home-bank-cross); the stream test's `seg_dist` calls at least `5x` fewer on Sawada (139535,
  m:before-sawada-stream-rect-seg-dist).
- **SC-007** (FR-006): the caption probe's lane `seg_dist` calls are at least `5x` fewer on Kashikawa (49321,
  m:before-kashikawa-caption-lane-seg-dist) and Inashiro (46736, m:before-inashiro-caption-lane-seg-dist).
- **SC-008** (FR-007): the carve's vertex computations are at least `2x` fewer on Sawada (28011,
  m:before-sawada-carve-edge) and Inashiro (14690, m:before-inashiro-carve-edge); its supply-bank tests at least `1.3x`
  fewer on Sawada (162275, m:before-sawada-supply-clearance).
- **SC-009** (FR-008): the grove's outline tests are at least `1.5x` fewer on Sawada (253704, m:before-sawada-grove-inside)
  and Kashikawa (209535, m:before-kashikawa-grove-inside), its hard-ground tests at least `1.5x` fewer on the same two
  (82773, m:before-sawada-grove-hard; 92000, m:before-kashikawa-grove-hard), and every pool map's clumps are today's.
- **SC-010** (FR-009): the marsh's scalar keep-out tests are at least `5x` fewer on Sawada (28861,
  m:before-sawada-marsh-sparse) and Kuwabata (27617, m:before-kuwabata-marsh-sparse), and a test holds the marsh to its
  density and keep-outs.
- **SC-011** (the pool, FR-010): FR-001 to FR-006 and FR-008 leave every manifest they touch byte-identical - shown by
  regenerating the pool with them landed and FR-007 and FR-009 not yet landed, against the pool as committed at
  `c13a6ebe6`, since the moving changes would hide them afterwards. The maps FR-007
  and FR-009 move hold feature 276's FR-006 condition in full: every live pool map regenerates, `make done` is green at the
  `100%` floor and every gate rule passes (the overlap rules among them); every pool map, the rescue-rounds scenario and the
  10- and 20-household toys seat at least as many houses as today, with no new or larger shortfall, and keep their forms
  (dispersed or nucleated, the headman's house) and house kinds; each moved map's research entry gives its houses, paddies
  and ways before and after, and a material change is a finding to fix, not a report; and `make cohort N=24` shows no
  newly failing seed.
- **SC-012** (FR-011): `dev/performance.md` holds the after-profile's remaining costs with their levers priced; every
  before- and after-figure named here is in `measurements.json`, the after-figures carrying the command that re-runs them.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The marsh's marks are thrown and tested as arrays, so every marsh's marks land in different places at the same density and under the same keep-outs | map drawing convention (no rule, density or keep-out changes; only which random places the marks take) | 278 priced it; the GM: the maps may change "as long as the ... invariants ... hold" | point of change in `settlement/land/wet.py`; research R1 |
| A plot edge shared by two plots is tested against the supply banks once, walked in one direction | map drawing convention (the same rule and threshold; a plot exactly at it may flip in the last floating-point bits) | research R1; the same ruling | point of change in `waterfields/carve.py` |

## Assumptions

- The seconds are taken back to back against the base worktree; the counts are load-independent.

## Review history

- Round 1 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - the windbreak lever aimed at the re-seat when the gap fill makes
  nearly all the tests; the bund vertex is not pure while the row wander is off; the ring-index reuse named no condition;
  the byte-identity of the exact changes could not be seen under the moving ones, and main had moved past the base.
  Addressed: FR-008 is the gap fill's (a gap that took nothing is not re-offered; static verdicts remembered per point),
  R1 keyed by caller; FR-007 remembers vertices only once the wander is live; FR-002 reuses by content; SC-011 shows the
  exact changes byte-identical before the moving ones land, against the pool at the re-taken base `c13a6ebe6`.
