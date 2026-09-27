# Inventory - feature 269, the research backfill

Built 2026-09-27 by an audit of `future-work/*.md`, every research fragment (footnote count, words, absence and guess
phrases per fragment, over 316 fragments), and the engine's kinds labeled guess or with no `Entry:`. `fc` is
`future-work/farming-communities.md`; page paths are under `.claude/skills/diagram/research/`. Sizes S/M/L. Items are
numbered B01-B.. and grouped into research sessions by the page they belong on; each group owns a prefix range for
NEW questions on its page, and may also edit the EXISTING sections its items name (a thin-sourcing item is answered
in the section that makes the claim).

## Owned elsewhere (not this feature's; confirmed by each session, 2026-09-27)

- **Feature 265** (Diagram research, diagram-research-1..3): the record checks on towns, cities/river-cities,
  buildings, urban-features, ways, cities/capitals. Its sweeps (glossary tooltips, plain-word rewrites, English titles
  on 542 registry lines) have also edited fragments on fields, archetypes, homesteads, vegetation, water and
  cities/defenses, fabric and government; they are unpushed until 265 closes. So the groups that EDIT existing
  fragments run after the new-question groups, and the queue syncs from main between sessions.
- **Feature 267** (diagram-buildings): `future-work/compounds.md` "Research owed" R01-R53 and the in-field grave island
  (R52). Its reserved ranges: buildings 240-640, vegetation 170-200, religion-and-death 220-260, fields 220-240,
  cities/river-cities 050-080, urban-features 190-220, ways 060-090.
- **Feature 268** (Diagram shrines): religion-and-death 080, 090, 100, 110, 120 and the new 122, 124, 126; the
  country-shrine program in `buildings/programs.md`.
- Also out of scope: the six 265 pages' footnote-less sections (towns 020, 110, 120, 140, 150; buildings 110;
  cities/capitals 380, 390; cities/river-cities 030; ways 050). They go to 265's owner if 265's derived list lacks them.
- `presentation/*` and `settlements/060-080` are drawing conventions. They are not research.

## F1 - fields: paddy kinds (new: fields 250-280)

- B01 **Fallow patch**: was fallow ground kept within a hamlet's paddy, and where? `l7r/diagram/interactive/classes/fields.py:250`
  labels it guess, with "no dedicated entry - recorded as silent". Never researched. Kind `FallowPatch`, all hamlets. M.
- B02 **Bund and walking-bund width**: the 2-5 ft azemichi and ~3 ft levee are guesses; also azenuri (bund
  re-plastering). Edits `fields/020`, `vegetation/090`, `homesteads/100` (the 6 ft farmhouse setback rests on it).
  All hamlets. S-M.
- B03 **Mid-season drainage** (nakaboshi): was a premodern paddy drained mid-season? `fields/030` calls it a guess.
  Until a period source says so. S.

## F2 - fields: ways and seasons (new: fields 290-330)

- B04 **Where a field path ends**: at a bund head, at a gap in the outer bund, or where worked ground begins? `fc:2076`,
  `fc:2262` (three pool maps with no field-path end). Inashiro. M.
