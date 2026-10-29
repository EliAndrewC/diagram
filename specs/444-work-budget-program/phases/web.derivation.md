# Derivation - web (feature 444)

## Contract

- Reads: the placed homesteads and the cluster's declared shape (its hull, from the homesteads); lane ground, the homesteads' 6 ft raster of the gaps with its flood from the gate, and the households' ways already laid and reserved (`access_corridors`); the connector; the site's free-ground raster (32 ft cells: the field, the crop, the wet ground, the toe and the marsh) and the parts index; the field's outline index (the bund); the form (a dispersed hamlet draws no web).
- Writes: the web's lanes (`lanes`): the spine along the cluster, the back lanes cut across it, each run reached to the network, the door paths of the farms no way reaches; each lane's corridor; the web read as shapes - near-junctions closed, each junction made once, ends within a few paces met at one node, each lane pulled taut and cleared of hairpins (140 degrees) and zigzags (50 degrees within 40 ft).
- Keeps: the lanes after the houses (0246); the web cut in a frame of 100 ft (`BUNDLE_PITCH`) past the outermost house and trimmed back where a lane stops serving (0246, a departure); back lanes at the bundle's pitch, 100 ft; a lane's middle 7 ft off a garden fence (`WEB_FABRIC_GAP`), 3 ft off the field and the crop (`WEB_CROP_GAP`), 8 ft off the toe and the marsh (`WEB_HARD_GAP`, UNRESEARCHED); a stretch across the field, a crop or wet ground cut out (0081); a belt crossed, not followed (0072); no door path where a way's point nearest a house is within 60 ft of it or 12 ft of its built ground (`STEADING_ARRIVAL_FT`); a lane end within the frame's 100 ft of the field runs on to the bund (0014); a dispersed hamlet draws none (0031); each lane asked, trimmed and pulled taut before it is filed (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80), so the frame, 100 ft past each side, 950 by 1,285 ft at 20, 1,378 by 1,828 ft at 40, 2,049 by 2,642 ft at 80; a homestead's extent at most 184 ft, so it crosses at most 2 back lanes 100 ft apart; a household's way at most 3 legs and at most 62 lane-ground cells (the homesteads' budget: half a homestead's 4 x 184 ft perimeter over 6 ft); at most 7 placed parts in a 64 ft cell; at most 20 site-boundary segments in a 32 ft cell; at most 12 outline segments in a 64 ft cell; 1 ft a pixel at the hamlet scale.

## The algorithm

    the frame: the cluster's hull offset 100 ft (at most 4 points a house, each moved on its normal, 2 a point)
    the frame's ring, 100 ft deep outside the hull, added to lane ground in 6 ft cells: each decided from the free-ground
        raster (the 2 by 2 cells of 32 ft a 6 ft cell tested at the 8 ft widest margin straddles, each read with its segments),
        and only a cell within 8 ft of the hull against the parts of the 2 by 2 cells of 64 ft it straddles; then the
        homesteads' flood extended over the ring on its bucket queue, so the spine and the joins descend it there too
    the spine: traced along the cluster's long axis on lane ground's flood, end to end - each step the neighbor of least
        flood value read from its 8 (8), the step taken (1), its 25 ft band marked (10)
    the back lanes: a line across the frame every 100 ft along the long axis; each walked over lane ground's cells, its free
        stretches the runs (a homestead it crosses splits it); each run's two ends reached to the network along the flood
        within the pitch, traced as the spine is
    each lane, before it is filed: trimmed back to the last house it serves (its end legs walked); each run's end, as it is
        reached, against the ends and junctions in its 3 by 3 cells of a 25 ft endpoint index (closed or met at one node), and
        an end within the frame's 100 ft of the field given its one leg on to the bund, tested against the outline index's
        cells; the lane pulled taut by a funnel over its lane-ground cells, and its vertices' angles tested for a hairpin and,
        for a zigzag, the legs within 40 ft; then recorded, its corridor filed in the parts index and its cells marked on lane
        ground as a way's
    each household: the lane-ground cells within 12 ft of its built ground and within 60 ft of its house read for a way's
        mark (the 60 ft and 12 ft tests); none marked: its door path traced on the flood, as its way was

## Indexes

