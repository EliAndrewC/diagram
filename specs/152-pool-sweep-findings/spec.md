# Feature Specification: the pool sweep's recorded findings, worked off

**Feature Branch**: none (this project stays on `main`; `export SPECIFY_FEATURE=152-pool-sweep-findings`)
**Created**: 2026-08-29 | **Status**: draft | **Request**: [gm-request.md](gm-request.md) (verbatim)

## Why this feature exists

The 2026-08-29 pool sweep - four `settlement-review` passes over Inashiro, Kashikawa, Mizuguchi and
Sawada after feature 150's merge - fixed eight defects and RECORDED fourteen distinct findings with their
measurements (eighteen bullets; the windbreak, the caption, the copse and the notes drift are each
recorded twice, once per round), because fixing them inside a 291-commit merge would have put unreviewed change into an
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

*Independently testable*: for each pool map, whether any farmhouse lies BEYOND the drawn belt's
across-wind ends. Only that - the proximity measure this user story first carried (houses within 150 ft
of a clump) is the wrong property and SC-002 records why.

**Two vintages of numbers, deliberately kept apart.** The figures in the paragraph above are the
2026-08-29 SWEEP's record, as the reviewers measured them at the time. SC-002 carries a FRESH
re-measurement taken this session over the whole pool, on the span test rather than the proximity one -
Sawada 8 of 19 rather than 5 of 19, Kuwabata 45 undrawn against 47 drawn rather than 24 against 38 -
because the maps have been re-rolled since. **SC-002's numbers are the before-number FR-017 governs.**

### US2 - features that draw wrong (P2)

**US2.1 A copse reads as a copse.** Mizuguchi's records 205 ft and draws 2 clumps 175 ft apart; Inashiro's
records 313 ft and draws 2; Sawada's 17 clumps are drawn INSIDE the windbreak (13 of 17 touching a
windbreak clump), so two recorded features draw as one ragged wood. The project's own doctrine says they
are different plantings for different reasons. The recorded finding also names a KNOB candidate -
a copse embedded in the belt against one threading the houses - and constitution XII makes that a knob
rather than a picked answer, so it is specified here (FR-005) exactly as the kosatsuba knob is at US4.5.

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

**US4.3 A diagnostic the project maintains is green.** `make jogs` exits RED
on Sawada - 3 sideways steps in 776 rings, the largest 12.5 ft - and nobody reads it.

**US4.4 The notes describe the map that ships.** Kashikawa's accepted-limitation entry names a byre that
stands nowhere within 167 ft; Inashiro's clump, stand and fixture counts are stale; Mizuguchi's records a
board at a traffic optimum it no longer occupies.

**US4.5 Where a kosatsuba stands is a knob.** Both forms are attested - the takafuda stood at crossroads
and bridgeheads, and at the village well. Two supportable answers is a knob by constitution XII, and the
siter can express only one.

## Requirements

- **FR-001** (US1.1) The marsh modal MUST carry the tameike finding, classed and cited from `research/water.md`,
  visible to a reader who clicks marsh on a rendered map. Its second half - that the EMBANKMENT is mown
  and burned to keep the bank strong - is part of the SAME recorded finding, not a second deliverable:
  the section is titled "A reservoir's shore is reeded, and its EMBANKMENT is mown - the two are
  different ground", and the bank half is why the reeds stop where they do. Carrying one without the
  other would tell a reader the shore is reedy and leave them wondering why the bank beside it is not.
- **FR-002** (US1.2) The privy/manure seat roll MUST consult `plan.windward`, preferring among the ALREADY
  ATTESTED seats the one not within 90 degrees of the windward bearing. It MUST NOT invent a new seat.
- **FR-003** (US1.3) A windbreak belt MUST be derived from the drawn cluster's windward extent rather than an
  offset from its centroid, so an elongated cluster gets an elongated belt; and clumps refused by the
  per-crown filter MUST move the BAND rather than be dropped from the canopy.
- **FR-004** (US2.1) A `copse` MUST draw as a distinguishable stand: it may not be recorded at 205-313 ft
  and drawn as two clumps, and its clumps may not be seated inside the windbreak's own canopy.
- **FR-005** (US2.1) Where a copse sits MUST become a per-settlement KNOB - embedded in the belt, or
  threading the houses among the homesteads - because the recorded finding names both as supportable and
  constitution XII makes two supportable answers a knob rather than a choice.
