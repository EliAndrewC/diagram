# Feature Specification: A sheet on a map matches the map, and trees overlap nothing

**Feature**: `257-sheet-matches-map` | **Created**: 2026-09-20 | **Status**: Draft
**Input**: the GM's message of 2026-09-20, verbatim in [`request.md`](request.md), after reading the
Hoshigaoka country-shrine sheet of feature 254.

## Summary

Two things the GM asked for, in their order.

1. **An automated check that trees do not overlap other things.** On the Hoshigaoka shrine sheet the
   grove's canopies straddle the precinct fence, sit on the fence line inside it, and two lie on top
   of each other. No check in the Mode A registry looks at a tree: the shared overlap check reads
   built footprints only. The check is shared - every building type may draw a tree - and it proves
   itself on a red fixture and on the unfixed sheet before the sheet is fixed.

2. **A sheet whose subject already stands on a settlement map matches that map.** The country shrine
   is the first Mode A subject drawn for a building that a Mode B map already shows - the Hoshigaoka
   village map draws the shrine hall, its arch, its own well, the swept ground around it, the
   connector lane to the east and the water-mouth grove to the north-east; it draws no trees and no
   graveyard beside the shrine. The sheet drew a grove around the precinct and a burial ground beside
   it, because the program says a shrine has both. The GM: *"we shold make the diagram view match
   what is shown on the larger map of Hoshigaoka, e.g. we shouldn't put any trees or graveyard on the
   shrine diagram if those are not in correspnding places on the village map."* So a sheet declares
   the map its subject stands on, a check reads that map's recorded manifest and holds the sheet to
   it in both directions - nothing on the sheet that the map does not show there, nothing the map
   shows inside the sheet's frame that the sheet leaves out - and the Hoshigaoka sheet is redrawn to
   match: no grove, no burial ground, the hall at the footprint the map draws, the arch and the well
   where the map puts them.

The map is the canon for the site. Where the program's research says one thing and the map another
(the shrine's basin beside the approach; the map's well behind the hall), the map wins on that sheet
and the notes say so: the sheet is a close-up of a place the GM has already drawn.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - No tree overlaps anything on a Mode A sheet (Priority: P1)

The GM opens any Mode A sheet and no tree canopy lies across a building, a fence, a wall, a well, a
tub, a marker or a label; a tree stands on open ground. When a session draws a canopy over a fence
line, the audit names the tree and the thing it covers before the sheet reaches review.

**Why this priority**: the GM's first sentence; it fires on the sheet they were looking at.

**Independent Test**: run the audit on a fixture whose one tree covers a fence line and a building
corner - it names both; run it on every live sheet - it is quiet; delete the check - the fixture test
goes red.

**Acceptance Scenarios**:

1. **Given** a sheet with a tree canopy across the precinct fence, **When** the audit runs, **Then** it
   reports the tree, what it overlaps and by how much, and names the fix.
2. **Given** a tree standing wholly on open ground (the precinct's gravel, a court, a garden bed),
   **When** the audit runs, **Then** the ground is not an overlap.
3. **Given** two canopies drawn on top of each other, **When** the audit runs, **Then** it reports a
   duplicated tree.
4. **Given** a magistracy sheet with garden trees, **When** the sweep runs, **Then** the same check
   runs on it - the check is shared, not the shrine's.

### User Story 2 - A sheet of a building on a map matches the map (Priority: P1)

The GM holds the Hoshigaoka shrine sheet beside the Hoshigaoka village map and sees the same place:
the hall the map draws, at its size and facing; the arch in front of it where the map's torii
stands; the well where the map's well stands; bare swept ground around, because that is what the map
shows there; no grove and no graveyard, because the map has neither beside the shrine. A sheet
declares which map its subject stands on, and the audit holds it to that map.

**Why this priority**: the GM's second sentence, and the rule every later sheet of a mapped building
follows.

**Independent Test**: point the check at the sheet as it was before this feature - it names the grove
trees with no tree on the map, the burial ground with no cemetery, the hall's size against the map's;
point it at the redrawn sheet - it is quiet; point it at a sheet with no declaration - it says the
sheet is on no map and checks nothing.

**Acceptance Scenarios**:

1. **Given** a sheet whose notes declare the map and the subject's place on it, **When** the audit
   runs, **Then** every sheet feature of a class the map records (a tree, a burial ground, a well, an
   arch, water, a lane, another building) has a counterpart on the map at the corresponding place, or
   is named.
2. **Given** the same sheet, **When** the audit runs, **Then** every map feature of those classes that
   falls inside the sheet's frame has a counterpart on the sheet, or is named.
3. **Given** the same sheet, **When** the audit runs, **Then** the subject's footprint on the sheet is
   the footprint the map draws, within the map's own resolution - one map px per side - or is named.
4. **Given** a sheet whose notes declare no map, **When** the audit runs, **Then** the check reports
   that the sheet is on no map and nothing else.
5. **Given** the redrawn Hoshigaoka sheet, **When** the GM compares it with the village map, **Then**
   nothing stands on the sheet that the map does not show there, and the notes say which program
   items the map overrode and why.

### Edge Cases

- A sheet's frame reaches a map feature that is drawn at a scale the sheet cannot show (a lane's worn
  track, a scrub scatter): the check compares CLASSES the sheet draws as features (a lane is a
  feature; scatter is not) - the class table is the declaration of what corresponds.
