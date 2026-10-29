# Derivation - web (feature 444)

## Contract

- Reads: the placed homesteads and the cluster's declared shape (its hull, from the homesteads); lane ground, the homesteads' 6 ft raster of the gaps with its flood from the gate, and the households' ways already laid and reserved (`access_corridors`); the connector; the site's free-ground raster (32 ft cells: the field, the crop, the wet ground, the toe and the marsh) and the parts index; the field's outline index (the bund); the form (a dispersed hamlet draws no web).
- Writes: the web's lanes (`lanes`): the spine along the cluster, the back lanes cut across it, each run reached to the network, the door paths of the farms no way reaches; each lane's corridor; the web read as shapes - near-junctions closed, each junction made once, ends within a few paces met at one node, each lane pulled taut and cleared of hairpins (140 degrees) and zigzags (50 degrees within 40 ft).
- Keeps: the lanes after the houses (0246); the web cut in a frame of 100 ft (`BUNDLE_PITCH`) past the outermost house and trimmed back where a lane stops serving (0246, a departure); back lanes at the bundle's pitch, 100 ft; a lane's middle 7 ft off a garden fence (`WEB_FABRIC_GAP`), 3 ft off the field and the crop (`WEB_CROP_GAP`), 8 ft off the toe and the marsh (`WEB_HARD_GAP`, UNRESEARCHED); a stretch across the field, a crop or wet ground cut out (0081); a belt crossed, not followed (0072); no door path where a way's point nearest a house is within 60 ft of it or 12 ft of its built ground (`STEADING_ARRIVAL_FT`); a lane end within the frame's 100 ft of the field runs on to the bund (0014); a dispersed hamlet draws none (0031); each lane asked, trimmed and pulled taut before it is filed (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80), so the frame, 100 ft past each side, 950 by 1,285 ft at 20, 1,378 by 1,828 ft at 40, 2,049 by 2,642 ft at 80; a homestead's extent at most 184 ft, so it crosses at most 2 back lanes 100 ft apart; a household's way at most 3 legs and at most 62 lane-ground cells (the homesteads' budget: half a homestead's 4 x 184 ft perimeter over 6 ft); at most 7 placed parts in a 64 ft cell; at most 20 site-boundary segments in a 32 ft cell; at most 12 outline segments in a 64 ft cell; 1 ft a pixel at the hamlet scale.

## The algorithm

    the frame: the cluster's hull offset 100 ft (at most 4 points a house, each moved on its normal, 2 a point)
    the frame's ring, 100 ft deep outside the hull, added to lane ground in 6 ft cells: each decided from the free-ground
        raster (its 32 ft cell read, and where undecided its segments tested), and only a cell within 8 ft of the hull (the
        widest margin) against the parts of the 2 by 2 cells of 64 ft it straddles
    the spine: traced along the cluster's long axis on lane ground's flood, end to end - each step the neighbor of least
        flood value read from its 8 (8), the step taken (1), its 25 ft band marked (10)
    the back lanes: a line across the frame every 100 ft along the long axis; each walked over lane ground's cells, its free
        stretches the runs (a homestead it crosses splits it); each run's two ends reached to the network along the flood
        within the pitch, traced as the spine is
    each lane, before it is filed: trimmed back to the last house it serves (its end legs walked), pulled taut by a funnel
        over its lane-ground cells, and its vertices' angles tested for a hairpin and, for a zigzag, the legs within 40 ft;
        then recorded and its corridor filed in the parts index and its legs in the ways index
    each household: the ways' legs in the cells of 64 ft its built ground covers grown 12 ft read for the point nearest its
        house (the 60 ft and 12 ft tests); none near: its door path traced on the flood, as its way was
    each run's end within the frame's 100 ft of the field: one leg on to the bund, tested against the outline index's cells
    settle: each run's two ends against the ends and junctions in their 3 by 3 cells of a 25 ft endpoint index

## Indexes

