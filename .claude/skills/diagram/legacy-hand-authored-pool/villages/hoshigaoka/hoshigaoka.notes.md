# Design notes: Hoshigaoka ("Star Hill"), the water-first BASE CASE

*Reconstructed 2026-08-08 from the generator's docstring and comments. Everything below is sourced
from `hoshigaoka.gen.py`.*

**Subject**: an average farming village, purpose-built to nail the **single-field case** - one pond,
one contiguous paddy. This is the most common case: a broad gentle valley holds one contiguous paddy
expanse, and multiple blocks are the TERRAIN-driven variant for broken ground.

**Why it exists**: it is the foundation the rest of the water-first family stands on. Kikuta was
later rebuilt on it; Hikari no Sato is the split multi-block variant; Ueda is the large-village
variant flowing the other way.

**How it was built, which is the transferable part**: water-first, layer by layer, **each layer
approved by eye, with the checks and tests backfilled afterwards as ratchets**. In order: the
irrigation pond + sluice + comb supply net + paddies + drain; the dry *hatake* margin, reed marsh,
and the grazing-scrub *satoyama* ring; the nucleated farmhouse cluster with its kura, threshing
yards, kitchen gardens, shared draft-animal byres and communal wells; the fengshui windbreak grove;
the village shrine - Bishamon's, the country monk Otsuki's seat (GM 2026-09-20) - with its own ablution well, at the water-mouth and the back-slope graveyard;
the lanes, connector track and plank footbridges across the ditches.

## Map notes

<!-- READ BY THE INTERACTIVE MAP (`l7r/diagram/interactive/notes.py`, feature 156): these bullets
     appear on the page's title card and in feature modals. Everything is optional and the reader is
     forgiving by design (GM 2026-08-29: "we should not presume that such sections exist ... should
     default to simply not pulling anything in if the parsing fails") - a missing, misspelled or
     half-written block simply contributes nothing. The key list and the format are documented in
     `l7r/diagram/interactive/CLAUDE.md`. Every other word in this file is prose and is never parsed. -->

### Place

- **imperial road**: directly south
- **county**: Hayakawa
- **town**: Hayakawa
- **town direction**: further south, beyond the Imperial road

*No **district** key: a village IS its district and the two names are always the same, so the page
never states it (GM 2026-08-29). The county is what a village page says instead. The county, the road
and the town are the GM's own, dictated 2026-08-29. A district takes its
main village's name (`l7r.md`, "Place Names"), so Hoshigaoka names both.*

## GM decisions (settled)

| Decision | Value |
|---|---|
| Fall | NW-high, water falls SE |
| Field form | ONE contiguous block - the base case, not a variant |
| Focal feature | the crescent pond (fire water + the fengshui "gathering of qi"), distinct from the NW irrigation pond - Hoshigaoka's optional distinctiveness axis against Kikuta, read by the twin-detector via `focal_set` |
| Shrine avenue | SEVEN torii (GM 2026-09-26: "Yes, I do want the seven"; the ruling of 2026-07-22). The shrine's avenue was drawn with one arch because the per-hall roll gave 1, against the seven-arch ruling of 2026-07-22. The map is frozen, and regenerating it under the current engine re-laid the whole village (61 houses for 70 households), so the GM chose a hand edit: six arches added to the svg at the generator's own points (392, 1111-1186, 15 px apart), the png re-rasterized, the manifest's `torii` and the hall's `torii_count` brought to seven, and `torii_count=7` pinned in the generator for conversion. |
| Shrine grounds | The shrine's GROVE, sacred tree and basin, and its seven arches at the 12 ft pitch (feature 268, the GM 2026-09-27: "Add grove to map ... a grove around the shrine, plus the sacred tree and a stone basin by the approach"; "All maps, ~10-13 ft"). A second hand edit of the frozen map: a grove of 137 overlapping canopies (a closed canopy, feature 270), their edge crowns straddling a ragged wooded floor, filling a 137 by 223 ft precinct from the shrine well at its back edge to the outermost arch, a ragged swept clearing at the hall with a forecourt holding the three innermost arches, the approach's gravel under the arches, a footpath to the well, a roped sacred tree beside the approach and a stone basin at the innermost arch (drawn at 6 ft where it is 3 ft - a map drawing convention, so it can be seen), added to the svg (in the mirror; the render is gitignored) and the manifest (`village_groves` role `shrine`, `tree_crowns`, `wells` flagged `basin`); the seven arches moved to (392, 1092-1128, 6 px apart), drawn in plan, and the gen's `SHRINE_TORII` brought to the pitch for conversion. The shrine sheet (`pool/country-shrines/hoshigaoka-shrine/`) draws the same trees one for one. The shrine glyph itself redrawn at 36 by 16 px (72 by 32 ft) from the record's bands (feature 270, the GM 2026-09-27: the former 30 by 24 px was the glyph's size, not a measurement), the arches moved one pitch off its new face (392, 1088-1124). Research: religion-and-death 090, 120, 122, 124, 126. Known and small (settlement-review round 4, PASS): the manifest's grove `poly` is the precinct's bounding rectangle, where the drawing's floor edge is ragged; the clearing's tongue behind the hall keeps square corners; the approach ends at the grove's edge with no track to the lane (the map's to change at conversion). |

## Review log

- **The headman's seat has been swept three times.** The original (455, CY-60) lay across two of its
  own field's irrigation ditches; the first correction still lapped one - the overlap matrix is the
  first rule that ever compared a house against a ditch. **2026-08-08** the RNG re-roll moved the
  bundle solve's landing spot and it lapped a ditch a third time. Nudges do not work here: the
  solver converges to the same pocket from anywhere nearby, so the seat had to move a clear 70 px
  west, to (430, CY-44). (600, 560, 650 and CY-90 were each tried and each broke something else.)

## Known open

- **No `notes.md` existed for this map until 2026-08-08**, so anything settled between its authoring
  and that date lives only in gen comments and may not be recorded here. Treat gaps as unrecorded
  rather than as decided.
