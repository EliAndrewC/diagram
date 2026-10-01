# Feature 291 - how many sides a homestead grove takes

**Feature**: 291-homestead-grove-sides | **Created**: 2026-09-29 | **Status**: Draft
**Input**: the GM's request and rulings, verbatim in [`request.md`](request.md).

## Summary

The research record says, flatly, that before 1868 a farmstead's grove went round the whole house, and that the
windward-only belt is the modern form. Its evidence does not bear that out: the full ring is reported firmly for one
region (the Izumo plain, tied to its flood banks), a 1625 domain order is ambiguous, and the same record holds the
Sendai grove on the north and west, "often lacking the south or the east side", planted that way under the first
Sendai lord and kept for centuries, the Tonami grove open on its east front, and other regions' groves on one or two
sides. No source counts farmsteads by grove shape.

This feature (1) corrects the record so each shape is cited to the region and date that attest it; (2) makes the
homestead grove's sides a per-settlement knob - two sides one time in two, three sides three in ten, four sides one in five (the GM's weights, 5 : 3 : 2), the four-sided share
rising to two in five where the farmsteads stand on flood-prone ground - with the windward side the deep one; and (3) fixes
the per-house grove placement that has kept the dispersed and linear settlement forms (the forms whose farms carry
their own grove) switched off since feature 126, and switches them back on, so the knob reaches maps.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The record says what its sources say (Priority: P1)

A reader following a grove's "See references" from a map reaches an answer that says which regions put the grove on
two sides, which on three, and which all the way round, each with its footnote, and that no source says how common
each was.

**Independent Test**: read the corrected entries; `quote-check` and `record-format` confirm them.

**Acceptance Scenarios**:

1. **Given** the homestead grove entries, **When** a reader looks for the grove's shape before 1868, **Then** they find
   the Sendai two-sided form, the Tonami front-open form and the Izumo full ring, each attributed to its region and
   footnoted, and no sentence saying all premodern groves went round the house.
2. **Given** the shelter-belt entry holding the GM's 2026-08-29 hook ruling, **When** a reader reads it, **Then** it
   says the GM's 2026-09-29 ruling reverses it for the farmstead grove, whose sides are now a rolled knob, quoting
   both rulings; and that the village belt stays on one or two windward sides on that entry's own evidence and the
   GM's 2026-09-29 approval of "the homestead grove only".

### User Story 2 - Farmstead groves take two, three or four sides (Priority: P1)

The GM opens a generated hamlet whose farms carry their own groves and sees groves on two, three or all four sides of
the house, the same shape at every farm in that hamlet, with the deep stand on the windward side.

**Independent Test**: roll many settlements and count the forms; draw one of each and look.

**Acceptance Scenarios**:

1. **Given** a settlement whose farms carry groves, **When** it is generated, **Then** every farm's grove has the one
   side count rolled for that settlement.
2. **Given** a three-sided grove, **When** drawn, **Then** the open side is the front - the lee side where the farm's
   yard and way in are.
3. **Given** a three- or four-sided grove, **When** drawn, **Then** the windward arms are the full depth and the other
   planted sides a thinner band.
4. **Given** a settlement on flood-prone ground, **When** rolled, **Then** four sides comes up two times in five.

### User Story 3 - Dispersed and linear hamlets come back (Priority: P1)

The generator rolls the dispersed and linear settlement forms again, at the weights feature 126 set, and their
per-house groves pass every check a grove answers to.

**Independent Test**: the hamlet cohort passes with the forms in the roll.

**Acceptance Scenarios**:

1. **Given** the settlement-form roll, **When** a hamlet is generated without a pinned form, **Then** it can come up
   nucleated, dispersed or linear at feature 126's weights (5 : 3 : 2).
2. **Given** a dispersed or linear hamlet, **When** generated, **Then** every farm carries its rolled grove, no grove
   lies on a lane, over a byre or other structure, or across a garden's morning sun, and every household is seated.

### Edge Cases

- A map whose windward key is a single cardinal (N, S, E, W): two sides still means two - the windward face and one
  flank.
- A nucleated hamlet: its farms still shelter behind the village belt and carry no grove of their own; the knob is
  rolled and recorded but draws nothing.
- The village-scale shelter belt is not this knob and keeps one or two windward sides.

## Requirements *(mandatory)*

### Functional Requirements

**The record**

