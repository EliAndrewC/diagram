# Derivation - notice (feature 444)

## Contract

- Reads: the finished map in its decided view (`meta.view`) and the title placard; the ways (on a hamlet the whole network, `lanes`, none declared main); the houses; the registry of what stands; the waters; the `kosatsuba_seat` knob (`center`, or a landmark from `kosatsuba_anchor`).
- Writes: the notice board (`kosatsuba`), a roofed 16 by 6 ft frame on the verge, and its caption's proved seat, which rides to the label phase (`board_caption_seat`).
- Keeps: every hamlet posts a board (0190); placed last of the features, after the crop, against the view (0190, the GM 2026-08-29); on a way's verge at the busiest clear seat, scored by the dwellings within 260 ft (0190; `place_kosatsuba`), seats 12 ft apart along the verge (`BOARD_ALONG_STEP_PX`, 1 ft a pixel); inside the view and off the title placard; clear of what stands and of every watercourse (`fixture_clear_of_water`); kept only where the one caption placer seats its caption clean beside it, at its preferred offset or a ring within reach (0242, feature 266); an `entrance` board only where every way out passes it; every rule asked before the board is drawn (S4); no RNG.
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the view 1,521 by 1,726 ft and 2,274 by 2,486 ft (x2.16 in area: 5,653,164 at 20, 12,210,835 at 40, 26,375,402 at 80 sq ft); the features' footprints, each clipped to the view (crowns, scrub, the built parts, the ways at 14 ft, the field, the water, the groves, the marsh at most the view), 8,270,531 sq ft at 20 and about half at 10 (x1.98: 8,646,896 at 20, 17,120,855 at 40, 33,899,292 at 80); the ways' length 4,703 and 8,917 ft (x1.9: 8,917 at 20, 16,943 at 40, 32,191 at 80); the houses' density at most 2.9e-5 a sq ft, so at most 18 houses within 3 by 3 cells of 260 ft, never more than the households; at most 29 things in a 64 ft cell and 26 water segments; the caption, "notice board", 52.8 by 8.4 ft at an 8 ft font (one line; two lines 28 by 17.6), its rings from half an em to 8 em in half-em steps, 16 rings of 8 ranked positions and 2 line layouts, 256 candidates in reach; 1 ft a pixel at the hamlet scale.

## The algorithm

    the obstacle mask over the view in 4 ft cells (the caption's ring step): each feature's cells within the view marked, then
        the mask's prefix sums (a summed-area table), so a box is clear in 4 reads
    the seats: along both verges of every way, 12 ft apart, inside the view's 60 ft siting band and off the placard
    each seat's score, the dwellings within 260 ft, from its 3 by 3 cells of a 260 ft house index; the seats sorted by score
    in that order until one is kept: its 7 by 3 ft probe against the registry's things in its cells, and against the waters in
        its cells; the caption's 256 candidates in reach, each box tested on the mask (4); an `entrance` board, the way out's
        passing (1, read from the access tree)
    draw the board on the first kept seat, with its caption's proved seat; recorded and filed

## Indexes

- obstacle mask: cells of 4 ft (the caption's ring step, half an em at an 8 ft font), over the view; densest 1 a cell (each cell's prefix sum), from a smallest side of 4 ft
- house index: cells of 260 ft (the score's reach), so a seat's dwellings lie in its 3 by 3 cells; densest the houses' density x 9 x 260 squared, 18, never more than the households, from a smallest side of 260 ft
- registry: cells of 64 ft; densest 29 things a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft against the 7 by 3 ft probe, in at most 2 by 2 cells
- water index: cells of 64 ft; densest 26 water segments a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the board | always 1 |
| the board (registry cells written) | per item | 5 | recorded (1) and filed in at most 4 cells (4) | always 5 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the obstacle mask (mask cells written) | once | 1,247,077 at 20, 2,596,410 at 40, 5,415,632 at 80 | the view's 4 ft cells (353,323 at 20, 763,178 at 40, 1,648,463 at 80), each zeroed and summed (2), and each feature's cells within the view marked, the clipped footprints over 16 sq ft (540,431 at 20, 1,070,054 at 40, 2,118,706 at 80) | 80 households |
| the seats (house index, registry, water index and mask cells examined) | over the run | 1,487 x 1,293 at 20, 2,824 x 1,294 at 40, 5,366 x 1,295 at 80 | the seats, 2 x the ways' length over 12 ft (1,487 at 20, 2,824 at 40, 5,366 at 80); each: its score's 9 cells and their at most 18 houses (27 at 20, 27 at 40, 27 at 80), its place in the sort (log2 of the seats rounded up), its probe's 2 by 2 cells of 64 ft with their 29 things and the cell (120) and their 26 water segments and the cell (108), the view and the placard (2), and the caption's 256 candidates, each 4 mask reads, and the decision (1,025) | every seat tested, the last kept |

So: 1 x 5 x 1, plus the mask, plus the seats x their test.

## Totals

- at 20: 1 x 5 x 1 + 1247077 + 1487 x 1293 = 3169773
- at 40: 1 x 5 x 1 + 2596410 + 2824 x 1294 = 6250671
- at 80: 1 x 5 x 1 + 5415632 + 5366 x 1295 = 12364607

## Cheaper algorithms considered

- sweep: not used - the seats are taken by score, not in space
- grid or spatial index: used - the house index for the score, the registry and the water index for the probe, the mask for the caption
- priority queue: not used - the seats are sorted once by score; every seat may be asked
- incremental update: not used - one board is placed
- memoizing what a scan does not change: used - the obstacle mask is built once and its summed-area table answers every caption box in 4 reads