- **FR-006** (US2.2) The caption seat filter MUST reject a seat whose rotated quad laps a solid feature,
  and MUST reject one that a drawn way separates from the subject it names.
- **FR-007** (US2.3) The flooded-plot tint MUST test the FINAL ring's AREA, not only its sharpness, so a
  basin absorbed to several design cells is demoted.
- **FR-008** (US2.4) A persimmon's fruit dots MUST vary per tree, rolled off the map's own position hash.
- **FR-009** (US3.1) A lane link within the join reach MUST NOT be defeated by a single movable farm
  fixture standing in the corridor; either the fixture yields or the link routes past it.
- **FR-010** (US3.2) A lane MUST reach something. No threshold is set here: the recorded case measured
  206.1 ft from any way and 246.5 ft from any farmhouse, and what counts as "reaching nothing" is for the
  plan to derive from the existing rule (`lanes_reach_something` and the trim that already pulls internal
  ends back), not for this spec to invent a number the GM never set.
- **FR-011** (US3.3) A through-route MUST keep its width across a junction, rather than necking to a back
  lane's tread between two wider ways that never meet.
- **FR-012** (US4.1) Seated fixture counts MUST agree with their declared per-household shares, or the
  record MUST state what the share actually means.
- **FR-013** (US4.2) A homestead's fixture ring MUST vary its offset and pitch off the map's own hash.
- **FR-014** (US4.3) `make jogs` MUST exit green on every pool map. It carries NO "or ledger it" arm: the
  recorded finding is precisely that a maintained diagnostic is red and nobody reads it, so a residue
  written down and shipped red would satisfy the words while leaving the defect on the map. If a residue
  turns out genuinely unfixable, the project's own three exits (fix, revert, or a GM waiver for that
  specific case) govern - a spec may not pre-authorize the outcome the GM asked to end.
- **FR-015** (US4.4) Every notes file MUST describe the map that ships.
- **FR-016** (US4.5) Where a kosatsuba stands MUST become a per-settlement knob - the busiest frontage, or
  the drawing-water place - both being attested.
- **FR-017** Every fix MUST be measured against the number already recorded for it, before and after.
- **FR-018** No fix may be declared done on a check alone: the pool is re-rolled and re-reviewed.

## Success Criteria

- **SC-001** **SUPERSEDED 2026-08-29 by the research, and revised in place the way SC-002 was.** It read:
  *"No pool map has a majority of privies/manure pits within 90 degrees of its windward bearing; Sawada
  specifically goes from 12/12 to a minority."* That criterion encodes the WIND hypothesis, and the
  research pass the GM's own conditional called for CONTRADICTED it: the one primary source reachable
  (Wang & Ochiai 2022) puts 72.7% of toilets southeast-to-south for solar warmth to speed fermentation of
  night soil, its wind-siting finding covers storage buildings and retirement houses rather than toilets,
  and the words leeward, downwind, odor and hygiene appear nowhere in it. The GM then ruled the 72.7%
  figure be used literally. A criterion that still tests wind would mark the researched behavior a
  failure - Kashikawa has 13 of 15 privies within 90 degrees of its windward bearing precisely BECAUSE
  its sun side lies that way.

  It now reads: **privies are seated southeast-to-south at the rate the ground allows, and the shortfall
  against 72.7% is explained by measurement rather than tuned away.** Measured: 0% before this feature,
  46% after, with a recorded radius sweep showing that reaching 73.8% costs privies drawn into
  neighbouring farmsteads. The honest route to the rest is a stage reorder, recorded and not attempted.

  *This is flagged in the handback, not buried here: the GM asked for the wind change in their own words
  and a source overturned it, which they should hear from me rather than discover from a manifest.*
