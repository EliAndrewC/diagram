# Feature 298 - tiled ground cover

**Feature Branch**: none (main, in the clone `diagram-performance`)
**Created**: 2026-10-01
**Status**: Accepted - FAITHFUL at round 3 (2026-10-01)
**Request**: [`request.md`](request.md) - the GM's words verbatim: drawing "individual blades of grass and lines for marshland
and scrubland" serves no purpose that individual trees do; "instead of then drawing individual glyphs within that, can we perhaps
have some tiled pattern where a relatively small block of background is then repeated within that, or even like set as the
background image for that shape?"; "I don't mind the visual repetition. And I don't mind the issue about edges"; the zone's
contents handled by layering ("as long as we are using Z indexing ... to make sure that that thing appears on top"); bamboo
"would we be able to use a similar approach here?"; swept clearings "worst case scenario, we could lay that down as its own
rendered thing over top of the background"; and "please create a spec kit feature for this and then work the feature from start
to finish and let me know when it has landed back on main."
**Predecessors**: 223/224/225 (the blade buckets, the off-map cull, the merged blade paths), 287 (the marsh re-throw), 297.

## Summary

Three ground covers are drawn today as thousands of individual glyphs that stand for an area, not for objects: the scrub and
rough-grazing grass (tufts of blades and brush dots, `settlement/land/cover.py`), the marsh (reed tufts, glints and a pale tint,
`settlement/land/wet.py`) and the bamboo stand (paired culm marks, `settlement/homestead_parts/stands.py`). Grass and reeds are
55-68% of four pool hamlets' SVGs (27% of Kuwabata's) and 4.8 MB of Kashikawa's 20.5 MB page (observed 2026-10-01, method: a
census of the pool SVGs and page by stroke color; research R1). Each becomes ONE shape per zone filled with a repeating tile of the same
glyphs, at the same density and colors, drawn where the GM asked: the scrub and the marsh at the bottom of the stack, just above
the land, so everything standing in them draws over them. Trees stay individual - the GM: drawing individual trees "serves a
useful purpose". The scatters that threw, tested and culled the glyphs one at a time go, and the feature measures what that buys
in generation, finish and page time, which is what the GM cares about ("the size of the SVG file likely reflects a larger inputs
size that likely slows us down algorithmically").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Scrub and marsh are a tiled fill under everything (Priority: P1)

**Why this priority**: the GM's first ask, and nearly all of the ink.

**Independent Test**: regenerate the five pool hamlets; count the glyph elements and read the maps.

**Acceptance Scenarios**:

1. **Given** a hamlet with scrub, **When** it is generated, **Then** each scrub zone is one filled shape whose fill is a repeating
   tile of grass tufts and brush dots, and no individual blade or brush dot is drawn.
2. **Given** a hamlet with marsh, **When** it is generated, **Then** each marsh is one filled shape whose fill is a repeating tile
   of reed tufts, glints and the pale tint, and no individual reed, glint or tint mark is drawn.
3. **Given** a lane, house, well, pond, field, tree or any other feature inside a scrub zone or a marsh, **When** the map is drawn,
   **Then** that feature draws over the fill (the fill is below it in the stack).
4. **Given** ground the scatter kept bare inside a zone that nothing draws over (a swept clearing, a verge, the hamlet's own ground),
   **When** the map is drawn, **Then** no fill shows there.

### User Story 2 - Bamboo stands are a tiled fill (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a bamboo stand, **When** it is generated, **Then** it is one shape filled with a repeating tile of the culm mark,
   at the stand's present spacing, and no individual stand mark is drawn.
2. **Given** a household's small bamboo strip, **When** the map is drawn, **Then** it still reads as bamboo (the tile is small
   enough that a strip shows several marks).

### User Story 3 - What the change buys is measured (Priority: P1)

**Acceptance Scenarios**:

1. **Given** the base (`/tmp/base298`) and the clone, **When** the five pool hamlets are regenerated back to back, **Then** the
   SVG and page sizes, the regeneration time, the hinterland stage and the stage total are recorded for each, before and after.

### Edge Cases

- A scrub zone overlapping a marsh: the marsh's ground is taken out of the scrub's shape, so the two fills do not overlap (today the
  grass thins into the marsh over a feather; the GM does not mind the edge).
- A zone left with no area once the bare ground is taken out draws nothing.
- Water drawn translucent over a marsh: the water's own ground is taken out of the marsh's shape, as the reeds kept off it.
- The scraggly pines in scrub are trees and stay individual; the woodland's crowns stay individual; the grove's windbreak bamboo
  (culms under the crowns of a tree grove, not a stand) stays individual.
- A zone partly off the map: the shape is clipped by the map's frame as any shape is; nothing needs culling glyph by glyph.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each scrub and rough-grazing zone (the commons' grass, every role that throws blades today) MUST be drawn as one shape
  per zone filled with a repeating tile of grass tufts and brush dots - the same glyphs, colors, stroke and density per area as
  today's scatter - in place of the individual blades and dots.
- **FR-002**: Each marsh MUST be drawn as one shape per marsh filled with a repeating tile of reed tufts, glints and the pale tint,
  as FR-001, in place of the individual reeds, glints and tint marks, and the marsh's re-throw (`offer_rethrow` / `throw_again`)
  goes with them.
