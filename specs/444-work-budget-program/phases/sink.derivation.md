# Derivation - sink (feature 444)

## Contract

- Reads: the field's drain outfall and its heading, the fall (`meta.down_deg` 90 on the reference: straight down the sheet), the crop's edge (the fan's outline, a closed ring of points), the brook (its points in order down the fall), the drain's corridor below the outfall, the dikes (none on a valley comb), and the sink rolled (the reference: `pond`, present at 10 and 20 households).
- Writes: the tail pond - an ellipse with radii rx and ry (the manifest's `pond` is (cx, cy, rx, ry)): rx 95 and ry 60 ft at 10 households, 134 and 85 ft at 20, measured 2026-10-28 (`phases/items.md`), x1.41 a doubling as the map's side (134 at 20, 190 at 40, 268 at 80 for rx, 85 at 20, 121 at 40, 170 at 80 for ry); rx lies across the fall - and the drainage ditch from the outfall to it (`pond_run`).
- Keeps: the pond downslope of the outfall, the set-back SOLVED (`pond_setback`: the smallest that clears), the pond stepped across the fall where it must be (`pond_seat`), its rim clear of the crop and the brook, the ditch crossing no dike, brook or forbidden ground (0061); past `POND_SETBACK_LIMIT` (300 ft, a GUESS) the field drains off the frame. The cohort's checks: the pond's footprint against the overlap matrix - carried by the exact tests below.
- Bounds: one pond and one run at every size; the setback at most 300 ft; the step across the fall reaches one pond width (2 rx) to each side - a GUESS knob (`pond_seat` states the step, not its reach). Measured the same day in the band below at 20 households: 53 consecutive outline segments within its width, 27 brook points (so at most 28 brook segments touching it) and 5 drain points; at 40 and 80 the outline's x1.06 a doubling (its segments lengthen as the band widens) rounded up, the brook's and the drain's in proportion to the band's length (470 at 20, 542 at 40, 640 at 80 ft); the outline's points x1.16 a doubling (78 at 20, 90 at 40, 105 at 80), the brook's x1.12 (237 at 20, 265 at 40, 297 at 80).

## The algorithm

    the band: down the fall from the outfall, 300 ft plus the pond's height (2 ry) long, three pond widths (6 rx) wide
    gather: scan every outline point once against the band's box (the outline is a closed ring); bisect the brook (ordered
        down the fall) to the band's start and walk it through the band; test the drain's last points against the box
    file each gathered segment into the corridors it spans - three, each a pond width (2 rx) across, one a line, covering the
        band exactly; a segment shorter than a pond width spans at most two
    for each of three lines - the fall's and one to each side, a pond width across:
        each segment in its corridor blocks one interval of setbacks: solve it exactly (its tangency and two endpoints); test
            the line's ditch against every gathered segment (a side line's ditch crosses the middle corridor)
        sort the intervals; sweep them for the smallest setback, from the outfall, in no interval and within 300 ft
    take the line with the smallest setback whose ditch crosses nothing; record the pond and the ditch

## Indexes

- corridors: cells of 268 ft across the fall at 20 households (2 rx; 380 ft at 40, 536 ft at 80) and the band's length along it; densest every segment gathered, from a smallest side of 268 ft against the longest outline segment, 222 ft: a segment spans at most 2 corridors

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the whole stage: one pond and its run | the same at every size |
| the gather | per item | 114 at 20, 132 at 40, 153 at 80 | the outline's points scanned once (78 at 20, 90 at 40, 105 at 80), the brook bisected (8 halvings over 237 points, 9 past 256) and walked through the band (28 at 20, 33 at 40, 39 at 80 segments) | 80 households |
| the drain's box tests | per item | 7 | its last points against the band's box, at most 7 | always 7 |
| lines solved (S2) | per item | 3 | the fall's line and one to each side - the step's reach the Bounds state | always 3 |
| segments gathered (S1) | per item | 87 at 20, 97 at 40, 108 at 80 | the outline's 53 at 20, 57 at 40, 60 at 80, the brook's 28 at 20, 33 at 40, 39 at 80 and the drain's 6 at 20, 7 at 40, 9 at 80 in the band (5 drain points can touch 6 segments, in proportion above) | 80 households |
| the corridors (cells examined) | per item | 2 | a segment's intervals solved only on the lines whose corridors it spans - at most 2 (the Indexes) | a segment straddling a corridor's edge |
| the interval, per segment and line | per item | 3 | a tangency and two endpoints, solved exactly | always 3 |
| the line's ditch, per segment | per item | 1 | each line's straight ditch tested against every gathered segment | always 1 |
| the sort, per segment and line | per item | 7 at 20, 7 at 40, 7 at 80 | the intervals sorted, log2 of the segments, rounded up | 80 households |
| the sweep, per segment and line | per item | 1 | the sorted intervals walked once for the first gap | always 1 |
| the record | per item | 2 | the pond and the ditch | always 2 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |

So: the gather and the drain's tests, twice the segments x (3 + the sort + 1) for the intervals, 3 lines x the segments x 1 for the ditches, and the record.

## Totals

- at 20: 1 x (114 + 7 + 2 x 87 x (3 + 7 + 1) + 3 x 87 x 1 + 2) x 1 = 2298
- at 40: 1 x (132 + 7 + 2 x 97 x (3 + 7 + 1) + 3 x 97 x 1 + 2) x 1 = 2566
- at 80: 1 x (153 + 7 + 2 x 108 x (3 + 7 + 1) + 3 x 108 x 1 + 2) x 1 = 2862

## Cheaper algorithms considered

- sweep: used - each line's sorted intervals are swept once for the smallest clear setback; the brook, ordered down the fall, bisected to the band
- grid or spatial index: used - the band's three corridors (the Indexes), each segment filed into those it spans as it is gathered
- priority queue: not used - the intervals are sorted once, not kept in order as they change
- incremental update: not used - each line is solved once
- memoizing what a scan does not change: used - the band's segments are gathered once and read by all three lines
