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
names them), not listed by hand - in TWO forms asked two ways: the paddy's outline as a few facing chords asked by
SIDE, and everything else as one union outline with its holes asked by CONTAINMENT, with the two or three water
courses that cross the homestead ground as corridor segments beside them. A candidate bundle then asks only whether
its rectangles' nine points are on the house side of the chords and outside the outline and clear of those
corridors, whether its box overlaps a bundle already standing, the eave gap against the nearest house, and the sun
rules. And the seats are proposed FROM
that boundary rather than guessed and spiraled toward it, so few proposals fail.

## Functional requirements

- **FR-001 The site boundary is computed once, at the start of the stage, from every geometry the fit test
  read.** `stage_homesteads` builds it from the SAME sources the retired tests read - not a hand list. The AREA
  members enter the blob: the no-build polygons (`block_polys`: the hem plots the comb registers, the pond's box,
  a mosaic's ponds), the field polygons (`_field_chains`' source), the hard ground's polygons (`_hard_ground`'s
  registered hard polygons, every marsh, every dry plot - and the reed-marsh TOE that `hinterland()` will draw after the houses, asked of `toe_band()` as the ways ask it because `wet_polys` does not hold it at seat time, and registered ONCE among `hard_polys` at seat time so that the boundary and every placer after this stage that asks `_hard_clear` - the byres, the sheds, the wells - refuse it alike), and every keep-out ellipse (`self.ellipses`, the pond
  AND a crescent pond's half-disk) as a 24-gon. Each enters at the pad its test holds it to today, which is zero
  for all of them, and the hard ground's members are grown first by the allowance `_hard_clear` applies - it
  inflates the rectangle to the swept extent of the farmhouse's +/-5 degree tilt before testing, which on the
  house footprint is 2 px on the long side (46 ft x sin 5 deg, halved) - so the blob refuses what `_hard_clear`
  refused within a pixel for every rectangle. TWO OUTLINES, asked two ways: the FIELD polygons alone become feature
  140's `facing_chains` facing the cluster's seat, each chord pushed out by its own `FIELD_KEEPOUT_EPS`, asked by
  SIDE as `_field_blocks_rect` asks today; every other area member is unioned into ONE outline with its holes and
  asked by CONTAINMENT - a point inside an exterior ring and inside none of its holes, or a ring vertex inside the
  rectangle - as `_rect_hits`, `_hard_clear` and the ellipses loop ask today. Reducing the WHOLE blob to facing
  chains was the first cut and is refused: a dike mosaic's far chords refused the ground between its ponds, and
  Kuwabata seated 11 of 16 households. The LINE members stay lines, as two corridor sets each
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
  a relatively small number of line segments** - the GM's own measure of the trade - in the part that IS segments:
  ten to thirty chords and a few dozen corridor segments are expected per hamlet (7-10 and 13-22 measured, R2); the
  union is one to three rings of a few hundred vertices, asked by containment through a `RingIndex` rather than
  as segments, and R2 reports all of it per pool map (FR-005).
- **FR-002 The hamlet's fit test reads the boundary and nothing else about the ground - test by test, with the
  points each tests and any inflation it applies.** When the boundary is set, the fit path (`_fits_any_side` ->
  `_bundle_common_fits` / `_bundle_side_fits`) is, for every test it makes today:
  - `_rect_blocked` -> `_rect_hits(block_polys)` (the rect's corners, vertices and edge crossings against each
    polygon, pad 0): ABSORBED - the polygons are in the containment outline (FR-001); the rect is asked at its four
    corners, four edge midpoints and center (nine points), so a member narrower than half a rectangle's side cannot
    pass between two corners unseen;
  - `_rect_blocked` -> `_field_blocks_rect` (corners and center against the paddy's chains, gap 0): ABSORBED into
    the site CHAINS - the same facing chains over the paddy's outline, asked by side at nine points;
  - `_rect_blocked` -> `_rect_on_water` (corners and center by segment distance at half-width + 5, and edge
    crossings): ABSORBED into the water corridor set at the same points and clearance;
  - `_rect_blocked` -> `_hard_clear` (the rect inflated by the +/-5 degree tilt, then overlap at pad 0): ABSORBED -
    the hard ground's polygons are in the containment outline grown by that allowance; its ditch quads are the
    water corridors;
  - `_rect_blocked` -> the `self.ellipses` loop (corners and center inside the ellipse): ABSORBED - the ellipses
    are in the containment outline as polygons;
  - `_rect_blocked` -> `_near_corridor` (the CENTER against each registered corridor's clearance): ABSORBED into
    the registered-corridor set, center only;
  - `_wall_on_the_bund` (the HOUSE's rotated corners at `HOUSE_PADDY_GAP_FT + 1.0` against the paddy's chains):
    KEPT as written - a wall rule with its own research, the house alone; four chord tests per candidate;
  - `_house_on_a_tread`: KEPT (no tread exists at this stage on a hamlet; it costs nothing);
  - `_house_too_near_a_neighbor`: KEPT (the eave gap against the houses within reach);
  - `_sun_corridor_ok`, `_gardens_sun_ok`, `_yard_sun_conflict`: KEPT (between homesteads, not ground);
  - `_bundle_side_fits`' canvas bounds and the `self.bound` ring: KEPT;
  - `_bundle_side_fits`' placed-box overlap: KEPT.
  ONE rule about where a structure may lie moves in this feature, and only one: the reed-marsh toe, which no placer
  tested before it and which the houses, yards, gardens, groves, byres, sheds and wells all refuse now (D7, a
  Principle XIV overlap fix). Every other rule stands; what changes is how the ground is asked. A settlement without a boundary (every other tier, a hand call) runs the path as it is.
- **FR-003 Seats are proposed from the boundary and the band on the bundle pitch, every candidate is counted,
  and the spiral is bounded.** The GM's number - 157 proposals for 16 houses - is the count of CANDIDATE
  POSITIONS the stage tried, and that is what is measured and bounded here: `meta.seat_search` records every
  candidate position the stage tests (a front-row seat, a cloud seat, and every spiral offset the placer tries),
  the pre-test refusals included, beside the placer calls, the positions the fit test saw and the rectangles it
  judged. Then three changes to how the guesses are made. The front row's seats are offset from the site CHAINS - the
  paddy's facing chains - at the bundle pitch and the standoff ladder, ordered center-out, wrapped per the cluster
  shape, as now; the hem, the marsh and the pond are excluded at the PRE-TEST below, not by the chains.
  The ranks behind come from the rolled band at the bundle pitch - a lattice over the band the cluster shape
  describes, jittered from the map's seed so two maps still differ, ordered center-out - instead of
  `households * 6 + 30` random seeds per round for four rounds; the rounds still widen the band only while the
  quota is short. Every candidate is pre-tested before the placer is asked - a smallest-house-sized box asked at nine points
  against the chains and the containment outline and at its center against the registered corridors
  (`_site_blocks_rect`), and clear of the placed boxes - and the placer's spiral is
  bounded to six rings (30 px), with the old fifteen-ring spiral run in RESCUE rounds only while the quota is still
  short after the lattice's four rounds - three of them, each over a wider band, the lattice held against the standing
  houses only (a rescue spends guesses on purpose). There is no pool conditional: MEASURED, no pool hamlet reaches the
  rescue rounds (`meta.seat_search.rounds` per map, R2), one cohort seed of 48 does - seed 25, which seats 14 of 20
  without them once the reed-marsh toe is in the boundary - and a toy hamlet's tenth household needed the long slide. A re-roll after a stranded farmhouse draws its lattice at a new phase (the draw salted by the count of
  forbidden seats), so the retry seats elsewhere as the random cloud's retries did by themselves.
- **FR-004 The invariants are what verify it.** The gate's placement tests (`households_consistent`,
  `field_ringed`, the eave gap, the sun corridors, `no_structure_overlaps`, the cluster-shape aspects, the
  bund and ditch clearances) judge every rolled map; a 48-map cohort is run; a settlement-review of the five
  pool maps judges the layouts, since every map will change.
- **FR-005 Measured before and after.** Per pool hamlet: the stage time; candidates, placer calls, positions
  and rectangles per house (R1's table against R2's); and the size of the boundary the fit test was asked
  against, in the terms the manifest's `site_boundary` keeps - the chords, the water segments, the registered-corridor
  segments, and the rings and holes with their vertex counts - as the GM's own measure of the trade.

## Success criteria

- SC-1 `stage_homesteads` under 0.25 s on every pool hamlet (1.0 / 1.3 / 2.3 / 0.8 / 1.0 after 225).
- SC-2 Candidate positions tested per house (`meta.seat_search`, the pre-test refusals and the spiral's offsets
  included) under 12 on every POOL hamlet, quota met without a rescue round - against R1's 419 / 1,686 / 363
  positions the fit test saw per house - and placer calls per house under 2 (3 / 10 / 2 before). The quota-short
  case carries its own measured number, not a bound: cohort seed 25 - the one seed of 48 that reaches the rescue
  rounds - seats 20 of 20 at 13.4 candidates and 98 positions per house over six rounds (R2), against 12.4
  candidates and 1,566 positions on the same seed under the old cloud; `meta.seat_search.rounds` records how many
  rounds a roll needed, so a map that reached the rescue is never silent.
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
  allowance differs from the per-rectangle inflation it replaces - with the one exception recorded in D7.
- **D3 The band stays as the shape, the random seeds do not.** The rolled cluster shapes (crescent, round,
  elongated) are read from where the back ranks land, and the band they describe is kept as the ground those
  ranks are proposed over - but as a lattice at the bundle pitch, jittered from the seed, not `households * 6 +
  30` random throws per round. The spiral was compensating for wrong guesses; six rings is the adjustment a right
  guess needs, and the fifteen-ring rescue round exists for the quota, never for a guess. The candidates per house this leaves is a measured number (R2), not a claim.
- **D4 Maps move.** The GM's words: *"I am completely okay with the layout of these things changing somewhat
  ... as long as the actual invariants are maintained."* The gate's tests and the review are the invariants.
- **D5 The other tiers keep their tests.** The town's nucleated placement and the city's house-first path
  do not build a site boundary in this feature; the old battery stays for them, unchanged.
- **D6 Two defects fixed where the work found them (Principle XIV).** `_hard_clear`'s swept extent read the
  already-widened width when it added the height's share, so its allowance was a few tenths of a pixel too large -
  corrected; this alone can move a map. And the settlement-review measured the belt's southern sun strip at 22 px
  against the 39 ft a farmhouse owes the same bed and the 50 ft the belt keeps to the west: the strip now follows the
  generator's declared `sun_corridor` depth (`homestead_parts/stands.py`), 22 px where none is declared. The belt
  re-rolls on every pool map; the houses do not move for it. Two more from the cohort: `generate`'s re-roll loop kept a
  retry that seated FEWER households if it stranded no more (seed 25: 14 with two stranded, then 13 with none, the second
  kept) - the seated count may not fall now; and the cohort audit reported a stranded house but not a shortfall, so a
  seed that seated 13 of 20 read as a pass - `households_seated` is a cohort failure now, read off `meta.roll_placed`.
- **D7 The toe is asked before it is drawn, by every placer.** The review found three maps whose manifest put a
  farmhouse, a threshing floor and a byre inside the toe-marsh polygon (drawn ink clean - the marsh scatter keeps its
  halo). `install_site_boundary` registers `toe_band()` once among `hard_polys` - the same derivation the ways route
  around - so the boundary holds it AND every later placer that asks `_hard_clear` (the byres, the sheds, the wells)
  refuses it: a first cut put it in the blob alone and Inashiro's byre 2 stood 28 px into the reeds. This is the one
  rule about where a structure may lie that this feature moves (FR-002, D2) - an overlap fix under Principle XIV,
  inside the GM's "things not overlapping". The alternative - clipping the toe outline to the block polygons after the
  fact - would have left the record saying the reeds stop where a byre stands.

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
- Round 6 (2026-09-12, on the amendments made during implementation - the toe in the boundary, the six-ring spiral
  with rescue rounds, the re-roll's salted lattice, D6/D7): the substance of every amendment FAITHFUL (the toe is part
  of "literally everything"; the rescue spends guesses only where a household would otherwise be stranded); CHANGES
  REQUIRED on four record items - FR-001/D7 to state the toe's reach (registered among `hard_polys`, so the byres,
  sheds and wells refuse it), FR-002/D2 to name the toe as the ONE rule that moves instead of denying that any does,
  SC-2 to say it is measured over the pool with the quota met and to carry the rescue path's own number, FR-003's
  "never on a pool map" as a measurement (`meta.seat_search.rounds`) rather than a rule. Applied.
- Round 7 (2026-09-12): the four items resolved; CHANGES REQUIRED because the Summary and FR-001 still specified the
  ONE-BLOB design - the whole union reduced to facing chains - that the first cut measured wrong (a dike mosaic's far
  chords refused the ground between its ponds, Kuwabata 11 of 16) and the implementation replaced with TWO outlines
  asked two ways; five record items - the two forms and the refused cut, the size clause counting the rings, FR-002's
  field row into the chains, FR-003's front row from the paddy's chains with the exclusions at the pre-test, FR-005
  reporting the rings. Applied. Aside kept: SC-1's 0.25 s is missed on three of five maps and the Status says so.
  The seventh round is past the GM's five-round cap; rounds 6 and 7 were on text amended AFTER the FAITHFUL round 5
  to record what implementation measured, each returning new and smaller record items - the case the cap's own note
  names as not the argument it exists to end. Reported to the GM with the feature.
