# Derivation - notice, greenfield (feature 444 FR-015)

## Contract

- Reads: the lanes on the lots' lattice gaps and the track out; the seated lots' lattice; the plan's board siting (`kosatsuba_seat`: center, entrance, frontage, bridgehead); the registry and the water index; the view and the title placard.
- Writes: the notice board, a roofed 16 by 6 ft frame on a way's verge, and its caption's proved seat, which rides to `labels`.
- Keeps: every settlement down to a hamlet carries a board; where a map has no main road or street - a web of lanes - the board goes where the most buildings stand nearby; at a hamlet it stands 6 ft from the edge of the way, squared to it; a site whose caption fits outranks any whose caption does not, and among those the busiest wins; a board with nowhere to put a caption is still placed; the board the last thing placed, after the map is cropped to its frame; an entrance board only where a way comes in from outside, near where the households' ways have joined the way out (0190).
- Bounds (measured 2026-10-29 on the reference manifests at 10 and 20 households, the lots grown as the homesteads lay them): the `center` siting on both; the buildings near a site counted within 250 ft (0190's measure on its town maps, a GUESS for a hamlet), 1.54 lots of 162 ft, so a site's count lies inside its 5 by 5 window of lots on the lattice; the lattice's span 9 by 6, 12 by 9 and 16 by 12 lots (54, 108 and 192 cells), the lane gaps 21, 44 and 87; the seats along a gap's verge 12 ft apart (a GUESS knob); a clear seat's caption, 52.8 by 8.4 ft, clean at its preferred offset in one of 8 ranked positions at 0.66 of clear seats, a seat's probe clear at 0.78 (measured 2026-10-28 on the same manifests); the typical densities (`items.md`, rubric S8): things of every kind 5.5 a 64 ft cell near the houses.

## The algorithm

    the siting read (1); on `center`: the lots' occupancy summed over the lattice's span once (2 a cell), so a gap's 5 by 5
        window count - an upper bound on the buildings within 250 ft of any seat on it - is 4 reads; each lane gap's bound taken
        (4) and the gaps bucketed by it (1)
    in bound order: the gap's exact count, the lots within 250 ft of its middle from the lattice (17); its verge's seats from
        the middle out at 12 ft, 6 ft off the tread, until one is clear and its caption fits - each seat's probe asked of the
        registry and the water index's cells it overlaps, the view and the placard, and its caption's boxes in rank order until
        the first clean one; the search stops when the best exact count with a fitting caption reaches the next gap's bound
    on `entrance`: the track's start corner, which every household's way reaches, is the site, its verge seats as above
    written: the board (1) and filed (1.4), its caption's proved seat (1)

## Indexes

- the lots' lattice: cells of 162 ft, the seated lots by lattice index and their occupancy summed once over the span, from a smallest side of 162 ft
- registry: cells of 64 ft, every thing filed in every cell its box overlaps; the board's 16 by 6 ft box overlapping (1 + 16/64)(1 + 6/64) = 1.37 cells and a caption's box (1 + 52.8/64)(1 + 8.4/64) = 2.07, at the mean 5.5 things near the houses (`items.md`, rubric S8), from a smallest side of 64 ft
- water index: cells of 64 ft, the probe's same 1.37 cells, the mean 3.7 segments a crossed cell, an uncrossed cell read alone, from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the board, once a map | always 1 |
| the bounds (the lots' lattice cells examined) | per item | 213 at 20, 436 at 40, 819 at 80 | the occupancy summed over the span's 54, 108 and 192 cells (2 each), each lane gap's window read (4) and bucketed (1): 108 + 21 x 5 = 213, 216 + 44 x 5 = 436, 384 + 87 x 5 = 819 | a cluster of many short rows |
| the exact counts | per item | 51 | the gaps taken in bound order until the best exact count reaches the next bound, about 3 on a lattice where the middle gaps' windows tie (17 each) | a long, even cluster |
| the seats (registry and water index cells examined) | per item | 157 | 1 / 0.78 = 1.3 seats tried (S8, 1/p): each its probe in 1.37 cells at the mean 5.5 things and the cell (8.9), the water in the same cells read with them (1.4), the view and the placard (2), and its caption, about 8 boxes ranked to the first clean one (4 + 8 x 0.34 / 0.66), each in 2.07 cells at 6.5 (13.5): 108; 120.3 a seat | a lane lined with yards |
| the writes | per item | 3.4 | the board written (1) and filed in 1.37 cells (1.4), its caption's seat (1) | always 3.4 |
| slack | per item | 1 | the bounds and the seats' share are measured | not applicable |

So: 1 x (the bounds + 51 + 157 + 3.4 + 1) x 1, the siting read the last 1.

- pruning: the gaps are taken in order of an upper bound read from the lattice's summed occupancy, and the search stops once the best exact count with a fitting caption reaches the next gap's bound (rubric S9)

## Totals

- at 20: 1 x (213 + 51 + 157 + 3.4 + 1) x 1 = 425.4
- at 40: 1 x (436 + 51 + 157 + 3.4 + 1) x 1 = 648.4
- at 80: 1 x (819 + 51 + 157 + 3.4 + 1) x 1 = 1031.4

## Growth

From 20 to 80 households the stage grows at an exponent of about 0.64: the bounds over the lattice's span and its gaps.

## Cheaper algorithms considered

- sweep: used - a gap's verge walked out from its middle at 12 ft
- grid or spatial index: used - the lots' lattice for the counts, the registry and the water index for each seat
- priority queue: used - the gaps bucketed by their bound and taken in order
- incremental update: used - the occupancy summed once, each window four reads
- memoizing what a scan does not change: used - the summed occupancy read by every gap's window
