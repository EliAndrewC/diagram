# Derivation - web (feature 444)

## Contract

- Reads: the placed homesteads and the cluster's declared shape (its hull, from the homesteads); lane ground, the homesteads' 6 ft raster of the gaps with its flood from the gate, and the households' ways already laid and reserved (`access_corridors`); the connector; the site's free-ground raster (32 ft cells: the field, the crop, the wet ground, the toe and the marsh) and the parts index; the field's outline index (the bund); the form (a dispersed hamlet draws no web).
- Writes: the web's lanes (`lanes`): the spine along the cluster, the back lanes cut across it, each run reached to the network, the door paths of the farms no way reaches; each lane's corridor; the web read as shapes - near-junctions closed, each junction made once, ends within a few paces met at one node, each lane pulled taut and cleared of hairpins (140 degrees) and zigzags (50 degrees within 40 ft).
- Keeps: the lanes after the houses (0246); the web cut in a frame of 100 ft (`BUNDLE_PITCH`) past the outermost house and trimmed back where a lane stops serving (0246, a departure); back lanes at the bundle's pitch, 100 ft; a lane's middle 7 ft off a garden fence (`WEB_FABRIC_GAP`), 3 ft off the field and the crop (`WEB_CROP_GAP`), 8 ft off the toe and the marsh (`WEB_HARD_GAP`, UNRESEARCHED); a stretch across the field, a crop or wet ground cut out (0081); a belt crossed, not followed (0072); no door path where a way's point nearest a house is within 60 ft of it or 12 ft of its built ground (`STEADING_ARRIVAL_FT`); a lane end within the frame's 100 ft of the field runs on to the bund (0014); a dispersed hamlet draws none (0031); each lane asked, trimmed and pulled taut before it is filed (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80), so the frame, 100 ft past each side, 950 by 1,285 ft at 20, 1,378 by 1,828 ft at 40, 2,049 by 2,642 ft at 80; a homestead's extent at most 184 ft, so it crosses at most 2 back lanes 100 ft apart; a household's way at most 3 legs and at most 62 lane-ground cells (the homesteads' budget: half a homestead's 4 x 184 ft perimeter over 6 ft); at most 7 placed parts in a 64 ft cell; at most 20 site-boundary segments in a 32 ft cell; at most 12 outline segments in a 64 ft cell; 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does. The ways' shares (FR-014, measured 2026-10-28 on the reference manifests at 10 and 20): of the web's lane ends, 0.18 and 0.11 lie within 100 ft of the field (0.18 taken); of its vertices, 0.42 and 0.17 turn past 50 degrees (0.17, falling); the ends a 25 ft cell holds where any, 1.05 and 1.1; a homestead's mean extent 117 ft.