- B05 **Off-season crops and the straw rick**: paddy double-cropping (nimosaku); where the rick stood and for how long
  (`homesteads/210` calls the rick's duration a guess). `fc:2036`. M.
- B06 **Angle between neighboring dry plots' furrows**: `fc:1533-1640` records the East Asian record as silent, and
  the pass leaned on European open-field sources. M.

## F3 - fields: thin sections (edits existing)

- B07 Dry-field (hatake) crop placement, `fields/160` ("no source read places them"). S-M.
- B08 Samurai estates and temple glebe, `fields/140` and `fields/150` (no footnotes). S-M.
- B09 The grain-share guess, `fields/110`. S.

## H1 - homesteads: farmstead fixtures (edits 210-218; new: homesteads 250-290)

- B10 **Privy**: where it sat relative to the house and the manure heap, and its size. `homesteads/210-218`,
  `classes/homestead.py:195-304`. All live hamlets. M.
- B11 **Manure heap**: its place in the dooryard. M.
- B12 **Bath shed** (furoba): detached or not, and where. M.
- B13 **Hen coop share** (50-80%, a guess). S.
- B14 **Persimmon**: which side of the house, and the 18 ft crown. S.
- B15 **Woodpile**: against which wall. S.
  (The modals quote shares the maps do not draw, `fc:2197`; the handoff says which.)

## H2 - homesteads: siting (new: homesteads 300-330)

- B16 **Byre siting**: on the inner commons or at the settlement edge? Probably a knob. `fc:68`, `fc:1346`. Inashiro. M.
- B17 **How far a lane runs past its last steading**. `fc:818`. Sawada, Kashikawa. M.
- B18 **Spread of house bearings within one hamlet**: the 5 degrees is a guess (`homesteads/240`). S.

## H3 - homesteads: thin sections (edits existing)

- B19 Village packing and village form: `homesteads/170` (512 words, no footnotes), `190` (none), and `110`, `160`,
  `180` (no source cited). M.
- B20 Dooryard garden area (`homesteads/050`, guess) and the village-entrance stone (`homesteads/140`, guess; 140
  was split by 265 into 140 + 145, so work on whatever holds the claim after sync). S.

## W1 - water: kinds (new: water 290-330)

- B21 **Plank footbridges over ditches**: the `Footbridge` kind is a guess (`classes/water_and_ways.py:297`,
  `water/070`). S.
- B22 **Intake mouth**: what an intake mouth looked like (`fc:2371`); the weir's thickness (`hamletgen/consts.py:586`);
  the even 50/50 roll between the two intake forms (`consts.py:515`, `water/250`). M.
- B23 **A hamlet split by its water**: labeled a guess, `water/270`. S.

## W2 - water: thin sections (edits existing)

- B24 Reed economy on tameike margins, searched and not found (`water/280`). S.
- B25 `water/090`, `water/100`, `water/160` and `fields/090`: each carries one footnote over 500+ words. M.

## V1 - vegetation: woods (new: vegetation 210-250)

- B26 **Copse size**: how big a village copse was, and how many clumps. `fc:83-127` ("Do NOT pick one by eye").
  Mizuguchi, Inashiro. M.
- B27 **Woodland-commons shape, iriai boundaries, upslope siting**: "bounded by ridge, stream and path" has unknown
  provenance (`vegetation/140`). `fc:1200`, `fc:1223` (Kashikawa's woodland sits downslope). M.
- B28 **Coppice stocking and crown size**: the 500-800 stems/ha and 5-8 m crowns come from papers that could not be
  read (`vegetation/060`, `070`, `fc:1279`). M.

## V2 - vegetation: groves and margins (new: vegetation 260-290; edits existing)

- B29 **Bamboo in a farmstead grove** (yashikirin): whether it was there, and its share. `fc:2113`, `vegetation/150`, `154`,
  `hamletgen/homesteads/bamboo.py:21`. S-M.
- B30 **Windbreak belt vs copse**: was the belt a single ranked species? `fc:1397`. S.
- B31 Guessed sizes and margins: the water-mouth grove size and how far the hillside was stripped (`vegetation/010`,
  `050`); crop and bank margins (`090`, `110`); reed mowing (`120`); the width of a gap in the belt (`030`). M.

## A1 - archetypes: dike-pond (new: archetypes 200-240)

- B32 **Dike-pond livestock and ponds**: the pig sty, duck pen and fry pond shares are guesses (`classes/dikepond.py:276/305/330`,
  `hamletgen/pondstock.py`, `archetypes/170`, `171`, `180`). M.
- B33 **Mulberry density and crown width**: tighten the one modern figure for the GM's open decision (`fc:10`,
  `archetypes/140`). Research as support. The ruling stays the GM's. S.
- B34 **Fruit, cane and vegetable dikes**: any premodern attestation? For the GM's open decision (`fc:25`,
  `archetypes/173`). S.

## A2 - archetypes: thin sections (edits existing)

- B35 Hand-piled bunds and parcel edges: `archetypes/040`, `060` and `070` cite no source. The record has no national
  share of settlement forms, and nothing on whether a branch hamlet had its own chinju (`190`). M.

## R1 - religion-and-death: burial (new: religion-and-death 270-300; edits 160-206)

- B36 **Burial grounds**: their size, distance from water, and whether a graveyard stands beside its temple
  (`religion-and-death/160`, `170`, `180`, `206`: "no source found" or the project's own arithmetic). The 2% graves
  figure rests on an unread Buck survey. M.

## R2 - religion-and-death: city temples (edits existing; new 310-330)

- B37 City temples: monk counts "on no page read" (`010`); the temple-gate shop ratio and meibutsu (`050`); graveyard
  sharing (`070`); the bone-mound size (`204`). M.

## C1 - cities/defenses (edits existing; new 100-140)

- B38 Gate-tower and gatepost footprints, moat depth, the facing guard and inspection stations, tower count against
  wars fought, the patrol road, the fence at the rampart (`cities/defenses/020`, `040`, `050`, `060`, `080`, `090`). L.

## C2 - cities/government (edits existing; new 100-140)

- B39 Servant nagaya (6 guesses), martial training, ashigaru plots, the samurai count, ward gates
  (`cities/government/030` no footnotes, `050`, `070`, `080`, `085`). L. Check 267 G1B's handoff first (servant
  buildings) so the city question cites, not repeats, the compound one.

## C3 - cities/fabric (edits existing; new 160-190)

- B40 The street grid (`070`, no footnotes), the lodging-house count (`120`), alley surfaces (`080`), the street-share
  anchors (`030`). M.

## C4 - cities/hinterland and sizing (edits existing; new hinterland 060-090, sizing 030-050)

- B41 Near-city retreats and how far an estate reached (`hinterland/010`, `015`); the size of the strip outside a gate
  (`040`); the moat and fields (`030`); the population split (`sizing/010`). M.

## Queue order

New-question groups first, since they touch no fragment 265's unpushed sweeps edited. The audit's priority runs:
H1 (five guess kinds on every live hamlet), V1 (blocks a placer fix), H2 (knob candidates with measured defects
waiting), F1, W1. Then F2, V2, A1, R1. Then the edit-existing groups, after a sync from main: H3, F3, W2, A2, R2, C1,
C2, C3, C4.
