# Derivation - polder, greenfield (feature 444 FR-015; the round arbiter's ruling on ask:444-polder-sizes, route a)

The field stage's polder forms - the rice polder on its surveyed grid and the dike-pond block - written from their contract alone.
The dike-pond is derived here and bounds the budget: the polder grid draws no ponds, its plots (each split strip a 4-cornered ring
and its record, 5) in their place, at most the ponds' 13 a parcel, and shares every other row.

## Contract

- Reads: the plan (the field archetype, the pond layout - mosaic or chessboard - the dike crop, the leftover form, the fry form,
  the fall on the four cardinals, the wind); the households; the site's ground and the wild water the polder is diked against.
- Writes: the polder's block on its lattice of modules (0022: a rice polder's modules about 190 ft on a side, a dike-pond block's
  about 160 ft, most merged in pairs - so a pond's parcel about 160 by 320 ft with gaps of about 22 ft both ways); each pond's
  parcel, bank and water as four-sided rings (0019: "keeps every pond four-sided", the lattice bent by a smooth drift that fades to
  nothing at the fixed outer edge); the plots that are not ponds and their land use; the dike - its crest, its two faces, its
  sluice gaps (0027); its two rows of trees (0027: willow about 8.5 ft apart three quarters of the way out, mulberry about 4.4 ft
  apart a quarter of the way, on the field side, both rows cut where a channel crosses); the ring canal round the dike's inside
  foot (0019); the field ditches in the column corridors (0022: a ditch corridor of about 8 ft between columns); the reed fringe on
  the flanks that hold water back - every flank but the landward one (0019: "as every flank of a polder but the landward one does"), three of four; the wild pond that feeds the polder; the knobs the polder draws by, written to the meta;
  every water and crest segment filed in the water index.
