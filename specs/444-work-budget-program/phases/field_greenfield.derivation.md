# Derivation - field, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan (the field archetype, the plot size and regularity, the fall and the drainage bearing, the weir's form); the households; the site's ground below the brook's intake.
- Writes: the brook down the valley and its intake with its weir (0059); the field - its outline, cut into a comb of paddy basins, each basin's ring of corners; its main, branch and drain ditches; the beans sown on its bunds; the crop or state of the plots drawn apart (wet, dry and flooded); the hem along its drain; the dry hem of grain plots upslope of the supply canal, as many as the coarse grain the households need asks (0011), where the winter crop leaves it short; its pocket pond and, on some maps, a grave in a plot (0008); the drawing records of its channels; every water segment filed in the water index; each record asked of the overlap registry as it is written.
- Keeps: a basin about 1,500 sq ft on a hamlet map, its cell 1,488 sq ft, about 48 ft across its canal (0005: "about 48 ft across its canal and 26 to 36 ft along it"); no basin tapering to a point sharper than 25 degrees, none smaller than a quarter of its cell, none an arrowhead (0005) - the comb laid on a lattice whose rows converge with the fan, so no basin breaks them, each row's two outermost basins (the sharpest) tested and a breach refusing the field, where the 2026-10-29 derivation cut a refused point off into a headland; the farmland a household works (0017); a fan of paddies narrowing toward its drain, its bunds converging (0005); a ditch's branch leaving its parent leaning downstream, its sweeps about two and a half channel widths (0054); the water's direction within a right angle of the fall (0054).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): plots 376 and 853, their rings 1,959 and 4,209 corners (4.9 a plot at 20); plots with more than 4 corners, the ones the outline cuts, 163 and 265; the outline 67 and 78 points, 3,146 and 4,874 ft round; ditch segments 78 and 120; the brook 212 and 237 points; the beans 372 and 827; the plots drawn apart 71 and 129, the dry ones 13 and 26 polygons of 4 corners; the channels' drawing records 149 and 231 points; the drain's hem 36 and 61 points; one weir, one pocket pond. Past 20: the field's area grows with the households (0017: the land a household works), so the plots and the beans double a doubling (1,706 and 3,412 plots, 1,654 and 3,308 beans), the outline's length and the ditches with the field's side and the comb's rows as measured from 10 to 20 (x1.55: 411 and 637 cut plots, 185 and 285 segments), the outline's points x1.16 (90, 105), the brook with the view's side (x1.12: 265, 297), the drawing records x1.55 (358, 555), the hem x1.7 (104, 177), the plots drawn apart x1.8 (232, 418); the typical densities (`items.md`, rubric S8): water segments 3.7 and the field's outline segments 1.8 a crossed 64 ft cell. Re-measured 2026-11-01 on the reference rolls (seeds 4, 25, 39 and 47) at 20, 40 and 80 households for the figures the comb as laid sets: the brook's stations every 20 ft along its run across the view, 323, 448 and 631; the beans, 885, 1,770 and 3,383; the comb's rows, 22, 31 and 44, and the low row's basins 28, 40 and 56; the dry hem's plots where the winter crop is not barley, 114, 227 and 454 (0011's 0.85 acre a household in 0.15 acre plots), none where barley meets the need - the knob's even odds give 57, 114 and 227 expected; the hem's plot box, 91 by 72 ft turned along the canal, about 103 ft a side on the mean of its turns, overlapping (1 + 103/64) squared = 6.8 cells of 64 ft; the field's outline, about 4 edges in a 64 ft band of its height, its points 68, 96 and 135; the ditches' segments 54, 70 and 85; the water segments a crossed cell, 3.7, so a water piece meets about 7.4 others in its 2 cells; the brook's skirt 34 ft, an outline point asked within it, a box 68 ft a side over (1 + 68/64) squared = 4.25 cells, the brook's segments it hands back about 2; the brook's record in the registry drawn denser than its stations (430 pieces at 20), each water piece meeting about 6.9 others of its course and the ditches in its cells (re-measured: 2,533 / 376 at 20, 3,564 / 517 at 40, 4,865 / 715 at 80, no hem); a hem plot's cells holding about 4 laid plots round it and 2 water segments, 6 (re-measured, (4,929 - 3,564) / 227 at 40); the field's outline about 8 edges in a band it spans, about half the hem's points in bands above its head that no edge reaches, 4.4 edges a point re-measured.

- The single-field cap (FR-018, re-derived 2026-10-31, T18): one field is at most the cap, a settlement past it drawing several -
  research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.html#how-large-one-tract-of-paddy-grew (one tract
  watered from one intake ran about 1 to 45 ha, the largest found Fei's polder of about 60 ha) and its drawing page
  (#how-our-maps-size-a-settlements-farmland: the cap a knob rolled per settlement between about 45 and 60 ha). At the derivation's
  sizes the farmland is 1.3 acres gross a household (0017's drawing page) times the households: 26, 52 and 104 acres at 20, 40 and 80 -
  about 11, 21 and 42 ha, each under the cap's 45 ha floor. So each size draws ONE field, and no figure below changes; the cap
  binds only past about 85 households (45 ha at 1.3 acres a household), where the field count grows with the farmland and each field's work
  is this derivation's at its own size.
## The algorithm

    the field's area from the households and the land each works (2)
    the brook laid down the valley, each point placed and its bend kept to its sweep (2 a point); the intake, its weir and its channel to the field's fork (10)
    the brook filed in the water index first; the outline placed point by point over the ground below the intake, each point tested against the brook in the water index's cells its box overlaps (placed 1, tested 1, the about 3 brook segments handed back); then the ditches filed
    the comb: the main ditches across the fall at the row spacing, their branches leaning downstream, each segment laid on the lattice's own lines (1) - the outline is the lattice's edge, so no segment is tested against it
    each row between two ditches cut along at the plot length: an interior basin is a quadrilateral whose corners are the comb's own crossings - its angles the comb's, tested once for its row, not again a basin - so its 4 corners and its record written (5)
    no basin the outline cuts: the comb's basins are the lattice's quadrilaterals to its edge (the 2026-10-29 derivation clipped 265 to 637 cut basins against the outline; the comb as designed has none)
    the comb's basins all quadrilaterals of the lattice's own crossings: the field's outline is the lattice's edge, so no basin is clipped (each row's cuts, one a basin)
    the beans along the bunds between two basins of a row, where no ditch is laid, each placed and written (2) - no bead asked of the water here, every bead meeting the map's final water once, at its finish; the plots drawn apart, each written (2); the plots' states rolled: the low row's wet roll and its corners' arrowhead test (5 a low basin), and on the maps that draw the seasonal plots (one in two) a basin's flooded roll and, if not flooded, its gold roll (1.8 a basin, 0.9 over the odds)
    the dry hem: band by band out from the supply canal, each band's plots laid along the canal's course at the plot length, its normal smoothed and its side fixed once for the course, so a plot never folds back onto the rice; each plot's 4 corners placed and written (5); its middle and outer corners tested against the field's outline by the edges of their own 64 ft band (3 points, about 4 edges a band, 12); its box asked of the grid of plots already laid and of the water index, and filed in the grid (3 asks of 6.8 cells, 20); the plots and segments those asks hand back, about 2 laid neighbors and 2.4 water segments (4.4); the climb ends when the need is held, so every plot tried is a plot laid
    every record asked of the overlap registry as it is written: each water piece against the later pieces of its course and what stands sharing its cells (about 6.9); each hem plot against the about 4 laid plots round it and 2 water segments in its cells (6)
    the pocket pond, its radii fitted once to the room from its middle to its plot's nearest side (its 4 sides measured) and its 16 edge points held inside; on some maps the grave, its host rolled and its rings' corners tested
    the drain's hem, the channels' drawing records and the pocket pond, written once each point
    every ditch and brook segment filed in the water index's cells it crosses

## Indexes

- water index: cells of 64 ft, each segment filed in every cell it crosses, a box asked of the cells it overlaps; the mean 3.7 water segments a crossed cell, an uncrossed cell read alone (`items.md`, rubric S8), from a smallest side of 64 ft
- the hem's laid plots: cells of 64 ft, each plot's box filed in every cell it covers, a candidate's box asked of the cells it overlaps - a candidate lapping a laid plot has a point in that plot's box; densest case from a smallest side of 72 ft (a plot's depth out from the canal): plots abutting along a band and band on band, about 2 plots' boxes a cell, a query over a plot's 6.8 cells handing back the about 2 laid before it beside and below (the band above not yet laid)
- the field's outline by bands: cells of 64 ft (bands of the field's height), each edge in every band its height spans; a point's inside test crosses its ray only over its own band's edges; densest case from a smallest side of 64 ft (the band's depth): the outline's two flanks and, at the head's band, its head, about 4 edges a band
- the overlap registry: cells of 64 ft over what stands, each record's pieces binned in the same cells and asked only of what shares a cell; densest case from a smallest side of 64 ft: the water's 3.7 segments a crossed cell (`items.md`, rubric S8), the brook's own record drawn denser (about 6.9 pieces met a piece), a hem plot's cells holding about 4 laid plots round it and 2 water segments

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 853 at 20, 1,706 at 40, 3,412 at 80 | the basins, measured at 20, doubling with the field's area | the typical field |
| an interior basin | per item | 6 | its 4 corners and its record written (5); its row's cut, one a basin (1); its angles the comb's, tested with its row | always 6 |
| slack | per item | 1 | every factor is a count of the field's output measured on the reference rolls or a bounded construction (the hem lays only plots it keeps), none a search | not applicable |
| the area | once | 2 | the households read and the land each works applied | always 2 |
| the brook | over the run | 646 at 20, 896 at 40, 1,262 at 80 | each station placed and its bend kept (2): 323, 448 and 631 stations, every 20 ft along its run across the view (re-measured 2026-11-01; the row stood at 237 points at 20, x1.12 a doubling) | the typical valley |
| the intake | once | 9 | the intake (1), its weir's 4 corners (4), its channel's 3 points (3) and its record (1) | always 9 |
| the outline (water index cells examined) | over the run | 272 at 20, 384 at 40, 540 at 80 | each point placed (1), tested against the brook (1) and the about 2 brook segments its box's cells hand back (2): 68, 96 and 135 points, re-measured 2026-11-01 (the row stood at 2 a point and 8 at the intake on 78, 90 and 105) | a field hugging the brook |
| the ditches | over the run | 54 at 20, 70 at 40, 85 at 80 | each segment laid on the lattice's own lines (1), none tested against the outline, the lattice's edge: 54, 70 and 85 segments (re-measured 2026-11-01; the row stood at 3.2 a segment on 120, 185 and 285) | the typical field |
| the rows' angles | over the run | 176 at 20, 248 at 40, 352 at 80 | each row's two outermost basins, where the taper makes them sharpest, their 4 corners tested (8 a row): 22, 31 and 44 rows | always 8 a row |
| the cut basins (water index cells examined) | over the run | 0 | re-derived 2026-11-01: the comb's basins are all the lattice's own quadrilaterals, its outline the lattice's edge, so none is clipped (the row stood at 5,565, 8,631 and 13,377); the comb laid on the lattice: no basin clipped against the outline (the 2026-10-29 row charged 265, 411 and 637 cut basins a clip each, 21) | the typical field |
| the beans | over the run | 1,770 at 20, 3,540 at 40, 6,766 at 80 | each placed on its bund and written (2): 885, 1,770 and 3,383; none asked of the water, the bunds between a row's basins carrying no ditch and the finish settling every bead on the final water (re-measured 2026-11-01; the row stood at 2 a bean on 827 at 20) | the typical field |
| the plots drawn apart | over the run | 258 at 20, 464 at 40, 836 at 80 | each written (2): 129 at 20, 232 at 40, 418 at 80 (the dry plots, charged here at 4 corners until 2026-11-01, are the hem's row) | the typical field |
| the plots' states rolled | over the run | 908 at 20, 1,735 at 40, 3,351 at 80 | the low row's wet roll and arrowhead test (5 a low basin: 28, 40, 56); on a map that draws the seasonal plots, one in two, each basin's flooded roll and, if not flooded, its gold roll (1.8 a basin, 0.9 over the odds) | a seasonal map, 1.8 a basin |
| the dry hem (water index cells examined) | over the run | 798 at 20, 1,596 at 40, 3,178 at 80 | 14 a plot - its corners placed and written (5), its box asked of the water index's 6.8 cells and the 2.4 segments handed back, rounded down (9) - at the plots expected over the winter crop's even odds, 57, 114 and 227 (114, 227 and 454 where barley falls short, none where it meets the need) | barley short of the need: twice |
| the hem's laid plots (cells examined and written) | over the run | 912 at 20, 1,824 at 40, 3,632 at 80 | 16 a plot: its box asked of the grid's 6.8 cells and filed in them (13.6), the about 2 laid plots handed back, rounded up - at 57, 114 and 227 plots | barley short of the need: twice |
| the field's outline by bands (cells examined) | over the run | 809 at 20, 1,578 at 40, 3,086 at 80 | 13 a plot: its middle and two outer corners, each crossing its ray over the 4.4 edges a point meets - at 57, 114 and 227 plots; and the bands built for the hem alone, at its even odds, each of the outline's edges in the about 2 bands its height spans (68, 96 and 135) | barley short of the need: twice |
| the pocket pond and the grave | once | 15 | the pond, sunk on 55 maps in 100 (0008): its radii fitted once to the room from its middle to its plot's 4 sides (4) and its 16 edge points held inside (16), 20 at 0.55 = 11; the grave, drawn on 3 maps in 10 (0008): its host rolled (1) and its rings' corners tested (12), 13 at 0.3 = 4 | a pond and a grave, 33 |
| the overlap registry (cells examined) | over the run | 2,936 at 20, 4,251 at 40, 6,224 at 80 | each water piece (the brook's stations and the ditches' segments, 376, 517 and 715) against the about 6.9 others of its course and the ditches in its cells (6.8 at 80, re-measured with no hem), and each hem plot against the about 4 laid plots round it and 2 water segments in its cells (6, at 57, 114 and 227) | the typical field |
| the drawing records | over the run | 297 at 20, 467 at 40, 737 at 80 | the drain's hem (61, 104, 177 points), the channels' drawing points (231, 358, 555) and the pocket pond (5), each written once | the typical field |
| the water index (water index cells written) | over the run | 924 at 20, 1,272 at 40, 1,745 at 80 | each segment filed in the 1 + L(cos + sin)/64 cells it crosses - a 20 ft brook station 1.4 (322, 447 and 630), a ditch segment of about 120 ft 3.4 (54, 70 and 85) - and each outline point's box, asked within the brook's 34 ft skirt, read over 4.25 cells (68, 96 and 135) | the typical field |

So: the basins x (6 x 1), plus the area, the brook, the intake, the outline, the ditches, the rows' angles, the cut basins, the beans, the plots drawn apart, the plots' states, the dry hem, the hem's laid plots, the field's outline by bands, the pocket pond and the grave, the drawing records, the water index and the overlap registry.

## Totals

- at 20: 853 x 6 x 1 + 2 + 646 + 9 + 272 + 54 + 176 + 0 + 1770 + 258 + 908 + 798 + 912 + 809 + 15 + 297 + 924 + 2936 = 15904
- at 40: 1706 x 6 x 1 + 2 + 896 + 9 + 384 + 70 + 248 + 0 + 3540 + 464 + 1735 + 1596 + 1824 + 1578 + 15 + 467 + 1272 + 4251 = 28587
- at 80: 3412 x 6 x 1 + 2 + 1262 + 9 + 540 + 85 + 352 + 0 + 6766 + 836 + 3351 + 3178 + 3632 + 3086 + 15 + 737 + 1745 + 6224 = 52292

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.86 (from the totals, ln(52,292 / 15,904) / ln 4): the basins, the beans, the plots' states and the dry hem with the field's area, the brook, the ditches and the rows with its side.

## Earlier findings

- verdict-1, finding 1: fixed - the keep-out chords dropped; the drawing records are the hem, the channels' points and the pocket pond, 297, 467 and 737
- verdict-1, finding 2: fixed - the cut-off of a sharp point itemized (5) and charged at the measured share of the outline within 25 degrees of a basin's side, 0.55
- verdict-1, finding 3: fixed - a cut basin's clip reads the 2.5 cells its box overlaps
- verdict-1, finding 4: fixed - only the 3 new corners' angles are tested, the comb's 4 read with the row
- verdict-1, finding 5: fixed - the ditches at 0.2, 3.2 a segment
- verdict-1, finding 6: fixed - the outline's brook segments in the about 2 cells it shares with the brook at the intake
- verdict-1, finding 7: fixed - an interior basin's 4 corners and its record, 5
- verdict-1, finding 8: fixed - the dry plots x1.8 a doubling
- verdict-2, finding 1: fixed - the growth exponent read from the totals, 0.79 (ln(42,070 / 14,045) / ln 4), not 0.73
- verdict-5, finding 1: fixed - the registry's figure a water piece read from what its cells hold: the brook's record drawn denser than its stations, each piece meeting about 6.9 others of its course and the ditches, re-measured with no hem (the 2 cells x 3.7 it stood at was not its source)
- verdict-5, finding 2: fixed - the intake at 9, its parts summed; the bands' build charged at the hem's even odds (68, 96, 135); the pond at its 55 in 100 and the grave at its 3 in 10, 15
- verdict-5, finding 3: fixed - the outline point asked within the brook's skirt, 68 ft a side, 4.25 cells (the stage asked within twice the skirt, 136 ft, for the same answer; it now asks within the skirt)
- verdict-5, finding 4: fixed - the water index files no outline segment (algorithm and Indexes corrected); a hem plot's cells stated once, about 4 laid plots round it and 2 water segments; the outline's edges a point read as measured, 4.4, under the 8 in a band it spans
- verdict-4, finding 1: fixed - the pocket pond's radii fitted once to the room from its middle to its plot's sides, no shrinking retries (33, its parts named); the grave written in the contract's Writes (0008)
- verdict-4, finding 2: fixed - the beans asked of no water in the stage, the bunds between a row's basins carrying no ditch and the finish settling every bead; the brook filed in the one water index before the outline's test, no index of its own
- verdict-4, finding 3: fixed - a hem plot's registry figure derived: the about 4 laid plots round it and 2 water segments in its cells, 6, re-measured
- verdict-4, finding 4: fixed - the laid grid's density read per query (about 2 a cell, about 4 round a plot over its cells); the outline's segments not filed in the water index, the contract's Writes corrected; the bands' build charged in their row
- verdict-4, earlier finding (verdict-1 finding 2): fixed - the cut-off branch gone with the cut basins: the comb's lattice gives no basin under 25 degrees, each row's two outermost basins tested and a breach refusing the field, the contract's Keeps saying so
- verdict-3, finding 1: fixed - the single-field cap's line stands as verdict-3 read it; the re-derivation below changes no figure the cap reads, and each size still draws one field
- re-derived 2026-11-01 (the round arbiter, ask:444-T16-hem-budget, route b): the dry hem's search, which had no row, designed bounded and charged at the plots the grain need lays over the winter crop's odds; the beans' water test, the plots' states rolls, the rows' angle tests and the overlap registry's record check given rows; the comb's cut basins at 0, its basins the lattice's own; the brook, ditches and beans at the counts the comb as laid sets; the dry plots' polygons moved into the hem's row

## Cheaper algorithms considered

- sweep: used - each row between two ditches is cut along once at the plot length, and the comb's angles are tested once a row, not a basin
- grid or spatial index: used - the water index for the outline's points and the beans, the hem's grid of laid plots, the outline's bands for the hem's inside tests, the registry's cells
- construction in place of search: used - the hem's plots laid band by band on one side of the canal's course, so none is tried that the rice or a laid plot refuses; the comb's basins on the lattice, so none is clipped
- priority queue: not used - nothing is ranked
- incremental update: not used - each basin is laid once and never moved
- memoizing what a scan does not change: used - an interior basin's corner angles are its row's, read once for the row
