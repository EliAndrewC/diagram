# Feature Specification: The wind is northwest unless a map declares otherwise

**Feature**: `261-northwest-wind-by-default` | **Created**: 2026-09-26 | **Status**: Draft
**Input**: the GM's question about Kashikawa's windbreak and their acceptance of the proposed fix,
verbatim in [`request.md`](request.md).

## Summary

The GM ruled on 2026-08-29 that shelter belts stand on the north and west of a settlement, because the
winter wind blows from the northwest across China, Japan and "Rokugan in most places when the local
geography does not override the regional geography" (`research/vegetation/030-...`). The scripted
hamlet generator never applies that ruling. It decides each map's windward side in two steps, and
neither step uses the northwest:

1. **From the slope.** The windward side is the map's uphill direction, turned 45 degrees either way at
   random (`windward_for`, `WIND_TURNS`). Kashikawa falls to the northeast, so this step could only give
   south, southwest or west.
2. **From wherever the village came to rest.** If the houses end up facing more than about 70 degrees
   away from that wind, the wind is renamed after whatever the cluster's back faces
   (`ways/track.py`, "the site wins"). Kashikawa's cluster settled with its back to the southeast, so
   its manifest says `windward: SE` and its belt stands on the south and east.

The five scripted hamlets are windward W/N (Inashiro), SE (Kashikawa), NW (Kuwabata), S (Mizuguchi)
and NE (Sawada): one in five on the northwest, and that one by accident. The record meanwhile claims
the maps are built "northwest by default", which is false, and the windbreak's pop-up says only
"the windward, high side", which on Kashikawa is neither true nor explained.

This feature does what the GM accepted: **the windward side is the northwest on every map, unless the
map declares a local wind.** Terrain no longer overrides it silently - not the slope, and not the seat.
The village is placed with its back to the wind rather than the wind being renamed to fit the village.
No map in the pool declares a local wind, so every scripted hamlet is re-rolled with its belt on the
north and west.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every map's windbreak is on the north and west (Priority: P1)

The GM opens any scripted hamlet - Kashikawa first - and the windbreak forest stands on the north and
west of the village, as the regional wind demands.

**Why this priority**: it is the defect the GM reported, and "fixed everywhere for now" is the request.

**Independent Test**: re-roll the five scripted hamlets; each manifest records `windward: NW`, and each
map's windbreak stands on the northwest side of its own house cluster.

**Acceptance Scenarios**:

1. **Given** a scripted hamlet whose spec declares no wind, **When** it is generated, **Then** its
   windward side is the northwest, whatever its slope and wherever its cluster is seated.
2. **Given** the five pool hamlets re-rolled, **When** their manifests are read, **Then** every one
   records `windward: NW` and none of their specs declares a wind.
3. **Given** any re-rolled pool hamlet, **When** its windbreak belt is measured against its house
   cluster, **Then** the belt lies on the cluster's northwest side (its center is to the north-west of
   the cluster's center, and the belt covers the cluster's north-west fringe).
4. **Given** a hamlet whose best seat by slope alone would face away from the northwest, **When** it is
   generated, **Then** the seat search places the cluster with its back to the northwest instead, and
   the recorded wind is never changed to match a seat.

---

### User Story 2 - A local wind is a declaration, never an accident (Priority: P1)

A future map in a valley whose local wind is not the regional one declares that wind on its spec, and
only then does its windbreak move.

**Why this priority**: it is the rule the GM chose ("only when declared"), and it is what keeps the
override from creeping back.

**Independent Test**: generate a test hamlet with a declared local wind; its windward is exactly the
declared quarter; generate it again without the declaration; its windward is the northwest.

**Acceptance Scenarios**:

1. **Given** a spec that declares a windward quarter, **When** the hamlet is generated, **Then** that
   quarter is the windward side and nothing in generation changes it.
2. **Given** no declaration, **When** the hamlet is generated, **Then** no stage - plan, seat, ways,
   hinterland - derives, rolls or rewrites the wind.
