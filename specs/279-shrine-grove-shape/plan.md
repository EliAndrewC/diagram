# Plan - feature 279, the shape of a village shrine's grove

Spec: [`spec.md`](spec.md) (FAITHFUL, round 2). Request: [`request.md`](request.md).

## What the research found (research religion-and-death 129; FR-001)

- **Forms, tied to the ground** (accurate as forms): on a rise or in the paddy plain the wood stands **all
  around**; on a slope it stands **behind** the hall, **behind and at the sides**, or **at the sides**. Behind and
  at the sides is also Short's general description; behind only and at the sides only rest on one modern city
  survey alone, whose groves burned, were replanted and lost ground - a caveat that covers all its forms and is
  quoted on the record.
- **The outline**: no source gives a grove's plan; the precinct came to be surveyed land, but nothing says the wood
  followed that line; where the wood meets scrub or slope its edge is drawn irregular, its crowns' own (a guess).
  The one picture of an edge, the paddy-plain photograph, shows the wood's foot along the fields' straight edge:
  FR-005's escalation fires for the paddy-plain form, and it goes to the GM at hand-back before that form's edge
  is fixed. Hoshigaoka's wood meets no paddy (its ground is the back-slope's scrub).

## Decisions

- **D1 - the record** (FR-001-FR-003): research 129 on religion-and-death, with the photograph's reading; 124's
  decision points at it and says the wood covers some or nearly all of the precinct; three sources registered
  (Short 2012, Rots 2015, Fujita 2007), each through source-reader, quote-check, record-format and
  source-applicability.
- **D2 - the knob and every text that states the grove** (FR-004, FR-007, FR-008): knob 8, `grove form` -
  `behind`, `behind and sides`, `sides`, `all around` - in the country-shrines program (`buildings/programs.md`,
  hand prose) with the ground rule, equal weights between two or three candidates (a guess) and the paddy edge OPEN with
  the GM; the program's composition rule ("the precinct holds the grove"), its size anchors and its `types.json`
  notes restated to it; the shared `shrine grove` kind (`compound_kinds/grounds.py`) - its Why, Note and Caveat
  (the forms; the edge and the roll as guesses) and its Entry (research 129) - which also renders the program's
  `grove` row. Owed at conversion: the shrine-grove entry in `future-work/farming-communities.md` and
  `migration-plan.md` step 5 name the knob, the ground rule, the irregular edge and the open paddy question.
- **D3 - Hoshigaoka's form** (amended after the building-review of 2026-09-28): the map has no break of slope at the
  hall - its one terrain datum is an even fall to the south-east (`meta.down_deg` 45), the ground rising behind the
  hall toward the village and falling before it down the approach - so the hall is in neither of the survey's two
  classes. The rule for a mid-slope hall, recorded on research 129 and knob 8 as a guess: it takes both classes'
  forms, `behind`, `behind and sides`, `sides`. The roll is exactly
  `random.Random(zlib.crc32(b"hoshigaoka:shrine grove form")).choice(["behind", "behind and sides", "sides"])`, the
  candidates in the knob's order, and it gave **behind and sides**. (The first reading, a hall at the top of its
  slope, rolled `sides` between two; the review found no such break.)
- **D4 - the layout, laid once** (FR-005, FR-006, FR-007): feature 270's layout script, re-run with the grove's
  domain changed from the precinct box to one irregular region - behind the hall from the well at its back edge,
  round both flanks to ragged tips beside the forecourt's foot, the west tip lower; the lower approach open. The
  edge is a smooth-noise outline about a base shape with real bays and spurs (no near-plumb side); trees are thrown
  with their centers inside it, so edge crowns straddle it; the drawn floor is pulled inside the crowns. Everything
  else (clearing, approach, arches, basin, sacred tree, path, well) is unchanged, and the captions are re-seated by
  `make seat-label`. The one layout writes the map fragment, the manifest record and the sheet's tree list.
- **D5 - the map** (FR-006): the frozen map is edited by hand, as features 268 and 270 did. Its svg is a
  gitignored render that exists only in the mirror (`/diagram`; the clone has none - a frozen map is never
  regenerated), so the `shrine-grove` group is replaced there, with `MAIN_TREE_OK` and a backup kept, and the
  manifest's shrine grove record in the clone (tracked). The precinct's open ground, and the bare strips north and
  south of it that the old reservations left (settlement-review F3), carry the map's own scrub - grass tufts and
  shrub dots (no pines: tiled, they read as a planted grid) - copied from the open ground just west, kept only where
  it clears every shrine feature. The map's notes row records the wood once, as it now is.
- **D6 - the sheet and every text that places a feature against the old grove** (FR-007): the grove floor and tree
  list rewritten from D4, and the sheet's frame widened to hold the wood's outer crowns; the subtitle's "in its wood"
  dropped; the knob written as the program declares it (`**Grove form**: behind and sides`); the precinct's open
  ground drawn plain on the sheet where the map draws scrub, recorded as a map drawing convention; the precinct rect stays (layout,
  `-`), and the notes say the wood runs past its line, measured. Restated to the sides form, each by name - in `hoshigaoka-shrine.notes.md`: the "precinct is the
  grove" bullet (its area, crown count and canopy share re-measured from D4's layout), the arches bullet and the
  sacred tree bullet ("at the grove's edge", "the grove's biggest"), the knob list (`**Grove form**: sides`, with
  the roll's exact call), and the Map notes lines `torii`, `shrine grove` and `well` ("at the grove's back edge",
  "the outermost at the grove's edge"); in the sheet svg the comments at the parchment, the precinct, the approach,
  the arches and the well; the shared `approach` kind (`compound_kinds/shrine.py`: What and Covers, "from the
  grove's edge") and the program's approach rule (`buildings/programs.md`: "at the grove's edge") - the way enters
  the precinct, and the outermost arch stands there; and `future-work/farming-communities.md`'s "a village shrine's
  precinct IS its grove". The map's notes row "Shrine grounds" records feature 279's edit. The full list - every
  `grove` hit in every file the sheet renders from, each ruled on - is `research.md` R3.
- **D7 - verification** (SC-002, SC-003, FR-009): `STRAIGHT_RUN`, and the long-window `LONG_RUN` the
  settlement-review asked for (a 50 ft stretch of edge within a crown's radius of one line), measured on the tree
  list by the layout script and recorded in `measurements.json`, with each outer side's wander from its best-fit line
  (settlement-review round 2: the old box's long sides must not survive as the wood's outer edges); `matches_map` (the tree-overlap check) stays green; a `settlement-review`
  of the map and a `building-review` of the sheet, ledgered; the paddy-edge question and the side forms' single
  source raised with the GM at hand-back (through `escalation-check`); `make done` green.

## Phases

T01 record; T02 knob and owed list; T03 layout and map; T04 sheet; T05 reviews, gate, push.
