# Derivation - frame, greenfield (feature 444 FR-015)

## Contract

- Reads: the solid features' extents - the seated lots' lattice span, the field's box, the pond, the groves - and the plan's sheet scale; the try lattice's rasters of the field, the water, the marshes and the belt (`hinterland`) and the lots' lattice.
- Writes: the view - the box round the solid features plus the sheet's margin - and the crop to it; the title placard - the place name with its scale bar under it - in blank ground inside the view.
- Keeps: the frame the box round the solid features - houses, fields, water, groves, the pond - plus about 30 ft on a hamlet sheet; the wild ground, streams, channels and lanes cut off at the edge, never widening it; the placard placed by scanning the framed window from the top for a box that clears every feature, so the name lies across no building, field, water or grove, the search run over the final window; a scale bar a fixed length on the page reading 100 ft on a hamlet sheet (0241).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the view 1,521 by 1,726 and 2,274 by 2,486 ft, past 20 with the cluster's and the field's side (x1.47 a doubling: 3,343 and 4,914 ft wide); the placard 300 by 190 ft, found 129 ft below the view's top and 1,001 ft from its left edge at 20 (809 ft at 10), so its rows reach (129 + 190) / 77, about 4.1, rounded up to 5 rows of the 77 ft try lattice - its depth set by the margin and what stands along the view's top, not by the households, so held at 40 and 80 - and the walk's last row stops at its fit, 13 cells across and 4 more, 17 of the 30 at 20 (25 and 37 of 44 and 65 at 40 and 80, with the view's width); the view 30, 44 and 65 try cells wide; the lots' lattice span 9, 12 and 16 lots wide (19, 25 and 34 try cells); the solid features' extents 5 boxes of 4 sides; the placard's obstacles the solid features: the houses and the copse in their gaps, the lots' span taken solid whole, and the field, the water with the marshes on wet ground, and the belt, read from the one mask.

## The algorithm

    the view: the five solid extents' sides read and the box's four sides taken, the margin added (20 + 4)
    the placard: the lots' span's column interval read once (2); the view's try cells walked row by row from the top, each cell
        once - inside the lots' span, solid, nothing read; outside it its mask read (1), its column's run of free cells updated (1)
        and a running count of adjacent columns whose run holds three cells kept, reset on a short one (1); the first place where four adjacent
        columns (300 / 77) each hold a run of three cells (190 / 77) is the placard's, a first fit, not a best, so the walk stops
        there
    written: the view (4), the crop's frame (1), the name, the bar and its fine print (3)

## Indexes

- the try lattice: cells of 77 ft over the scrub's frame, which holds the view; each cell's raster mark (field, water, marsh, belt), drawn by `hinterland`, read here, from a smallest side of 77 ft
- the lots' lattice: cells of 162 ft, its span's column and row interval read once and taken solid, from a smallest side of 162 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the sheet, once a map | always 1 |
| the view | per item | 24 | the five extents' 20 sides read and the box's 4 sides with the margin | always 24 |
| the placard's walk (the try lattice and the lots' lattice cells examined) | per item | 413 at 20, 605 at 40, 893 at 80 | the span's interval (2); 4 full rows of the view's 30, 44 and 65 cells and the last row to the fit, 17, 25 and 37: 137, 201 and 297 cells, each its mask, its run and the running count (3); a cell inside the span read for nothing, counted at 3 all the same | a cluster or a grove along the view's top edge |
| the writes | per item | 8 | the view's 4 sides, the crop's frame, the name, the bar and its print | always 8 |
| slack | per item | 1 | the rows the walk reaches are measured; a first fit stops where it fits | not applicable |

So: 1 x (24 + the placard's walk + 8) x 1.

- pruning: the placard is the first fit from the top, not the best, so the walk stops at the first place it fits and never reads the rows below; the lots' span, the houses and the copse in their gaps, is taken solid from its interval, read once

## Totals

- at 20: 1 x (24 + 413 + 8) x 1 = 445
- at 40: 1 x (24 + 605 + 8) x 1 = 637
- at 80: 1 x (24 + 893 + 8) x 1 = 925

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.52: the view's width.

## Earlier findings

- verdict-1, finding 1: fixed - the lots' lattice read only in the span's columns, its interval taken once (95, 125, 170)
- verdict-1, finding 2: fixed - the four-column test counted, 4 a cell inside the span and 3 outside it
- verdict-1, finding 3: disputed - the fit's column in the last row is unmeasured, so the row is charged whole, about 10% of the walk
- verdict-1, finding 4: fixed - the obstacles the solid features: the houses from the lattice, the field, the water and marshes, and the groves - the belt in the mask, the copse inside the span
- verdict-2, finding 1: fixed - the last row charged to the fit, measured 13 cells across and 4 more (17 of 30 at 20)
- verdict-2, finding 2: fixed - the depth set by the margin and the view's top edge, not the households, said in the Bounds
- verdict-2, finding 3: fixed - a running count of adjacent columns whose run holds three cells, reset on a short one, 1 a cell
- verdict-2, finding 4: fixed - the lots' span taken solid, the houses and the copse in their gaps both, so nothing inside it is read

## Cheaper algorithms considered

- sweep: used - the view's top rows walked once, each column's free run kept as it goes
- grid or spatial index: used - the try lattice's rasters and the lots' lattice
- priority queue: not used - a first fit from the top
- incremental update: used - each column's free run updated a row at a time, never recounted
- memoizing what a scan does not change: used - the rasters drawn once by the hinterland, read here
