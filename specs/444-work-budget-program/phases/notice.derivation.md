# Derivation - notice (feature 444)

## Contract

- Reads: the ways' graph (its legs and their junctions, from which the ways out are read); the finished map in its decided view (`meta.view`) and the title placard; the ways (on a hamlet the whole network, `lanes`, none declared main); the houses; the registry of what stands; the waters; the `kosatsuba_seat` knob (`center`, or a landmark from `kosatsuba_anchor`).
- Writes: the notice board (`kosatsuba`), a roofed 16 by 6 ft frame on the verge, and its caption's proved seat, which rides to the label phase (`board_caption_seat`).
- Keeps: every hamlet posts a board (0190); placed last of the features, after the crop, against the view (0190, the GM 2026-08-29); on a way's verge at the busiest clear seat, inside the 60 ft siting band (`place_kosatsuba`: "no verge inside the ~60-real-ft siting band"), scored by the dwellings within 260 ft (0190), seats 12 ft apart along the verge (`BOARD_ALONG_STEP_PX`, 1 ft a pixel); inside the view and off the title placard; clear of what stands and of every watercourse (`fixture_clear_of_water`); kept only where the one caption placer seats its caption clean beside it, at its preferred offset or a ring within reach (0242, feature 266); an `entrance` board only where every way out passes it; every rule asked before the board is drawn (S4); no RNG.
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the view 1,521 by 1,726 ft and 2,274 by 2,486 ft (x2.16 in area: 5,653,164 at 20, 12,210,835 at 40, 26,375,402 at 80 sq ft); the small features' footprints (crowns, scrub, the built parts, the ways at 14 ft, the water), 595,000 sq ft at 20, about 2,190 features with about 38,000 4 ft steps of edge between them, marking about 77,000 cells of 4 ft at 20 (x1.9: 77,000 at 20, 146,300 at 40, 277,970 at 80); the large polygons, the field, the marsh and the groves, filled by one scanline pass, their rings' crossings about 5,000 cells; the ways' legs at most 8 a household; a caption box's reach from a way's middle at most 130 ft (the 7 ft half-width, the 6 ft board, 8 em, 64 ft, and the caption's 52.8 ft), so the mask needs only the corridor of 2 x 130 ft along the ways, at most the view (2,318,420 at 20, 4,405,180 at 40, 8,369,660 at 80 sq ft); the ways' length 4,703 and 8,917 ft (x1.9: 8,917 at 20, 16,943 at 40, 32,191 at 80); the houses' density at most 2.9e-5 a sq ft, so at most 18 houses within 3 by 3 cells of 260 ft, never more than the households; at most 29 things in a 64 ft cell and 26 water segments; the caption, "notice board", 52.8 by 8.4 ft at an 8 ft font (one line; two lines 28 by 17.6), its rings from half an em to 8 em in half-em steps, 16 rings of 8 ranked positions and 2 line layouts, 256 candidates in reach; 1 ft a pixel at the hamlet scale.

