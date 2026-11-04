# Derivation - waterward, greenfield (feature 444 FR-015)

## Contract

- Reads: the plan's settlement form and field archetype.
- Writes: a polder's waterward fringe: the reed strips outside its dike on the flanks that face the water, laid before the houses so they treat it as wet ground (feature 150); on any other form, nothing.
- Keeps: drawn only on a polder hamlet; nothing on a valley hamlet.
- Bounds: the reference spec is a nucleated valley hamlet with a pond sink, at every size (`items.md`), so the stage writes nothing on the rolls its budget is held to; a polder hamlet's figure is its own phase's, when one is rolled.

## The algorithm

    the plan's form read once (1); not polder: done

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the form's test, once a map | always 1 |
| the form's test | per item | 1 | one read of the plan | always 1 |
| slack | per item | 1 | nothing varies | not applicable |

So: 1 x 1 x 1.

## Totals

- at 20: 1 x 1 x 1 = 1
- at 40: 1 x 1 x 1 = 1
- at 80: 1 x 1 x 1 = 1

## Growth

Flat, an exponent of 0: one test.

## Cheaper algorithms considered

- sweep: not used - nothing is laid on the reference spec
- grid or spatial index: not used - nothing is geometric on it
- priority queue: not used - nothing is ranked
- incremental update: not used - one test
- memoizing what a scan does not change: not used - there is no scan
