# Plan - feature 279, the shape of a village shrine's grove

Spec: [`spec.md`](spec.md) (FAITHFUL, round 2). Request: [`request.md`](request.md).

## What the research found (research religion-and-death 129; FR-001)

- **Forms, tied to the ground** (accurate as forms): on a rise or in the paddy plain the wood stands **all
  around**; on a slope it stands **behind** the hall, or **behind and at the sides**. A modern city survey also
  counts a grove **at the sides only**; on the survey's own evidence (burned, replanted, grounds shrunk and built
  on) that form may be what the city left, so it is not drawn - a deliberate deviation, recorded.
- **The outline**: no source gives a grove's plan; the precinct came to be surveyed land, but nothing says the wood
  followed that line. The edge is drawn irregular, the edge of its crowns (a guess). No source shows a straight
  edge, so FR-005's escalation branch does not fire.

## Decisions

- **D1 - the record** (FR-001-FR-003): research 129 on religion-and-death; 124's decision points at it and says
  the wood covers some or nearly all of the precinct; three sources registered (Short 2012, Rots 2015, Fujita
  2007), each through source-reader, quote-check, record-format and source-applicability (done, findings applied).
- **D2 - the knob** (FR-004, FR-008): `grove form` - `behind`, `behind and sides`, `all around` - declared in the
  country-shrines program's knob list (`buildings/programs.md`, hand prose, beside knobs 1-7) with the ground rule
  and labels; the program's `grove` item stays (its kind is shared). Owed at conversion:
  `future-work/farming-communities.md`'s shrine-grove entry and `migration-plan.md` step 5 name the knob, its
  ground rule and the irregular edge.
- **D3 - Hoshigaoka's form**: the hall stands at the top of its slope and the approach climbs to it from the
  south, so the ground leaves one candidate: **behind and sides**. No roll.
- **D4 - the layout, laid once** (FR-005, FR-006, FR-007): feature 270's layout script, re-run with the grove's
  domain changed from the precinct box to an irregular region - the wood behind the hall (to the well at its back
  edge) and down both flanks to ragged tips short of the outermost arches, the lower approach open. The region's
  edge is a smooth-noise outline (several low frequencies, amplitude about a crown); trees are thrown with their
  centers inside it, so edge crowns straddle it. Everything else (clearing, approach, arches, basin, sacred tree,
  path, well, captions) is unchanged. The one layout writes the map fragment, the manifest record and the sheet's
  tree list, so the sheet matches the map tree for tree.
- **D5 - the map** (FR-006): the frozen map is edited by hand, as features 268 and 270 did: the `shrine-grove`
  group in the svg (in the mirror; the render is gitignored) and the manifest's `village_groves` record of role
  `shrine` (tracked) are replaced from D4. The ground the wood gives up inside the old box would be bare tan in
  the scrub, so the scrub scatter is extended into it: a donor patch of the map's own scatter (grass tufts, shrub
  dots, scraggly pines) from the open ground just west of the grove is copied, tiled and kept only where it clears
  the wood, the clearing, the approach, the arches, the sacred tree, the basin, the well and the path. The map's
  notes record the edit.
- **D6 - the sheet** (FR-007): the grove floor and tree list rewritten from D4; its `shrine grove` Map notes line
  and its header comment updated to the form; the precinct rect stays (layout, `-`).
- **D7 - verification** (SC-002, SC-003, FR-009): `STRAIGHT_RUN` measured on the tree list by the layout script
  and recorded in `measurements.json`; `matches_map` (the tree-overlap test) stays green; a `settlement-review` of
  the map and a `building-review` of the sheet, ledgered; `make done` green.

## Phases

T01 record; T02 knob and owed list; T03 layout and map; T04 sheet; T05 reviews, gate, push.
