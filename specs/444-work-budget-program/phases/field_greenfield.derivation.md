# Derivation - field, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan (the field archetype, the plot size and regularity, the fall and the drainage bearing, the weir's form); the households; the site's ground below the brook's intake.
- Writes: the brook down the valley and its intake with its weir (0059); the field - its outline, cut into a comb of paddy basins, each basin's ring of corners; its main, branch and drain ditches; the beans sown on its bunds; the crop or state of the plots drawn apart (wet, dry and flooded); the hem along its drain; its pocket pond; the drawing records of its channels; every water and outline segment filed in the water index.
- Keeps: a basin about 1,500 sq ft on a hamlet map, its cell 1,488 sq ft, about 48 ft across its canal (0005: "about 48 ft across its canal and 26 to 36 ft along it"); no basin tapering to a point sharper than 25 degrees, none smaller than a quarter of its cell, none an arrowhead, a refused point cut off into a headland along the drain before it is taken into the basin beside it (0005); the farmland a household works (0017); a fan of paddies narrowing toward its drain, its bunds converging (0005); a ditch's branch leaving its parent leaning downstream, its sweeps about two and a half channel widths (0054); the water's direction within a right angle of the fall (0054).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): plots 376 and 853, their rings 1,959 and 4,209 corners (4.9 a plot at 20); plots with more than 4 corners, the ones the outline cuts, 163 and 265; the outline 67 and 78 points, 3,146 and 4,874 ft round; ditch segments 78 and 120; the brook 212 and 237 points; the beans 372 and 827; the plots drawn apart 71 and 129, the dry ones 13 and 26 polygons of 4 corners; the channels' drawing records 149 and 231 points; the drain's hem 36 and 61 points; one weir, one pocket pond. Past 20: the field's area grows with the households (0017: the land a household works), so the plots and the beans double a doubling (1,706 and 3,412 plots, 1,654 and 3,308 beans), the outline's length and the ditches with the field's side and the comb's rows as measured from 10 to 20 (x1.55: 411 and 637 cut plots, 185 and 285 segments), the outline's points x1.16 (90, 105), the brook with the view's side (x1.12: 265, 297), the drawing records x1.55 (358, 555), the hem x1.7 (104, 177), the plots drawn apart x1.8 (232, 418); the typical densities (`items.md`, rubric S8): water segments 3.7 and the field's outline segments 1.8 a crossed 64 ft cell.

