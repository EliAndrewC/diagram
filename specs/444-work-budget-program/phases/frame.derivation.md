# Derivation - frame (feature 444)

## Contract

- Reads: the view decided at the end of `stage_hinterland` (`plan.view`, `meta.view`); the title pocket the hinterland reserved (`meta.title_pocket`: the first blank box the title's scan finds, held 40 ft clear of every feature glyph, `TITLE_POCKET_CLEAR_FT`); the queued canopy; every hard feature, for the content's frame; on a polder the waterward reed strips and the registry.
- Writes: the crop to the decided view (`crop_to_view`); `meta.view_drift` where the content's frame differs; the title, the bold place name and its scale bar of 100 ft (`title`, `M['title']`); on a water-facing flank, the waterward strip extended to the view's edge and joined to its record (`waterward_to_the_frame`).
- Keeps: the crop takes exactly the decided view (CONVENTION, feature 287 M6); the title over blank space in the framed window (CONVENTION), over nothing but cover, never a feature; a reed fringe runs off the picture, its extension scattered with every keep-out it honors and unioned with its strip as one ground and one record (feature 150 T55); every rule asked before the title is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the crowns 389 and 717 (x1.84: 717 at 20, 1,320 at 40, 2,428 at 80); the hard features (the built parts, the lanes, the water segments, the plots, the marshes and the groves; the crowns and the scrub are cover, which the title may lie over), about 902 and 1,632 (x1.81: 1,632 at 20, 2,954 at 40, 5,347 at 80); the view's long side 1,726 and 2,486 ft (x1.47: 2,486 at 20, 3,655 at 40, 5,372 at 80); the title placard 252 by 159 ft in a pocket of 300 by 190 ft; the title's band at most the placard's height and 34 ft, 193 ft (`TITLE_BAND_ALLOWANCE`); the waterward band at most that deep, since the view otherwise stops at the strip and passes it only where the title's band grew it (`waterward_to_the_frame`, `to_the_strips`); the strip is a marsh record, its ring at most the pool's longest marsh ring, 662 points (Kashikawa; 414 and 485 on the reference), no pool map carrying a waterward strip; at most 21 and 29 things in a 64 ft cell (x1.38: 29 at 20, 40 at 40, 55 at 80, no geometric ceiling, a crown and a part differing in size); 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does.

## The algorithm

    the canopy flushed: each queued crown written (1)
    the content's frame from every hard feature's box (1 each; cover is not read), against the decided view: the drift, if any, recorded (4)
    the crop: the decided view set (4)
    the title: the reserved pocket read (1), the placard tested against the registry's things in the cells it covers, and
        drawn with its scale bar (2) - the pocket is the first blank box the scan finds, held clear, so the scan is not rerun
    on a water-facing flank whose view reaches past the strip: the band between the strip and the view's edge, at most the
        title's band deep along the view's side, tested against the registry's things in its cells (the keep-outs), and
        joined to the strip's ring by
        clipping the ring against the band's rectangle in one walk, each point against its 4 sides

## Indexes

- registry: cells of 64 ft; densest the mean 4 things a cell (`items.md`'s typical densities, rubric S8), from a smallest side of 64 ft against the placard, 252 by 159 ft, in at most 5 by 4 cells

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the frame, once | always 1 |
| the crop | per item | 4 | the decided view's four sides set | always 4 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the canopy | once | 717 at 20, 1,320 at 40, 2,428 at 80 | each queued crown written once | 80 households |
| the drift | once | 1,636 at 20, 2,958 at 40, 5,351 at 80 | each hard feature's box read once for the content's frame (1), and the frame against the view (4) | 80 households |
| the title (registry cells examined) | once | 103 | the pocket read (1), the placard's at most 5 by 4 cells of 64 ft with the mean 4 things and the cell (100, `items.md`), the title and its scale bar written (2) | always 103 |
| the waterward band (registry cells examined) | once | 1,000 at 20, 1,475 at 40, 2,125 at 80 | the band, the view's long side by the title's 193 ft band, in (the side over 64 rounded up, plus 1) by 5 cells (200 at 20, 295 at 40, 425 at 80), each with the mean 4 things and the cell (5) | a polder with a water-facing flank |
| the union (ring points) | once | 2,664 at 20, 2,664 at 40, 2,664 at 80 | the strip's ring, at most 662 points, and the band's 4 corners, clipped in one walk, each against the band's 4 sides, 4 x (662 + 4) | a polder with a water-facing flank |

So: 1 x 4 x 1, plus the canopy, the drift, the title, the waterward band and the union.

## Totals

- at 20: 1 x 4 x 1 + 717 + 1636 + 103 + 1000 + 2664 = 6124
- at 40: 1 x 4 x 1 + 1320 + 2958 + 103 + 1475 + 2664 = 8524
- at 80: 1 x 4 x 1 + 2428 + 5351 + 103 + 2125 + 2664 = 12675

## Earlier findings

- verdict-2, finding 1: fixed - carried from the verdict as it stood (its notes stand); the derivation re-scored to the typical case under FR-014
- verdict-1, finding 1: fixed - the things a cell grow at their measured rate, 29, 40 and 55, in the title and the band
- verdict-1, finding 2: fixed - the band is at most the title's band deep because the view passes the strip only where the title's band grew it (`to_the_strips`), cited
- verdict-1, finding 3: fixed - the union clips the strip's ring against the band's rectangle in one walk, 4 x (points + 4)
- verdict-1, finding 4: fixed - the drift reads the hard features only; the crowns and the scrub are cover
- verdict-1, finding 5: fixed - the strip's ring is a marsh record's, bounded by the pool's longest marsh ring, 662, no pool map carrying a strip

- reason above the reference: the frame is one thing a roll, so its cost per thing is the whole stage - each hard feature's box read once for the view and the title's pocket tested - not a cost per house or per part placed

- FR-014 re-score: the registry's things a cell at the mean 4 of `items.md` in place of the densest 29, 40 and 55; every other factor an exact count (ask:444-budget-standard)

## Cheaper algorithms considered

- sweep: not used - the title takes the reserved pocket; no window is scanned
- grid or spatial index: used - the registry's cells for the placard and the band
- priority queue: not used - nothing is ranked
- incremental update: not used - each piece is written once
- memoizing what a scan does not change: used - the title's pocket was found by the hinterland's scan and is read, not sought again