3. **Given** the manifest of any generated hamlet, **When** it is read, **Then** it records whether the
   wind was the regional default or a declared local wind.

---

### User Story 3 - The map explains its windbreak's side (Priority: P2)

The GM, or a player, clicks the windbreak on a map and is told which side it stands on and why.

**Why this priority**: the GM's complaint was partly "I don't see any explanation for that".

**Acceptance Scenarios**:

1. **Given** a map with the default wind, **When** the windbreak's pop-up opens, **Then** it says the
   belt stands on the north and west because the regional winter wind blows from the northwest.
2. **Given** a map with a declared local wind, **When** the windbreak's pop-up opens, **Then** it says
   which side the belt stands on and that the map declares a local wind departing from the regional
   northwest.

---

### User Story 4 - The record says what the generator does (Priority: P2)

The research entry on shelter belts, the map notes and the generator's docs describe the rule the
engine actually follows.

**Acceptance Scenarios**:

1. **Given** `research/vegetation/030-...`, **When** it is read, **Then** it says every map's windward
   side is the northwest unless the map declares a local wind, and its measured arcs are the re-rolled
   maps' own.
2. **Given** the scripted hamlets' notes files and `hamletgen.md`, **When** they are read, **Then** no
   passage still says the wind is derived from the slope or re-read from the seat, except as history
   of what this feature retired where the notes keep a dated log.

### User Story 5 - A village may stand across its brook, and the way crosses it (Priority: P1)

The GM, on the seats the brook refused (request.md, 2026-09-26): *"if we find instead that our placement
algorithm ends up not making it possible to lay out a known-to-be-valid settlement configuration then we should
fix the placement algorithm instead."* The record puts a settlement's own small channel through the middle of the
place (the Harie finding, feature 230), so a hamlet on the far bank from its rice, or astride its brook, is a
valid layout; the engine refused it only because no way could cross the brook.

**Why this priority**: without it Kashikawa and Inashiro cannot face the regional wind at all.

**Independent Test**: a hamlet whose best wind-facing seat stands across the brook from its field is seated
there, and a way crosses the brook squarely to the field on a drawn plank footbridge.

**Acceptance Scenarios**:

1. **Given** a hamlet whose houses stand on one bank and its field on the other, **When** it is generated,
   **Then** at least one way crosses the brook to the field, squarely, and a plank footbridge is drawn at every
   point a way crosses the brook.
2. **Given** a seat the brook runs through, **When** it is generated, **Then** it is not refused for that
   alone; every household reaches a way, and any way the brook divides is joined by a drawn crossing.
3. **Given** any farmstead, **When** it is drawn, **Then** its own buildings, yard, garden and fixtures stand on
   the same bank as its house.
4. **Given** Inashiro at its reference seed 4 and Kashikawa and Mizuguchi at their original seeds (3 and 23), **When**
   they are generated, **Then** they seat facing the northwest wind with every household and a full belt, unless a
   research-supported refusal is measured and recorded.

### User Story 6 - What the reviews of the re-rolled maps found is fixed (Priority: P2)

The five settlement reviews of the re-rolled maps (constitution XIV: fix defects where found) found the copse
spread from a bounding box into a wood that hides the belt, the entrance notice board re-seated away from the
entrance, the belt thinned to one row on its windward face, the brook folding back where it leaves the frame,
the windbreak pop-up naming a side a one-sided belt does not occupy, and notes and declarations that no longer
match the maps.

**Acceptance Scenarios**:

1. **Given** any pool hamlet, **When** it is reviewed, **Then** none of those findings stands.

### Edge Cases