- **FR-001**: Every entry of the research record that says the premodern farmstead grove went round the whole house, or
  that the windward-only grove is only the modern form, MUST be corrected so each shape is attributed to the region
  and date its source gives: the Izumo full ring before Meiji; the Sendai north-and-west grove, lacking the south or
  east, planted under the first Sendai lord and kept for several hundred years; the Tonami grove open on its east front
  (undated); the 1625 Takada order read as it is written (cedar around the homestead, camellia and bamboo grass on the
  south). Each assertion is footnoted; the record says no source counts farmsteads by grove shape.
- **FR-002**: The record MUST state the decision: the farmstead grove's sides are a knob rolled per settlement at 50 / 30
  / 20 (two / three / four), four sides two in five on flood-prone ground, the weights a GUESS by the GM's ruling of
  2026-09-29, quoted; the windward arms deep and the rest thinner (Tonami's pattern, a GUESS for the full ring); the
  open side of three the front.
- **FR-003**: The shelter-belt entry holding the 2026-08-29 hook ruling MUST record the GM's 2026-09-29 ruling as
  reversing it for the farmstead grove, both quoted; the village belt stays on one or two windward sides on that
  entry's own evidence and by the GM's approval of "the homestead grove only".
- **FR-004**: Every map modal written from a changed entry MUST be checked for drift and rewritten where it drifted.

**The knob**

- **FR-005**: The homestead grove's side count MUST be a per-settlement knob, pinnable by a map, otherwise rolled from
  the map's seed: two sides, three and four weighted 5 : 3 : 2.
- **FR-006**: On flood-prone ground the four-sided share MUST be two in five, the other two keeping their 5 : 3 ratio.
  Flood-prone ground MUST be a site property a map can pin, and is otherwise set from the site: true where the fields
  are reclaimed low ground behind dikes (the polder archetypes, the grid polder and the dike-and-pond) or the houses
  stand on a dike.
- **FR-007**: Two sides MUST be the windward pair (for a diagonal windward key, its two faces; for a cardinal, that face
  and one flank). The FRONT is the lee side where the farm's yard and way in are, and a three-sided grove leaves it
  open: three sides MUST add the one remaining face that is not the front. Four sides MUST close the ring.
- **FR-008**: The windward arms MUST keep today's depth; every other planted side MUST be a thinner band.
- **FR-009**: The rolled side count MUST be recorded on the map and stated in the grove's modal.

**The placement**

- **FR-010**: Each farm MUST be seated with room for the grove its settlement rolled, and every rolled side planted,
  for every side count; and the per-house grove MUST pass every rule feature 126 measured failing: it lies on no lane
  tread (`groves_clear_of_lanes`), stands on the windward side it was rolled for (`groves_on_windward_side`), leaves
  every garden its morning sun (`gardens_unshaded_from_east`), lies on no structure and puts no crown over one,
  byres and later-seated fixtures included (`groves_clear_of_structures`, `structures_clear_of_trees`), and every
  household is seated.
- **FR-011**: The settlement-form roll MUST restore feature 126's weights (nucleated 5, dispersed 3, linear 2), and the
  hamlet cohort MUST pass with them, as the bar feature 126 set for switching them back on.
- **FR-012**: The pool hamlets MUST be regenerated; a hamlet whose seed now rolls another form takes it, except the
  reference hamlet Inashiro, which the GM kept nucleated (2026-09-29).

**The row village** (amendment 3)

- **FR-013**: A LINEAR hamlet's farms MUST stand in a row along one line, never in ranks behind the row. The record
  (homesteads/155) gives two lines, and both MUST be drawn: a STREET LAID FIRST, the farms fronting it (the planned
  row's form, which a paddy row may borrow - the `kotobank-santome-shinden` write-up - and homesteads/150's linear
  hamlet whose farms front a street along the road), drawn straight, as a surveyed road is; or the DRY EDGE THE GROUND
  GIVES - a levee, a dike, a fan's foot - which the field's margin stands for on these maps (this project's reading),
  the row curving with it. Where the site decides it the site's line is taken: flood-prone ground (FR-006) takes the
  dike line; otherwise the line MUST be a per-settlement knob, pinnable, rolled at even odds (a GUESS: the record gives
  no count), and recorded on the map.
- **FR-014**: The farms along a line MUST stand one FRAME apart - the farm's grove and its ground plus the lane's room
  between two farms' groves (homesteads/715) - a physical necessity of FR-010, since a grove farm cannot stand on a
  narrower lot. The width this gives is a GUESS at or just past the top of the record's range, 9 ken to 40 ken (homesteads/156); the
  40 ken is a dry-field colony's figure and is not carried over as a paddy row's.
- **FR-015**: Which side of its street a row stands on MUST be a per-settlement knob, pinnable, otherwise rolled at even
  odds: ONE side, the street between the row and its field (farmland across the road, Shimotome), or BOTH sides, each
  farm's holding behind it (Santome, Nobidome); the odds a GUESS (homesteads/155: no count of which was commoner).
  Recorded on the map. On BOTH, the far row's holding MUST be drawn behind it in the form the record gives its line: on
  a street laid first, a strip behind the farm (the planned row's form, which a paddy row may borrow; its crop dry field
  and its depth a GUESS); on the dry edge, compact and near the house (accurate for a dike row, homesteads/156; carried to a levee
  or fan-foot row as this project's reading).
- **FR-016**: A row the line cannot hold MUST grow another street parallel to the first, with its own row or rows, as a
  planned colony grew more roads (homesteads/156) - not ranks behind a row. How many farms a line holds before the next
  street is the ground's, the count a GUESS.
- **FR-017**: Each street MUST be drawn as one continuous way along its row, joined to the connector, a rank wider than
  the lanes off it, and every farm of the row MUST reach it.

**What the reviews found** (amendment 3)

- **FR-018**: A DISPERSED farm MUST draw its own water (homesteads/200: a dispersed farm carries its own water; a shared
  well within reach is the nucleated arrangement), in the form a per-settlement knob sets - pinnable, rolled at even odds
  and recorded: a small channel led off the irrigation water (the nearest drawn ditch or the brook, or a channel already
  led off it to another farm - amendment 6, a GUESS) into the farm's own
  lot, ending in its dooryard (homesteads/200, the Tonami museum: "in many areas a small channel was led into the house's
  grounds"), or its own well in its dooryard, off its way in (the other areas, this record's reading, a GUESS); the odds
  a GUESS (amendment 5). A LINEAR row's water MUST be a
  per-settlement knob, pinnable, rolled at even odds and recorded: each farm its own well in its dooryard, or wells
  shared along the street within reach of the farms they serve - the record rules only on the dispersed farm, and its
  one row's wells (Santome's, few, deep and shared on a water-poor upland) do not transfer; the odds a GUESS.
- **FR-019**: A farm's grove MUST draw bamboo only where that farm rolled a household bamboo stand. (Its door clause - "every
  grove farm of a LINEAR row MUST have its front door ... reached by a way" - is dropped by amendment 9.)

### Key Entities

- **Grove side count**: 2, 3 or 4; one per settlement; recorded on the map.
- **Flood-prone ground**: a property of the settlement's site - pinned by the map, or set from its polder fields or
  dike-top houses (FR-006); recorded on the map.
- **Row line**: a street laid first, or the dry edge; one per linear settlement; set by the site or rolled; recorded (FR-013).
- **Row sides**: one or both; one per linear settlement; recorded on the map (FR-015).
- **Row water**: own wells or shared wells; one per linear settlement; recorded on the map (FR-018).

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002, FR-003): no entry of the record asserts a universal premodern full ring; the corrected entries
  pass `quote-check` and `record-format`.
- **SC-002** (FR-004, FR-009): every modal the push names as owed is answered by an `entry-drift` check; the grove's modal states the side count its map rolled, read from the map.
- **SC-003** (FR-005, FR-006): over 1,000 rolled seeds the counts sit within three standard errors of the 5 : 3 : 2 weights off
  flood ground and the 15 : 9 : 16 weights on it; and a test rolls a real polder site and finds it flood-prone, reading the
  flood table.
- **SC-004** (FR-007, FR-008): unit tests prove the faces planted for each side count and windward key, and that the
  non-windward bands are thinner than the windward arms.
- **SC-005** (FR-010, FR-011): the cohort passes (every seed's checks green, every household seated) with the three
  forms rolled and each side count present among its non-nucleated seeds; and in every non-nucleated seed every farm's
  grove plants every side its settlement rolled - no farm on fewer.
- **SC-007** (FR-013, FR-014, FR-015, FR-016, FR-017): in every linear seed of the cohort and on every linear pool map, every farmhouse stands
  within one frame depth of a street, no farm stands behind another on the same side of its street, each street is one
  continuous way, a BOTH row's far farms each have their holding drawn behind them, and both values of the line and of
  the sides appear among the linear seeds.
- **SC-008** (FR-018, FR-019): in every dispersed seed the farm-water knob's value is drawn - every farm a channel ending in
  its own lot, or a well of its own not in its way in - and both values appear among the dispersed seeds; in every linear
  seed the water knob's value is drawn (own wells, or every farm within reach of a shared well) and both values appear;
  and in every non-nucleated seed
  and pool map the farms drawing grove bamboo are exactly the farms that rolled it.
- **SC-006** (FR-012): the pool is regenerated, `make done` is green, and every regenerated pool map whose layout moved
  gets its settlement-review.

## Decisions Recorded

- **Weights**: 50 / 30 / 20, a GUESS, the GM's ruling of 2026-09-29. Two sides is the form reported in the most regions
  and the only one with a general statement and an early-Edo date; three is Tonami's; four is Izumo's.
- **Flood ground**: four sides two in five, the other two scaled to keep 5 : 3 (weights 15 : 9 : 16) - the Izumo ring's own
  stated cause was flood; the scaling is a GUESS.
- **Per settlement, not per farm**: grove shape is reported as regional custom.
- **Windward deep, rest thinner**: Tonami's tall cedar on the windward faces and lesser trees elsewhere; a GUESS for the
  Izumo ring; the thinner depth is a GUESS.
- **The front is the open side of three**: Tonami's east front had little grove.
- **The 2026-08-29 hook ruling is reversed for the farmstead grove** (the GM approved "This reverses the GM's
  2026-08-29 hook ruling"); both rulings are recorded. **The village belt is not this knob**: it stays on one or two
  windward sides on `vegetation/030`'s own evidence, and the GM approved "the homestead grove only".
- **Flood-prone ground is the polder site** (FR-006): the Izumo ring stood on a flood plain behind an earth bank; the
  engine's diked low ground is the polder archetypes and the dike-top line. Reading it from those is this project's
  decision (a GUESS as to where else floods threatened farms), and a map may pin it either way.
- **Every farm carries its settlement's grove** (FR-010, spec-fidelity round 1): no farm quietly loses sides for want
  of room; a farm is seated where its grove fits.
- **The pool takes its seed's roll, Inashiro excepted by the GM** (FR-012): under the restored roll Inashiro,
  Mizuguchi and Kashikawa roll linear, Kuwabata and Sawada stay nucleated. Asked, the GM chose "Keep Inashiro, let
  others roll": the reference hamlet (and the test baselines built on it) is pinned nucleated in its spec; Mizuguchi
  and Kashikawa take their linear roll.

- **Both lines, the site's where it decides** (FR-013): a street laid first and the dry edge are both attested
  (homesteads/155), and a paddy row may borrow the planned row's street; flood-prone ground takes the dike; elsewhere
  even odds, a GUESS. The field's margin standing for a levee, dike or fan foot is this project's reading.
- **One frame apart** (FR-014): a physical necessity of FR-010, the grove plus the lane's room between two groves (homesteads/715);
  its width a GUESS at or just past the top of the record's 9-40 ken range. The 9 ken row is not this form's value because a 9 ken
  lot cannot hold a grove farm; the 40 ken is a dry-field colony's and does not transfer (source-applicability).
- **Sides at even odds** (FR-015): both attested, no count - a GUESS. The far row's holding follows its line: a strip
  behind on a street laid first (the borrowed planned form; dry field and depth a GUESS), compact near the house on the
  dry edge (homesteads/156: accurate for a dike row; a levee or fan-foot row this project's reading).
- **Row water** (FR-018): the record rules on the dispersed farm only; a row's water is a knob, even odds, a GUESS.
- **A channel led off another farm's channel** (FR-018, amendment 6): a farm's channel MAY be led off a channel already
  drawn to another farm - the irrigation water carried on - a GUESS: no page read says whether neighbors shared a channel.
  Measured 2026-09-30 by rolling Audit-19 (11 farms, the only irrigation water the field's head) with the farms taken
  nearest the water first: without it 1 of 11 farms drew a channel, with it 11 of 11; Audit-905 drew 20 of 20 either way.
- **A dispersed farm's water** (FR-018, amendment 5): the channel into the lot is ACCURATE (homesteads/200, the Tonami
  museum, "in many areas"); that the other areas dug a well is this record's reading, a GUESS, so the two are a knob at
  even odds (a GUESS). The channel is drawn from the nearest drawn supply ditch, or the brook where it is nearer (the
  nearest a map drawing convention; the brook standing for the irrigation water, this project's reading - a brook is
  the water the ditches are fed from - a GUESS), to the dooryard and ends there - its
  return to the field is not drawn (a deliberate deviation: no page read says where it left the lot); where in the
  dooryard it ends is a GUESS.

## Review history

**Round 1** (spec-fidelity, MODE 2, 2026-09-29): CHANGES. (a) flood weights, (b) the cardinal reading and (c) FR-012
faithful. Changes applied: the 2026-08-29 ruling recorded as REVERSED for the farmstead grove, not recast as standing
for the belt; the no-room edge case deleted and FR-010 requiring every farm seated with room for its rolled grove;
FR-010 naming every rule feature 126 measured failing, `groves_on_windward_side` included; flood-prone ground defined
(pinnable, else the polder archetypes or dike-top houses) with a test on a real polder site; the front defined as the
lee side with the yard and the way in, the side three leaves open.

**Round 2** (spec-fidelity-verify, MODE 3, 2026-09-29): CHANGES, one item - SC-005 now checks that every farm in a
non-nucleated seed plants every side its settlement rolled, so the fallback round 1 removed cannot return unseen.

**Round 3** (spec-fidelity-verify, MODE 3, 2026-09-29): FAITHFUL. The spec is accepted.

**Amendment 1** (2026-09-29, after acceptance; wording only): the GM's weights restated as the ratios they are (5 : 3 : 2; 15 : 9 : 16 on flood ground) rather than percentages, which spec-lint reads as unmeasured figures; SC-001 names FR-001 to FR-003 one by one and SC-002 covers FR-009 (the modal states the side count). Nothing changed in substance.

**Amendment 2** (2026-09-29, the GM's decision): FR-012 - the GM, asked how the pool should take the restored roll (three hamlets roll linear), chose "Keep Inashiro, let others roll (Recommended)": the reference hamlet is pinned nucleated, Mizuguchi and Kashikawa take their roll.

**Amendment 3** (2026-09-29, the GM's instruction and the research it asked for): FR-013 to FR-019, SC-007, SC-008. The
linear form drew a block of groved farms three and four deep (the settlement-review of Kashikawa, NEEDS-WORK), and asked
what a row village of such farms should look like, the GM answered: *"what it should look like should be based on our
research and not just something that you ask me ... find out from our research what types of settlement layouts
existed, and then have our settlements reflect the range of settlement layouts that we are able to find. And then, if
our research is thin and we are straightforwardly unable to come up with an answer, then we make a tunable knob for the various possibilities which all seem reasonable by virtue of being in line with our other research and not contradicting anything that our research has already established."* The
research is homesteads/155 and 156 (R6, checked). FR-018 and FR-019 carry the reviews' other findings (no wells; bamboo drawn on
farms that rolled none; a door no way reached), each decided by the record.

**Amendment 3, round 1** (spec-fidelity-verify, MODE 3, 2026-09-29): CHANGES - both attested lines to be drawn (a paddy row may borrow the street laid first), the frame by FR-010's necessity with its width a GUESS, the lane's room in the frame, the far row's holding drawn, own wells for the dispersed form only and a row's water a knob, the converted feet removed. **Round 2**: CHANGES - the compact holding cited to homesteads/156 and labeled; plan D9's id. **Round 3**: FAITHFUL. Amendment 3 is accepted.

**Amendment 4** (2026-09-29, the record's own finding): FR-019's door clause and SC-008's door check scoped to the LINEAR
row. As written they held every grove farm, and the first cohort with the check found every dispersed farm failing it -
a dispersed hamlet lays no lanes at all, by homesteads/150's finding ("a dispersed hamlet has no interconnected lane
network to be reached by. The rule in the entry above is a rule about nucleated settlements"). The row farm's door
remains held (FR-017, FR-019).

**Amendment 4, round 1** (spec-fidelity-verify, MODE 3, 2026-09-29): the narrowing FAITHFUL - the GM never asked for the
door clause, and homesteads/150 says a dispersed hamlet has no network to be reached by; one plan line (D19) to bring into
line, done. Amendment 4 is accepted.

**Amendment 5** (2026-09-30, the record's own finding): FR-018 and SC-008 - a dispersed farm's own water is a knob. The R7
check of homesteads/200 found the own well unattested and a source that attests the other form: on the Tonami fan "the
water table was deep and wells were hard to dig, so in many areas a small channel was led into the house's grounds and
used for cooking, washing and drinking water" (tonami-sankyoson-museum, translated). The GM's standing rule (2026-09-29:
"we should try to find out from our research what types of settlement layouts existed, and then have our settlements
reflect the range ... we make a tunable knob for the various possibilities") makes it a knob: the channel, attested,
and the well, the reading of "many areas".

**Amendment 5, round 1** (spec-fidelity-verify, MODE 3, 2026-09-30): CHANGES - faithful in substance; the nearest source
and the brook to be labeled, plan D18/D19 and T16 to carry the knob, and homesteads/200's map paragraph to be owed by a
task. **Round 2**: CHANGES - the brook standing for the irrigation water labeled a GUESS. **Round 3**: FAITHFUL.
Amendment 5 is accepted. The reviewer's aside for the GM: the source ties the channel to the fan's deep water table, so
if the generator ever knows its ground, the ground could set the value rather than an even roll.

**Amendment 6** (2026-09-30, the plan review's finding): FR-018 - a farm's channel may be led off another farm's channel.
The plan review of D18 ruled the branching outside FR-018 (its water is "the nearest drawn ditch or the brook") and asked
for the measurement: without it, Audit-19's farms drew 1 channel in 11, the first walling the field's head off from the
rest; with it, 11 in 11. Labeled a GUESS - whether neighbors shared a channel no page read says.

**Amendment 7** (2026-09-30, the GM's decision): feature 287 ("placer guarantees") landed on main while this feature was
open, and its seating, access tree, lane law and web settle were built for the nucleated form alone - the form main
rolled - while this feature's row villages, dispersed farms, farm water and door paths were built on the code 287
replaced. Asked how to land this feature ("Port all of 291", "Land in two parts", "Keep 291's unseated rule"), the GM
chose **"Port all of 291 (Recommended)"**: *"Rebuild row villages and dispersed farms on 287's machinery in this feature,
taking 287's rule: every household seated or the site refused. Then regenerate, gate, review all five maps and run the
cohort."* So FR-013 and FR-016 hold as written - a row, then another street, never ranks - and a row village whose
streets cannot hold every farm on any margin of the ladder is REFUSED by name (`SiteRefused`, 287 plan D2), never
shipped with a farm unseated (the remainder this feature's plan D15 reported is retired). Every requirement of this spec
is otherwise unchanged; what moves is where each is implemented, recorded in the plan (D20).

**Amendment 8** (2026-09-30, an exception put to `spec-fidelity` under constitution XVI - FAITHFUL, on conditions): FR-019
and SC-008. FR-019's front door is "the open side of its grove"; under amendment 7 a door path is a tree lane the settle
never cuts, so it must keep the whole lane law as drawn, and on cohort seeds 11, 23 and 904 (measured 2026-09-30) a
far-row farm - fronting its own holding, its grove's deep bands between house and street (research homesteads/159) - had
no lawful path from the front-door point, which stood beyond the door reach (`DOOR_REACH_FT`) from any way. FR-019 is kept by a way
reaching the farm's dooryard on an OPEN side of its grove: the front door, or - only where no lawful way leaves the front -
a flank of the dooryard facing no band of the farm's own grove (so a two-sided grove's; a three- or four-sided grove's farm
still needs its front, and a site where none is lawful is refused), with open ground between that flank and the front
door. Each such farm is recorded (`meta.door_flanks`, the lane's `from_flank`), and SC-008's door check counts a farm so
reached. Alternatives priced and refused: the flank path begun at the front door (doubles back; the law refuses it);
refusing such sites (most both-sides rows); turning far-row farms to face their street (against homesteads/159). To be
raised with the GM once the implementation works.

**Amendment 9** (2026-09-30, the GM's ruling): FR-019's door clause and SC-008's door check are DROPPED. The clause came
from a settlement-review finding written into the spec by amendment 3 (a Kashikawa farm whose only lane stopped short of
its door), not from the record - homesteads/715 finds the grove leaving the front OPEN, a finding about the grove's
shape, and nothing read says a way must arrive at the front door (amendment 4's review had already noted the GM never
asked for it). The GM, asked: "Yes, just drop the door clause because there is no actual reason to have that there."
A row farm is held to what stands without it: reached by the lane network (feature 287's rule, the settle's
`unreached_houses`) and its way ending on its own street (FR-017, `row_rules`). Amendment 8's exception is moot; the flank
of the dooryard stays in the door-path search as a preference after the front, and `row_rules.doors_unreached` and
`reached_from_a_flank` are removed.

