# Derivation - pond_bank, greenfield (feature 444 FR-015)

## Contract

- Reads: the pond (its ellipse) and its reed fringe; the registry of what stands near it - the houses' roofs, the wellheads, the yards' and kitchen beds' sunny ground, the ways, the crop and the water.
- Writes: the bank's form for the map, bare or planted; on a planted bank its trees, mulberry and cudrania alternating round it, each a crown, filed in the registry.
- Keeps: the bank's form rolled at even odds (0061: "The two come up at even odds, a GUESS"); a planted bank's trees beyond the reed fringe, about one every 30 ft of bank, each crown about 12 ft across (0061, each a GUESS); a tree left out where its crown would fall on a roof, a wellhead, or the sunny ground of a yard or a kitchen bed, or its trunk on a lane, the crop or the water (0061), each asked before the tree is drawn.
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the pond 189 by 121 ft and 268 by 171 ft across, its radii x1.41 a doubling (378 by 241 ft at 40, 535 by 341 ft at 80); its bank's length, the ellipse's perimeter, about 497 ft at 10 and 702 ft at 20 (993 at 40, 1,404 at 80); the bank bare on both reference rolls; the typical densities (`items.md`, rubric S8): things of every kind 3.3 an occupied 64 ft cell.

## The algorithm

    the bank's form rolled (1); bare: done
    planted (even odds): the bank walked at 30 ft steps beyond the reeds; at each step the crown's 12 ft box against the things
        in the registry cells its box overlaps, 1.41 on average (each 1, the cell 1), and the trunk's point against the ways,
        the crop and the water there, the same cells' things; kept, the tree written (1) and filed in the cells its box
        overlaps (1.41), its species the alternation's next (0)

## Indexes

- registry: cells of 64 ft, every thing placed so far filed in every cell its box overlaps, so a box is asked of the cells it overlaps and no ring; the mean 3.3 things an occupied cell (`items.md`, rubric S8), a 12 ft crown's box overlapping (1 + 12/64)^2 = 1.41 cells on average, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the bank, once a map | always 1 |
| the form's roll | per item | 1 | the even-odds roll | always 1 |
| slack | per item | 1 | the trees are the bank's length over 30 ft, and each test its box's mean cells at the mean density | not applicable |
| the planted bank (registry cells examined) | over the run | 98 at 20, 141 at 40, 200 at 80 | at its share of the rolls, one half (S9: work only a knob's branch needs is charged at that branch's share): the bank's length over 30 ft, 23 at 20, 33 at 40, 47 at 80 trees, each its crown and trunk tested in the 1.41 cells its box overlaps at the mean 3.3 things and the cell (6.1), written (1) and filed in its 1.41 cells (1.4): 8.5 a tree, half of 196, 281 and 400, rounded up | a planted bank beside the houses |

So: 1 x (1 x 1), plus the planted bank.

## Totals

- at 20: 1 x (1 x 1) + 98 = 99
- at 40: 1 x (1 x 1) + 141 = 142
- at 80: 1 x (1 x 1) + 200 = 201

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.51: one pond, its bank's length growing with its radii.

## Earlier findings

- verdict-1, finding 1: fixed - the registry files a thing in every cell its box overlaps, so a crown's box asks the 1.41 cells it overlaps; 8.5 a tree
- verdict-1, finding 2: fixed - the halves recomputed from 196, 281 and 400, rounded up
- verdict-1, finding 3: fixed - the memoizing line says half the steps share a cell, within the rounding

## Cheaper algorithms considered

- sweep: used - the bank walked once at its 30 ft step
- grid or spatial index: used - the registry's cells under each crown's box
- priority queue: not used - the trees are laid in order round the bank
- incremental update: not used - each tree is tested once and never moved
- memoizing what a scan does not change: not used - about half of consecutive 30 ft steps share a 64 ft cell, a saving of about half an operation a tree, within the rounding