- **A map whose fall makes a northwest-backed seat hard.** Kashikawa falls to the northeast and
  Mizuguchi to the east (both put the northwest margin on a flank), and **Sawada falls to the northwest**
  (`down_deg=225` in the engine's screen convention, 0 = east, 90 = south; `sawada.gen.py`: "land falling
  northwest"), which is the direct opposition: its uphill side is the southeast, so its northwest margin
  is the field's low foot, where the seat's hard constraints (dwellings above the drain, off the wet toe)
  bite. The seat's hard constraints still hold; the seat search must find a margin whose back faces the
  northwest among the margins they allow. The wind is not renamed to rescue a seat.
- **When the placement algorithm cannot draw a valid layout, the algorithm is fixed** (the GM, 2026-09-26/27,
  request.md). A seed is changed only where the research itself rules a layout out, never to route around what the
  engine cannot yet draw; where a seat is refused for an engine limitation, the limitation is removed. Once crossings exist, Kashikawa is measured at its original seed
  3 and Mizuguchi at its original seed 23 - both were re-seeded partly to dodge the brook - and each goes back to its
  original seed unless that measurement records a refusal the research supports, the reason recorded either way.
  Sawada's re-seed (6 -> 24) stands: seed 6 was refused by the drain and the wet toe, rules FR-010 keeps.
- **The brook.** A seat is no longer refused because the brook runs between it and its field or through it; it is
  refused only where no crossing can be drawn. The feature-230 finding that motivated the strike-out - half a
  homestead across the water with no way over - is prevented by keeping each farmstead's own things on its
  house's bank and by drawing the crossing, not by refusing the seat.
- **The belt and the cropland.** A northwest belt must still stand clear of the crop and the dry hem,
  and still pass every rule the belt obeys today (continuous within its sides, embracing the cluster).
- **The homestead groves.** Each farmstead's own grove (the yashikirin L-belt) takes its sides from
  the same windward key, so it moves to the north and west with the village belt.
- **The cohort.** The generator's regression cohort (seeds rolled with no declared wind) changes
  wholesale; its pinned baseline is re-measured, and any new failure is fixed, not pinned.
- **The legacy pool** (18 hand-authored maps) is frozen and never regenerated; it is out of scope. The
  one legacy map that declares a wind (Ubame) declares the northwest.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A scripted hamlet's windward side MUST be the northwest unless its spec declares one.
- **FR-002**: A declared windward side MUST be used as declared; it is the only way a map's wind departs
  from the northwest.
- **FR-003**: The wind MUST NOT be derived from the slope, rolled, or rewritten from the cluster's seat
  at any stage of generation. The slope-derived rule and the seat re-read are retired.
- **FR-004**: The cluster MUST be seated with its back to the windward side; where the slope and the
  wind pull different ways, the wind's pull is strong enough that the chosen seat's back faces within
  45 degrees of the windward bearing on every pool map.
- **FR-005**: No pool map's spec MAY declare a windward side; a test MUST fail if one does.
- **FR-006**: The five scripted hamlets MUST be re-rolled; each MUST record `windward: NW`, each MUST
  have its windbreak on its cluster's northwest side, and each MUST pass the full gate.
- **FR-007**: Each manifest MUST record whether its wind is the regional default or a declared local
  wind.
- **FR-008**: The windbreak's pop-up on each map MUST state the side the belt stands on and why - the
  regional northwest wind, or the map's declared local wind.
- **FR-009**: The research entry, the generator docs (`hamletgen.md`, code comments at the point of
  change) and the five notes files MUST describe the new rule; the record's false "northwest by default"
  claim and its measured arcs are corrected.
- **FR-010**: Every rule the belt and the seat obeyed before (clear of crop, continuous, embracing the
  cluster, dwellings above the drain, no household lost) MUST still hold on every re-rolled map.

- **FR-011**: A way (lane, field path or connector) MUST be able to cross the brook where the layout needs it, and
  crosses it squarely, with a plank footbridge drawn at every crossing of the brook by a way.
- **FR-012**: A seat MUST NOT be refused for standing across the brook from its field or for being run through
  by the brook when a crossing can be drawn; every household reaches a way, the ways on the two banks are joined by
  a drawn crossing, and at least one way reaches the field.
- **FR-013**: Every farmstead's own buildings, yard, garden and fixtures MUST stand on its house's bank.
- **FR-014**: The dooryard copse MUST stand among the houses (within dooryard reach of a house), and the
  against-the-belt copse at the belt's back; neither is spread over the cluster's bounding box.
- **FR-015**: A notice board seated at the entrance MUST stand at the entrance - on the way the connector meets,
  within the entrance band - so every departure passes it.
- **FR-016**: The windbreak MUST keep its researched depth on its windward face (no stretch thinner than the
  record's minimum belt depth), and its side MUST NOT be named in the pop-up as a side it does not occupy.
- **FR-017**: The brook MUST NOT fold back on itself where it leaves the frame.
- **FR-018**: Every pool map's notes, declarations and gen docstring MUST match what the map draws (intake form,
  district direction, the water's story, the layout's move).

### Key Entities

- **Windward side**: the compass quarter the cold wind blows from; the northwest by default, or a
  declared local quarter.
- **Wind source**: whether a map's windward side is the regional default or a declared local wind.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-006): 5 of 5 scripted hamlets record `windward: NW` (today: 1 of 5).
- **SC-002** (FR-004, FR-006): 5 of 5 have their windbreak belt's center to the north-west of their cluster's
  center, with the cluster's back facing within 45 degrees of northwest.
- **SC-003** (FR-002, FR-003, FR-005): 0 pool specs declare a wind; 0 code paths derive or rewrite the wind, and a
  declared wind is used as declared (a test covers each).
- **SC-004** (FR-006, FR-010): every re-rolled map passes the full gate and seats all its declared households.
- **SC-005** (FR-008): every windbreak pop-up names its side and its reason.
- **SC-006** (FR-007): 5 of 5 manifests record where their wind came from.
- **SC-007** (FR-009): 0 passages in the research entry, `hamletgen.md` or the five notes files still say the
  wind is derived from the slope or re-read from the seat, except as a dated closure in a notes log.

- **SC-008** (FR-011, FR-012): 5 of 5 pool hamlets seat facing the northwest - Inashiro at 4, Kuwabata at 21, Sawada
  at 24, and Kashikawa and Mizuguchi at the seeds the Edge Case's measurement settles on (their originals, 3 and 23,
  unless a research-supported refusal is recorded); every way crossing the brook has a plank footbridge; every
  hamlet whose field is across the brook has a way that reaches it.
