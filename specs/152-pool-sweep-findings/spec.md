# Feature Specification: the pool sweep's recorded findings, worked off

**Feature Branch**: none (this project stays on `main`; `export SPECIFY_FEATURE=152-pool-sweep-findings`)
**Created**: 2026-08-29 | **Status**: draft | **Request**: [gm-request.md](gm-request.md) (verbatim)

## Why this feature exists

The 2026-08-29 pool sweep - four `settlement-review` passes over Inashiro, Kashikawa, Mizuguchi and
Sawada after feature 150's merge - fixed eight defects and RECORDED sixteen more with their
measurements, because fixing them inside a 291-commit merge would have put unreviewed change into an
already-large landing. The GM read that list and asked for all of it: *"the other findings that you say
you recorded but are not fixed. also seem like they are worth doing. So please go through and take care
of The rest of those as well."*

Two items the GM raised in their own words rather than by reference, and one they confirmed by eye:

- the tameike research finding belongs in what a reader is shown when they click the marsh;
- the privy seats should account for wind - *"that does sound like an important engine change"*;
- the windbreak: *"the Windbreak Forest looked a little spotty, as in it's not clear that it will, in
  fact, be breaking much wind. Given how many houses appear uncovered."* The GM saw this themselves,
  independently of the reviewer's measurement.

Every item below already has its measurement taken; none needs re-deriving. This feature does not add a
capability, a map or a tier - the scope is the closed list.

## User Scenarios

### US1 - what the GM named (P1)

**US1.1 A reader clicking the marsh is told why the reeds are there.** The interactive map's modal for
marsh currently explains the wet ground; it does not carry the finding that active management SUSTAINS
a reed fringe (a Kagawa study found dredging and algae-cutting positively correlated with emergent-plant
richness), nor its companion - that the embankment itself is mown and burned to keep the bank strong.
Both are researched, cited and already in `research/water.md`; the reader never sees them.

*Independently testable*: open a map's `.html`, click a marsh, and read the finding with its class
(accurate / deviation / guess) and its sources.

**US1.2 A privy does not stand upwind of the house it serves.** Measured across the pool: the seat table
is expressed in the HOUSE's local frame and houses draw at rot 0-4 degrees, so "back" is north on every
map. Sawada came out **12 of 12 upwind**; Inashiro 0/11, Kuwabata 0/9, Mizuguchi 0/4, Kashikawa 3/14 -
downwind by luck, not by rule. Nothing consults `plan.windward`.

*Independently testable*: roll each pool map and count privies and manure pits within 90 degrees of the
declared `windward` bearing from their own house. No map may be dominated by upwind seats.

**US1.3 A windbreak belt shelters the cluster it is drawn for.** On Kuwabata the belt covers 50% of the
frontage it exists to shelter and **13 of 16 houses have no clump within 150 ft**, the gate's own embrace
radius; 24 clumps are recorded `clumps_offpage` and never drawn. On Sawada the drawn belt is 510 ft
against a 714 ft cluster with **5 of 19 houses beyond its end**, and the bare strip GREW from 57 to 85 px
since it was deferred. The mechanism is known: the band is offset into the wind from the house CENTROID
and sized across the wind, so an elongated cluster gets a band that lands on its own flank.

*Independently testable*: for each pool map, the share of farmhouses with a drawn belt clump within
150 ft, and the drawn belt's across-wind span against the cluster's.

### US2 - features that draw wrong (P2)

**US2.1 A copse reads as a copse.** Mizuguchi's records 205 ft and draws 2 clumps 175 ft apart; Inashiro's
records 313 ft and draws 2; Sawada's 17 clumps are drawn INSIDE the windbreak (13 of 17 touching a
windbreak clump), so two recorded features draw as one ragged wood. The project's own doctrine says they
are different plantings for different reasons.

**US2.2 A caption is not seated across a lane from its own glyph, nor on top of a feature.** Inashiro's
"notice board" caption stands with the full width of lane 1 between it and its board, 22 ft from a shrine
on the caption's own side. The seat filter scores hug and lane clearance only - never the fabric, never
whether a way separates caption from subject.

**US2.3 A basin the size of a pond is not tinted as a flooded plot.** Sawada's surviving flooded plot is
6,706 sq ft - 4.9x the median basin and the largest of 776 - on the one map whose brief is that it has no
pond. Every demotion predicate tests SHARPNESS; none tests SIZE, so a basin `close_seams` absorbed up to
five design cells keeps the tint it was given as one.

