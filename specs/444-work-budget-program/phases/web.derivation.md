# Derivation - web (feature 444)

## Contract

- Reads: the placed homesteads and the cluster's declared shape (its hull, from the homesteads); lane ground, the homesteads' 6 ft raster of the gaps with its flood from the gate, and the households' ways already laid and reserved (`access_corridors`); the connector; the site's free-ground raster (the field, the crop, the wet ground, the toe and the marsh) and the parts index; the field's outline index (the bund); the form (a dispersed hamlet draws no web).
- Writes: the web's lanes (`lanes`): the spine along the cluster, the back lanes cut across it, each run reached to the network, the door paths of the farms no way reaches; each lane's corridor; then the web read as shapes - near-junctions closed, each junction made once, ends within a few paces met at one node, each lane pulled taut and cleared of hairpins (140 degrees) and zigzags (50 degrees within 40 ft).
- Keeps: the lanes after the houses (0246); the web cut in a frame of 100 ft (`BUNDLE_PITCH`) past the outermost house and trimmed back where a lane stops serving (0246, a departure); back lanes at the bundle's pitch, 100 ft; a lane's middle 7 ft off a garden fence (`WEB_FABRIC_GAP`), 3 ft off the field and the crop (`WEB_CROP_GAP`), 8 ft off the toe and the marsh (`WEB_HARD_GAP`, UNRESEARCHED); a stretch across the field, a crop or wet ground cut out (0081); a belt crossed, not followed (0072); no door path where a way's point nearest a house is within 60 ft of it or 12 ft of its built ground (`STEADING_ARRIVAL_FT`); lanes run on to the bund (0014); a dispersed hamlet draws none (0031); each lane asked before it is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80), so the frame, 100 ft past each side, 950 by 1,285 ft at 20, 1,378 by 1,828 ft at 40, 2,049 by 2,642 ft at 80; the ways' legs at most 8 a household (2.4 and 7.2 a household measured: a household's way is at most 3 legs, the homesteads' budget, and the web's lanes are pulled taut between the plots they serve); a homestead's extent at most 184 ft, so it crosses at most 2 back lanes 100 ft apart; at most 7 placed parts in a 64 ft cell; at most 12 outline segments in a 64 ft cell; at most 3 and 21 way legs in a 64 ft cell (21 taken, measured at 10 and 20); 1 ft a pixel at the hamlet scale.

## The algorithm

    the frame: the cluster's hull offset 100 ft (each hull point moved, 2 a point)
    the frame's ring, 100 ft deep outside the homesteads' gap bands, added to lane ground in 6 ft cells, each decided from the
        free-ground raster and the parts index (9)
    the spine: traced along the cluster's long axis on lane ground's flood, end to end
    the back lanes: a line across the frame every 100 ft along the long axis; each walked over lane ground's cells, its free
        stretches the runs (a homestead it crosses splits it); each run's ends reached to the network along the flood (the
        25 ft join, marked as each way is laid)
    lay each lane: recorded, its corridor filed in the parts index
    each household: the ways' legs in its 3 by 3 cells of 64 ft read for the point nearest its house (the 60 ft and 12 ft
        tests); none near: its door path traced on the flood, as its way was
    trim each lane's ends back to the last house it serves (each end's legs walked)
    each run's end near the field: one leg on to the bund, tested against the outline index's cells it crosses
    settle: each lane end against the ends and junctions in its 3 by 3 cells of a 25 ft endpoint index (closed or met at
        one node); each lane pulled taut by a funnel over its lane-ground cells; each vertex's angle tested for a hairpin,
        and for a zigzag the legs within 40 ft

## Indexes

