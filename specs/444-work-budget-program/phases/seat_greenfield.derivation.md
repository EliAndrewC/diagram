# Derivation - seat, greenfield (feature 444 FR-015)

## Contract

- Reads: the field's outline; the plan's fall, wind, settlement form and the cluster's shape (`cluster_shape`); the households.
- Writes: where the settlement sits - the cluster's anchor on the field's margin, its long axis and its shape - drawn nowhere, into the plan; the band kept for the shelter belt on the cluster's windward side.
- Keeps: a village's cluster sits on the higher, drier ground beside its paddy (0031: "On the higher, drier ground beside its paddy, as old settlements stood on the natural levee"); its shape the shape of its dry ground, a lump, a string or a crescent at a field's edge, rolled (0031), a hamlet never split (0031: "a hamlet never splits"); a clustered village shelters behind one belt at its windward edge (0031, 0072), so the band for it is kept before any house is seated.
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households): the field's outline 67 and 78 points, x1.16 a doubling (90 at 40, 105 at 80); one anchor, one axis, one band.

## The algorithm

    the plan's form, shape, fall and wind read (4)
    each outline point's height along the fall taken and compared with the best so far (2 a point): the highest margin, the dry side
    the anchor at that margin's midpoint, set off the outline by half a lot; the axis along the margin for a string or a crescent, across it for a lump (2)
    the belt's band on the anchor's windward side, its edge and depth from the households (2); written (3)

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the settlement's seat, once a map | always 1 |
| the plan read | per item | 4 | the form, the shape, the fall and the wind | always 4 |
| the margin's scan | per item | 156 at 20, 180 at 40, 210 at 80 | each of the outline's points (78, 90, 105) projected on the fall and compared (2); a pass over all of them, because the highest is a maximum over the outline, and the outline is the field's own few dozen points, not a set the houses add to (S9: `- pruning:` below) | the typical field |
| the anchor, the axis and the band | per item | 7 | the anchor and the axis (2), the band's edge and depth (2), the three written (3) | always 7 |
| slack | per item | 1 | every factor is a count of the field's outline and the plan's fields | not applicable |

So: 1 x (4 + the margin's scan + 7) x 1.

- pruning: none - the highest point of the outline is a maximum over all of it, the outline 78 to 105 points of the field's own, growing x1.16 a doubling; a bound would need the outline's points already sorted by height, which costs the same pass.

## Totals

- at 20: 1 x (4 + 156 + 7) x 1 = 167
- at 40: 1 x (4 + 180 + 7) x 1 = 191
- at 80: 1 x (4 + 210 + 7) x 1 = 221

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.2: the outline's points alone grow.

## Cheaper algorithms considered

- sweep: used - one pass over the outline's points
- grid or spatial index: not used - nothing is tested against what stands; the homesteads test their own lots
- priority queue: not used - one maximum is kept as the pass goes
- incremental update: not used - one seat
- memoizing what a scan does not change: not used - one pass
