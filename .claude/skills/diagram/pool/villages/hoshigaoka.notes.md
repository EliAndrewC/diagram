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
the earth-god shrine (with its own ablution well) at the water-mouth and the back-slope graveyard;
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