- lane ground: cells of 6 ft (the homesteads'); densest 1 a cell, from a smallest side of 6 ft - a cell holds one state and one flood value
- parts index: cells of 64 ft (the homesteads'); densest 7 placed parts a cell, from a smallest side of 64 ft
- ways index: cells of 64 ft, the laid ways' legs filed as each is laid; densest 48 legs a cell, from a smallest side of 64 ft against the lanes' spacing: two lanes run at least the 20 ft threading gap apart, so at most 64 / 20 + 1, 4, lanes cross a cell, and a leg spans at least one 6 ft lane-ground cell, so at most 64 / 6 + 1, 12, legs of one lane lie in it
- outline index: cells of 64 ft (the field's); densest 12 outline segments a cell, from a smallest side of 64 ft
- endpoint index: cells of 25 ft (`KNOT_FT`, the reach at which two ends meet), so an end's partners lie in its 3 by 3 cells; densest 4 ends a cell (measured at 10 and 20, 3 and 4: a junction meets at most four ways), from a smallest side of 25 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the web, one network | always 1 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the frame (hull points moved) | over the run | 160 at 20, 320 at 40, 640 at 80 | the hull's at most 4 points a house, each moved on its normal, 2 | 80 households |
| the frame's ring (lane ground cells written) | over the run | 255,276 at 20, 380,646 at 40, 572,376 at 80 | the ring outside the hull, the hull's perimeter, at most the cluster's 2 x (width + length), by 100 ft plus pi x 100 squared, over 36 sq ft (11,068 at 20, 16,462 at 40, 24,712 at 80 cells), each decided from its 32 ft raster cell and its at most 20 segments (21); the cells within 8 ft of the hull (816 at 20, 1,248 at 40, 1,908 at 80) also against the 2 by 2 cells of 64 ft they straddle with their 7 parts (28) | 80 households |
| the back lanes (lane ground cells examined) | over the run | 2,240 at 20, 4,620 at 40, 9,604 at 80 | 14 at 20, 20 at 40, 28 at 80 lines, the frame's long side over 100 ft plus 1, each the frame's short side over 6 ft plus 1 cells, each read (1) | 80 households |
| the spine (lane ground cells examined) | over the run | 7,087 at 20, 10,165 at 40, 14,858 at 80 | at most the frame's long side plus its short side (the flood's walk bends round the plots, at most one side's width aside) over 6 ft (373 at 20, 535 at 40, 782 at 80 cells), each traced: its 8 neighbors read, the step, its 25 ft band marked, 2 x 25 / 6 + 1 rounded up, 10 (19) | 80 households |
| the joins (lane ground cells examined) | over the run | 34,884 at 20, 64,600 at 40, 121,448 at 80 | the runs, the lines plus 2 a house (54 at 20, 100 at 40, 188 at 80), each of their two ends reached along the flood within the pitch, 100 ft over 6 ft, 17 cells, each traced (19) | every run joined at both ends |
| the laying (parts index cells written) | over the run | 2,916 at 20, 5,548 at 40, 10,718 at 80 | the lanes' length - the back lanes, the spine, 100 ft at each run's end, and 372 ft a household's door path - 33,775 at 20, 65,646 at 40, 129,423 at 80 ft, in at most 237 at 20, 441 at 40, 833 at 80 legs (3 a household's way, 3 a run: its stretch and its two joins, and the spine's at most one bend a line plus 1), its 20 ft corridor in at most 2 cells across: 2 x (the length at root 2 over 64 ft, plus 3 a leg) | every lane at its longest |
| the door paths (ways index and lane ground cells examined) | over the run | 48,080 at 20, 96,160 at 40, 192,320 at 80 | each household: the cells of 64 ft its built ground, at most 184 ft, grown 12 ft, 208 ft, covers, at most 5 by 5, each read with its at most 48 legs (1,225); its door path traced, at most 62 cells (the homesteads' figure for a way), each traced (19); and the decision (1) | every household needing one |
| the trims (legs walked) | over the run | 237 at 20, 441 at 40, 833 at 80 | each leg walked at most once from a lane's end, before it is filed | every lane trimmed |
| the bund (outline index cells examined) | over the run | 8,424 at 20, 15,600 at 40, 29,328 at 80 | each run's two ends, one leg of at most 100 ft (an end within the frame's 100 ft of the field), at root 2 over 64 ft plus 3 cells, each with its 12 segments (13) | every end near the field |
| the knots (endpoint index cells examined) | over the run | 4,860 at 20, 9,000 at 40, 16,920 at 80 | each run's two ends: its 3 by 3 cells of 25 ft, each read with its at most 4 ends, 9 x (4 + 1) | every end near another |
| the taut pull (lane ground cells examined) | over the run | 11,260 at 20, 21,882 at 40, 43,142 at 80 | a funnel over each lane's cells before it is filed, the lanes' length over 6 ft, each cell's two sides tested once (2) | every lane pulled |
| the kinks (legs tested) | over the run | 2,133 at 20, 3,969 at 40, 7,497 at 80 | each vertex's angle (1) and, for a zigzag, the legs within 40 ft, at most 40 / 6 rounded up, 7, and the decision (1) | every vertex a kink |

So: 1 x 1, plus the frame, the ring, the back lanes, the spine, the joins, the laying, the door paths, the trims, the bund, the knots, the taut pull and the kinks.

## Totals

- at 20: 1 x 1 + 160 + 255276 + 2240 + 7087 + 34884 + 2916 + 48080 + 237 + 8424 + 4860 + 11260 + 2133 = 377558
- at 40: 1 x 1 + 320 + 380646 + 4620 + 10165 + 64600 + 5548 + 96160 + 441 + 15600 + 9000 + 21882 + 3969 = 612952
- at 80: 1 x 1 + 640 + 572376 + 9604 + 14858 + 121448 + 10718 + 192320 + 833 + 29328 + 16920 + 43142 + 7497 = 1019685

## Earlier findings

- verdict-1, finding 1: fixed - a ring cell is decided from its 32 ft raster cell and its at most 20 segments (21; the raster's cells are 32 ft, 1 ft a pixel is the map's scale), and only a cell within 8 ft of the hull against the 2 by 2 cells of 64 ft it straddles (28)
- verdict-1, finding 2: fixed - the door path's 62 cells is the homesteads' figure for a household's way, cited in the Bounds
- verdict-1, finding 3: fixed - the ways index's 48 legs a cell is a geometric ceiling, 4 lanes 20 ft apart by 12 legs of at least 6 ft; the legs are derived, 3 a household's way, 3 a run and the spine's bends
- verdict-1, finding 4: fixed - the bund leg is at most 100 ft because only an end within the frame's 100 ft of the field runs on; a traced step reads its 8 neighbors; the spine is the frame's long side plus its short side over 6 ft, with no second root 2; the band is 2 x 25 / 6 + 1 cells
- verdict-1, finding 5: fixed - each lane is trimmed, pulled taut and cleared of kinks before it is filed (S4)
- verdict-1, finding 6: fixed - the ring's area is the hull's perimeter by 100 ft plus pi x 100 squared
- verdict-1, finding 7: fixed - the knots read 9 cells x (4 + 1) an end
- verdict-1, finding 8: fixed - the joins count both ends of a run
- verdict-1, finding 9: fixed - the door path's window is the cells the built ground grown 12 ft covers, 5 by 5

## Cheaper algorithms considered

- sweep: used - the back lanes are a sweep of parallel lines across the frame, each walked once over lane ground
- grid or spatial index: used - lane ground and its flood (the homesteads'), the parts, ways, outline and endpoint indexes
- priority queue: not used - the flood is the homesteads' (on its bucket queue); the web only traces along it
- incremental update: used - each lane's legs are filed in the ways index and its band marked as it is laid
- memoizing what a scan does not change: used - lane ground and its flood are read, not rebuilt; only the frame's ring is added, and only its cells near the hull read the parts
