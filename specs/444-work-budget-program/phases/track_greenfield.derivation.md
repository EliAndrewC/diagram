# Derivation - track, greenfield (feature 444 FR-015), revised 2026-11-05 under FR-022 rule 2 (T32)

The stage's first greenfield pin (223 at 40, verdict-2 SOUND) stays the reference for every FR-022 line. This revision prices the
stage as it stands after T30: the track out's choice (its start, its leg's water cells, its spur) moved to the homesteads, whose
re-derivation prices it (T30 D1), and the work below added under "Work the first derivation missed".

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
    filed in the registry: each segment's ribbon, 4 corners (4 each); each segment's box binned in every 120 ft cell the box
        covers (x^2 / pi + 4x / pi + 1 for a segment x cells long at a random bearing)
    a row village only: the street's span - each farm's nearest street segment from the street's cells (a 64 ft grid of its
        segments, the farm's cell and its 8 neighbors), its projection, the span's ends drawn in short of the brook (its
        crossings with the street, the brook's legs in the street's cells); each end's run to the sheet's edge (2); the ford
        that makes the walk shortest (the fords, 2 each) and its leg (the brook's legs); threaded and squared as the track out is

## Indexes

- the overlap registry: cells of 120 ft, a box binned in every cell it covers, from a smallest side of 120 ft
- a row street's segments: cells of 64 ft, each segment filed in every cell it crosses, from a smallest side of 64 ft (the road's only, never on the reference)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the connector, once a map | always 1 |
| the points written | per item | 4 | the recorded track's 4 points, measured at 20; its legs do not grow with the households (one leg out, threaded round the cluster's edge) | always 4 |
| the ribbons (corners written) | per item | 12 | 3 segments, 4 corners each | always 12 |
| the overlap registry's cells (cells written) | per item | 149 at 20, 232 at 40, 461 at 80 | each of the 3 segments' boxes binned in every 120 ft cell it covers: a segment x = (length / 3) / 120 cells long at a random bearing covers x^2 / pi + 4x / pi + 1 cells (its box's mean area plus its edges' strips); x = 10.5, 13.6, 20.0 at 20, 40, 80 gives 49.7, 77.3, 153.8 a segment | a track across the view's diagonal |
| a row street's segments' cells (cells examined) | per item | 0 | the reference roll is nucleated and lays no row road; a row village's farms each ask their cell and its 8 neighbors | a row village: its farms x 9 |
| slack | per item | 1 | every factor is a length or a count of the reference rolls' input | not applicable |

So: 1 x (4 + 12 + the overlap registry's cells + a row street's segments' cells) x 1.

Not priced, and why: the driver's backstop over the whole map (every record re-read against what the registry holds) runs after
no stage rebuilt in Rust (feature 444 T26 D3), so it is not this stage's work once the track is.

## Totals

- at 20: 1 x (4 + 12 + 149 + 0) x 1 = 165
- at 40: 1 x (4 + 12 + 232 + 0) x 1 = 248
- at 80: 1 x (4 + 12 + 461 + 0) x 1 = 477

## Growth

The registry's cells grow with the square of the track's length (each segment's box), its length x1.47 a doubling past 20: exponent about 0.78 from 20 to 80.

## Work the first derivation missed

- the registry's record of the connector - each segment's ribbon of 4 corners and its box binned in the registry's 120 ft cells
  (the first derivation filed the legs in a ways index and priced no registry)
- a row village's road (0033, 0035): the street's span, each end's run off the sheet, the ford, the thread and the squaring - a
  form the nucleated reference never rolls, so its factor is 0 at the reference sizes; for a row village, its farms each ask 9
  cells of the street's grid, its two runs 2 points each, the fords 2 each and the brook's legs once, threaded and squared as
  the track out is
- moved out, to the homesteads (T30 D1): the start (16 at 40), the leg's water cells (97), the spur (5) and their writes (105)

## Earlier findings

- verdict-1, finding 1: fixed - the start found by walking the lattice's lines across the bearing from the outermost inward, about 2 lines of R + 1 cells
- verdict-1, finding 2: fixed - the 7 ft holds by construction: the track and the spur leave from a lot's corner, 29 ft off every homestead square; the registry row dropped
- verdict-1, finding 3: fixed - the writes count the 5 points, the gate among them
- verdict-1, finding 4: fixed - the spur filed in its about 3 cells
- verdict-1, finding 5: fixed - the spur's 7 ft from every garden holds by construction, as the track's

- verdict-2, finding 1: fixed - SOUND, its rows kept as the revision's reference; the track out's rows it priced moved to the homesteads (T30 D1), the stage's remaining work priced above

- verdict-3, finding 1: fixed - the registry's cells priced as the registry bins them, each segment's box in every cell it covers, not the cells a line crosses
- verdict-3, finding 2: fixed - the 4 points and 12 corners named as one seed's at 20; under half the total either way (S10)
- verdict-3, finding 3: fixed - the row road at 0 for the nucleated reference, its stated form under "Work the first derivation missed" (a row village's farms each 9 cells, its runs, fords and legs), priced when a row roll joins the manifest
- verdict-3, finding 4: fixed - the driver's stage-end backstop: not this stage's, and not run after it - the driver walks the manifest after no stage rebuilt in Rust (feature 444 T26 D3), and the track is one since T32

## Cheaper algorithms considered

- sweep: not applicable - one lane written.
- the registry's binning: its rule (each box in every cell it covers) is the shared index's, not this stage's; filing only the cells a segment crosses would cut it to about 70 at 40, a change to the registry for every placer
- grid or spatial index: used - the registry's 120 ft cells; the row road's farms ask a 64 ft grid of the street's segments.
- priority queue: not applicable.
- incremental update: used - the track is chosen once, at the homesteads, and drawn here as chosen.
- memoizing what a scan does not change: not applicable.