- lane ground: cells of 6 ft (the homesteads'); densest 1 a cell, from a smallest side of 6 ft - a cell holds one state and one flood value
- parts index: cells of 64 ft (the homesteads'); densest 7 placed parts a cell, from a smallest side of 64 ft
- ways index: cells of 64 ft, the laid ways' legs filed as each is laid; densest 21 legs a cell (measured at 10 and 20, 3 and 21, the ceiling taken), from a smallest side of 64 ft
- outline index: cells of 64 ft (the field's); densest 12 outline segments a cell, from a smallest side of 64 ft
- endpoint index: cells of 25 ft (`KNOT_FT`, the reach at which two ends meet), so an end's partners lie in its 3 by 3 cells; densest 4 ends a cell (measured at 10 and 20, 3 and 4: a junction meets at most four ways), from a smallest side of 25 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the web, one network | always 1 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the frame (hull points moved) | over the run | 160 at 20, 320 at 40, 640 at 80 | the hull's at most 4 points a house, each moved on its normal, 2 | 80 households |
| the frame's ring (lane ground cells written) | over the run | 111,753 at 20, 160,308 at 40, 234,558 at 80 | the frame's perimeter by 100 ft over 36 sq ft, each cell decided from the raster and the parts index (9) | 80 households |
| the back lanes (lane ground cells examined) | over the run | 2,240 at 20, 4,620 at 40, 9,604 at 80 | 14 at 20, 20 at 40, 28 at 80 lines, the frame's long side over 100 ft plus 1, each the frame's short side over 6 ft plus 1 cells, each read (1) | 80 households |
| the spine (lane ground cells examined) | over the run | 3,333 at 20, 4,741 at 40, 6,853 at 80 | the frame's long side at root 2 over 6 ft, each cell traced (1) and its 25 ft band marked (10) | 80 households |
| the joins (lane ground cells examined) | over the run | 10,098 at 20, 18,700 at 40, 35,156 at 80 | the runs, the lines plus 2 a house (54 at 20, 100 at 40, 188 at 80), each end reached along the flood within the pitch, 100 ft over 6 ft, 17 cells, each traced (1) and marked (10) | every run joined |
| the laying (parts index cells written) | over the run | 2,196 at 20, 4,352 at 40, 8,688 at 80 | the lanes' length - the back lanes, the spine, 100 ft a run, and 372 ft a household's door path at most - 27,958 at 20, 55,026 at 40, 109,669 at 80 ft, in at most 8 legs a household, its corridor in at most 2 cells across: 2 x (the length at root 2 over 64 ft, plus 3 a leg) | every lane at its longest |
| the door paths (ways index and lane ground cells examined) | over the run | 17,620 at 20, 35,240 at 40, 70,480 at 80 | each household: its 3 by 3 cells of 64 ft with their at most 21 legs (198), and its door path traced, 62 cells each traced and marked (682), and the decision (1) | every household needing one |
| the trims (legs walked) | over the run | 160 at 20, 320 at 40, 640 at 80 | each leg walked at most once from a lane's end | every lane trimmed |
| the bund (outline index cells examined) | over the run | 8,424 at 20, 15,600 at 40, 29,328 at 80 | each run's two ends, one leg of at most 100 ft on to the bund, at root 2 over 64 ft plus 3 cells, each with its 12 segments (13) | every end near the field |
| the knots (endpoint index cells examined) | over the run | 1,404 at 20, 2,600 at 40, 4,888 at 80 | each run's two ends: its 3 by 3 cells of 25 ft (9) and their at most 4 ends | every end near another |
| the taut pull (lane ground cells examined) | over the run | 9,320 at 20, 18,342 at 40, 36,558 at 80 | a funnel over each lane's cells, the lanes' length over 6 ft, each cell's two sides tested once (2) | every lane pulled |
| the kinks (legs tested) | over the run | 1,440 at 20, 2,880 at 40, 5,760 at 80 | each vertex's angle (1) and, for a zigzag, the legs within 40 ft, at most 40 / 6 rounded up, 7, and the decision (1) | every vertex a kink |

So: 1 x 1, plus the frame, the ring, the back lanes, the spine, the joins, the laying, the door paths, the trims, the bund, the knots, the taut pull and the kinks.

## Totals

- at 20: 1 x 1 + 160 + 111753 + 2240 + 3333 + 10098 + 2196 + 17620 + 160 + 8424 + 1404 + 9320 + 1440 = 168149
- at 40: 1 x 1 + 320 + 160308 + 4620 + 4741 + 18700 + 4352 + 35240 + 320 + 15600 + 2600 + 18342 + 2880 = 268024
- at 80: 1 x 1 + 640 + 234558 + 9604 + 6853 + 35156 + 8688 + 70480 + 640 + 29328 + 4888 + 36558 + 5760 = 443154

## Cheaper algorithms considered

- sweep: used - the back lanes are a sweep of parallel lines across the frame, each walked once over lane ground
- grid or spatial index: used - lane ground and its flood (the homesteads'), the parts, ways, outline and endpoint indexes
- priority queue: not used - the flood is the homesteads' (on its bucket queue); the web only traces along it
- incremental update: used - each lane's legs are filed in the ways index and its band marked as it is laid
- memoizing what a scan does not change: used - lane ground and its flood are read, not rebuilt; only the frame's ring is added
