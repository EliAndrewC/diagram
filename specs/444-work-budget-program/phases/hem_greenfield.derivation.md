# Derivation - hem, greenfield (feature 444 FR-015, T28)

## Contract

- Reads: what the field handed on for the hem (the canal's course it climbs from, the side it climbs to, the fall, the grain it lays and the bands it may climb, the roll's seed), the field's outline, the field's water at its widths, and the settlement's ground the seat chose (its band out past its two half-depths and the belt's far edge, the band's length along its margin).
- Writes: the dry plots - each plot's ring, its crop, its rows' direction and its tract - into the map's record and the readers' net, the no-build registries, the overlap registry, the grain drawn and the room left on the title card, and each plot's ink: its crop's paint, its outline and its furrowed rows.
- Keeps: a hem of small rectangular plots just upslope of the supply canal (0006), in tracts of two to four strips (0006), as many as the hamlet's coarse grain needs (0011: about 0.85 acre a household); none onto the rice, onto another plot, or in the water; the dry fields behind the houses where the settlement stands on the paddy's high edge, the houses between the canal and the dry fields (0006, Torisu Hongo); every dry plot drawn in ridged rows (0006).
- Bounds (measured 2026-11-04, `make stage-sizes STAGE=hem DUMP=` and `STAGE=waterward DUMP=` on the reference rolls, seeds 4, 25, 39, 47): the dry plots laid 94, 150 and 249 at 20, 40 and 80 households (the mean), each about 91 by 72 ft (0006's plot, its diagonal about 116 ft); the canal's course 25 to 49 points, 1,092 to 4,761 ft; the field's water 378, 520 and 719 segments; the field's outline 68, 96 and 135 points; the settlement's ground one ring of 4 points, its band 2 x 389 to 2 x 918 ft long and 12 + 2 x 152 + 146 to 12 + 2 x 300 + 146 ft deep (the seat's measured half-extents).

## The algorithm

    the hem's inputs and the settlement's ground read (6)
    the field's water filed in cells, each segment in the cells it crosses
    the hem laid band by band out from the canal, as the field laid it (its search the field's SOUND derivation's: each plot's
      seat, its water, its laps, its outline test, filed as it is kept)
    each column along the canal asked first whether its first strip would stand on the settlement's ground; where it would, its
      strips stood behind it a strip's depth at a time until clear
    written: each plot's record and net entry, its no-build entries, its overlap-registry record, its ink - corners, outline and
      furrowed rows - and the grain drawn and the room left

## Indexes

- the field's water: cells of 64 ft, each segment filed in the cells it crosses (about 2, its segments 60 ft long on the mean); a plot's box asks its about 6.8 cells and the about 2.4 segments they hold (the field's SOUND derivation, verdict-10); densest case from a smallest side of 64 ft, a cell where the brook and a ditch meet
- the laid plots: cells of 64 ft, each plot's box filed in every cell it covers (about 6.8), a candidate's box asked of the same; densest case from a smallest side of 72 ft, a plot's depth, about 2 laid plots a cell
- the field's outline by bands: cells of 64 ft, each a horizontal band of the outline's edges, a point asked of its band's 4.4 edges (measured, the field's derivation); densest case from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 94 at 20, 150 at 40, 249 at 80 | the dry plots laid, measured on the reference rolls | the whole canal hemmed on a cleared middle |
| the plot's seat and its tests | per item | 28 | the field's SOUND row: the seat's 4 offsets a cursor's steps (4), its lap test's 5 points against the about 2 laid plots (10), its water test (8) and its tract's row direction (6) | as the field's |
| the field's water's cells | per item | 14 | its corners placed and written (5), its box asked of the 6.8 cells and the 2.4 segments handed back (9) | as the field's |
| the laid plots' cells | per item | 16 | its box asked of the grid's 6.8 cells and filed in them (13.6), the about 2 laid plots handed back | as the field's |
| the field's outline by bands's cells | per item | 13 | its middle and two outer corners, each crossing its ray over the 4.4 edges of its band | as the field's |
| the record and the net | per item | 6 | its record (the ring's 4 corners and its crop, rows and tract) and its net entry (2) | always 6 |
| the overlap registry | per item | 10 | the plot's box read off its 4 corners (4) and asked of its cells' about 2 laid plots and 2 water segments (6) | the hem beside the water |
| the ink's corners and outline | per item | 8 | its 4 corners walked for its paint and its 4 for its outline | always 8 |
| the furrows | per item | 84 | the rows across the plot's 116 ft diagonal at a row every 5 ft (24, 0006's ridged rows, the spacing a GUESS), the 4 corners walked 3 ways (12), each row's 2 crossings found by bisecting the rows (2) and its write (1) | a plot at its diagonal turn |
| the settlement's ground | over the run | 600 at 20, 1,134 at 40, 2,000 at 80 | the columns along the band's length (2 x 389, 2 x 643 and 2 x 918 ft over a 91 ft column: 9, 14 and 20), each pushed a strip's 72 ft at a time through the ground's depth (480, 622 and 758 ft: 7, 9 and 11 steps), each step a seat (4) and its middle and corners against the ring (5); the rest of the columns one test each, folded in the seat's row | every column on the ground |
| the water filed | once | 756 at 20, 1,040 at 40, 1,438 at 80 | each of the field's water segments in about 2 cells (378, 520, 719) | the typical field |
| the inputs read | once | 6 | the line, the side, the fall, the bounds, the seed and the settlement's ground | always 6 |
| slack | per item | 1 | every factor is a count of the stage's own plots or the field's SOUND rows | not applicable |

So: items x (28 + 14 + 16 + 13 + 6 + 10 + 8 + 84) x slack + the settlement's ground + the water filed + the inputs read.

## Totals

- at 20: 94 x (28 + 14 + 16 + 13 + 6 + 10 + 8 + 84) x 1 + 600 + 756 + 6 = 18188
- at 40: 150 x (28 + 14 + 16 + 13 + 6 + 10 + 8 + 84) x 1 + 1134 + 1040 + 6 = 29030
- at 80: 249 x (28 + 14 + 16 + 13 + 6 + 10 + 8 + 84) x 1 + 2000 + 1438 + 6 = 48015

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.70 (18,188 to 48,015): the plots with the grain the hamlet needs or the canal's length, the water with the field. No loop over a growing set runs inside another: each plot's tests read cells and bands, never a whole ring or every plot.

## Work the first derivation missed

The hem had no derivation of its own: its search was priced in the field's (`phases/field_greenfield.derivation.md`, SOUND at verdict-10), whose rows for the hem's search are kept here as they stood. Moved with it, and priced here for the first time:

- the furrows - every dry plot drawn in ridged rows (0006); the field's derivation priced its ink's corners but not the rows its dry plots' ink draws
- the settlement's ground - the dry fields behind the houses (0006, Torisu Hongo, recorded 2026-11-04): each column asked whether its first strip stands on the seat's ground, and pushed behind it where it does
- the water filed - the field's water index does not outlive the field's stage, so the hem files the water it asks

## Cheaper algorithms considered

- sweep: used - the hem laid band by band along the canal's course, a forward cursor
- grid or spatial index: used - the water's cells, the laid plots' cells, the outline's bands; the furrows' rows found by bisection, not every row against every edge
- priority queue: not used - the plots are laid in order along the canal, none searched
- incremental update: not used - one hem
- memoizing what a scan does not change: used - the water filed once for all the plots; the settlement's ground's push stops at the first clear depth