- **SC-009** (FR-013): 0 farmstead parts across the brook from their house on the pool and the 48-seed cohort.
- **SC-010** (FR-014): on every pool map, every dooryard copse clump stands within dooryard reach of a house.
- **SC-011** (FR-015): on every pool map whose board is seated at the entrance, it stands within the entrance band.
- **SC-012** (FR-016): 0 pool belts thinner than the minimum depth across their windward face; 0 pop-ups naming a
  side the belt does not occupy.
- **SC-013** (FR-017): 0 brook exits turning more than the brook's own bend limit.
- **SC-014** (FR-018, FR-006, FR-010): a settlement-review of every pool map returns PASS, and the cohort has no
  regression against its baseline.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class (accurate / deviation / guess) | Why | Recorded at |
|---|---|---|---|
| The windward side is the northwest on every map by default | accurate (the East Asian winter monsoon; the Sendai *igune* on the north and west because the winter winds are north-northwesterly) + the GM's ruling of 2026-08-29 | the regional wind is the fact the belt communicates; the GM ruled it holds "in most places" | `research/vegetation/030-...` (already cited), `plan.py` at the default |
| A local wind departs from the northwest only when a map declares it | the GM's ruling, 2026-09-26 ("only when declared") | a silent terrain override put Kashikawa's belt on the opposite side with no explanation | `research/vegetation/030-...`, `plan.py`, the windbreak pop-up |
| The slope-derived wind (katabatic drainage) is retired as a default | the GM's ruling, 2026-09-26 | the katabatic finding stays in the record as the reason a map MAY declare a local wind | `research/vegetation/030-...`, `consts.py` where `WIND_TURNS` stood |
| The seat bends to the wind, never the wind to the seat | map convention following the ruling | the belt's side is the information; a renamed wind makes it circular | comment at the seat search and at the retired re-read |
| A way may cross the brook on a plank footbridge; the brook strike-out is retired | accurate (a settlement's own small channel runs through the middle of the place - the Harie finding, feature 230) + the GM's ruling, 2026-09-27 | the strike-out was labeled a guess forced by what the engine could draw | `research/water/270-...`, `seat_cluster`'s penalty comment, `brook_fords` in ways/checks.py |
| Fords every ~160 ft (`m:ford-spacing`, research R7), where the brook bends under 20 degrees | guess, with an absence note | no page read says how often a hamlet bridged its own channel; square crossings are what a plank needs | `research/water/270-...` (absence note), `FORD_SPACING` / `FORD_BEND_DEG` in consts.py |
| A farmstead's own things stand on its house's bank | guess, labeled, with an absence note | the record is silent either way (searched 2026-09-27); a holding split by water reads as two holdings | `research/homesteads/250-...`, `_parts_across_stream` in rolling/fit.py, `across_the_brook` in homesteads/fixtures.py |
| The dooryard copse within 90 ft of a farmhouse (`m:copse-house-reach`, research R8), the against-the-belt copse within 60 ft of the belt | accurate for the form ("in the gaps between the houses"); the reach a calibration | the review found a copse spread into a wood hiding the belt | `COPSE_HOUSE_REACH_FT` / `COPSE_BELT_REACH_FT` in consts.py |
| A brook turns no more than 100 degrees at a vertex | map convention (a drawing defect fixed; the limit a calibration) | a fold at the frame is an artifact of clamped stations, not a stream | `BROOK_MAX_TURN_DEG` in consts.py, `unfold` in water/brook.py |
| The belt holds 30 ft of depth wherever no way, brook or page edge cuts it | accurate (vegetation/020: shallower "reads as a row of blobs") | the review found a windward arm one tree deep | `tests/hamletgen/test_pool_wind.py` |
| An entrance board stands on the approach where a seat there passes every departure | accurate (research/urban-features.html: the kosatsuba broadside to the one way out) | Inashiro's board was squared to a one-farmstead straggler at the outermost join, 87.7 degrees off the track | plan D19, `place_kosatsuba` and the frame re-seat at the entrance filter |
| No homestead grain plot on an archetype that buys its grain in | accurate (research/archetypes.html: the district "abandoned rice to plant mulberry" and buys its grain in) + Kuwabata's GM-confirmed economy | Kuwabata drew six barley, millet and buckwheat plots against its own economy | plan D19, `GRAIN_BOUGHT_IN` in `homesteads/fields.py` |
| A farmstead fixture stands on its house's side of every lane; a shrine with no seat passes to the next house with room | accurate for the shrine and coop (research/homesteads.html: "in a corner of the house plot", "in their yard"); the pass is a map convention (the share counts households, not which) | Mizuguchi drew a coop, a woodpile and its one shrine beyond the lane behind their house | plan D19, `across_a_lane` and `shrine_owed` in `homesteads/fixtures.py` |

## Assumptions

- A map's seed is a roll, not a fact about the place, but a seat refused for an engine limitation is fixed in the
  engine, not re-seeded (the GM, 2026-09-27). Declared fall, water sink and other declared knobs are kept
  (Kashikawa's `brook_side` confluence included).
- Only the scripted hamlet generator derives a wind; the older settlement engine already defaults to the
  northwest and the legacy pool is frozen.

## Review history

- Round 1 (2026-09-26, `spec-fidelity`, Opus): CHANGES REQUIRED, two items, both applied. The round found
  nothing unrequested and nothing kept of the behavior the GM asked to change, and judged FR-004's 45-degree
  bar calibration rather than a loophole (one compass quarter; a seat backing due N or due W is still "north
  and west"). (1) **Sawada's fall was misstated** as southwest; it is northwest (`down_deg=225`, screen
  convention), which makes it the direct-opposition map and the hardest - the Edge Case now says so. (2) **The
  re-seed assumption did not say what happens when no seed works**: the Edge Cases now name the five exits
  that are NOT taken and route the case to the exception check and the GM, and the plan owes a per-map
  measurement at the current seeds before relying on re-seeding.
- Round 2 (2026-09-26, `spec-fidelity`, Opus): **FAITHFUL**. Both round-1 items RESOLVED; the fall bearings of
  all three maps named were re-checked against their generators, and the requirement ids the new Edge Case
  cites point where they should. Accepted.
- Round 3 (2026-09-26, `spec-fidelity`, Opus; the first round after the post-acceptance amendment 36dc70e2,
  read as a verify round on the diff): **FAITHFUL**. The amendment touches only Success Criteria: each SC now
  names the FRs it measures, SC-003 adds "a declared wind is used as declared" (FR-002, already required),
  SC-006 measures FR-007 and SC-007 measures FR-009 with the same dated-log exception that User Story 4
  scenario 2 carried at acceptance. No FR, story, edge case or decision changed; each SC-to-FR mapping was
  checked against the FR text and none measures anything the request did not ask for. SC-007 measures the
  retire-the-old-wording half of FR-009; the corrected arcs half stays carried by FR-009 itself and User
  Story 4 scenario 1, unchanged. Accepted.
- Round 1 of the amendment e8e4cefc (2026-09-27, `spec-fidelity-verify`, Opus; the counter reset by the
  amendment; read as a verify round on the amendment's diff, against request.md's rulings of 2026-09-26/27):
  **CHANGES REQUIRED**. FR-013 (a farmstead's own things on its house's bank) SERVES the ruling: it replaces the
  strike-out's purpose (R4's byre/well/garden across the water) with a placement rule, never a seat refusal, and is
  honestly labeled a guess. US6 and FR-014..FR-018 are within the request under constitution XIV (defects the
  reviews found in the maps this feature re-rolled), each FR mapping to a named finding. Item 1: the re-seeds made
  to dodge the brook are kept. R4 records the brook among the refusals of Kashikawa's wind-facing margins at seed 3,
  and R1 records Mizuguchi's seed-23 seat as divided by the brook (8/12) - the engine limitation US5 removes - while
  Sawada's seed 6 was refused by the drain and wet toe, which FR-010 keeps. The Edge Case's "measures each pool
  hamlet at its current seed" now reads as 8/27/24, and SC-008 pins 8 and 27, so the spec both states the GM's rule
  and ships the route-around. It must require, once crossings exist, measuring Kashikawa at seed 3 and Mizuguchi at
  seed 23, returning each to its original seed unless that measurement records a refusal the research supports, and
  SC-008 and User Story 5 scenario 4 must name the seeds that measurement settles on.
- Round 2 of the amendment (2026-09-27, `spec-fidelity-verify`, Opus; read as a verify round on the diff of
  fec93fdc): **FAITHFUL**. Item 1 RESOLVED: the Edge Case now requires, once crossings exist, measuring Kashikawa at
  its original seed 3 and Mizuguchi at its original seed 23, returning each to it unless the measurement records a
  refusal the research supports, the reason recorded either way; Sawada's 6 -> 24 stands on the drain and wet toe
  (FR-010). SC-008 no longer pins 8 and 27 but names the seeds that measurement settles on; User Story 5 scenario 4
  names Inashiro 4 and the originals 3 and 23 with the same research-supported exception. The changed passages add
  no figure with a unit (seeds are identifiers), nothing unrequested, and contradict no FR, SC or Assumption (the
  Assumptions' "an engine limitation is fixed in the engine, not re-seeded" agrees). plan.md D4 and
  plan-review.json D4 still describe the 8/27 re-seeds; that is for the plan's next review, not a spec finding.
