# Derivation - track, as it stands after T30 (feature 444 T32, FR-022 rule 2)

The track out is chosen at the homesteads once the last house stands (T30; the homesteads' re-derivation prices it). What this
stage still does is draw it, and - a row village - lay the road its first street runs on. This re-derivation drops the track
out's choice (the start, the leg's water cells, the spur) from `track_greenfield.derivation.md` and prices what remains.

## Contract

- Reads: the track out as the homesteads recorded it (`way_out_track`); a row village's first planned street, its farms, the
  houses' frames, the brook and its fords, and the steadings the road is threaded through.
- Writes: the connector lane (its points), filed in the overlap registry: each segment a ribbon of 4 corners, its box binned in
  the registry's 120 ft cells; a row village two lanes, the far one marked as the road running on.
- Keeps: the connector drawn after every house (0246); the street runs on off the map as the road into it (0033); a way crosses
  the brook at a ford, square (0035, 0084).
- Bounds (measured 2026-11-05 on the reference manifest at 20 households, seed 25, `make hamlet`; the 40 and 80 lengths are
  `track_greenfield.derivation.md`'s): the recorded track 4 points, 3 segments, 3,790 ft long at 20; 4,900 and 7,200 ft at 40
  and 80 (x1.47 a doubling, the view's side). The reference roll is nucleated: it lays no row road.

## The algorithm

    the recorded track written as the connector: its points (1 each)
    filed in the registry: each segment's ribbon, 4 corners (4 each); its box binned in the registry's 120 ft cells, one a cell
        along its length at a random bearing ((length / 120) x 1.27)
    a row village only: the street's span - each farm's nearest street segment from the street's cells (a 64 ft grid of its
        segments, the farm's cell and its 8 neighbors), its projection, the span's ends drawn in short of the brook (its
        crossings with the street, the brook's legs in the street's cells); each end's run to the sheet's edge (2); the ford
        that makes the walk shortest (the fords, 2 each) and its leg (the brook's legs); threaded and squared as the track out is

## Indexes

- the overlap registry: cells of 120 ft, a box binned in every cell it covers, from a smallest side of 120 ft
- a row street's segments: cells of 64 ft, each segment filed in every cell it crosses (the road's only, never on the reference)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the connector, once a map | always 1 |
| the points written | per item | 4 | the recorded track's 4 points, measured at 20; its legs do not grow with the households (one leg out, threaded round the cluster's edge) | always 4 |
| the ribbons (corners written) | per item | 12 | 3 segments, 4 corners each | always 12 |
| the registry's cells (cells written) | per item | 40 at 20, 52 at 40, 76 at 80 | the track's box binned along its length: 3,790 / 120 x 1.27 = 40 at 20 (4,900 and 7,200 ft: 52, 76) | a track across the view's diagonal |
| slack | per item | 1 | every factor is a length or a count of the reference rolls' input | not applicable |

So: 1 x (4 + 12 + the registry's cells) x 1.

Not priced, and why: the driver's backstop at every stage's end (`resync`: every record on the manifest re-read against what the
registry holds, its ribbons rebuilt to compare) is the driver's, over the whole map after every stage alike - not work this stage
does; FR-012's counters are keyed by the stage that just ran, so the audit will find it here.

## Totals

- at 20: 1 x (4 + 12 + 40) x 1 = 56
- at 40: 1 x (4 + 12 + 52) x 1 = 68
- at 80: 1 x (4 + 12 + 76) x 1 = 92

## Growth

The registry's cells grow with the track's length, x1.47 a doubling past 20: exponent about 0.36 from 20 to 80.

## Cheaper algorithms considered

- sweep: not applicable - one lane written.
- grid or spatial index: used - the registry's 120 ft cells; the row road's farms ask a 64 ft grid of the street's segments.
- priority queue: not applicable.
- incremental update: used - the track is chosen once, at the homesteads, and drawn here as chosen.
- memoizing what a scan does not change: not applicable.