## The algorithm

    the frame: the cluster's hull offset 100 ft (at most 4 points a house, each moved on its normal, 2 a point)
    the frame's ring, 100 ft deep outside the hull, added to lane ground in 6 ft cells: each decided from the free-ground
        raster dilated by the 8 ft widest margin: each boundary segment in the 32 ft cells the ring meets marks the 6 ft cells within
        8 ft of it, once, with its margin class (3 ft off the field and the crop, 7 ft off a fence, 8 ft off the toe and marsh), and a ring cell then reads its 32 ft cell's state and its own mark,
        and only a cell within 8 ft of the hull against the parts of the 2 by 2 cells of 64 ft it straddles; then the
        homesteads' flood extended over the ring on its bucket queue, so the spine and the joins descend it there too
    the spine: traced along the cluster's long axis on lane ground's flood, end to end - each step the neighbor of least
        flood value read from its 8 (8), the step taken (1), the cell marked a way's (1), its 25 ft join band marked (10)
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
| slack | per item | 2 | what varies around the typical case (S8): the spread around the mean, a door path traced where a household's way misses its door | a sprawling cluster |
| the frame (hull points moved) | over the run | 144 at 20, 224 at 40, 344 at 80 | the hull's points, the fringe houses' corners - the cluster's perimeter over the 204 ft pitch, 4 corners each - each moved on its normal, 2 | the typical cluster |
| the frame's ring (lane ground cells written) | over the run | 58,854 at 20, 88,004 at 40, 132,500 at 80 | the ring's 6 ft cells (11,068 at 20, 16,462 at 40, 24,712 at 80), each its 32 ft cell's state and its mark (2); the raster cells it meets, 4.6 across for each 32 ft of the mid-ring perimeter at the mean (575 at 20, 856 at 40, 1,284 at 80), each its boundary's length in the cell, about 9 cells of 6 ft plus one a segment end at the mean 2.5, marking 4 across (46); the cells within 8 ft of the hull, 2.33 across for each 6 ft of it (1,426 at 20, 2,181 at 40, 3,335 at 80), each in its about 1.8 cells of 64 ft with the mean 3 parts and the cell (7.2) | the typical cluster |
| the ring's flood (lane ground cells examined) | over the run | 132,816 at 20, 197,544 at 40, 296,544 at 80 | the homesteads' flood extended over the ring, 12 a cell: popped (1), 8 neighbors read (8), pushed twice (2), its bucket scanned (1) | the typical cluster |
| the back lanes (lane ground cells examined) | over the run | 2,240 at 20, 4,620 at 40, 9,604 at 80 | 14 at 20, 20 at 40, 28 at 80 lines, the frame's long side over 100 ft plus 1, each the frame's short side over 6 ft plus 1 cells, each read (1) | the typical cluster |
| the spine (lane ground cells examined) | over the run | 4,300 at 20, 6,100 at 40, 8,820 at 80 | an 8-neighbor descent along the long axis, the frame's long side over 6 ft (215 at 20, 305 at 40, 441 at 80 cells), each traced: 8 neighbors read, the step, its way mark, its join band of 10 (20) | the typical cluster |
| the joins (lane ground cells examined) | over the run | 7,600 at 20, 13,400 at 40, 24,400 at 80 | the runs, the lines plus the mean 1.17 a house (a homestead's mean 117 ft extent over the 100 ft pitch; 38 at 20, 67 at 40, 122 at 80), each of their two ends reached along the flood a quarter pitch at the mean, 25 ft over 6 ft, 5 cells, each traced (20) | the typical cluster |
| the laying (parts index cells written) | over the run | 1,118 at 20, 2,134 at 40, 4,164 at 80 | the lanes' length - the back lanes, the spine, 25 ft at each run end's join and the bund legs at the 0.18 of ends near the field, 100 ft each - 17,853 at 20, 35,150 at 40, 70,506 at 80 ft, in 203 at 20, 367 at 40, 679 at 80 legs (3 a household's way, a run's stretch and its 2 joins and its 0.36 bund legs, the spine's bends); its corridor at a random angle, 2 x (the length x (4/pi) over 64 ft, plus 1 a leg) | the typical cluster |
| the door paths (lane ground cells examined) | over the run | 100 at 20, 200 at 40, 400 at 80 | each household's own way, laid by the homesteads, tested first at its door (5); the scan outward from the door, stopping at the first mark, only where it fails, inside the slack | the typical cluster |
| the trims (legs walked) | over the run | 203 at 20, 367 at 40, 679 at 80 | each leg walked at most once from a lane's end, before it is filed | the typical cluster |
| the bund (outline index cells examined) | over the run | 206 at 20, 362 at 40, 659 at 80 | the run ends near the field, 0.18 of them (measured), one leg of at most 100 ft in at most 5 cells, each with the mean 2 outline segments and the cell (15) | the typical cluster |
| the knots (endpoint index cells examined) | over the run | 1,444 at 20, 2,546 at 40, 4,636 at 80 | each run's two ends: its 3 by 3 cells of 25 ft, each read with the mean 1.1 ends (measured) and the cell (19) | the typical cluster |
| the taut pull (lane ground cells examined) | over the run | 5,952 at 20, 11,718 at 40, 23,502 at 80 | a funnel over each lane's cells before it is filed, the lanes' length over 6 ft, each cell's two sides tested once (2) | the typical cluster |
| the kinks (legs tested) | over the run | 273 at 20, 492 at 40, 910 at 80 | each vertex's angle (1), and the zigzag's look at the 0.17 of vertices that turn past 50 degrees (measured), 2 each (1.34) | the typical cluster |

So: 1 x 2, plus each row.

## Totals

- at 20: 1 x 2 + 144 + 58854 + 132816 + 2240 + 4300 + 7600 + 1118 + 100 + 203 + 206 + 1444 + 5952 + 273 = 215252
- at 40: 1 x 2 + 224 + 88004 + 197544 + 4620 + 6100 + 13400 + 2134 + 200 + 367 + 362 + 2546 + 11718 + 492 = 327713
- at 80: 1 x 2 + 344 + 132500 + 296544 + 9604 + 8820 + 24400 + 4164 + 400 + 679 + 659 + 4636 + 23502 + 910 = 507164

## Earlier findings

- verdict-4, finding 1: fixed - the bund's, the kinks' and the knots' shares measured on the reference manifests (0.18, 0.17, 1.1); the laying, taut pull, trims and kinks on the re-scored length and legs (no door path, the bund legs at 0.18); the joins at a quarter pitch; the runs at the mean 1.17 a house; the door test on the household's own way first; the ring's marking, the near-hull straddle and the bands at their means; the spine an 8-neighbor descent; the frame on the fringe houses
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
- verdict-2, finding 4: fixed - the bund leg meets at most 5 cells, 1 + its run and its rise over 64 ft rounded up (verdict-3's reading)
- verdict-2, finding 5: fixed - with no ways index there is no leg filing to count; the way marks are the trace's own band marks
- verdict-2, finding 6: fixed - the ring's raster is dilated by the 8 ft margin once (each segment marking the 6 ft cells within 8 ft of it, 720 a raster cell at the densest), and a ring cell reads its 32 ft cell's state and its mark (2), verdict-2's own alternative
- verdict-2, finding 7: fixed - the corridor is the lane and its 7 ft clearance a side (`LANE_CLEARANCE`), under 64 ft
- verdict-3, finding 1: fixed - the ring's flood's 26 is cited from the homesteads' flood row with its parts, the buckets scanned a run term at most 9 a cell
- verdict-3, finding 2: fixed - the dilation marks each 6 ft cell with its margin class, 3, 7 or 8 ft, the 8 ft band the widest
- verdict-3, finding 3: fixed - a traced cell is marked a way's (1) apart from its 25 ft join band, and the door tests read the way's mark
- verdict-3, finding 4: fixed - the bund's 5 cells
- verdict-3, finding 5: fixed - the ring's raster cells are 5 across for each 32 ft of the mid-ring perimeter; the cells near the hull 3 across for each 6 ft of it; the door's 12 ft band 3 across for each 6 ft of the perimeter and its corners, 404
- reason above the reference: the web is one network laid over the whole cluster's gaps, its frame's ring and its back lanes, so its items row is 1; at 40 it is about 8,193 a household
- FR-014 re-score: each factor at the typical case (rubric S8): the ring's boundary marks and its parts at the mean densities of `items.md`, the flood at the homesteads' typical 12 a cell, no door path where a household's own way passes its door, the bund legs only at the run ends near the field; slack 2 (ask:444-budget-standard; the accept was ask:444-T04-web-round-4)

## Cheaper algorithms considered

- sweep: used - the back lanes are a sweep of parallel lines across the frame, each walked once over lane ground
- grid or spatial index: used - lane ground and its flood (the homesteads'), the parts, outline and endpoint indexes
- priority queue: not used - the flood is the homesteads' (on its bucket queue); the web only traces along it
- incremental update: used - each lane's cells are marked on lane ground as a way's as it is laid, for the households' tests
- memoizing what a scan does not change: used - lane ground and its flood are read, not rebuilt; only the frame's ring is added, its raster dilated once, and only its cells near the hull read the parts