- lane ground: cells of 6 ft (the homesteads'); densest 1 a cell, from a smallest side of 6 ft - a cell holds one state and one flood value
- parts index: cells of 64 ft (the homesteads'); densest 7 placed parts a cell, from a smallest side of 64 ft
- outline index: cells of 64 ft (the field's); densest 12 outline segments a cell, from a smallest side of 64 ft
- endpoint index: cells of 25 ft (`KNOT_FT`, the reach at which two ends meet), so an end's partners lie in its 3 by 3 cells; densest 4 ends a cell (measured at 10 and 20, 3 and 4: a junction meets at most four ways), from a smallest side of 25 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the web, one network | always 1 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the frame (hull points moved) | over the run | 160 at 20, 320 at 40, 640 at 80 | the hull's at most 4 points a house, each moved on its normal, 2 | 80 households |
| the frame's ring (lane ground cells written) | over the run | 919,356 at 20, 1,368,366 at 40, 2,055,096 at 80 | the ring outside the hull, the hull's perimeter, at most the cluster's 2 x (width + length), by 100 ft plus pi x 100 squared, over 36 sq ft (11,068 at 20, 16,462 at 40, 24,712 at 80 cells), each decided from the at most 2 by 2 cells of 32 ft it straddles at the 8 ft margin, each read with its at most 20 segments (4 x 20 + 1, 81); the cells within 8 ft of the hull (816 at 20, 1,248 at 40, 1,908 at 80) also against the 2 by 2 cells of 64 ft with their 7 parts (28) | 80 households |
| the ring's flood (lane ground cells examined) | over the run | 287,768 at 20, 428,012 at 40, 642,512 at 80 | the homesteads' flood extended over the ring's cells, 26 a cell on its bucket queue (the homesteads' figure: popped, 8 neighbors read, at most 8 pushes, the buckets scanned) | 80 households |
| the back lanes (lane ground cells examined) | over the run | 2,240 at 20, 4,620 at 40, 9,604 at 80 | 14 at 20, 20 at 40, 28 at 80 lines, the frame's long side over 100 ft plus 1, each the frame's short side over 6 ft plus 1 cells, each read (1) | 80 households |
| the spine (lane ground cells examined) | over the run | 7,087 at 20, 10,165 at 40, 14,858 at 80 | at most the frame's long side plus its short side (the flood's walk bends round the plots, at most one side's width aside) over 6 ft (373 at 20, 535 at 40, 782 at 80 cells), each traced: its 8 neighbors read, the step, its 25 ft band marked, 2 x 25 / 6 + 1 rounded up, 10 (19) | 80 households |
| the joins (lane ground cells examined) | over the run | 34,884 at 20, 64,600 at 40, 121,448 at 80 | the runs, the lines plus 2 a house (54 at 20, 100 at 40, 188 at 80), each of their two ends reached along the flood within the pitch, 100 ft over 6 ft, 17 cells, each traced (19) | every run joined at both ends |
| the laying (parts index cells written) | over the run | 4,040 at 20, 7,632 at 40, 14,636 at 80 | the lanes' length - the back lanes, the spine, at each run's end 100 ft of join and 100 ft of bund leg, and 372 ft a household's door path - 44,575 at 20, 85,646 at 40, 167,023 at 80 ft, in at most 345 at 20, 641 at 40, 1,209 at 80 legs (3 a household's way; 5 a run: its stretch, its two joins and its two bund legs; and the spine's at most one bend a line plus 1), its corridor (the lane and its 7 ft clearance a side, under 64 ft) in at most 2 cells across: 2 x (the length at root 2 over 64 ft, plus 3 a leg) | every lane at its longest |
| the door paths (lane ground cells examined) | over the run | 34,800 at 20, 69,600 at 40, 139,200 at 80 | each household: the lane-ground cells within 12 ft of its built ground, its 4 x 184 ft perimeter by 12 ft over 36 sq ft, 246, and within 60 ft of its house, pi x 60 squared over 36 sq ft, 315, each read for a way's mark (561); its door path traced, at most 62 cells (the homesteads' figure for a way), each traced (19); and the decision (1) | every household needing one |
| the trims (legs walked) | over the run | 345 at 20, 641 at 40, 1,209 at 80 | each leg walked at most once from a lane's end, before it is filed | every lane trimmed |
| the bund (outline index cells examined) | over the run | 8,424 at 20, 15,600 at 40, 29,328 at 80 | each run's two ends, as reached, one leg of at most 100 ft (an end within the frame's 100 ft of the field): 100 x root 2 / 64 + 3, 5.2, rounded up to 6 cells, each with its 12 segments (13) | every end near the field |
| the knots (endpoint index cells examined) | over the run | 4,860 at 20, 9,000 at 40, 16,920 at 80 | each run's two ends, as reached and before the lane is filed: its 3 by 3 cells of 25 ft, each read with its at most 4 ends, 9 x (4 + 1) | every end near another |
| the taut pull (lane ground cells examined) | over the run | 14,860 at 20, 28,550 at 40, 55,676 at 80 | a funnel over each lane's cells before it is filed, the lanes' length over 6 ft, each cell's two sides tested once (2) | every lane pulled |
| the kinks (legs tested) | over the run | 3,105 at 20, 5,769 at 40, 10,881 at 80 | each vertex's angle (1) and, for a zigzag, the legs within 40 ft, at most 40 / 6 rounded up, 7, and the decision (1) | every vertex a kink |

