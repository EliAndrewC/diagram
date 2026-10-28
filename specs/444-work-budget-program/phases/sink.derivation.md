# Derivation - sink (feature 444)

## Contract

- Reads: the field's drain outfall and its heading, the fall (`meta.down_deg` 90 on the reference: straight down the sheet), the crop's edge (the fan's outline, its points in order), the brook (its points in order down the fall), the drain's own corridor below the outfall, the dikes (none on a valley comb), and the sink rolled (the reference: `pond`, present at 10 and 20 households).
- Writes: the tail pond - an ellipse with radii rx and ry (the manifest's `pond` is (cx, cy, rx, ry)): rx 95 ft and ry 60 ft at 10 households, 134 ft and 85 ft at 20, measured 2026-10-28 (`phases/items.md`), growing as the map's side, x1.41 a doubling; rx lies across the fall - and the drainage ditch from the outfall to it (`pond_run`).
- Keeps: the pond downslope of the outfall, the set-back SOLVED (`pond_setback`), the pond stepped across the fall where it must be (`pond_seat`, the stage's docstring), its rim clear of the crop and the brook, the ditch crossing no dike, brook or forbidden ground (0061); past `POND_SETBACK_LIMIT` (300 ft, a GUESS) the field drains off the frame. The cohort's checks: the pond's footprint against the overlap matrix - carried by the exact clearance tests below.
- Bounds: one pond and one run at every size; the setback at most 300 ft; the step across the fall reaches one pond width (2 rx) to each side - a GUESS knob: `pond_seat` states the step, not its reach, so the budget is held at this reach. Measured the same day in the band below at 20 households: 53 consecutive outline segments within its width, 27 brook points and 5 drain points within it; extended at 40 and 80 by the band's length (the outline's in proportion, its segments lengthening as fast as the band widens: x1.06 a doubling).

## The algorithm

    the band: down the fall from the outfall, 300 ft plus the pond's height (2 ry) long, three pond widths (6 rx) wide
    find the band's two edges on the outline and on the brook by binary search along each (both ordered), and take the
        segments between; the drain's segments in the band are its last few
    on the fall's line and on one line to each side, a pond width (2 rx) across: for each gathered segment, solve exactly the
        smallest setback at which the ellipse clears it - its tangency and its two endpoints, 3 basic operations - the line's
        setback the largest of these
    take the line whose setback is smallest and within 300 ft; route the ditch as one segment from the outfall to the pond,
        met once against each gathered segment
    record the pond and the ditch

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the whole stage: one pond and its run | the same at every size |
| the searches | per item | 30 | 2 binary searches on the outline (at most 105 points at 80, 7 halvings) and 2 on the brook (237 points, 8 halvings) | the longest outline and brook |
| lines solved (S2) | per item | 3 | the fall's line and one to each side - the step's reach the Bounds state | always 3 |
| segments gathered (S1) | per item | 84 at 20, 93 at 40, 102 at 80 | the outline's 53 at 20, 56 at 40, 59 at 80, the brook's 27 at 20, 32 at 40, 37 at 80 and the drain's 4 at 20, 5 at 40, 6 at 80 in the band (the Bounds) | 80 households |
| the solve, per segment and line | per item | 3 | a tangency and two endpoints | always 3 |
| the ditch | per item | 84 at 20, 93 at 40, 102 at 80 | one segment met once against each gathered segment | 80 households |
| the record | per item | 2 | the pond and the ditch, written once | always 2 |
| slack | per item | 1 | every factor is a bound at its worst case | not applicable |

So: the searches, 3 lines x the segments x 3, the ditch's tests and the record - growing with the band's length, slowly.

## Totals

- at 20: 1 x (30 + 3 x 84 x 3 + 84 + 2) x 1 = 872
- at 40: 1 x (30 + 3 x 93 x 3 + 93 + 2) x 1 = 962
- at 80: 1 x (30 + 3 x 102 x 3 + 102 + 2) x 1 = 1052

## Cheaper algorithms considered

- sweep: not used - the setback is solved per segment, not searched along the line
- grid or spatial index: not used - the outline and the brook are ordered, so a binary search finds the band's segments without an index
- priority queue: not used - three lines, compared once
- incremental update: not used - one solve per segment and line, nothing is repeated
- memoizing what a scan does not change: used - the band's segments are gathered once and read by all three lines and the ditch
