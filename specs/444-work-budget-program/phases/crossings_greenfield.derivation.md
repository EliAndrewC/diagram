# Derivation - crossings, greenfield (feature 444 FR-015)

## Contract

- Reads: the field's comb - its main ditches and its branches, and the field path laid on a branch's bund (the plan's `field_path`); the brook; the ways and any water they cross, handed on by `track` and `web`.
- Writes: the footbridges where the field path crosses a main ditch, each a log or plank laid across it; the places along the brook where it may be forded; a bridge where a way crosses a water.
- Keeps: a plank or log footbridge where a field path crosses a farm ditch (0084); a road bridge where a way crosses a river or canal (0087); a way keeps to dry ground and crosses water only at a bridge or a ford.
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): footbridges 6 and 9, each a log across a main ditch where the path on a branch crosses it, past 20 with the main ditches crossed (x1.5 a doubling: 14 and 20); the brook's fording places 31 and 44, about one every 160 ft of the brook, past 20 as measured from 10 to 20 (x1.42: 62 and 88), written into the plan's list of ford points - a point a way may cross at, no box drawn, so not a registry thing; the brook itself 212 and 237 points (`items.md`), 5,404 and 7,362 ft, past 20 with the view's side (x1.12: 265 and 297); a footbridge a log about 10 ft long across a main ditch and 4 ft wide, its span the ditch's (each a GUESS, 0084); the track out and the lanes crossing no water on either roll (the lanes run in the lots' gaps, clear by construction).

## The algorithm

    the field path's crossings are the comb's own junctions, where the path's branch meets each main ditch: each junction read
        from the comb (1), its bridge's record - its middle's two coordinates, its turn along the branch, its span across the
        ditch, its width and its form - written (6) and filed in the registry's cells it overlaps (1 a cell)
    the brook's fording places: its stored points walked once, the length summed (1 a point), a ford point written to the
        plan's list at each 160 ft (1)
    each crossing handed on by the ways, at its share of the rolls: none on the reference rolls

## Indexes

- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a 10 by 4 ft footbridge overlapping (1 + 10/64)(1 + 4/64) = 1.2 cells, written here, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 9 at 20, 14 at 40, 20 at 80 | the footbridges, one a main ditch the path crosses | the comb's main ditches |
| the bridge (registry cells written) | per item | 8.2 | its junction read (1), its record written (6), filed in 1.2 cells (1.2) | always 8.2 |
| slack | per item | 1 | every factor is a count of the comb's own junctions | not applicable |
| the fords | over the run | 281 at 20, 327 at 40, 385 at 80 | the brook's points walked once (237, 265, 297) and a ford point written at each 160 ft (44, 62, 88) | the typical valley |

So: footbridges x 8.2 x 1, plus the fords.

## Totals

- at 20: 9 x 8.2 x 1 + 281 = 354.8
- at 40: 14 x 8.2 x 1 + 327 = 441.8
- at 80: 20 x 8.2 x 1 + 385 = 549

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.31: the brook's points, with the view's side, and the main ditches crossed.

## Earlier findings

- verdict-1, finding 1: fixed - the brook's stored points walked once, 237, 265 and 297, a ford written at each 160 ft
- verdict-1, finding 2: fixed - a ford is a point in the plan's list a way may cross at, no box drawn, so not filed in the registry
- verdict-1, finding 3: fixed - the record's 6 are its middle's two coordinates and its four other fields
- verdict-1, finding 4: fixed - the footbridge's size named a GUESS on 0084's log and plank bridges, its span the ditch's

## Cheaper algorithms considered

- sweep: used - the brook walked once at its 160 ft step
- grid or spatial index: used - the registry, written for each bridge
- priority queue: not used - nothing is ranked
- incremental update: not used - each bridge is laid once
- memoizing what a scan does not change: used - the crossings are the comb's junctions, read rather than found by intersecting the path with the ditches
