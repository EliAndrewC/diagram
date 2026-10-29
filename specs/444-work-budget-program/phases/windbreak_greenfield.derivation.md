# Derivation - windbreak, greenfield (feature 444 FR-015)

## Contract

- Reads: the seated lots' lattice (each household's 104 ft square inside its 162 ft lot, its house at the square's north side, its yard below it); the lanes on the lattice's gaps; the plan's copse siting (`copse_siting`).
- Writes: the village copse among the homes - its clumps on a grid in the gaps between the houses, each a crown - and its grove record; each clump filed in the registry.
- Keeps: no canopy tree within 50 ft east, west or south of a yard or bed, from the plot's north edge down, its own farm's or a neighbor's (0038: "No canopy tree stands in a yard's or bed's sun, whatever stand it belongs to"); nothing built on a lane (0246); the copse among the houses (`copse_siting`, its form a knob).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the copse among the houses on both, its clumps 223 and 462 (about 23 a household), past 20 with the households; the gap between two rows of lots 58 ft deep, from 133 to 191 ft below the north lot's north edge, the north lot's yard ending 83 ft below it and the south lot's house starting at 191; a lane in a gap's middle, its tread and a 10 ft keep each side, so the clumps stand in the gap's two strips of 19 ft; the gaps between two columns of lots lie within 29 ft east or west of the yards and beds, so no clump stands in them; a clump's box about 12 ft across, overlapping (1 + 12/64)^2 = 1.4 cells of 64 ft.

## The algorithm

    the siting read (1); for each household: the gap south of its lot read from the lattice - its lane, if the tree marked one (1)
    in each of the gap's two 19 ft strips, the clumps on a jittered grid (each its slot 1): every clump keeps the sun by the
        lattice's geometry - the strip lies 50 ft and more south of the north lot's yard (from 133 ft against its yard's end at
        83) and north of the south lot's house and yard - and off the lane by the strip's keep, so none is tested
    each clump written (1) and filed in the registry's cells it overlaps (1.4); the grove record written once (2)

## Indexes

- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a 12 ft clump overlapping 1.4 cells, written and never asked, from a smallest side of 64 ft
- the lots' lattice: cells of 162 ft, the seated lots and their gaps by lattice index, looked up directly, from a smallest side of 162 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households, one gap south of each lot | the households |
| the gap (the lots' lattice cells examined) | per item | 1 | the gap's lane read from the lattice | always 1 |
| the clumps (registry cells written) | per item | 78.5 | 23.1 clumps a household (462 at 20), each its slot (1), written (1) and filed in 1.4 cells (1.4): 3.4 x 23.1 | a household with a deeper gap |
| slack | per item | 1 | the clumps a household measured, each a fixed count of operations | not applicable |
| the siting and the record | once | 3 | the siting read (1) and the grove record written (2) | always 3 |

So: households x (1 + 78.5) x 1, plus the siting and the record.

## Totals

- at 20: 20 x (1 + 78.5) x 1 + 3 = 1593
- at 40: 40 x (1 + 78.5) x 1 + 3 = 3183
- at 80: 80 x (1 + 78.5) x 1 + 3 = 6363

## Growth

Linear, an exponent of 1.0: a household's gap and its clumps.

## Cheaper algorithms considered

- sweep: used - each gap's strips filled once on a jittered grid
- grid or spatial index: used - the lots' lattice for the gaps, the registry written
- priority queue: not used - nothing is ranked
- incremental update: not used - each clump is laid once
- memoizing what a scan does not change: used - the sun's keep is the lattice's geometry, never asked of a clump