So: 1 x 1, plus the frame, the ring, the ring's flood, the back lanes, the spine, the joins, the laying, the door paths, the trims, the bund, the knots, the taut pull and the kinks.

## Totals

- at 20: 1 x 1 + 160 + 919356 + 287768 + 2240 + 7087 + 34884 + 4040 + 34800 + 345 + 8424 + 4860 + 14860 + 3105 = 1321930
- at 40: 1 x 1 + 320 + 1368366 + 428012 + 4620 + 10165 + 64600 + 7632 + 69600 + 641 + 15600 + 9000 + 28550 + 5769 = 2012876
- at 80: 1 x 1 + 640 + 2055096 + 642512 + 9604 + 14858 + 121448 + 14636 + 139200 + 1209 + 29328 + 16920 + 55676 + 10881 = 3112009

## Earlier findings

- verdict-1, finding 1: fixed - a ring cell is decided from its 32 ft raster cell and its at most 20 segments (21; the raster's cells are 32 ft, 1 ft a pixel is the map's scale), and only a cell within 8 ft of the hull against the 2 by 2 cells of 64 ft it straddles (28)
- verdict-1, finding 2: fixed - the door path's 62 cells is the homesteads' figure for a household's way, cited in the Bounds
- verdict-1, finding 3: fixed - no ways index is read: the door tests read lane ground's way marks, which each way sets as it is laid
- verdict-1, finding 4: fixed - the bund leg is at most 100 ft because only an end within the frame's 100 ft of the field runs on; a traced step reads its 8 neighbors; the spine is the frame's long side plus its short side over 6 ft, with no second root 2; the band is 2 x 25 / 6 + 1 cells
- verdict-1, finding 5: fixed - each lane is trimmed, pulled taut and cleared of kinks before it is filed (S4)
- verdict-1, finding 6: fixed - the ring's area is the hull's perimeter by 100 ft plus pi x 100 squared
- verdict-1, finding 7: fixed - the knots read 9 cells x (4 + 1) an end
- verdict-1, finding 8: fixed - the joins count both ends of a run
- verdict-1, finding 9: fixed - the door path's window is the cells the built ground grown 12 ft covers, 5 by 5
- verdict-2, finding 1: fixed - the ways index and its 48 are gone: a household's tests read the lane-ground cells within 12 ft of its built ground and 60 ft of its house for a way's mark, 561 cells
- verdict-2, finding 2: fixed - the homesteads' flood is extended over the ring on its bucket queue, 26 a cell, its own row
- verdict-2, finding 3: fixed - the knots and the bund leg are asked at each run's end as it is reached, before the lane is filed, and the bund legs are in the laying's legs and length (S4)
- verdict-2, finding 4: disputed - the bund's cells are 100 x root 2 / 64 + 3 = 5.2, rounded up to 6, the laying row's own rule; 5 would round down
- verdict-2, finding 5: fixed - with no ways index there is no leg filing to count; the way marks are the trace's own band marks
- verdict-2, finding 6: fixed - a ring cell reads the 2 by 2 cells of 32 ft it straddles at the 8 ft margin, 81
- verdict-2, finding 7: fixed - the corridor is the lane and its 7 ft clearance a side (`LANE_CLEARANCE`), under 64 ft

## Cheaper algorithms considered

- sweep: used - the back lanes are a sweep of parallel lines across the frame, each walked once over lane ground
- grid or spatial index: used - lane ground and its flood (the homesteads'), the parts, outline and endpoint indexes
- priority queue: not used - the flood is the homesteads' (on its bucket queue); the web only traces along it
- incremental update: used - each lane's cells are marked on lane ground as a way's as it is laid, for the households' tests
- memoizing what a scan does not change: used - lane ground and its flood are read, not rebuilt; only the frame's ring is added, and only its cells near the hull read the parts
