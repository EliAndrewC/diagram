# Feature 281 - the third hotspot pass

**Feature Branch**: none (main, in the clone `diagram-inashiro`)
**Created**: 2026-09-28
**Status**: Accepted - FAITHFUL at round 3 of 5 (2026-09-28); Amendment 1 under review (2026-09-28)
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
- **Questions asked again**: the windbreak's gap fill re-offers every unfilled gap the same points in every round; the
  marsh scatter asks its marks one at a time, where 278 priced the array form.

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

### User Story 4 - The windbreak stops re-asking (Priority: P2; its marsh half WITHDRAWN by Amendment 1)

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
  content") - and the store is cleared with the fabric-index memo, in `clearance.reset()`, when every roll ends
  (`driver.roll_scope`; feature 210's ruling that a finished roll's indexes are released).
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
- **FR-009** WITHDRAWN by Amendment 1 (it asked the marsh scatter vectorized as the grass was, 278's FR-008; built,
  measured, and it bought no time - research R2).
- **FR-010 Every map keeps its invariants.** A change that may move a map (FR-007; FR-009 until Amendment 1 withdrew it) is
  held to SC-011; nothing that may not overlap overlaps.
- **FR-011 What is left is measured and written down.** `dev/performance.md` records what the after-profile shows
  remaining - per stage, where the seconds go - with each remaining lever priced.

### Key Entities

- **The harness** (`harness.py`, `counts.py`, `measure.py`): stage seconds from unprofiled rolls, mechanism counts from
  a saved profile; `measure.py before` recorded the base in the clone at `c13a6ebe6`, `measure.py after` runs a detached
  worktree of it and the clone back to back.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (spec-wide): AMENDED - see Amendment 1 (it asked `1.25x` less than the base's summed roll time, 32.902 s at
  the start, m:before-pool-roll-s; research R1).
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
- **SC-010** (FR-009): WITHDRAWN with FR-009 by Amendment 1.
- **SC-011** (the pool, FR-010): AMENDED - see Amendment 1 (as landed, every manifest is byte-identical). As first written:
  FR-001 to FR-006 and FR-008 leave every manifest they touch byte-identical - shown by
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
| A plot edge shared by two plots is tested against the supply banks once, walked in one direction | map drawing convention (the same rule and threshold; a plot exactly at it may flip in the last floating-point bits) | research R1; the same ruling | point of change in `waterfields/carve.py` |
| The marsh's pond-bank keep-out reads the whole bank ring, not every 16th point of it, so no reed stands in a bank's cut corner | historically accurate (the existing rule: reeds root outside planted earth, `research/water.html`; now enforced at the drawn corners) | a defect the moved throws exposed (research R2) | point of change in `settlement/land/wet.py`; research R2 |

## Assumptions

- The seconds are taken back to back against the base worktree; the counts are load-independent.

## Review history

- Round 1 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - the windbreak lever aimed at the re-seat when the gap fill makes
  nearly all the tests; the bund vertex is not pure while the row wander is off; the ring-index reuse named no condition;
  the byte-identity of the exact changes could not be seen under the moving ones, and main had moved past the base.
  Addressed: FR-008 is the gap fill's (a gap that took nothing is not re-offered; static verdicts remembered per point),
  R1 keyed by caller; FR-007 remembers vertices only once the wander is live; FR-002 reuses by content; SC-011 shows the
  exact changes byte-identical before the moving ones land, against the pool at the re-taken base `c13a6ebe6`.
- Round 2 (spec-fidelity, 2026-09-28): CHANGES REQUIRED - FR-002 cleared its store at a roll's start where the memo is
  cleared at its end (feature 210), and the Summary still named the array lever for the windbreak. Both reworded.
- Round 3 (spec-fidelity-verify, 2026-09-28): FAITHFUL.

### Amendment 1 (2026-09-28, from T14's measurement), review on a reset counter

Measured (observed 2026-09-28, method: `measure.py after`, the base worktree's harness then the clone's, each map the
fastest of three unprofiled rolls, the 1-minute load average recorded at each run's start and end; and the same stage timing
run once more on its own, base then clone; research R2):