- The single-field cap (FR-018, re-derived 2026-10-31, T18): one field is at most the cap, a settlement past it drawing several -
  research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.html#how-large-one-tract-of-paddy-grew (one tract
  watered from one intake ran about 1 to 45 ha, the largest found Fei's polder of about 60 ha) and its drawing page
  (#how-our-maps-size-a-settlements-farmland: the cap a knob rolled per settlement between about 45 and 60 ha). At the derivation's
  sizes the farmland is `GROSS_ACRES_PER_HOUSEHOLD` (1.3 acres, 0017) times the households: 26, 52 and 104 acres at 20, 40 and 80 -
  about 11, 21 and 42 ha, each under the cap's 45 ha floor. So each size draws ONE field, and no figure below changes; the cap
  binds only past about 85 households (45 ha / 1.3 acres), where the field count grows with the farmland and each field's work
  is this derivation's at its own size.
## The algorithm

    the field's area from the households and the land each works (2)
    the brook laid down the valley, each point placed and its bend kept to its sweep (2 a point); the intake, its weir and its channel to the field's fork (10)
    the outline placed point by point over the ground below the intake, each point tested against the brook in its water-index cell (1 + the cell's mean segments and the cell)
    the comb: the main ditches across the fall at the row spacing, their branches leaning downstream, each segment laid (1) and tested against the outline segments in the 2 cells it crosses (the cell's mean outline segments and the cell, each)
    each row between two ditches cut along at the plot length: an interior basin is a quadrilateral whose corners are the comb's own crossings - its angles the comb's, tested once for its row, not again a basin - so its 4 corners and its record written (5)
    a basin the outline cuts: clipped against the outline segments in the 2.5 cells its box overlaps, its 3 extra corners found and written (2 a corner), only those new corners' angles tested (3), its area against a quarter of its cell (1), the arrowhead test (1); a new corner sharper than 25 degrees, at the measured share, cut off into a headland: the chord's two corners written and their angles tested, the point dropped (5)
    the beans along the bunds, each placed and written (2); the plots drawn apart, each rolled and written (2); the dry plots' polygons (4)
    the drain's hem, the channels' drawing records and the pocket pond, written once each point
    every ditch, brook and outline segment filed in the water index's cells, about 2 a segment

## Indexes

- water index: cells of 64 ft, each segment filed in every cell it crosses, a box asked of the cells it overlaps; the mean 3.7 water and 1.8 outline segments a crossed cell, an uncrossed cell read alone (`items.md`, rubric S8), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 853 at 20, 1,706 at 40, 3,412 at 80 | the basins, measured at 20, doubling with the field's area | the typical field |
| an interior basin | per item | 5 | its 4 corners and its record written; its angles the comb's, tested with its row | always 5 |
| slack | per item | 1 | every factor is a count of the field's output measured on the reference rolls, none a search; the cut basins' share is measured, not a bound | not applicable |
| the area | once | 2 | the households read and the land each works applied | always 2 |
| the brook | over the run | 474 at 20, 530 at 40, 594 at 80 | each point placed and its bend kept (2), 237 at 20, x1.12 a doubling | the typical valley |
| the intake | once | 10 | the intake, its weir's 4 corners and its channel's 3 points, and its record | always 10 |
| the outline (water index cells examined) | over the run | 164 at 20, 188 at 40, 218 at 80 | each point placed (1) and its water-index cell read (1), 78 at 20, 90 at 40, 105 at 80; the brook's segments only in the cells the outline shares with the brook, the about 2 at its intake where the field takes its water, at the mean 3.7 (8) | a field hugging the brook |
| the ditches (water index cells examined) | over the run | 384 at 20, 592 at 40, 912 at 80 | each segment laid (1) and its 2 cells read (2); the outline's segments only in a cell the outline crosses - a ditch's end at the field's edge, 2 ends of 12 ditches against 120 segments, 0.2 a segment at the mean 1.8: 3.2 a segment, 120, 185 and 285 segments | the typical field |
| the cut basins (water index cells examined) | over the run | 5,565 at 20, 8,631 at 40, 13,377 at 80 | each basin the outline cuts (265, 411, 637): clipped in the 2.5 cells a 48 by 31 ft basin's box overlaps, (1 + 48/64)(1 + 31/64), at the mean 1.8 outline segments and the cell (7); its 3 extra corners found and written (6) - (4,209 - 588 x 4) / 265 = 7.0 corners a cut basin, 4 of them the comb's; those 3 new corners' angles (3); its area (1); the arrowhead (1); the cut-off of a sharp point, 5 (the chord's 2 corners written, their 2 angles, the point dropped), at the share of the outline running within 25 degrees of a basin's side, 0.54 and 0.55 measured at 10 and 20 (2.75): 20.75, rounded to 21 | the typical field |
| the beans | over the run | 1,654 at 20, 3,308 at 40, 6,616 at 80 | each placed on its bund and written (2) | the typical field |
| the plots drawn apart | over the run | 362 at 20, 652 at 40, 1,172 at 80 | each rolled and written (2): 129 at 20, 232 at 40, 418 at 80; the dry plots' polygons, 4 corners each (26, 47, 84: x1.8 a doubling, as the plots drawn apart) | the typical field |
| the drawing records | over the run | 297 at 20, 467 at 40, 737 at 80 | the drain's hem (61, 104, 177 points), the channels' drawing points (231, 358, 555) and the pocket pond (5), each written once | the typical field |
| the water index (water index cells written) | over the run | 868 at 20, 1,078 at 40, 1,372 at 80 | each ditch, brook and outline segment filed in about 2 cells: 434, 539 and 686 segments | the typical field |

So: the basins x (5 x 1), plus the area, the brook, the intake, the outline, the ditches, the cut basins, the beans, the plots drawn apart, the drawing records and the water index.

## Totals

- at 20: 853 x 5 x 1 + 2 + 474 + 10 + 164 + 384 + 5565 + 1654 + 362 + 297 + 868 = 14045
- at 40: 1706 x 5 x 1 + 2 + 530 + 10 + 188 + 592 + 8631 + 3308 + 652 + 467 + 1078 = 23988
- at 80: 3412 x 5 x 1 + 2 + 594 + 10 + 218 + 912 + 13377 + 6616 + 1172 + 737 + 1372 = 42070

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.73: the basins and the beans with the field's area, the cut basins, the outline and the ditches with its side.

## Earlier findings

- verdict-1, finding 1: fixed - the keep-out chords dropped; the drawing records are the hem, the channels' points and the pocket pond, 297, 467 and 737
- verdict-1, finding 2: fixed - the cut-off of a sharp point itemized (5) and charged at the measured share of the outline within 25 degrees of a basin's side, 0.55
- verdict-1, finding 3: fixed - a cut basin's clip reads the 2.5 cells its box overlaps
- verdict-1, finding 4: fixed - only the 3 new corners' angles are tested, the comb's 4 read with the row
- verdict-1, finding 5: fixed - the ditches at 0.2, 3.2 a segment
- verdict-1, finding 6: fixed - the outline's brook segments in the about 2 cells it shares with the brook at the intake
- verdict-1, finding 7: fixed - an interior basin's 4 corners and its record, 5
- verdict-1, finding 8: fixed - the dry plots x1.8 a doubling

## Cheaper algorithms considered

- sweep: used - each row between two ditches is cut along once at the plot length, and the comb's angles are tested once a row, not a basin
- grid or spatial index: used - the water index for the outline's points, the ditches' segments and the cut basins
- priority queue: not used - nothing is ranked
- incremental update: not used - each basin is laid once and never moved
- memoizing what a scan does not change: used - an interior basin's corner angles are its row's, read once for the row
