# Feature 226 - the site boundary, and the seats proposed from it

**Status**: IN PROGRESS 2026-09-12. `spec-fidelity` round 1: CHANGES REQUIRED (the boundary derived from every geometry the retired tests read, test by test; the guesses counted where the GM counted them, the cloud's throws reduced; the page struck from the record's purpose). rounds 2-4 the pads, the points and the allowance, the size bound; round 5 FAITHFUL.
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - R1 the per-house counts
before (from the profile), R2 the after. **Predecessors**: 140 (the paddy's outline as a few facing chords -
the same idea, for the paddy alone), 126 (houses before lanes), 137/150 (the placer's rules as they stand), 224
(the predicted frame - the other "compute the ground once" of this line).

## Summary

At the moment the homesteads are seated, everything the map holds is fixed and nothing that comes later is
placed without regard to the houses. So the ground a homestead may stand on is ONE thing, computed once: the
outline that separates it from everything else - derived from every geometry the fit test reads today (FR-001
names them), not listed by hand - as a few chords on the house side, with the two or three water courses that cross
the homestead ground as corridor segments beside them. A candidate bundle then asks only whether its rectangles'
corners are on the right side of those segments and clear of those corridors, whether its box overlaps a bundle
already standing, the eave gap against the nearest house, and the sun rules. And the seats are proposed FROM
that boundary rather than guessed and spiraled toward it, so few proposals fail.

## Functional requirements

- **FR-001 The site boundary is computed once, at the start of the stage, from every geometry the fit test
  read.** `stage_homesteads` builds it from the SAME sources the retired tests read - not a hand list. The AREA
  members enter the blob: the no-build polygons (`block_polys`: the hem plots the comb registers, the pond's box,
  a mosaic's ponds), the field polygons (`_field_chains`' source), the hard ground's polygons (`_hard_ground`'s
  registered hard polygons, every marsh, every dry plot), and every keep-out ellipse (`self.ellipses`, the pond
  AND a crescent pond's half-disk) as a 24-gon. Each enters at the pad its test holds it to today, which is zero
  for all of them, and the hard ground's members are grown first by the allowance `_hard_clear` applies - it
  inflates the rectangle to the swept extent of the farmhouse's +/-5 degree tilt before testing, which on the
  house footprint is 2 px on the long side (46 ft x sin 5 deg, halved) - so the blob refuses what `_hard_clear`
  refused within a pixel for every rectangle. The union is simplified and reduced to the chains of its outline
  that face the cluster's seat - feature 140's `facing_chains` on the whole blob, each chord pushed out by its own
  `FIELD_KEEPOUT_EPS` as the paddy's chains are today. The LINE members stay lines, as two corridor sets each
  with the points and clearance its test applies today: the water obstacles (`_water_obstacles`: the channels,
  the field ditches, the streams) at their half-width plus 5, tested at the rectangle's corners and center as
  `_rect_on_water` does; the registered corridors (`self.corridors`, whatever registered them) at their registered
  clearance, tested at the rectangle's CENTER only as `_near_corridor` does - a footprint test of that clearance
  was tried and reverted (Nagahara's well, Hoshizora's punishment ground; `_house_on_a_tread`'s docstring) and is
  not retried here. The field ditches' quads that `_hard_ground` also builds do NOT enter the blob: they are the
  same lines the water obstacles hold at a wider clearance, and a line in the blob would make a finger whose
  facing chord refuses the ground behind it. A corridor segment lying wholly inside the blob is dropped. Both sets
  are set on the settlement (`_site_chains`, `_site_corridors`) and recorded in the manifest (`site_boundary`) for
  the gate's checks and FR-005's measurement only - no page element, hit region or modal text. **The boundary is
  a relatively small number of line segments** - the GM's own measure of the trade: ten to thirty chords and a few
  dozen corridor segments are expected per hamlet, and R2 reports the counts per pool map (FR-005).
- **FR-002 The hamlet's fit test reads the boundary and nothing else about the ground - test by test, with the
  points each tests and any inflation it applies.** When the boundary is set, the fit path (`_fits_any_side` ->
  `_bundle_common_fits` / `_bundle_side_fits`) is, for every test it makes today:
  - `_rect_blocked` -> `_rect_hits(block_polys)` (the rect's corners, vertices and edge crossings against each
    polygon, pad 0): ABSORBED - the polygons are in the blob; the rect is asked at its four corners, four edge
    midpoints and center (nine points), so a member narrower than half a rectangle's side cannot pass between
    two corners unseen;
  - `_rect_blocked` -> `_field_blocks_rect` (corners and center against the paddy's chains, gap 0): ABSORBED -
    the field polygons are in the blob, the same test over the whole outline;
  - `_rect_blocked` -> `_rect_on_water` (corners and center by segment distance at half-width + 5, and edge
    crossings): ABSORBED into the water corridor set at the same points and clearance;
  - `_rect_blocked` -> `_hard_clear` (the rect inflated by the +/-5 degree tilt, then overlap at pad 0): ABSORBED -
    the hard ground's polygons are in the blob grown by that allowance; its ditch quads are the water corridors;
  - `_rect_blocked` -> the `self.ellipses` loop (corners and center inside the ellipse): ABSORBED - the ellipses
    are in the blob as polygons;
  - `_rect_blocked` -> `_near_corridor` (the CENTER against each registered corridor's clearance): ABSORBED into
    the registered-corridor set, center only;
  - `_wall_on_the_bund` (the HOUSE's rotated corners at `HOUSE_PADDY_GAP_FT + 1.0` against the paddy's chains):
    KEPT as written - a wall rule with its own research, the house alone; four chord tests per candidate;
  - `_house_on_a_tread`: KEPT (no tread exists at this stage on a hamlet; it costs nothing);
  - `_house_too_near_a_neighbor`: KEPT (the eave gap against the houses within reach);
  - `_sun_corridor_ok`, `_gardens_sun_ok`, `_yard_sun_conflict`: KEPT (between homesteads, not ground);
  - `_bundle_side_fits`' canvas bounds and the `self.bound` ring: KEPT;
  - `_bundle_side_fits`' placed-box overlap: KEPT.
  No rule about where a house, a yard, a garden or a grove may lie moves in this feature; what changes is how
  the ground is asked. A settlement without a boundary (every other tier, a hand call) runs the path as it is.
- **FR-003 Seats are proposed from the boundary and the band on the bundle pitch, every candidate is counted,
  and the spiral is bounded.** The GM's number - 157 proposals for 16 houses - is the count of CANDIDATE
  POSITIONS the stage tried, and that is what is measured and bounded here: `meta.seat_search` records every
  candidate position the stage tests (a front-row seat, a cloud seat, and every spiral offset the placer tries),
  the pre-test refusals included, beside the placer calls, the positions the fit test saw and the rectangles it
  judged. Then three changes to how the guesses are made. The front row's seats are offset from the site chains
  (the house side of the whole blob) at the bundle pitch and the standoff ladder, ordered center-out, wrapped
  per the cluster shape - as now, but from a boundary that already excludes the hem, the marsh and the pond.
  The ranks behind come from the rolled band at the bundle pitch - a lattice over the band the cluster shape
  describes, jittered from the map's seed so two maps still differ, ordered center-out - instead of
  `households * 6 + 30` random seeds per round for four rounds; the rounds still widen the band only while the
  quota is short. Every candidate is pre-tested before the placer is asked - its center on the house side of the
  chains and clear of the corridors, a house-sized box clear of the placed boxes - and the placer's spiral is
  bounded to three rings (37 offsets), because a seat that needs more than 15 px of adjustment was a wrong guess.
- **FR-004 The invariants are what verify it.** The gate's placement tests (`households_consistent`,
  `field_ringed`, the eave gap, the sun corridors, `no_structure_overlaps`, the cluster-shape aspects, the
  bund and ditch clearances) judge every rolled map; a 48-map cohort is run; a settlement-review of the five
  pool maps judges the layouts, since every map will change.
- **FR-005 Measured before and after.** Per pool hamlet: the stage time; candidates, placer calls, positions
  and rectangles per house (R1's table against R2's); and the size of the boundary the fit test was asked
  against - the chords and the corridor segments - as the GM's own measure of the trade.

## Success criteria

- SC-1 `stage_homesteads` under 0.25 s on every pool hamlet (1.0 / 1.3 / 2.3 / 0.8 / 1.0 after 225).
- SC-2 Candidate positions tested per house (`meta.seat_search`, the pre-test refusals and the spiral's offsets
  included) under 12 on every hamlet - against R1's 419 / 1,686 / 363 positions the fit test saw per house - and
  placer calls per house under 2 (3 / 10 / 2 before).
- SC-3 Every pool map seats its declared households within the gate's band; the 48-map cohort passes; no
  farmhouse stands off the connected way network on the pool.

## Decisions Recorded

- **D1 One blob, a few chords - and the water as corridors.** A closed boundary cannot separate the houses
  from a line that crosses their ground; the stream and the feeder are two or three polylines and are tested
  by distance from each corner. Carving them into the boundary as slots was the alternative and buys nothing
  the corridor test does not.
- **D2 No pad moves, no point set moves, no allowance is dropped.** The first draft grew one blob by the house's
  set-back and tested every rectangle at gap 0 (a rule change for the yard, the gardens and the grove); the
  second tested the registered corridors at the corners (a reverted experiment) and dropped `_hard_clear`'s tilt
  allowance. Both caught by the spec review. Each member enters the blob at its own pad, the hard ground grown
  by the tilt allowance, each corridor set keeps its own points and clearance, the rectangle is asked at nine
  points so nothing thinner than half a side slips between corners, and the house's wall rule stays its own test.
  The boundary changes how the ground is asked, not what it answers - to within the pixel the fixed tilt
  allowance differs from the per-rectangle inflation it replaces.
- **D3 The band stays as the shape, the random seeds do not.** The rolled cluster shapes (crescent, round,
  elongated) are read from where the back ranks land, and the band they describe is kept as the ground those
  ranks are proposed over - but as a lattice at the bundle pitch, jittered from the seed, not `households * 6 +
  30` random throws per round. The spiral was compensating for wrong guesses, and three rings is the adjustment
  a right guess needs. The candidates per house this leaves is a measured number (R2), not a claim.
- **D4 Maps move.** The GM's words: *"I am completely okay with the layout of these things changing somewhat
  ... as long as the actual invariants are maintained."* The gate's tests and the review are the invariants.
- **D5 The other tiers keep their tests.** The town's nucleated placement and the city's house-first path
  do not build a site boundary in this feature; the old battery stays for them, unchanged.

## Review history

- Round 1 (2026-09-12): CHANGES REQUIRED. (1) FR-001 hand-listed the blob's members and FR-002 retired tests whose
  geometry the list missed - `self.ellipses` (a crescent pond's half-disk), every registered corridor, the `bound`
  ring; now the blob is derived from every geometry the retired tests read and FR-002 accounts for every test of
  the path, absorbed or kept. (2) FR-003 pre-tested seats BEFORE the counter the GM's 157 was read from, so SC-2
  could be met by moving the counter; now every candidate position is counted, the cloud's `households * 6 + 30`
  throws become a pitch lattice over the band, SC-2 bounds the counted number. (3) The page struck from the
  manifest record's purpose. The corridors (D1) and the tiers (D5) FAITHFUL. Two stale comments to correct under
  Principle XIV (`consts.py` "the cloud never runs"; `fit.py` "drawn BEFORE the houses").
- Round 2 (2026-09-12): the three items resolved; CHANGES REQUIRED on new text - D2 had baked the HOUSE's set-back
  into one blob and tested every rectangle at gap 0, a rule change for the yard, the gardens and the grove; now each
  member enters at the pad its test applies (zero), each corridor keeps its clearance, `_wall_on_the_bund` is KEPT as
  the house's own rule. The Summary's hand list replaced by the derivation. Applied.
- Round 3 (2026-09-12): the pad item resolved; CHANGES REQUIRED on two members of the same family - the registered
  corridors had moved from center-only to corners (a reverted experiment), and `_hard_clear`'s tilt allowance was
  dropped. Closed as a class: FR-002 now pins the POINTS and INFLATION of every test beside its pad; the corridors
  are two sets (water at corners and center, registered at the center); the hard ground is grown by the allowance;
  the ditch quads stay out of the blob (a finger's far chord would refuse the ground behind it); nine points per rect.
- Round 4 (2026-09-12): the class closed; CHANGES REQUIRED on one clause lost in the rewrite - the stated bound on the
  boundary's size ("a relatively small number of line segments", the GM's own measure); restored in FR-001 and
  reported by FR-005. Aside taken under Principle XIV: `_hard_clear` inflated `h` from the already-swept `w`.
- Round 5 (2026-09-12): FAITHFUL. The aside kept: the `_hard_clear` sweep fix can move a map on its own (one axis was over-inflated) - accounted in R2 beside the boundary.