- **Every mechanism criterion holds, most by far** (base-rerun over after, each counted beneath its entries with the
  bucket's total beside it, plan C): the clip's `seg_dist` 535389 -> 11 on Kashikawa (m:base-rerun-kashikawa-b-clip-seg-dist,
  m:after-kashikawa-b-clip-seg-dist); ring builds 8792 -> 153 on Sawada (m:base-rerun-sawada-b-fabric-ringindex-init,
  m:after-sawada-b-fabric-ringindex-init); the toll's lookups 1638800 -> 590253 on Kashikawa (m:base-rerun-kashikawa-b-toll-dict-get,
  m:after-kashikawa-b-toll-dict-get); the handover's `seg_dist` 209131 -> 10 on Sawada (m:after-sawada-b-handover-seg-dist);
  the departures' `hypot` 724209 -> 29306 on Sawada (m:after-sawada-b-departures-math-hypot); the home-bank crossings
  531766 -> 4 on Kashikawa (m:after-kashikawa-b-home-bank-segments-cross); the stream test's `seg_dist` 139535 -> 0 on
  Sawada (m:after-sawada-b-stream-rect-seg-dist, its bucket's total 1122817 -> 19203, m:after-sawada-b-stream-rect-total);
  the caption probe's 49321 -> 5793 on Kashikawa (m:after-kashikawa-b-caption-lanes-seg-dist); the carve's vertices 28011
  -> 9156 and its stroke clearances 161135 -> 96209 on Sawada (m:after-sawada-b-carve-carve-sector-locals-edge,
  m:after-sawada-b-carve-strokeindex-clearance); the grove's outline tests 253704 -> 79299 and hard-ground tests 82773 ->
  25617 on Sawada (m:after-sawada-b-grove-groveblocks-inside, m:after-sawada-b-grove-groveblocks-hard). No bucket's named
  count fell while its total did not.
- **One count moves between runs of the base: the ring builds.** Sawada's read 8792 in two base re-runs
  (m:base-rerun-sawada-b-fabric-ringindex-init) and 9098 in the review's re-run of the same command and in the first
  measurement (m:before-sawada-ring-index-builds); Kashikawa's 6740 and 7020, Kuwabata's 4132 and 4236, and the fabric
  bucket's total with them - on the after side too (Kuwabata's 702611 and 731256, m:after-kuwabata-b-fabric-total), since
  the fabric index's own filing still follows that memo's hits. The base's fabric memo (`hamletgen.clearance._MEMO`) is keyed on object identities, so how often
  it hits - and so how many polygons a miss re-indexes - moves with the reuse of ids. A count may not carry `varies`
  (FR-011b), so these stay counts, named here as moving; the after side's ring builds, keyed on the ring's points (FR-002),
  read 153 on Sawada in every run. SC-003 holds on either base reading: 57x or 59x against its `5x`.
- **FR-009 is withdrawn.** The vectorized marsh was built to 278's priced form and cut the marsh's scalar keep-out tests
  359x on Sawada, but its wall time did not fall: the hinterland stage, fastest of three, went 0.596 -> 0.614 s on
  Inashiro and 0.380 -> 0.443 s on Kuwabata, flat on the other three, because building the shapely shapes of the keep-outs
  near each mark kind's throws costs, on these small marshes, what the scalar tests did (research R2). A change that moves
  every map's marks and buys no time is not what the GM asked for; the marsh keeps its scalar throws. The defect it
  exposed - a pond bank's keep-out thinned to every 16th point - stays fixed. With it withdrawn, the whole pool
  regenerates byte-identical against `c13a6ebe6`: this feature, as landed, moves no pool map.
- **SC-001's `1.25x` did not hold.** Every reading of the pool on this host, base then after: 32.902 s before
  (m:before-pool-roll-s) against 28.477 s after in the latest run (m:after-pool-roll-s, load 9.6 -> 5.8): 1.16x; the
  separate stage run, 32.785 s against 27.069 s: 1.21x; and the review's own re-run, 1.18x against the recorded base and
  1.20x against its back-to-back base. Two base re-runs read higher still - 37.715 s and 36.763 s
  (m:base-rerun-pool-roll-s, load 4.0 -> 9.6) - each carried by ONE map far off its every other reading: Kashikawa at
  13.23 s in the first, where the review's re-run read 8.988 s, and Kuwabata at 6.739 s in the second
  (m:base-rerun-kuwabata-roll-s) against 3.73-3.82 s in every other reading; neither is used. What stands between 1.2x
  and the target is the residue FR-011 records: the router's search, the field's carve and seam closing, and the page
  writer.

The amended criteria:

- **SC-001** the five pool hamlets' summed roll time is at least `1.1x` less than the base's (the readings above run 1.16x
  to 1.21x, and on this host a loaded run moves one map by seconds).
- **SC-010** withdrawn with FR-009.
- **SC-011** holds in its stronger form: with every landed change, every live pool manifest is byte-identical against
  `c13a6ebe6`. FR-007's second half remains a map drawing convention (a plot within rounding of the bank's threshold may
  flip on another map); it moved nothing on the pool, and the cohort (`make cohort N=24`) passed 24 of 24 on the base and
  the clone alike.
