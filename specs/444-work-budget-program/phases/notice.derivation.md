# Derivation - notice (feature 444)

## Contract

- Reads: the ways' graph (its legs and their junctions, from which the ways out are read); the finished map in its decided view (`meta.view`) and the title placard; the ways (on a hamlet the whole network, `lanes`, none declared main); the houses; the registry of what stands; the waters; the `kosatsuba_seat` knob (`center`, or a landmark from `kosatsuba_anchor`).
- Writes: the notice board (`kosatsuba`), a roofed 16 by 6 ft frame on the verge, and its caption's proved seat, which rides to the label phase (`board_caption_seat`).
- Keeps: every hamlet posts a board (0190); placed last of the features, after the crop, against the view (0190, the GM 2026-08-29); on a way's verge at the busiest clear seat, inside the 60 ft siting band (`place_kosatsuba`: "no verge inside the ~60-real-ft siting band"), scored by the dwellings within 260 ft (0190), seats 12 ft apart along the verge (`BOARD_ALONG_STEP_PX`, 1 ft a pixel); inside the view and off the title placard; clear of what stands and of every watercourse (`fixture_clear_of_water`); kept only where the one caption placer seats its caption clean beside it, at its preferred offset or a ring within reach (0242, feature 266); an `entrance` board only where every way out passes it; every rule asked before the board is drawn (S4); no RNG.
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the view 1,521 by 1,726 ft and 2,274 by 2,486 ft (x2.16 in area: 5,653,164 at 20, 12,210,835 at 40, 26,375,402 at 80 sq ft); the small features' footprints (crowns, scrub, the built parts, the ways at 14 ft, the water), 595,000 sq ft at 20, about 2,190 features with about 38,000 4 ft steps of edge between them, marking about 77,000 cells of 4 ft at 20 (x1.9: 77,000 at 20, 146,300 at 40, 277,970 at 80); the large polygons, the field, the marsh and the groves, filled by one scanline pass; the ways' legs at most 8 a household; the view 1,521 by 1,726 ft and 2,274 by 2,486 ft (x2.16: 5,653,164 at 20, 12,210,835 at 40, 26,375,402 at 80 sq ft); the large polygons' ring crossings about 5,000 at 20, growing with the view's side (x1.47: 5,000 at 20, 7,350 at 40, 10,805 at 80); the ways' length 4,703 and 8,917 ft (x1.9: 8,917 at 20, 16,943 at 40, 32,191 at 80); the houses' density at most 2.9e-5 a sq ft, so at most 18 houses within 3 by 3 cells of 260 ft, never more than the households; at most 29 things in a 64 ft cell and 26 water segments; the caption, "notice board", 52.8 by 8.4 ft at an 8 ft font (one line; two lines 28 by 17.6), its rings from half an em to 8 em in half-em steps, 16 rings of 8 ranked positions and 2 line layouts, 256 candidates in reach; 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does.

