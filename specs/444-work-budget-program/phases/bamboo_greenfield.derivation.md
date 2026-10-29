# Derivation - bamboo, greenfield (feature 444 FR-015)

## Contract

- Reads: the households and the plan's household bamboo; each lot's north strip, its west 22 ft left free by `hinterland`'s woods.
- Writes: each household's bamboo stand - its polygon to scale and its symbolic marks inside it on a jittered grid - filed in the registry.
- Keeps: a stand drawn as a stand-level glyph with its marks inside (0075, a map drawing convention after Japan's topographic legend); no bamboo within 50 ft east, west or south of a yard or bed, from its north edge down (0038: "Bamboo keeps the same clear ground as a tree").
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the stands 3 and 6, all a household's (0.3 a household at 20), each 16 by 22 ft with 7 marks; a lot's north strip 162 by 29 ft, north of its own house and so of its own yard and beds, its west 22 ft free; a stand's box overlapping (1 + 16/64)(1 + 22/64) = 1.7 cells of 64 ft.

## The algorithm

    each household rolled for a stand (1); a kept one set in its lot's north strip's free west end, by the lattice's geometry north
        of its own yard and beds and south of nothing's, so it keeps the sun untested; its polygon's 4 corners written (4), its 7
        marks on a jittered grid each placed and written (2), its record written (1) and filed in the cells it overlaps (1.7)

## Indexes

- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a stand's box overlapping 1.7 cells, written and never asked, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households, each rolled | the households |
| the roll | per item | 1 | the household's stand rolled | always 1 |
| the stand (registry cells written) | per item | 6.2 | at the 0.3 a household that keep one: its 4 corners (4), its 7 marks (14), its record (1), filed in 1.7 cells (1.7): 20.7 x 0.3 | every household with a stand, 20.7 |
| slack | per item | 1 | the share measured, each stand a fixed count | not applicable |

So: households x (1 + 6.2) x 1.

## Totals

- at 20: 20 x (1 + 6.2) x 1 = 144
- at 40: 40 x (1 + 6.2) x 1 = 288
- at 80: 80 x (1 + 6.2) x 1 = 576

## Growth

Linear, an exponent of 1.0: a roll a household.

## Cheaper algorithms considered

- sweep: not used - each stand is laid once
- grid or spatial index: used - the registry, written for each stand
- priority queue: not used - nothing is ranked
- incremental update: not used - each stand is laid once
- memoizing what a scan does not change: used - the stand's slot is the strip's free end, left by the woods