- **FR-003**: Each bamboo stand (`bamboo_stand`) MUST be drawn as one shape filled with a repeating tile of the culm mark at the
  stand's present spacing, in place of the individual marks.
- **FR-004**: The scrub and marsh fills MUST be drawn at the bottom of the stack, immediately above the land, so every feature
  standing in them draws over them. The bamboo stand's fill stays at the stand's present place in the stack: it draws exactly where
  today's marks draw, at the same place, so nothing that draws over or under a stand changes.
- **FR-005**: A zone's filled shape MUST leave out the ground its scatter keeps bare today and that nothing draws over: for scrub the
  hard keep-outs (`_commons_keep`: clearings, the avoided ground, the no-build blocks, the urban halo, the lane verges, the crop
  margin, the watercourse margin) and every marsh; for a marsh, the ground its reeds keep off (dike crests, pond banks,
  watercourses, crescent ponds, the pond). The soft feathers at a zone's rim and into a marsh or wood are not kept (the GM: "I
  don't mind the issue about edges").
- **FR-006**: Trees MUST stay individual: the scrub's scraggly pines, the woodland's crowns, every grove crown, and the windbreak
  grove's bamboo culms.
- **FR-007**: The interactive page MUST keep every highlight and modal it has: scrub, marsh and bamboo highlight by their zone
  shapes; the ink census rules on every new shape (no unclassed ink a class did not have before); the modals' prose describes the
  fill.
- **FR-008**: Every consumer of the individual glyphs MUST be moved to the fill or retired with the glyphs: the page's scrub hit
  region from blade roots, the scatter audit's blade and reed families, the tests that count blades and reeds, the placement-stages
  page, and the docs and research record that describe the glyphs.
- **FR-009**: The pool MUST regenerate and pass the gate at its coverage floor; maps change only in how the three covers are drawn (and
  whatever a removed random draw shifts, within the rules - the GM 2026-09-30: maps "do NOT need to remain identical in output").
- **FR-010**: The measurements of User Story 3 MUST be recorded with their keys or labels, and reported to the GM as measured,
  including any cost that did not go down.

### Key Entities

- **Cover tile**: a `<pattern>` per cover kind and map scale - its glyphs laid once, at the scatter's density.
- **Cover shape**: per zone, the zone's ground minus the bare ground (FR-005), filled with its tile and carrying the zone's class.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-002, FR-003, FR-006): on the five pool hamlets, zero blade, brush-dot, reed, glint, tint or stand-mark
  elements; one cover shape per drawn zone; the scrub's pines, every crown and the windbreak's culms still drawn one by one.
- **SC-002** (FR-004, FR-005): on the five pool hamlets, every scrub and marsh cover shape lies below every non-cover feature in the stack, and no
  scrub or marsh cover shape overlaps a recorded clearing, the avoided ground or a no-build block (a test on the manifests).
- **SC-003** (FR-010): each pool hamlet's SVG and page are smaller than the base's; the regeneration, the hinterland stage and the
  stage total before and after are recorded for each (back to back, fastest of three), whichever way they move.
- **SC-004** (FR-007, FR-008, FR-009): no consumer of the retired glyphs is left (a grep for the blade and reed buckets); `make done` green; the page's census lists no new unclassed ink; scrub, marsh and bamboo still
  highlight.
- **SC-005** (FR-001-FR-005): the GM's look - Kashikawa and Inashiro read with tiled scrub and marsh, everything in them on top;
  a settlement-review of each moved pool map is run (or waived per the GM's 2026-08-29 ruling, recorded).

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Scrub grass and marsh reeds drawn as a repeating tile per zone | map drawing convention | the GM's request; the glyphs stood for an area, not objects | `land/cover.py`, `land/wet.py`, research/vegetation |
| Bamboo stands drawn as a repeating tile | map drawing convention (as the culm mark already was) | the GM's request | `homestead_parts/stands.py` |
| Scrub and marsh fills at the bottom of the stack | map drawing convention | the GM: "Z indexing ... to make sure that that thing appears on top" | the cover splice in `settlement/finish.py` |
| The zones' rim feathers dropped | map drawing convention | the GM: "I don't mind the issue about edges" | the points of change |

## Assumptions

- The tile's repetition is acceptable (the GM: "I don't mind the visual repetition").
- resvg, the page's rasterizer and browsers render `<pattern>` fills; the dry-crop and fallow fills are the precedent.

## Review history

- Round 1 (spec-fidelity, 2026-10-01): CHANGES REQUIRED - SC-002 named every cover shape while FR-004 keeps bamboo in place;
  FR-004's reason rested on an unmeasured claim. Addressed: SC-002 names scrub and marsh (its first clause); FR-004's reason restated.
- Round 2 (spec-fidelity-verify): CHANGES REQUIRED - SC-002's second clause still named every cover shape. Addressed: it names
  scrub and marsh, so SC-002 does in both clauses.
- Round 3 (spec-fidelity-verify): FAITHFUL. Aside: pasture grass is tiled too (FR-001 names every role that throws blades).