- **SC-002** The belt's recorded extent spans the cluster across-wind on every pool map, and the DRAWN
  canopy fills it except where the page cuts the belt.

  *Revised 2026-08-29, after the fix, on a measurement that showed the first wording could not be met by
  a correct map.* It read "no farmhouse stands BEYOND the drawn belt's across-wind ends". A communal
  grove is explicitly allowed to clip at the frame - *"a partially visible belt reads as 'the wood
  continues'"* - so where the belt runs off the page its DRAWN end is the page, not the belt, and a house
  near that corner is beyond the drawn canopy however long the belt is. Measured after the fix: 3 of 82
  houses stand past the last drawn clump, and two of the three are exactly that case (Kashikawa's and
  Sawada's remaining undrawn clumps sit at that end, off the page); the third is Kuwabata's, 24 ft, which
  is under one clump diameter. On all five maps the belt POLYGON covers every house. Measuring the
  polygon's span is the test that asks about the belt rather than about the crop. This replaces
  a first draft that asked for 80% of houses within 150 ft of a clump, which measures the wrong thing: a
  tree line shelters well downwind of 150 ft, so proximity is not shelter, and the 80% was a number the
  GM's request does not set. What the GM described is houses that are not BEHIND the belt at all -
  *"how many houses appear uncovered"* - and that is an across-wind span test with no invented threshold.
  Measured before, 2026-08-29: **Kashikawa 8 of 20 houses beyond the belt's ends (belt 494 ft against a
  759 ft cluster), Sawada 8 of 19 (499 against 663), Kuwabata 3 of 16 (339 against 557)**; Inashiro and
  Mizuguchi already 0. The same three maps discard most of their own canopy as "off-page" - Kuwabata 45
  undrawn against 47 drawn, Sawada 84 against 95, Kashikawa 61 against 99 - which is the suspected
  mechanism and what FR-003 addresses.
- **SC-003** A reader clicking marsh sees the tameike finding with its sources.
- **SC-004** `make jogs` exits green on every pool map.
- **SC-005** Every notes file describes the map that ships (no stale count, no absent byre).
- **SC-006** The whole pool passes `make maps` to the same standard as before, and a settlement-review
  pass over the changed maps returns no NEW error.

## Assumptions

- The pre-existing tripwire seed 37 failure remains out of scope; it is not this feature's to fix, and
  constitution XIII's "pre-existing failures are NOT regressions ... not fixed under someone else's
  feature" is the project's own rule for it. **The check/seed pairing is a FRESH measurement, not a
  citation**: `make tripwire` in this clone on 2026-08-29 reported `tripwire seed 37:
  paddy_bunds_do_not_stagger`, and the same seed fails identically on a detached worktree at main's tip,
  which is how it was established as pre-existing. `specs/139-remaining-test-failures` T06 ledgers
  `paddy_bunds_do_not_stagger` against seeds 12 and 39, and seed 37's older ledgered checks are
  `lanes_form_one_network` / `lanes_bend_like_paths` - so what seed 37 fails has MOVED since those were
  written, and this feature does not adopt it either way. **This exclusion covers the tripwire cohort
  ONLY. It does not touch US4.3**: `make jogs` red on Sawada is in scope and is fixed here, even though
  `jogs.py` is a sibling tool of the same check family.
- "Recorded but not fixed" means the **fourteen distinct** findings in
  `specs/150-kuwabata-dike-pond-hamlet/tasks.md` - eighteen bullets, of which the windbreak, the caption,
  the copse and the notes drift are each recorded twice, once per sweep round.
  D3's caption sketch is included even though the defect no longer shows on Kuwabata, because the
  mechanism is unchanged and Inashiro still shows it.

## Spec-fidelity review

Three rounds against the GM's verbatim request (`gm-request.md`), by an independent `spec-fidelity`
agent, per constitution XVI.

- **Round 1: NEEDS-CHANGES, five items.** Two were real scope defects, not wording. `FR-004` through
  `FR-014` was written as a placeholder range - eleven slots for twelve items - so one requirement would
  have fallen out with nothing marking which. And the tripwire exclusion mis-cited its ledger:
  `specs/139` pairs `paddy_bunds_do_not_stagger` with seeds 12 and 39, not 37, so what was presented as
  a citation was actually a fresh measurement. Also: a dropped copse-siting knob, an uncounted "sixteen",
  and FR-001 reading as two deliverables.
- **Round 2: NEEDS-CHANGES, two items.** `FR-014` carried an escape arm - *"or its residue MUST be
  ledgered with a measurement"* - which would have let a red diagnostic ship while satisfying the
  requirement, and contradicted this spec's own Assumptions. That is the exact failure class this review
  exists to catch. And `US1.3` still stated the superseded proximity measure alongside a second vintage
  of numbers, leaving `FR-017` two candidate before-numbers.
- **Round 3: FAITHFUL.** Verified no requirement contains an "except when", an escape arm or an invented
  threshold; every number in the requirements traces to a recorded finding. One text sweep applied here:
  US4.3's heading still carried the arm FR-014 had voided.

**Raised for the GM, not blocking**: FR-005 and FR-016 each add a per-settlement knob (copse siting,
kosatsuba siting), and constitution VI makes a knob owe one map per VALUE at verification. That is the
largest single cost in this feature and the spec does not size it; the plan does.