## The algorithm

    the obstacle mask in 4 ft cells (the caption's ring step) over the corridor within 130 ft of a way's middle: each small
        feature's cells marked, edge cells included; the large polygons filled by one scanline pass over the corridor; then the
        mask's prefix sums (a summed-area table), so a box is clear in 4 reads
    the ways out, once: the cut points and bridges of the ways' graph from its exits (one depth-first pass), so a seat on
        every way out is read in one lookup
    the seats: along both verges of every way, 12 ft apart, inside the view's 60 ft siting band and off the placard
    each seat's score, the dwellings within 260 ft, from its 3 by 3 cells of a 260 ft house index; the seats sorted by score
        (a counting sort: the score a whole number of at most 18)
    in that order until one is kept: its 7 by 3 ft probe against the registry's things in its cells, and against the waters in
        its cells; the caption's 256 candidates in reach, each box tested on the mask (4); an `entrance` board, its leg among the
        ways out's cut points (1)
    draw the board on the first kept seat, with its caption's proved seat; recorded and filed

## Indexes

- obstacle mask: cells of 4 ft (the caption's ring step, half an em at an 8 ft font), over the corridor within 130 ft of the ways; densest 1 a cell (each cell's prefix sum), from a smallest side of 4 ft
- house index: cells of 260 ft (the score's reach), so a seat's dwellings lie in its 3 by 3 cells; densest the houses' density x 9 x 260 squared, 18, never more than the households, from a smallest side of 260 ft
- registry: cells of 64 ft; densest 29 things a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft against the 7 by 3 ft probe, in at most 2 by 2 cells
- water index: cells of 64 ft; densest 26 water segments a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the board | always 1 |
| the board (registry cells written) | per item | 5 | recorded (1) and filed in at most 4 cells (4) | always 5 |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the obstacle mask (mask cells written) | once | 516,706 at 20, 977,272 at 40, 1,852,282 at 80 | the corridor's 4 ft cells (144,902 at 20, 275,324 at 40, 523,104 at 80), each zeroed and summed (2); the large polygons' scanline pass over them, each cell once, and their rings' crossings, 5,000 (149,902 at 20, 280,324 at 40, 528,104 at 80); the small features' marks, edge cells included (77,000 at 20, 146,300 at 40, 277,970 at 80) | 80 households |
| the ways out (graph nodes and legs) | once | 680 at 20, 1,360 at 40, 2,720 at 80 | one depth-first pass over the ways' graph, its legs (160 at 20, 320 at 40, 640 at 80) and nodes (at most the legs and one a lane end, the households), each entered and left once (2) | an `entrance` board |
| the sort (counting) | once | 1,506 at 20, 2,843 at 40, 5,385 at 80 | each seat into its score's bucket (1), and the 19 buckets read | 80 households |
| the seats (house index, registry, water index and mask cells examined) | over the run | 1,487 x 1,284 at 20, 2,824 x 1,284 at 40, 5,366 x 1,284 at 80 | the seats, 2 x the ways' length over 12 ft (1,487 at 20, 2,824 at 40, 5,366 at 80); each: its score's 9 cells and their at most 18 houses (27 at 20, 27 at 40, 27 at 80), its bucket read (1), its probe's 2 by 2 cells of 64 ft with their 29 things and the cell (120) and their 26 water segments and the cell (108), the view and the placard (2), the caption's 256 candidates, each 4 mask reads, and the decision (1,025), and the entrance's cut-point lookup (1) | every seat tested, the last kept |

So: 1 x 5 x 1, plus the mask, the ways out, the sort, plus the seats x their test.

## Totals

- at 20: 1 x 5 x 1 + 516706 + 680 + 1506 + 1487 x 1284 = 2428205
- at 40: 1 x 5 x 1 + 977272 + 1360 + 2843 + 2824 x 1284 = 4607496
- at 80: 1 x 5 x 1 + 1852282 + 2720 + 5385 + 5366 x 1284 = 8750336

## Earlier findings

- verdict-1, finding 1: fixed - an `entrance` board's rule is read from the ways out's cut points, found once by a depth-first pass over the ways' graph, its own row, and a seat's lookup (1) is in its count; the ways' graph is in the Reads
- verdict-1, finding 2: fixed - the mask's marks count each small feature's cells edge-inclusive, and the large polygons by one scanline pass, so the mask is a ceiling
- verdict-1, finding 3: fixed - the mask covers only the corridor within 130 ft of a way's middle, where a caption box can land
- verdict-1, finding 4: fixed - a counting sort over the scores, at most 18
- verdict-1, finding 5: fixed - the footprints are stated once, the small features' and the large polygons' apart
- verdict-1, finding 6: fixed - the 60 ft siting band is `place_kosatsuba`'s own, cited

## Cheaper algorithms considered

- sweep: not used - the seats are taken by score, not in space
- grid or spatial index: used - the house index for the score, the registry and the water index for the probe, the mask for the caption
- priority queue: not used - the seats are counting-sorted once by score; every seat may be asked
- incremental update: not used - one board is placed
- memoizing what a scan does not change: used - the obstacle mask is built once and its summed-area table answers every caption box in 4 reads