**US2.4 A persimmon's fruit is not a stencil.** All four dots sit at exactly (+/-3.5, +/-3.5), r 1.3, on
every tree on every map - a rigid mirrored 2x2, which is the doctrine's own strongest face-read trigger,
and the anti-twin problem in miniature.

### US3 - the lane web (P3)

**US3.1 A lane is not severed by a fixture standing in the gap.** Kuwabata's back lane comes apart with
25.0 ft between two rounded caps and a 10 x 3.5 ft woodpile 5.6 ft off the line. Every endpoint-reach
check passes because each piece reaches the network at its OTHER end.

**US3.2 A lane reaches something.** Kashikawa's lane 0 ends 206.1 ft from any other lane and 246.5 ft from
the nearest farmhouse, blunt-capped in open grazing, with `lanes_reach_something` green on it.

**US3.3 A through-route keeps its width.** Mizuguchi's necks 6 ft -> 3 ft -> 6 ft for 11 ft where two 6 ft
lanes never meet and the only ink joining them is a 3 ft back lane.

### US4 - records that disagree with the map (P4)

**US4.1 Seated fixture counts match their declared shares.** Inashiro declares manure .531 per household
and seats 2 of 15 - p about 0.002 under a binomial. Either the placer refuses at a rate nothing records,
or the shares do not mean what the record reads. The interactive map otherwise tells a reader that a
manure heap stands on 53% of farmsteads while the sheet shows 13%.

**US4.2 A homestead is composed, not stamped.** 13 of 20 Kashikawa farmhouses carry the fixture row at
dy -18 to -21 ft; privies at bearing 31-41 degrees at 10 of 13; at 3 of 4 manure homesteads the pit sits
9.5 ft directly above the privy with x agreeing to 0.7 ft. The arrangement is right and researched; the
VARIANCE is nil.

**US4.3 A diagnostic the project maintains is green, or its failure is ledgered.** `make jogs` exits RED
on Sawada - 3 sideways steps in 776 rings, the largest 12.5 ft - and nobody reads it.

**US4.4 The notes describe the map that ships.** Kashikawa's accepted-limitation entry names a byre that
stands nowhere within 167 ft; Inashiro's clump, stand and fixture counts are stale; Mizuguchi's records a
board at a traffic optimum it no longer occupies.

**US4.5 Where a kosatsuba stands is a knob.** Both forms are attested - the takafuda stood at crossroads
and bridgeheads, and at the village well. Two supportable answers is a knob by constitution XII, and the
siter can express only one.

## Requirements

- **FR-001** The marsh modal MUST carry the tameike finding and the embankment finding, each classed and
  cited from `research/water.md`, visible to a reader who clicks marsh on a rendered map.
- **FR-002** The privy/manure seat roll MUST consult `plan.windward`, preferring among the ALREADY
  ATTESTED seats the one not within 90 degrees of the windward bearing. It MUST NOT invent a new seat.
- **FR-003** A windbreak belt MUST be derived from the drawn cluster's windward extent rather than an
  offset from its centroid, so an elongated cluster gets an elongated belt; and clumps refused by the
  per-crown filter MUST move the BAND rather than be dropped from the canopy.
- **FR-004** through **FR-014** One per US2/US3/US4 item above, each fixed at its named mechanism.
- **FR-015** Every fix MUST be measured against the number already recorded for it, before and after.
- **FR-016** No fix may be declared done on a check alone: the pool is re-rolled and re-reviewed.

## Success Criteria

- **SC-001** No pool map has a majority of privies/manure pits within 90 degrees of its windward bearing;
  Sawada specifically goes from 12/12 to a minority.
- **SC-002** On every pool map, at least 80% of farmhouses have a drawn windbreak clump within 150 ft,
  and no map records more than a handful of clumps it never draws.
- **SC-003** A reader clicking marsh sees the tameike finding with its sources.
- **SC-004** `make jogs` exits green on every pool map, or its residue is ledgered with a measurement.
- **SC-005** Every notes file describes the map that ships (no stale count, no absent byre).
- **SC-006** The whole pool passes `make maps` to the same standard as before, and a settlement-review
  pass over the changed maps returns no NEW error.

## Assumptions

- The pre-existing tripwire seed 37 failure (`paddy_bunds_do_not_stagger`, ledgered in
  `specs/139-remaining-test-failures`) remains out of scope; it is not this feature's to fix.
- "Recorded but not fixed" means the sixteen items in `specs/150-kuwabata-dike-pond-hamlet/tasks.md`.
  D3's caption sketch is included even though the defect no longer shows on Kuwabata, because the
  mechanism is unchanged and Inashiro still shows it.