- Keeps: every pond four-sided (0019); modules of whole size, never a grid of uniform rectangles (0022: "Our maps never draw the
  parcels as a grid of uniform rectangles"); the dike's band 14 to 40 ft across, changing in width, never a ruled line (0027); no
  channel outside the dike (0019); the polder's paddy at least the households' (0017), in whole modules.
- Bounds: a bounded n: households 10-20 (0019's GUESS: "the ten to twenty households this project guesses ... for a small
  polder"; the plan draws no polder past 20). Measured 2026-10-31 on the dike-pond at seed 4 (`phases/polder.bounds.json`,
  `polder.sizes.json`, `polder.dike.json`): ponds 19 and 38, the plots that are not ponds 21 and 42, the dike's crest 3,885 and
  5,165 ft at 10 and 20 households; the block about 1,323 by 694 and 1,664 by 1,043 ft; two sluice gaps; one wild pond.

## The algorithm

    the polder's paddy from the households and the land each works, in whole modules at or above it (2)
    the block's rows and columns, from at most the square root of the modules' count of shapes on the cardinal grid (2 a shape)
    the lattice's crossings placed (1 a crossing), each moved by the mosaic's smooth drift, zero on the outer edge, on a mosaic only -
      two rolls in three (1 a crossing, at that share)
    each pond: its parcel, bank and water rings, 4 corners each from the lattice, and its record (13)
    each plot that is not a pond: its land use rolled and written (2); the land use's record (2)
    the dike: its crest a point every 27 ft round the block - the band's mean breadth, 0027's 14-40 ft, so its width changes once a
      breadth (placed, its width rolled in 14-40 ft: 2 a point); its two faces offset
      from the crest at each point (1 a point a face); its two sluice gaps cut (2 each)
    its trees: willow every 8.5 ft and mulberry every 4.4 ft along the crest's length, each placed on its row and written (2)
    the ring canal at the dike's inside foot, a point at each crest point, every 27 ft (1); the field ditches, one a column corridor,
      its 2 points written (1 each) and its record (2): 4 each; the reed fringe along the three water flanks, a point every 27 ft
      (1); the wild pond and its layer (6)
    the knobs written to the meta (7)
    every water segment filed in the water index - each pond's four water sides, the ring canal's, the crest's, each ditch, and the
      wild pond's box - in every cell it crosses, 1 + its length / 64 a segment

## Indexes

- water index: cells of 64 ft, each segment filed in every cell it crosses, 1 + its length / 64 a segment, its densest case from a smallest side of 64 ft (a pond's 124 ft water side, 3 cells); the polder's lattice is its own grid, so no placement asks the index - the index is written for the stages after.

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 19 at 10, 38 at 20 | the ponds, measured at 10 and 20 | the dike-pond's; the polder grid's plots fewer a module |
| a pond | per item | 13 | its parcel, bank and water rings, 4 corners each, and its record | always 13 |
| slack | per item | 1 | every factor a count of the polder's output measured or set by its research, none a search | not applicable |
| the area | once | 2 | the households read and the paddy each works applied, rounded up to whole modules | always 2 |
| the block's shapes | over the run | 14 at 10, 18 at 20 | 2 a shape over the square root of the modules' count, 38 and 76 modules (two to a pond) | a near-square block |
| the lattice crossings | over the run | 88 at 10, 158 at 20 | 53 and 95 crossings (the modules plus two sides' lines plus one), each placed (1) and drifted on a mosaic at its share, two rolls in three (0019's layout knob) | a mosaic |
| the plots not ponds | over the run | 42 at 10, 84 at 20 | each land use rolled and written (2), 21 and 42 plots | always 2 a plot |
| the land use's record | once | 2 | written once | always 2 |
| the dike's crest | over the run | 288 at 10, 382 at 20 | a point every 27 ft, the band's mean breadth (0027's 14-40 ft), of 3,885 and 5,165 ft, placed and its width rolled (2), 144 and 191 points | a long narrow block |
| the dike's faces | over the run | 288 at 10, 382 at 20 | two faces offset at each crest point (1 a face) | always 2 a crest point |
| the sluice gaps | once | 4 | two gaps cut, 2 each | always 4 |
| the willow row | over the run | 914 at 10, 1216 at 20 | a tree every 8.5 ft of the crest (0027), placed and written (2), 457 and 608 | the longest crest |
| the mulberry row | over the run | 1766 at 10, 2348 at 20 | a bush every 4.4 ft of the crest (0027), placed and written (2), 883 and 1,174 | the longest crest |
| the ring canal | over the run | 144 at 10, 191 at 20 | a point at each crest point, at the dike's foot (1) | always the crest's count |
| the field ditches | over the run | 40 at 10, 48 at 20 | one a column corridor, 10 and 12 columns, its 2 points (1 each) and its record (2): 4 each | a wide block |
| the reed fringe | over the run | 108 at 10, 143 at 20 | a point every 27 ft along the three flanks that hold water back (0019), three quarters of the crest (1) | always three flanks |
| the wild pond | once | 6 | the pond's 4 figures and its layer's 2 | always 6 |
| the meta | once | 7 | the polder's knobs written | always 7 |
| the water index (cells examined, each written) | over the run | 844 at 10, 1366 at 20 | 1 + length / 64 cells a segment: each pond's water about 124 by 248 ft (0022's 160 by 320 ft parcel, its water about 0.29 of 0.48 ha), 16 cells, 304 and 608; each ditch one segment the block's height, 694 and 1,043 ft, 12 and 17 cells, 120 and 204; the crest's and the ring canal's 144 and 191 segments of 27 ft, 1.42 cells, 205 and 272 each; the wild pond's box, 164 by 108 ft (measured 2026-10-31, the pond's radii 82 and 54 ft), 10 cells | the typical block |

So: the ponds times 13 times the slack, plus each over-the-run and once row.

## Totals

- at 10: 19 x 13 x 1 + 2 + 14 + 88 + 42 + 2 + 288 + 288 + 4 + 914 + 1766 + 144 + 40 + 108 + 6 + 7 + 844 = 4804
- at 20: 38 x 13 x 1 + 2 + 18 + 158 + 84 + 2 + 382 + 382 + 4 + 1216 + 2348 + 191 + 48 + 143 + 6 + 7 + 1366 = 6851

## Growth

From 10 to 20 households the polder grows at an exponent of about 0.51 (ln(6,851 / 4,804) / ln 2): the ponds, the plots and the
lattice with its area, the dike, its trees, the canal and the fringe with its perimeter, which grows as the square root.

## Cheaper algorithms considered

- sweep: not used - the lattice is laid in order, row by row, and nothing is searched
- grid or spatial index: used - the polder is its own lattice, so no placement asks a neighbor; the water index is written for later stages
- priority queue: not used - nothing is chosen best-first
- incremental update: used - the lattice's crossings are moved once and every pond takes its corners from them, never recomputed
- memoizing what a scan does not change: used - the crest's points carry the band's width, and the faces and both tree rows are read off them, not rescanned

## Earlier findings

- verdict-1, finding 1: fixed - the point spacing derived: every 27 ft, the dike band's mean breadth (0027's 14-40 ft), so the width changes once a breadth; the ring canal and the fringe take the crest's points
- verdict-1, finding 2: fixed - the fringe's three flanks cited: 0019, every flank but the landward one
- verdict-1, finding 3: fixed - a ditch's 4 shown: its 2 points (1 each) and its record (2)
- verdict-1, finding 4: fixed - the mosaic's drift charged at its share, two rolls in three (the layout knob's table), each crossing placed (1) on every roll
- verdict-1, finding 5: fixed - the index's cells at 1 + length / 64 a segment, the mean, not the densest case
- verdict-1, finding 6: fixed - the ponds' water sides at their length (124 by 248 ft, 16 cells a pond), each ditch one segment the block's height (12 and 17 cells), the ditches counted as segments, not points
- verdict-1, finding 7: fixed - the wild pond filed in the index (its 164 by 108 ft box, 10 cells)
