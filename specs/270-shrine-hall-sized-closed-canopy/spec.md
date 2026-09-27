# Feature 270 - crowns may overlap; the shrine hall sized from the research

**Feature Branch**: `270-shrine-hall-sized-closed-canopy` (no branch; `export SPECIFY_FEATURE=270-shrine-hall-sized-closed-canopy`)

**Created**: 2026-09-27

**Status**: done - FAITHFUL at round 2; plan CLEAR at round 4; all tasks ticked

**Input**: the GM's two answers of 2026-09-27, verbatim in [`request.md`](request.md).

## Summary

Two answers to feature 268's closing questions. **Crowns may overlap**: the GM's 2026-09-20 rule ("an automated
check to prevent trees from overlapping with other things") was never meant to stop tree crowns overlapping one
another, and the pack audit's `trees_overlap` does - so a shrine grove draws as spaced trees (42% canopy) where a
kept wood has a closed canopy. **The hall is sized from the research**: the Hoshigaoka shrine hall's 60 by 48 ft
footprint came from the village map's glyph, not from the GM, so it is presumed not a real measurement and the
building is sized from the record's measured bands (religion-and-death 120: a village hall about 20 to 35 ft on a
side; the one-roof hall-and-dwelling building 2,100 to 3,600 sq ft, its depth 26 to 43 ft at the one attested
example), on the sheet and on the village map together. (Figures observed 2026-09-27; method: read from the
record's question 120 and the pack audit's report on the 268 sheet; research.md R1-R3.)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tree crowns may overlap one another (Priority: P1)

A sheet's canopies may overlap each other; the audit still reports a tree drawn on top of another (a duplicated
tree - the case the GM's 2026-09-20 rule was written against, feature 257's "two lie on top of each other") and a
crown over a building, a way, a well, a wall or fence, furniture, a glyph, a tub or a caption.

**Independent Test**: the audit on a sheet whose crowns partly overlap each other and nothing else reports
nothing; a concentric pair is reported as a duplicated tree; a crown over a building or a caption is reported.

**Acceptance Scenarios**:

1. **Given** two partly overlapping canopies on open ground, **When** the pack audit runs, **Then** it reports
   nothing; **Given** two trees whose trunks stand closer than trees can grow, **Then** it reports a duplicated tree.
2. **Given** a canopy over a building or a caption, **When** the audit runs, **Then** it is reported as before.

### User Story 2 - The shrine's grove is a closed wood (Priority: P1)

The Hoshigaoka grove is redrawn with overlapping crowns so it reads as a kept wood, on the sheet and on the
village map alike, the two still matching tree for tree.

**Independent Test**: the canopy covers most of the grove's ground; `matches_map` passes.

### User Story 3 - The hall is sized from the research (Priority: P1)

The Hoshigaoka hall-and-dwelling is drawn at a footprint set from the record's bands - its hall end within the
village-hall band, the whole within the one-roof band and no deeper than the attested depth - on the sheet and on
the village map; the program's rule says a building's size on a sheet comes from the research unless the GM gave
it, never from a map glyph; the notes say what set each dimension and label it.

**Independent Test**: the size-audit finds the building inside the record's bands; the program check passes;
`matches_map` passes with the map's building at the new footprint.

**Acceptance Scenarios**:

1. **Given** the redrawn sheet, **When** the building is measured, **Then** its footprint, its hall end and its
   depth each sit inside the record's bands and the notes label each (accurate as a band, the value a guess).
2. **Given** the village map, **When** its shrine is read, **Then** its footprint is the sheet's and the arches,
   the forecourt, the basin and the grove follow the new face.

### Edge Cases

- The magistracy sheets' trees: removing the crown-on-crown test affects every sheet; nothing else about their
  trees changes.
- The one-roof form stays (the GM, 2026-09-19); the hall stays on the map's approach axis.
- The frozen village map is edited by hand as in feature 268.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `trees_overlap` MUST NOT report canopies that merely overlap each other; it MUST still report a
  duplicated tree (two trunks closer than trees can grow - the threshold taken from the record or labeled a guess,
  never left unsourced) and a canopy over anything else it covered; its test (rewritten, not deleted) and docs say so.
- **FR-002**: The Hoshigaoka grove MUST be redrawn with overlapping crowns so the canopy covers most of the
  grove's ground outside the clearing, the approach, the path and the well, on the sheet and the village map,
  matching tree for tree.
- **FR-003**: The Hoshigaoka hall-and-dwelling MUST be drawn at a footprint set from the record's measured bands
  (question 120), its hall end inside the village-hall band, the whole inside the one-roof band, its depth inside
  the attested depth; the 60 by 48 ft map footprint is not used. The village map's shrine glyph and manifest MUST
  be brought to it, with the arches, the forecourt, the basin, the clearing and the grove following. (Figures
  observed 2026-09-27; method: read off the sheet's notes and the map manifest.)
- **FR-004**: `buildings.md` and the program MUST say that a building's dimensions on a sheet come from the
  research unless the GM gave them, and are never taken from a map's glyph as a measurement; the sheet's notes label each
  dimension with what set it.
- **FR-005**: The redrawn sheet MUST pass the pack audit, `size-audit` and `building-review`, and the map's edited
  region `settlement-review`, each ledgered.

### Key Entities

- The pack audit's `trees_overlap`; the country-shrine program; the Hoshigaoka sheet and the frozen village map.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): no finding for crowns that overlap without duplicating a tree on any pool sheet; a
  duplicated tree and every other `trees_overlap` finding kind still fire.
- **SC-002** (FR-002): the grove's canopy covers most of the ground it is allowed to cover, measured on the layout.
- **SC-003** (FR-003, FR-004): the hall's footprint, hall end and depth each inside the record's bands, stated
  with their source in the notes.
- **SC-004** (spec-wide; FR-005): `make done` green; every review pass a ledger row.

## Assumptions

- "Size the shrine based on our actual research" covers the hall-and-dwelling building (the sanctuary is already
  at its measured 6 ft); the precinct's size stays as feature 268 set it except where the new face moves the
  forecourt and the arches.

## Review history

- Round 1 (spec-fidelity, MODE 2, 2026-09-27): CHANGES REQUIRED, one item - FR-001 dropped the one tree-on-tree
  case the GM's 2026-09-20 rule was written against (feature 257: "two lie on top of each other"). Applied: FR-001,
  SC-001 and User Story 1 keep a duplicated-tree finding (two trunks closer than trees can grow, the threshold
  sourced or labeled a guess) while letting crowns overlap; the test is rewritten, not deleted. Also taken: FR-004
  "never taken from a map's glyph as a measurement".