- A map feature partly inside the frame (a lane crossing one corner): it counts as inside when any
  part of it lies inside the frame.
- The subject on the map is a glyph (the village map's shrine is a hall glyph with its arch, not a
  plan): the correspondence is of position, size and facing, never of interior detail.
- The map manifest is regenerated and the subject moves: the sheet's declaration names the manifest
  and the subject's map position, and the check reads the manifest at run time, so a moved subject
  fails the sheet, which is the point.
- A tree canopy inside a burial ground: the burial ground's markers are furniture, so a canopy over
  them is an overlap; a canopy on the plot's bare ground is not.
- Two sheets of subjects on the same map: each declares its own position; nothing is shared.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 - a tree is known by its drawing.** A Mode A sheet draws a tree as a canopy circle in the
  vocabulary's canopy green (the fill every pool sheet already uses for a tree), and the audit's
  parser classifies a circle as a tree by that fill - its own or its group's - or by standing in a
  group marked `id="trees"`. So the sheets drawn before this feature carry trees the check reads
  without a retrofit, and a canopy drawn outside any group is still a tree; a sheet that draws no
  canopy has no trees. The vocabulary in `buildings.md` names the fill.
- **FR-002 - the tree-overlap check, shared.** A registered check, in the shared layer, reports every
  tree canopy that overlaps a thing that is not open ground: a built footprint, a piece of
  furniture (a privy, a door, a marker, a board, a mat), a wall or fence stroke, a point glyph (a
  well, a tub, a basin), a text label, or another tree - with what it overlaps and by how much in
  feet. Open ground (the precinct interior, a court, a garden bed, a plot's earth) is where a tree
  stands and never an overlap. Two canopies may touch and no more: the touching tolerance is the one
  the built-footprint overlap check already uses, not a second number. The check names its fix. It
  has a red fixture on which it fires, and it fires on the Hoshigaoka sheet as committed before this
  feature (its canopies straddle the fence line and two lie on each other).
- **FR-003 - a sheet declares the map its subject stands on.** The sheet's notes file carries one
  line, `**On map**: <the map's recorded manifest, by path> - <the subject's class> at (<x>, <y>)`,
  naming the Mode B map and the subject's position in that map's own coordinates. The manifest is
  the map's recorded output (the JSON the pool keeps beside every map), never the generator re-run.
  A sheet whose subject stands on no map carries no such line.
- **FR-004 - the map-correspondence check, shared.** A registered check, in the shared layer, that on
  a sheet declaring a map (a) maps the sheet's frame and every feature of a corresponding class into
  the map's coordinates through the subject's position and the two scales, (b) reports every sheet
  feature of a corresponding class with no map counterpart within the map's drawing grain, (c)
  reports every map feature of a corresponding class inside the sheet's frame with no sheet
  counterpart within that grain, and (d) reports the subject's footprint when a side differs from the
  map's by more than the map's own resolution - one map px - because the map records a footprint
  to the pixel and a sheet can draw it exactly; the grain is for positions, which the map places
  by search. The corresponding classes are a table the check owns:
  trees to the map's tree crowns, grove clumps and forest; a burial ground to its cemeteries; a
  water point - a well or a purification basin, one class, because the map's shrine well IS the
  shrine's ablution water - to its wells; an arch to its torii; water to its streams, ponds and
  channels; a lane to its lanes; any other building to its houses, buildings, storehouses, byres and
  sheds. A class the map cannot record (a fence, a sanctuary, a garden bed, a privy, a tub) is not in
  the table and the map's silence about it is not evidence. The grain is a
  measurement (research.md R1), never a remembered number.
- **FR-005 - a sheet on no map is said to be on no map.** On a sheet with no declaration the check
  reports "on no map" and nothing else; a declaration that names a manifest that does not exist, or
  a position at which the manifest has no feature of the named class, is a finding.
- **FR-006 - the Hoshigaoka sheet matches the Hoshigaoka map.** The country-shrine exemplar is redrawn
  to what the village map shows at the shrine: the hall at the map's footprint and facing, the arch
  where the map's torii stands, the shrine's one water point where the map's well stands - behind
  the hall on its axis, so the fence runs north far enough to hold it, and no second water point
  beside the approach - swept ground around, no grove and no burial ground. Its frame is stated in
  the notes and shows what the map shows there and nothing the map does not: 60 ft in front of the
  arch to 20 ft behind the well, and 100 ft either side of the axis, so the connector lane (nearest
  148 ft from the arch, 112 to 172 ft east of the axis), the water-mouth grove, the crescent pond and
  the nearest byre stay outside it (research.md R3). Its notes declare the map (FR-003) and say, item by item, which
  program items the map overrode (the grove, the burial ground, the water point's place) and that
  the map is the canon for the site. The redrawn sheet passes every registered check, is reviewed by `building-review` and
  `size-audit`, and the passes are ledgered.
- **FR-007 - the rule is written where the next sheet is drawn.** `buildings.md` states, under its
  surroundings rule and its "Adding a building type" procedure, that a sheet of a subject a settlement
  map already draws declares the map and matches it, program items included; the country-shrine
  program's site knob says the same; and the `building-review` agent compares a declared map with
  the sheet as one of its passes.
- **FR-008 - the gate holds both.** The sweep over every live Mode A sheet runs both checks; each has
  a red fixture the registry test proves it fires on; the check code is covered in full; the audit
  report prints both in registry order.
- **FR-009 - the map does not move.** Nothing on the Hoshigaoka village map changes for this feature:
  the sheet follows the map, never the reverse. Where the map's own generator says one thing and its
  recorded manifest another, the manifest - what the map shows - is what the sheet matches, and the
  disagreement is reported to the GM, not fixed here.

### Key Entities

- **Tree canopy**: a circle in the vocabulary's canopy green, by its own fill or its group's, or a
  circle in a group marked `id="trees"`; a thing the tree-overlap check compares with everything
  that is not open ground.
- **Map declaration**: the `**On map**:` line of a sheet's notes - a manifest path, a subject class,
  a map position.
- **Correspondence class**: one row of the check's table - a sheet class (by declared id or by the
  parser's classification) and the manifest keys it corresponds to.
- **Drawing grain**: the distance within which a sheet feature and a map feature are the same feature,
  measured from the map's own placement (research.md R1).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: (FR-001, FR-002, FR-008) the tree-overlap check fires on its red fixture and on the
  Hoshigaoka sheet as committed before this feature, naming the fence and the doubled tree; after the
  redraw every live Mode A sheet passes it; deleting the check turns the fixture test red.
- **SC-002**: (FR-003, FR-004, FR-005, FR-008) the map check fires on its red fixture and on the
  pre-redraw Hoshigaoka sheet - the grove with no tree on the map, the burial ground with no
  cemetery, the hall's size against the map's; the redrawn sheet passes; every sheet with no
  declaration reports "on no map" and nothing else.
- **SC-003**: (FR-006, FR-009) laid over the village map at the shrine, every feature the redrawn
  sheet draws of a corresponding class has its counterpart on the map and every map feature inside
  the sheet's frame has its counterpart on the sheet; the village map's manifest is byte-identical
  before and after.
- **SC-004**: (FR-007, FR-008) the rule stands in `buildings.md`, the shrine program and the review
  agent; `make done` is green with both checks covered in full; the sweep's cost is re-measured and
  recorded (`measurements.json`, `m:sweep-cost`).

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| The map is the canon for a sheet whose subject it draws: the sheet's grove, burial ground and water point follow the map, not the program | deliberate deviation from the program's research (the temizuya beside the approach; the grove around the sanctuary) | the GM, 2026-09-20: the diagram view matches what is shown on the larger map | `buildings.md` (the rule), the sheet's notes (the overrides, item by item), `programs.md` knob 4 |
| A tree may stand on open ground and on nothing else, another tree included | map drawing convention | a canopy is drawn over the ground it grows from; over a building, a fence, a label or another canopy it reads as a mistake, which is what the GM saw - the GM, 2026-09-20, "trees ... overlapping with other things" | the check's docstring; `buildings.md` |
| Correspondence is judged within the map's own drawing grain, measured | map drawing convention | a settlement map places a glyph to a few pixels at its scale; a sheet drawn at the building scale cannot be held tighter than the map that placed the thing | research.md R1; the check's docstring |
| The hall on the sheet takes the map's footprint | deliberate deviation from the program's own proportions, on the GM's word of 2026-09-20 | the map's block is the building the GM drew; the one-roof band still holds it, which corroborates but does not decide | the sheet's notes; the record's country-shrine section unchanged |

## Assumptions

- The map is `legacy-hand-authored-pool/villages/hoshigaoka`, frozen hand-authored; its recorded
  manifest is `hoshigaoka.json` beside it, at 2 ft per map pixel (`meta.ftpx`), and its shrine is
  the `religious` entry of kind `shrine` at map (392, 1074), a 30 by 24 px block - 60 by 48 ft.
- The map draws ONE torii in front of the shrine (its manifest records one; its generator's comment
  promises seven) - the sheet matches the one drawn; the disagreement is reported to the GM (FR-009).
- The map's shrine well stands 108 ft due north of the hall's center, 84 ft behind the hall's rear
  face; the redrawn sheet's fence and frame extend north to hold it (research.md R3).
- The map's connector lane, water-mouth grove, crescent pond, nearest byre and the village graveyard
  all lie outside the sheet's stated frame - 100 ft either side of the axis, from 60 ft in front of
  the arch to 20 ft behind the well (research.md R3); the swept clearing the map records around the
  shrine covers the whole of that frame.
- The magistracy sheets stand on no declared map today (the county towns are legacy maps not yet
  matched); they carry no declaration and the check says so; matching them is a later feature.
- The audit stays a hand-drawn sheet's tool; the check reads a recorded manifest and never runs a
  generator.

## Review history

- Round 1 (2026-09-20, `spec-fidelity`, Opus): CHANGES REQUIRED, five items, all applied. (1) FR-001
  declared trees by a group id no live sheet carried, so the check could not fire on the sheet the GM
  saw - a tree is now known by its drawing (the canopy fill), the group id an alternative. (2) FR-002
  left tree-on-tree overlap to a duplicate rule with an unsourced threshold - a canopy may now touch
  another and no more, with the built-footprint check's own touching tolerance. (3) The map cannot
  record a basin, so it could not override one - the basin and the well are one class, the water
  point, and FR-006 says the shrine's one water point stands where the map's well stands. (4) The
  frame assumption could not hold the map's well far behind the hall - the frame is stated and
  the fence runs north to the well. (5) Decisions row 4 reclassed from "historically accurate" to a
  deliberate deviation on the GM's word. The reviewer's aside for the GM (the seven-arch sando drawn
  as one arch since the count re-roll; the well far behind the hall) is carried to the writeup.
- Round 2 (2026-09-20, `spec-fidelity`, Opus): CHANGES REQUIRED, four items, all applied. (1) Key
  Entities still defined a tree by the group id round 1 struck - now FR-001's definition. (2) The
  frame's south edge named "the lane's edge in front of the arch", a landmark the map does not have
  there - now stated as research.md R3 states it, with the lane's true distances. (3) R3's tree and grove
  figures were wrong by about a hundred feet - re-derived from the manifest (the nearest crown,
  clump and grove edge, each stated in R3), with the frame-to-outline clearance stated and why it is
  not the check's concern (the outline is not a feature the check reads).
  (4) the grain measurement's recorded command did not re-run - now one command.
- Round 3 (2026-09-20, `spec-fidelity-verify`, Opus): CHANGES REQUIRED, two items, both applied.
  (1) R3's new clearance clause mixed two axes (a center distance less the half-width) - now the
  measured clearances to the frame itself, and the edge named right. (2) The measurement commands
  chained with `&&`, which the figures script (no shell) cannot run - now one command each; the
  baseline names its commit. Items 1 and 2 of round 2 confirmed RESOLVED.