## The algorithm

    the seats: along both verges of every way, 12 ft apart, inside the view's 60 ft siting band and off the placard
    each seat's score, the dwellings within 260 ft, by a sliding window along each way: a house enters and leaves each leg's
        window once (from the house index's 3 by 3 cells of 260 ft about the leg), and each seat reads the window (1)
    the seats counting-sorted by score (the score a whole number of at most 18)
    the ways out, once: the cut points and bridges of the ways' graph from its exits (one depth-first pass), so a seat on
        every way out is read in one lookup
    in score order until one is kept - the busiest clear seat, so the first few: its 7 by 3 ft probe against the registry's
        things and the waters in its cells; the view and the placard; the caption's 256 candidates in reach, each box against the
        registry's things in the at most 3 by 2 cells of 64 ft it covers; an `entrance` board, its leg among the cut points (1)
    draw the board on the first kept seat, with its caption's proved seat; recorded and filed

## Indexes

- house index: cells of 260 ft (the score's reach), so a leg's dwellings within reach lie in its 3 by 3 cells; densest the houses' density x 9 x 260 squared, 18, from a smallest side of 260 ft
- registry: cells of 64 ft; densest the mean 4 things a cell near the ways (`items.md`'s typical densities: 3.3 an occupied cell, 5.5 about the houses), from a smallest side of 64 ft against the probe and a caption box, each in at most 3 by 2 cells
- water index: cells of 64 ft; densest the mean 4 water segments a crossed cell (`items.md`), from a smallest side of 64 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 1 | the board | always 1 |
| the board (registry cells written) | per item | 5 | recorded (1) and filed in at most 4 cells (4) | always 5 |
| slack | per item | 2 | what varies around the typical case (S8): a busy junction whose first seats fail their caption | a crowded center |
| the score (house index cells examined) | over the run | 7,247 at 20, 14,344 at 40, 28,406 at 80 | the sliding window: each of the ways' legs (160 at 20, 320 at 40, 640 at 80, 8 a household) admitting and releasing its at most 18 houses in reach (36), and each seat (1,487 at 20, 2,824 at 40, 5,366 at 80, 2 x the ways' length over 12 ft) reading its window (1) | 80 households |
| the sort (counting) | once | 1,506 at 20, 2,843 at 40, 5,385 at 80 | each seat into its score's bucket (1), and the 19 buckets read | 80 households |
| the ways out (graph nodes and legs) | once | 680 at 20, 1,360 at 40, 2,720 at 80 | one depth-first pass over the ways' graph, its legs and nodes, each entered and left once (2) | an `entrance` board |
| the seats tested (registry and water index cells examined) | over the run | 10 x 7724 | the busiest clear seat, so at most the first 10 in score order are tested (S8: the candidates the search order reaches; the slack covers a center whose first seats fail): each its probe's 2 by 2 cells with the mean 4 things and the cell (20) and with the mean 4 water segments and the cell (20), the view and the placard (2), the caption's 256 candidates each in at most 3 by 2 cells of 64 ft with the mean 4 things and the cell (30), and the entrance lookup (1) | the typical center |

So: 1 x 5 x 2, plus the score, the sort, the ways out and the seats tested.

## Totals

- at 20: 1 x 5 x 2 + 7247 + 1506 + 680 + 10 x 7724 = 86683
- at 40: 1 x 5 x 2 + 14344 + 2843 + 1360 + 10 x 7724 = 95797
- at 80: 1 x 5 x 2 + 28406 + 5385 + 2720 + 10 x 7724 = 113761

## Earlier findings

- verdict-1, finding 1: fixed - an `entrance` board's rule is read from the ways out's cut points, found once by a depth-first pass over the ways' graph, its own row, and a seat's lookup (1) is in its count; the ways' graph is in the Reads
- verdict-1, finding 2: fixed - the mask's marks count each small feature's cells edge-inclusive, and the large polygons by one scanline pass, so the mask is a ceiling
- verdict-1, finding 3: disputed - a summed-area table needs a rectangle: over the corridor's 64 ft tiles a caption box, under 64 ft, straddles up to 2 by 2 tiles and costs 16 reads, not 4; over the seats that is 1,487 x 256 x 12, about 4.6M more at 20, against the about 0.62M the view's whole table costs beyond the corridor's at 20 (1,136,000 against 517,000), so the view's table is the cheaper ceiling
- verdict-1, finding 4: fixed - a counting sort over the scores, at most 18
- verdict-1, finding 5: fixed - the footprints are stated once, the small features' and the large polygons' apart
- verdict-1, finding 6: fixed - the 60 ft siting band is `place_kosatsuba`'s own, cited
- verdict-2, finding 1: fixed - the mask is over the view's rectangle, so its summed-area table answers a box in 4 reads; no corridor is stamped
- verdict-2, finding 2: fixed - the large polygons' crossings grow with the view's side, x1.47
- verdict-2, finding 3: fixed - the probe is 0190's 7 by 3 ft face, the search's; the board drawn is 16 by 6 ft, each in at most 2 by 2 cells
- FR-014 re-score: each factor at the typical case (rubric S8): the board is the busiest clear seat, so the first few seats in score order are tested, not every seat; with so few tested the view's obstacle mask costs more than it saves and is dropped, each caption box asked of the registry's cells at the mean densities of `items.md`; the score by a sliding window along each way; slack 2 (ask:444-budget-standard; the accept was ask:444-T05-notice-round-3)
- reason above the reference: the board is one thing a roll, sited against the whole ways network - the score's window over every way and the first seats' caption tests - so its cost per thing is the whole stage, not a cost per house

## Cheaper algorithms considered

- sweep: used - the score by a sliding window along each way, each house entering and leaving a leg's window once
- grid or spatial index: used - the house index for the score, the registry and the water index for the probe, the mask for the caption
- priority queue: not used - the seats are counting-sorted once by score; every seat may be asked
- incremental update: not used - one board is placed
- memoizing what a scan does not change: not used - the view's obstacle mask would cost more than the few seats tested; each caption box reads the registry's cells
