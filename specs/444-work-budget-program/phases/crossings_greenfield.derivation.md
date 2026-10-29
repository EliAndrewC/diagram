# Derivation - crossings, greenfield (feature 444 FR-015)

## Contract

- Reads: the field's comb - its main ditches and its branches, and the field path laid on a branch's bund (the plan's `field_path`); the brook; the ways and any water they cross, handed on by `track` and `web`.
- Writes: the footbridges where the field path crosses a main ditch, each a log or plank laid across it; the places along the brook where it may be forded; a bridge where a way crosses a water.
- Keeps: a plank or log footbridge where a field path crosses a farm ditch (0084); a road bridge where a way crosses a river or canal (0087); a way keeps to dry ground and crosses water only at a bridge or a ford.
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): footbridges 6 and 9, each a log across a main ditch where the path on a branch crosses it, past 20 with the main ditches crossed (x1.5 a doubling: 14 and 20); the brook's fording places 31 and 44, about one every 160 ft of the brook, past 20 as measured from 10 to 20 (x1.42: 62 and 88); the track out and the lanes crossing no water on either roll (the lanes run in the lots' gaps, clear by construction).

## The algorithm

    the field path's crossings are the comb's own junctions, where the path's branch meets each main ditch: each junction read
        from the comb (1), its bridge's record - its middle, its turn along the branch, its span across the ditch, its width
        and its form - written (6) and filed in the registry's cells it overlaps (1 a cell)
    the brook's fording places: its points walked at 160 ft, each written (2)
    each crossing handed on by the ways, at its share of the rolls: none on the reference rolls

## Indexes

- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a 10 by 4 ft footbridge overlapping (1 + 10/64)(1 + 4/64) = 1.2 cells, written here, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 9 at 20, 14 at 40, 20 at 80 | the footbridges, one a main ditch the path crosses | the comb's main ditches |
| the bridge (registry cells written) | per item | 8.2 | its junction read (1), its record written (6), filed in 1.2 cells (1.2) | always 8.2 |
| slack | per item | 1 | every factor is a count of the comb's own junctions | not applicable |
| the fords | over the run | 88 at 20, 124 at 40, 176 at 80 | each fording place found at its 160 ft step (1) and written (1): 44, 62 and 88 | the typical valley |

So: footbridges x 8.2 x 1, plus the fords.

## Totals

- at 20: 9 x 8.2 x 1 + 88 = 161.8
- at 40: 14 x 8.2 x 1 + 124 = 238.8
- at 80: 20 x 8.2 x 1 + 176 = 340

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.54: the main ditches crossed and the brook's length.

## Cheaper algorithms considered

- sweep: used - the brook walked once at its 160 ft step
- grid or spatial index: used - the registry, written for each bridge
- priority queue: not used - nothing is ranked
- incremental update: not used - each bridge is laid once
- memoizing what a scan does not change: used - the crossings are the comb's junctions, read rather than found by intersecting the path with the ditches
