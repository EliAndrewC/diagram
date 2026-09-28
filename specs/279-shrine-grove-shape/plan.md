# Plan - feature 279, the shape of a village shrine's grove

Spec: [`spec.md`](spec.md) (FAITHFUL, round 2). Request: [`request.md`](request.md).

## What the research found (research religion-and-death 129; FR-001)

- **Forms, tied to the ground** (accurate as forms): on a rise or in the paddy plain the wood stands **all
  around**; on a slope it stands **behind** the hall, **behind and at the sides**, or **at the sides** - the two
  side forms on a slope rest on one modern city survey, whose groves burned, were replanted and lost ground, a
  caveat that covers all its forms and is quoted on the record.
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
  hand prose) with the ground rule, equal weights between two candidates (a guess) and the paddy edge OPEN with
  the GM; the program's composition rule ("the precinct holds the grove"), its size anchors and its `types.json`
  notes restated to it; the shared `shrine grove` kind (`compound_kinds/grounds.py`) - its Why, Note and Caveat
  (the forms; the edge and the roll as guesses) and its Entry (research 129) - which also renders the program's
  `grove` row. Owed at conversion: the shrine-grove entry in `future-work/farming-communities.md` and
  `migration-plan.md` step 5 name the knob, the ground rule, the irregular edge and the open paddy question.
- **D3 - Hoshigaoka's form**: the hall stands at the top of its slope and the approach climbs to it from the
  south, so the candidates are `behind and sides` and `sides`; the roll (the map has no seed, so the seed is the
  map's name: `random.Random(zlib.crc32(b"hoshigaoka:shrine grove form"))`, equal weights) gave **sides**.
- **D4 - the layout, laid once** (FR-005, FR-006, FR-007): feature 270's layout script, re-run with the grove's
  domain changed from the precinct box to two irregular flanks - the wood on both sides of the precinct from about
  the hall's back line down past it to ragged tips short of the outermost arches; the ground behind the hall (the
  well and its path) and the lower approach open. Each flank's edge is a smooth-noise outline (several low
  frequencies, amplitude about a crown); trees are thrown with their centers inside it, so edge crowns straddle
  it. Everything else (clearing, approach, arches, basin, sacred tree, path, well, captions) is unchanged. The one
  layout writes the map fragment, the manifest records (one `village_groves` record of role `shrine` per flank,
  as the sheet-to-map check reads every record's clumps) and the sheet's tree list.
- **D5 - the map** (FR-006): the frozen map is edited by hand, as features 268 and 270 did. Its svg is a
  gitignored render that exists only in the mirror (`/diagram`; the clone has none - a frozen map is never
  regenerated), so the `shrine-grove` group is replaced there, with `MAIN_TREE_OK` and a backup kept, and the
  manifest's shrine grove record in the clone (tracked). The ground the wood gives up inside the old floor would
  be bare tan in the scrub, so the map's own scatter (grass tufts, shrub dots, scraggly pines) is carried into it
  from a donor patch just west of the grove, tiled and kept only where it clears the wood, the clearing, the
  approach, the arches, the sacred tree, the basin, the well and the path. The map's notes record the edit.
- **D6 - the sheet** (FR-007): the grove floor and tree list rewritten from D4; the sheet notes' knob list gains
  `**Grove form**: sides`; its `shrine grove` Map notes line and its header comment say the form; the precinct
  rect stays (layout, `-`).
- **D7 - verification** (SC-002, SC-003, FR-009): `STRAIGHT_RUN` measured on the tree list by the layout script
  and recorded in `measurements.json`; `matches_map` (the tree-overlap check) stays green; a `settlement-review`
  of the map and a `building-review` of the sheet, ledgered; the paddy-edge question and the side forms' single
  source raised with the GM at hand-back (through `escalation-check`); `make done` green.

## Phases

T01 record; T02 knob and owed list; T03 layout and map; T04 sheet; T05 reviews, gate, push.
