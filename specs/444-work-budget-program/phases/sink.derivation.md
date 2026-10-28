# Derivation - sink (feature 444)

## Contract

- Reads: the field's drain outfall and its heading, the fall, the crop's edge (the plots along it, the narrowest 26 ft, 0005), the brook (8 segments), the forbidden ground the field reserved below the outfall (the drain's own corridor, its 4 segments), the dikes (none on a valley comb), and the sink rolled (the reference: `pond`, present at 10 and 20 households, measured 2026-10-28 from the reference manifests, `phases/items.md`).
- Writes: the tail pond - an ellipse, its semi-axes a and b about 47 and 30 ft at 10 households and 67 and 43 ft at 20 (the manifest's `pond`, measured the same day), growing as the map's side, the square root of the households (a about 95 ft at 40 and 134 ft at 80) - and the drainage ditch from the outfall to it (`pond_run`).
- Keeps: the pond downslope of the outfall, the set-back SOLVED (`pond_setback`), the pond stepped across the fall where it must be (`pond_seat`, the stage's docstring), its rim clear of the crop and the brook, the ditch crossing no dike, brook or forbidden ground (0061); past `POND_SETBACK_LIMIT` (300 ft, a GUESS) the field drains off the frame. The cohort's checks: the pond's footprint against the overlap matrix (a HARD feature every later stage avoids) - carried by the exact clearance tests below.
- Bounds: one pond and one run at every size; the setback at most 300 ft.

## The algorithm

    the band: the strip down the fall from the outfall, 300 ft plus the pond's length (2a) long and three pond widths (6a) wide
    examine the band's cells once, gathering the crop-edge segments, the brook's segments and the drain's corridor in them
    on the fall's line and on one line to each side of it, a pond width (2a) across: for each gathered segment, solve exactly
        the smallest setback at which the ellipse clears it (a tangency and its two endpoints, one solve); the line's setback is the
        largest of these
    take the line whose setback is smallest and within 300 ft; route the ditch as one segment from the outfall to the pond, met
        once against each gathered segment
    record the pond and the ditch

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 (the whole stage: one pond and its run) | the contract | the same at every size |
| lines solved (S2) | per item | 3 | the fall's line and one to each side a pond width across - the stepping across the fall the stage's docstring states (`pond_seat`); its reach, one pond width each way, a GUESS: the contract states the step, not how far it goes | always 3 |
| cells examined (S1) | per item | (300 + 2a) x 6a / 1,488: 117 at 20, 187 at 40, 307 at 80 | the band's area over a plot-sized cell (1,488 sq ft), each examined once | 80 households, the widest band |
| segments gathered (S1) | per item | 28 at 20, 34 at 40, 43 at 80 | the crop edge crossing the band's 6a width at the narrowest plot, 26 ft (16, 22, 31), the brook's 8 at most, the drain's 4 | 80 households |
| the solve, per segment and line | per item | 1 | one exact clearance of the ellipse from a segment along the line | always 1 |
| the ditch | per item | as the segments gathered | one segment met once against each gathered segment | 80 households |
| the record | per item | 2 | the pond and the ditch, written once | always 2 |
| slack | per item | 1 | every factor is a bound at its worst case, not an estimate | not applicable |

So: cells + 3 x segments + segments + 2 = 117 + 84 + 28 + 2 = 231 at 20, 187 + 102 + 34 + 2 = 325 at 40, and 307 + 129 + 43 + 2 =
481 at 80 households - growing as the pond does, an exponent of about 0.5 from 20 to 80.

## Cheaper algorithms considered

- sweep: not used - the setback is solved per segment, not searched along the line
- grid or spatial index: used - the band's cells give the segments the pond can meet, gathered once
- priority queue: not used - three lines, compared once
- incremental update: not used - one solve per segment and line, nothing is repeated
- memoizing what a scan does not change: used - the band's segments are gathered once and read by all three lines and the ditch
