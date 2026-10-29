# Derivation - sties, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's settlement form; each homestead's layout on its lot (the house and its outbuildings, each a box, the layout inside the lot's middle 104 ft square); the households.
- Writes: on a plain paddy hamlet, a small pig sty at the households that keep one, against the farmhouse or one of its outbuildings on the household's own plot, each a fixture of the kind `sty`, filed in the registry; no duck pen.
- Keeps: about two households in three keep a sty, the share varying from hamlet to hamlet around that figure (0049: "about two households in three, the share varying from hamlet to hamlet"); the sty about 8 by 6 ft, against the farmhouse or an outbuilding, on the household's own plot (0049, a GUESS); no duck pen at the houses (0049); a dike-pond hamlet's sties stand on its pond banks instead (0049), by `pond_stock`.
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): sties 7 of 10 and 15 of 20 (0.75 at 20); the layout's sty slot - against the house's back wall, beside the privy, inside the 104 ft square - kept free by the layout itself, as the layout keeps every one of its parts apart; a sty's 8 by 6 ft box overlapping (1 + 8/64)(1 + 6/64) = 1.2 registry cells of 64 ft.

## The algorithm

    the form read (1); on a plain paddy hamlet: the hamlet's share rolled around two in three (1)
    each household rolled against the share (1); a keeping household's sty set in its layout's sty slot, turned with the
        house (1), written (1) and filed in the registry's cells its box overlaps (1 a cell)

## Indexes

- registry: cells of 64 ft, every thing filed in every cell its box overlaps; a sty's box overlapping 1.2 cells, written and never asked - the slot is the layout's own, free of the lot's other parts by the layout and of every neighbor by the lot's 29 ft margin - from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | the households, each rolled | the households |
| the roll | per item | 1 | each household against the hamlet's share | always 1 |
| the sty (registry cells written) | per item | 2.4 | at the share that keeps one, 0.75 measured at 20: turned (1), written (1) and filed in 1.2 cells (1.2): 3.2 x 0.75 | every household keeping one, 3.2 |
| slack | per item | 1 | the share is measured, each sty's work exact | not applicable |
| the form and the share | once | 2 | the form read and the hamlet's share rolled | always 2 |

So: households x (1 + 2.4) x 1, plus the form and the share.

## Totals

- at 20: 20 x (1 + 2.4) x 1 + 2 = 70
- at 40: 40 x (1 + 2.4) x 1 + 2 = 138
- at 80: 80 x (1 + 2.4) x 1 + 2 = 274

## Growth

Linear, an exponent of 1.0: one roll a household.

## Cheaper algorithms considered

- sweep: not used - each household is rolled once
- grid or spatial index: used - the registry, written for each sty and never asked
- priority queue: not used - the sty's slot is the layout's
- incremental update: not used - each sty is set once
- memoizing what a scan does not change: used - the slot's box is the layout's, turned with the house
