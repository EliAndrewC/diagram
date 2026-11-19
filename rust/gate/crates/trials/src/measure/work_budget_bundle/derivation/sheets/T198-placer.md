# Derivation - the Mode A caption placer (feature 449 T198)

Written 2026-11-19 in the form of `.specify/templates/derivation.md`, to be judged against `docs/work-budget-rubric.md`. The
work is counted per caption placed. Mode A has no households, so the sizes are the six pool sheets, one Totals line each.

**Provenance (blind to the code).** Read: the template, the rubric, the `work-budget` agent's contract, two finished feature-444
derivations (`labels_greenfield`, `notice_greenfield`), the two research pages that state the problem
(`research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html`,
`research/questions/0330-how-a-leader-line-ties-a-caption-to-its-feature.drawing.html`), the caption-declaration paragraph of
`docs/buildings.md`, and the six sheets' SVG. Not read: the placer's source in either language, its tests, any log or count of its
work or timings, and the plan's sections that describe it. Every figure below comes from the rules or from my own small script
over the SVG, which implements the pseudocode below on each sheet's input. The script is not the project's placer and never ran it.
For the two sheets whose SVG already holds seated captions (`county-magistracy-example`, `ochiba-roundtrip-test`), the script reads
only each caption's words, size and what it names, and ignores its seat.

## Contract

- Sizes: pool sheets: county-magistracy-example, hayakawa-magistracy, ochiba-magistracy, ochiba-roundtrip-test, ubame-magistracy, hoshigaoka-shrine
- Scale: 3 px = 1 ft
- Reads: the finished sheet, meaning every drawn shape with its kind (`data-kind`), its id (`data-id`) and its outline, plus the
  sheet's extent (the viewBox). It also reads each declared caption: its words, face, size and declared lines (`tspan`s,
  `data-cont` lines), and what it names (`data-names`, or else the drawn shapes of the tagged group it stands in).
- Writes: each caption's seat (center and anchor), its angle, its lines, and a leader line where it stands more than twice the
  usual gap from its feature.
- Keeps: the rules of 0242 and 0330, below:
  - A feature large enough to hold its name is named on itself, over its middle when that is free.
  - A smaller feature is named beside it. Positions are tried in the ranked order above, below, right, upper right, lower right,
    left, upper left, lower left, at the usual gap, which is half the caption's letter height measured from the feature's drawn
    edge.
  - A place on empty ground wins. A caption never covers another caption, a building or a fixture while any other choice exists.
    Ground cover (courts, gardens, fields, groves) never blocks. A lane or stream crossed counts as half a building.
  - A place off the edge of the picture is never taken.
  - At the usual gap, a caption must stand nearer its own feature than any other. A place a step out is exempt.
  - When every place at the usual gap is taken, the same places are tried further out, and the nearer free place always wins.
    No leader is drawn out to twice the usual gap. Past that, a leader is drawn to the nearest drawn point of the feature's own
    parts, preferring a closed outline over a stroke and never ending in a dash gap.
  - A caption the map calls for is never left off. With no free ground, it goes where it covers the least.
  - A caption takes its feature's angle and is never drawn upside down.
  - A caption breaks across lines (one line, then two, then three, cut between words where the longest line is shortest, with no
    short word left alone on a line) only when that clears the ground. The wrapped block keeps the single line's place and angle.
  - Captions are placed last, on the finished map.
- Bounds (measured 2026-11-19 by my script on the six sheets' SVG; lengths in px, at the sheets' own scale bars of 3 px to 1 ft,
  each bar drawn 90 px long and labeled 30 ft):

| sheet | captions N | declared multi-line | mean letter size (px) | extent A (px^2) | drawn shapes | indexed (blocking + crossable) | ground (never indexed) |
|---|---|---|---|---|---|---|---|
| county-magistracy-example | 50 | 11 | 8.78 | 852 x 691 = 588732 | 190 | 154 + 0 | 36 |
| hayakawa-magistracy | 63 | 27 | 9.34 | 1082 x 696 = 753072 | 234 | 185 + 11 | 38 |
| ochiba-magistracy | 52 | 16 | 9.68 | 840 x 816 = 685440 | 184 | 162 + 2 | 20 |
| ochiba-roundtrip-test | 46 | 8 | 8.72 | 843 x 691 = 582513 | 165 | 143 + 0 | 22 |
| ubame-magistracy | 66 | 26 | 9.68 | 1054 x 792 = 834768 | 285 | 221 + 6 | 58 |
| hoshigaoka-shrine | 9 | 3 | 7.56 | 560 x 738 = 413280 | 205 | 60 + 2 | 143 |

  The sheets carry 286 captions in all. No sheet carries a `rotate` transform, so no caption is turned. A caption's block is its
  declared lines. Width is 0.52 em a glyph (0.58 bold) plus letter-spacing, and height is 1.15 em a line (a GUESS of the script; see
  the assumptions). The mean block over the six sheets is about 52 x 14 px.

## The algorithm

    once: box each indexed shape (one read per outline segment); file it in the grid's cells its box overlaps; map ids to shapes
          (ground kinds skipped by kind, their geometry never read)
    for each declared caption, in declaration order:
        resolve what it names (one lookup a part); its feature's box; its block (declared lines); gap g = letter height / 2
        1. inside: if the block fits the feature's box, one seat over the middle; clean if the grid finds nothing it overlaps
           but the feature's own parts and shapes wholly containing the feature (a room's building is its ground)
        2. the usual gap: the eight ranked seats at g, in rank order; each tested against the extent (O(1)) before the grid;
           the first clean one is asked the nearness test (the grid inflated by g; a distance per neighbor found); stop at the
           first seat that passes
        3. past the usual gap: a sweep per ranked direction, outward from 1.5g (a step out is at least g/2, so a seat refused
           by the nearness test is not taken again a hair further out) in chunks of one grid cell (c = 48 px; see "The
           sweep's chunk" below), all eight directions advanced
           together: each chunk's strip (the union of the block's positions over the chunk) asked of the grid once; each
           obstacle found gives the interval of offsets where the block overlaps it (O(1)); the direction's intervals sorted and
           merged; its first free offset read off directly. Stop at the first chunk where any direction has one; the nearest
           offset wins, rank breaks ties. Offset <= 2g: no leader; > 2g: a leader to the nearest drawn point over the
           feature's own parts' segments
        4. no clean offset within reach (96g, about 9 chunks): the seat covering least, scored from the hits already found; then two
           and three lines at that place (reading A of the wrap rule, below)
        write the seat, angle, lines and leader; file the caption's block in the grid

Nothing is placed and then moved (S4). Each caption is seated once, every rule is asked before it is placed, and the wrap is
decided before the write.

## Indexes

- Grid: uniform cells of c = 48 px (16 ft) over the sheet's extent. Each blocking or crossable shape is filed by its box in every
  cell the box overlaps, and each placed caption is filed the same way. Ground is never filed (0242: it is not in the way). A
  query reads the cells its box overlaps, reads every entry in them, deduplicates with a visit stamp, and compares each entry's box
  with the query box. The cell size is the measured minimum of total work over 32, 48 and 64 px, with the sweep's chunk one cell at
  each (66,977 / 61,084 / 63,570 on the script's count of every kind but the fixed ones; 75,750 / 66,247 / 67,186 with the build).
  It is also about the mean block (52 x 14 px), the standard choice of a cell about one query's size.
- Cells a query reads: K = (1 + width / c)(1 + height / c) for the query's box. For the block that is K_s. For the nearness
  query (the block grown by g on each side) it is K_n. For a sweep strip it is K_w, the mean over the eight directions of the box
  stretched by one chunk (c) along the direction: two level, two upright and four corner.
- Entries a cell holds: rho = I0 / (A / c^2), the sheet's mean, where I0 is the cells written at the build. Captions stand among
  buildings, so the reads near them run denser than the mean by kappa, measured per sheet (0.79 to 2.26, pooled 1.25). The
  entries a query reads are K x rho_loc, where rho_loc = kappa x rho.

## The sweep's chunk

No rule fixes a step, so the chunk is set from the index and measured against the alternatives, as the cell was. A chunk is how far
one strip query reaches outward. A chunk shorter than a cell makes consecutive strips read mostly the same cells again. A chunk
longer than a cell reads cells past the winning offset, the work S9 forbids. One cell is the index's own unit: each chunk adds
about one new column of cells to the strip. My script's count of every kind but the fixed ones, over the six sheets, with the sweep
from 1.5g to the same reach under each schedule:

| schedule | count | against the rule taken |
|---|---|---|
| one cell (48 px) a chunk from 1.5g: the rule taken | 61,084 | 1.00 |
| 8g a chunk from 1.5g (30 to 39 px on these sheets, about 0.8 cell) | 59,502 | 0.97 |
| 4g a chunk from 1.5g | 62,330 | 1.02 |
| a first strip from 1.5g to 2g, then one cell a chunk | 64,135 | 1.05 |
| a first strip to 2g, then 8g a chunk | 63,840 | 1.05 |
| a first strip to 2g, then half a cell (24 px) a chunk | 65,992 | 1.08 |
| a first strip to 2g, then two cells (96 px) a chunk | 66,233 | 1.08 |
| a first strip to 2g, then 4g a chunk | 68,022 | 1.11 |

- The whole spread is 1.14x, so the chunk is not a large driver of the budget.
- 8g measures 3% cheaper, but on these sheets it is about one cell expressed in letter units. The rule is stated in the index's
  unit so that it carries to a sheet with other letter sizes.
- A first strip ending at 2g, 0242's limit for a seat with no leader, costs 5% more. Of the 65 swept captions, 34 settle within
  2g, but the other 31 pass the strip and pay a second round of eight queries. The leader is decided from the offset found, not
  from the chunk, so the 2g boundary needs no strip of its own.
- Under the rule taken, 56 of the 65 swept captions stop in their first chunk. The farthest (one on hayakawa) stops in its fifth.

## The counted kinds

Each kind is one counter.

- `seat`: one candidate position of the block built and tested against the extent: the inside seat, a usual-gap seat, or one
  direction's first-free offset in one sweep chunk.
- `index_query`: one box asked of the grid.
- `index_cell`: one grid cell read by a query.
- `index_entry`: one entry read from a cell, its box compared with the query's.
- `exact_test`: one outline segment of an entry whose box met the block, tested against the block. A rectangle, circle or line is
  one segment, and a path has one segment per point pair.
- `shape_distance`: one distance from the block to a shape. These are the nearness test's neighbors and the leader's nearest
  point, one per segment of the feature's parts.
- `sweep_interval`: one obstacle's offset interval computed in a sweep strip.
- `sweep_compare`: one comparison sorting, merging or scanning a direction's intervals.
- `leader_crossing`: one test of a leader against what it would cross. No rule owes this test, so its budget is 0 (see the
  assumptions).
- `wrap_cut`: one way of cutting the words into two or three lines considered. Its typical figure is 0 (reading A).
- `index_insert`: one cell written, at the build or when a caption is filed.
- `shape_box`: one outline segment read to box an indexed shape, at the build.
- `name_lookup`: one id filed in the id map, or one part looked up for a caption.
- `write`: one caption field written: center x, center y, anchor, angle, lines, leader.

## The count, factor by factor

The pooled figure is in brackets. Each sheet's own figure is in the tables after this one.

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | N = 50, 63, 52, 46, 66, 9 (286) | every declared caption is placed and none is left off (0242) | 9 (hoshigaoka) to 66 (ubame) |
| inside seats | per item | f_t [0.79] seats and queries | 0242: a feature that holds its block is named on itself, over its middle; tried only where the block fits the feature's box | f_t 0.67 to 0.85 |
| usual-gap seats | per item | (1 - p_in) x m1 [0.53 x 5.33 = 2.81] | 0242: the eight ranked places at the usual gap, the first clean one winning (m1 <= 8); p_in [0.47] are seated inside and never reach them | m1 3.0 to 5.9 |
| usual-gap queries | per item | (1 - p_in) x m1 x (1 - x_off) [2.52] | 0242: a seat off the picture is refused by the O(1) extent test before the grid; x_off [0.10] | x_off 0 to 0.21 |
| nearness queries | per item | q_n [0.50] queries, each K_n cells and nd_q [3.64] distances | 0242: a seat at the usual gap stands nearer its own feature than any other; asked only of a seat already clean | q_n 0.30 to 0.76 |
| sweep strips | per item | p_s x C x 8 [0.227 x 1.25 x 8 = 2.27] queries and seats | 0242: the nearer free place always wins with no step fixed, so the offset is found exactly per direction, from 1.5g; all eight directions advance one chunk (one cell, c = 48 px, from "The sweep's chunk") at a time and stop at the first chunk holding a clean offset (S9) | p_s 0 to 0.30; C 1.0 to 1.64 |
| cells per query (S1) | per query | K_s, K_n, K_w = (1 + w/c)(1 + h/c) on the block, the inflated block and the strip [2.70, 3.38, about 5.7] | the grid at c = 48 px over the block's mean size | K_s 2.1 to 3.0 |
| entries per cell (S1) | per cell | rho_loc = kappa x I0 / (A / c^2) [3.86] | the sheet's index density, kappa its excess where captions stand | 2.51 (hayakawa) to 5.58 (roundtrip) |
| exact tests | per usual-gap query | ex_q [2.86] segments | 0242: the block as drawn is tested against true outlines; only an entry whose box met the block is tested | 0.78 to 3.42 |
| sweep intervals | per strip query | iv_e x the strip's entries [0.40 x 21.3 = 8.4] | one interval per distinct obstacle in the strip, after deduplication and skipping the feature's own parts | 0.36 to 0.48 of entries |
| sweep compares | per interval | cmp_iv [2.28] | the new intervals sorted (n log n with n about 4 kept), merged into the direction's list and scanned to the first free offset | 1.69 to 2.49 |
| leader distances | per item | p_L x parts x 1 segment [0.108 x 2.3] | 0330: the nearest drawn point over the feature's own parts | p_L 0 to 0.18 |
| leader crossings | per item | 0 | no rule in 0242 or 0330 owes it | not applicable |
| wrap cuts | per item | 0 typical | reading A: the declared block is placed if it clears anywhere within reach, and 2 and 3 lines are tried only on the cover-least branch, which no caption reached | see the assumptions |
| cover-least fallback | per item | 0 typical | 0242 "never left off"; 0 of 286 captions reached it; priced in the assumptions | not applicable |
| angle | per item | 0 | no sheet carries a turned feature; a turned one adds a frame change per seat and a 4-axis outline test in place of a box test | not applicable |
| caption filed | per item | K_s cells written [2.6] | 0242: a later caption never covers this one | 2.1 to 3.0 |
| names resolved | per item | parts [1.4 to 2.5] lookups | what the caption names: its `data-names` ids or its group's shapes | up to 35 parts (ubame's compound shrine) |
| writes | per item | 6 | center x, center y, anchor, angle, lines, leader | always 6 |
| index build | once | I0 = the cells each indexed shape's box overlaps, summed: 619, 1034, 940, 635, 1522, 413 | 0242: any built thing or crossable way may block, so each is filed once | a long wall line spans many cells |
| shape boxes | once | the indexed shapes' segments: 155, 210, 169, 152, 235, 68 | each outline read once to box it; ground skipped by kind, so hoshigaoka's 6,173 ground segments are never read | not applicable |
| id map | once | the shapes carrying an id: 103, 47, 40, 91, 50, 152 | one filing each | not applicable |
| slack | per item, on the search kinds | 1.5 | caption order, which no rule fixes: my script's five orders (declared, reversed, inside first, small first, big first) spread a sheet's count by at most 1.39 (hayakawa), and the six summed by at most 1.09 | not on the fixed kinds |

So, per sheet: the shape boxes, plus the id map, plus I0, plus N x (search x 1.5 + fixed). Here search is seats + queries + cells +
entries + exact tests + distances + sweep intervals + sweep compares, and fixed is captions filed + lookups + 6 writes.

The budget takes wrap reading A (assumption 3): the declared block is seated by the search, and 2 and 3 lines are tried only on the
cover-least branch. Reading B would add 1.22x to the search work (assumption 3).

- pruning: the search stops at the first clean candidate in the order inside, then the usual gap by rank, then the sweep's first
  chunk holding any clean offset. No seat past the winner's chunk is built and no cell past it is read (S9). Only the grid build
  touches a whole set, the sheet's indexed shapes, because any of them may block some caption and each is filed once. A query
  reads only the cells under its box. Nothing scores, sorts or paints every member of a set that grows with the sheet.

## The factors on each sheet

Geometry, from the SVG (w and h are the mean block in px, g the mean gap, parts the mean shapes a caption names):

| sheet | N | w | h | g | rho | kappa | rho_loc | K_s | K_n | K_w | parts |
|---|---|---|---|---|---|---|---|---|---|---|---|
| county-magistracy-example | 50 | 42.6 | 12.6 | 4.39 | 2.42 | 1.75 | 4.23 | 2.38 | 2.99 | 5.24 | 1.36 |
| hayakawa-magistracy | 63 | 55.4 | 16.2 | 4.67 | 3.16 | 0.79 | 2.51 | 2.88 | 3.60 | 6.00 | 2.48 |
| ochiba-magistracy | 52 | 52.8 | 14.7 | 4.84 | 3.16 | 0.99 | 3.13 | 2.74 | 3.47 | 5.80 | 2.12 |
| ochiba-roundtrip-test | 46 | 44.1 | 11.8 | 4.36 | 2.51 | 2.22 | 5.58 | 2.39 | 3.00 | 5.27 | 1.37 |
| ubame-magistracy | 66 | 61.3 | 15.9 | 4.84 | 4.20 | 1.05 | 4.41 | 3.03 | 3.80 | 6.24 | 2.44 |
| hoshigaoka-shrine | 9 | 33.7 | 11.3 | 3.78 | 2.30 | 2.26 | 5.20 | 2.10 | 2.59 | 4.80 | 2.33 |

Each branch's share, from my script running the algorithm above on the sheet's input (S8: the mean the sheet shows):

| sheet | f_t | p_in | m1 | x_off | q_n | p_s | C | p_L | ex_q | nd_q | iv_e | cmp_iv |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| county-magistracy-example | 0.82 | 0.46 | 4.67 | 0.048 | 0.52 | 0.18 | 1.00 | 0.08 | 1.66 | 4.65 | 0.476 | 1.69 |
| hayakawa-magistracy | 0.794 | 0.508 | 5.35 | 0.145 | 0.302 | 0.222 | 1.64 | 0.175 | 3.33 | 3.74 | 0.450 | 2.49 |
| ochiba-magistracy | 0.846 | 0.577 | 5.41 | 0.21 | 0.346 | 0.212 | 1.27 | 0.077 | 2.72 | 3.44 | 0.423 | 2.39 |
| ochiba-roundtrip-test | 0.804 | 0.413 | 5.89 | 0.094 | 0.543 | 0.304 | 1.21 | 0.152 | 2.97 | 3.36 | 0.358 | 2.27 |
| ubame-magistracy | 0.742 | 0.394 | 5.58 | 0.058 | 0.758 | 0.258 | 1.06 | 0.076 | 3.42 | 3.38 | 0.358 | 2.33 |
| hoshigaoka-shrine | 0.667 | 0.556 | 3.00 | 0 | 0.444 | 0 | 0 | 0 | 0.78 | 2.50 | 0 | 0 |

The typical operations per caption, the factors multiplied out:

| sheet | seats | queries | cells | entries | exact | near dist | leader dist | intervals | compares | search | filed + lookups + writes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| county-magistracy-example | 4.78 | 5.18 | 16.77 | 70.9 | 5.34 | 2.42 | 0.11 | 15.20 | 25.71 | 146.4 | 9.74 |
| hayakawa-magistracy | 6.35 | 6.27 | 27.38 | 68.8 | 10.14 | 1.13 | 0.43 | 19.83 | 49.28 | 189.6 | 11.36 |
| ochiba-magistracy | 5.29 | 5.15 | 20.97 | 65.6 | 7.21 | 1.19 | 0.16 | 16.51 | 39.46 | 161.5 | 10.86 |
| ochiba-roundtrip-test | 7.22 | 7.43 | 26.61 | 148.6 | 11.67 | 1.83 | 0.21 | 31.12 | 70.58 | 305.3 | 9.76 |
| ubame-magistracy | 6.30 | 6.86 | 28.38 | 125.1 | 13.42 | 2.56 | 0.18 | 21.49 | 50.01 | 254.3 | 11.47 |
| hoshigaoka-shrine | 2.00 | 2.44 | 5.35 | 27.8 | 1.56 | 1.11 | 0 | 0 | 0 | 40.3 | 10.43 |

Each sheet carries its own shares rather than pooled ones. With the six sheets' pooled shares, the formula under-predicts my
script's count on `ochiba-roundtrip-test` by 1.8x, past the slack. Its captions stand among small dense rooms, and 30% of them
need the sweep.

All the tables were measured with the sweep as the pseudocode states it: from 1.5g, one cell a chunk. The formula at slack 1 is set
beside my script's direct count of the same kinds on each sheet: 8684 / 8516, 13951 / 15188, 10112 / 9305, 15371 / 15365, 19348 /
20495, 1090 / 1041. That is 68,556 against 69,910 summed. This is not an independent check. The
shares and kappa come from the same script run, so the agreement within 10% shows only that the factorization multiplies back to
the count it was read from.

## Totals

Each line is shape boxes + id map + I0 + N x (search x 1.5 + fixed).

- at county-magistracy-example: 155 + 103 + 619 + 50 x (146.4 x 1.5 + 9.74) = 12344
- at hayakawa-magistracy: 210 + 47 + 1034 + 63 x (189.6 x 1.5 + 11.36) = 19924
- at ochiba-magistracy: 169 + 40 + 940 + 52 x (161.5 x 1.5 + 10.86) = 14311
- at ochiba-roundtrip-test: 152 + 91 + 635 + 46 x (305.3 x 1.5 + 9.76) = 22393
- at ubame-magistracy: 235 + 50 + 1522 + 66 x (254.3 x 1.5 + 11.47) = 27740
- at hoshigaoka-shrine: 68 + 152 + 413 + 9 x (40.3 x 1.5 + 10.43) = 1271
- the six sheets: 12344 + 19924 + 14311 + 22393 + 27740 + 1271 = 97983

That is about 343 operations a caption at the slack, and about 240 at slack 1. Both are far under the reference's 4,000 a thing
placed: a caption has at most eight ranked places a ring and a few neighbors under each.

## The budget by counted kind

Each cell is the kind's per-caption figure x N, with the slack on the search kinds, rounded per cell.

| kind | county-magistracy-example | hayakawa-magistracy | ochiba-magistracy | ochiba-roundtrip-test | ubame-magistracy | hoshigaoka-shrine | all six |
|---|---|---|---|---|---|---|---|
| seat | 358 | 600 | 413 | 498 | 624 | 27 | 2520 |
| index_query | 388 | 593 | 402 | 513 | 679 | 33 | 2608 |
| index_cell | 1258 | 2587 | 1636 | 1836 | 2810 | 72 | 10199 |
| index_entry | 5318 | 6502 | 5117 | 10253 | 12385 | 375 | 39950 |
| exact_test | 400 | 958 | 562 | 805 | 1329 | 21 | 4075 |
| shape_distance | 190 | 147 | 105 | 141 | 271 | 15 | 869 |
| sweep_interval | 1140 | 1874 | 1288 | 2147 | 2128 | 0 | 8577 |
| sweep_compare | 1928 | 4657 | 3078 | 4870 | 4951 | 0 | 19484 |
| leader_crossing | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| wrap_cut | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| index_insert | 738 | 1215 | 1082 | 745 | 1722 | 432 | 5934 |
| shape_box | 155 | 210 | 169 | 152 | 235 | 68 | 989 |
| name_lookup | 171 | 203 | 150 | 154 | 211 | 173 | 1062 |
| write | 300 | 378 | 312 | 276 | 396 | 54 | 1716 |
| total | 12344 | 19924 | 14314 | 22390 | 27741 | 1270 | 97983 |

The column totals differ from the Totals lines by the per-cell rounding.

## Growth

On a sheet, the work grows linearly in the captions N. Each caption's cost is set by the grid's local density (rho_loc) and its
block size, not by N, and the build is linear in the indexed shapes. Across the six sheets, the per-caption cost ranges from 40
(hoshigaoka, sparse) to 305 (roundtrip, captions among small dense rooms). That spread is density, not size. A log-log fit of
total against N across the sheets (1.47) mixes the two and is not a growth exponent. Per S6, the bound is per caption: at a fixed
density, twice the captions is twice the work.

## How far over is "far over"

S10 applies. A placer counting up to twice its sheet's line, with the excess named and reasonable, is LEEWAY. Past twice a sheet's
line or twice the sum, it is OVER. For scale, on the same sheets:

- Stepping rings at a fixed step of g with no sweep counts about 1.4x the index entries read (38,350 against 28,257 on my script), more at a finer step.
- A placer without the index tests every seat against every indexed shape and placed caption. On ubame that is about 66 x 6.3 x
  (227 + 33) = 108,000 tests against a line of 27,740, about 4x, and it grows as N x shapes.
- Sweeping all eight directions out to the reach for every caption, instead of stopping at the first chunk with a clean offset,
  costs about 72 strip queries a caption, about 4,100 a caption, which is about 12x.

## Cheaper algorithms considered

- sweep: used past the usual gap. Per direction, the obstacles' offset intervals give the first free offset exactly. This replaces
  stepped rings, whose count depends on a step no rule fixes and which my script measured at about 1.4x the entries read at a step of g.
- grid or spatial index: used. Uniform 48 px cells, measured as the cheapest of 32, 48 and 64 px. An R-tree is not used: 60 to 230
  indexed shapes a sheet at 2.5 to 6 entries a cell read already bound each query.
- priority queue: not used. The eight directions advance together a chunk at a time, and the first chunk holding a clean offset
  ends the search, so a heap over eight would be no cheaper than scanning them.
- incremental update: used. Each placed caption is filed into the grid (K_s cells) with no rebuild. A direction's intervals carry
  across chunks, and only the new ones are sorted and merged in.
- memoizing what a scan does not change: used. The feature's box and parts are resolved once a caption, the extent's offset
  limits once a direction, and the grid is built once a sheet.

## Assumptions, and the ones least sure

Each assumption is labeled as in `research/` and names the rule it reads.

1. **Which shapes block (least sure).** CONVENTION of this derivation, reading 0242's "never on another caption or a building"
   and "ground cover never blocks". Courts, gardens, yards, practice grounds, clearings, groves and the sheet's furniture
   (`data-kind="-"`) are ground. Roads, approaches, footpaths, rivers and revetments are crossable at half a building and count
   as not clean. Every other kind blocks, walls and doors included. A shape that wholly contains the caption's feature, such as a
   room's building, is its ground, not an obstacle. A placer that files ground too would read more entries. A placer that treats
   doors or interior lines as ground would read fewer and seat more captions inside.
2. **The inside seat is the middle only (least sure).** Reading 0242's "over its middle when that is free" as one seat, failing
   to the beside search. "Fits" is tested against the box around all the feature's parts, not its outline, so an L-shaped or
   multi-part feature can pass a fit its outline would refuse. Under that reading 135 of the 227 captions whose block fits their
   feature are seated inside. A reading
   that searches elsewhere inside the feature adds a few seats for each of the other 92 and saves their beside search, so the
   effect on the total is about neutral.
3. **Where the wrap is tried (least sure).** Reading A, budgeted: "drawn on one line if that clears the sheet", with the wrapped
   block keeping "the place the single line would have had". The declared block is placed by the search, and 2 and 3 lines are
   tried only where nothing clears within reach. Reading B tries 2 and 3 lines at every rejected seat and each sweep direction,
   and my script measured it at 1.22x the search work over the six sheets, inside the slack summed but not on every sheet.
4. **Text width (least sure).** The script sets a glyph at 0.52 em (0.58 bold) and a line at 1.15 em, a GUESS standing in for the
   face's real metrics. At 0.85x and 1.15x those widths, the script's count over the six sheets is 0.82x and 1.24x.
5. **The sweep's start and reach.** GUESS knobs, since no rule fixes a step or a reach. The chunk is set from the index and
   measured in "The sweep's chunk".
   - The sweep starts at 1.5g, a minimum step-out of g/2. Started at g, it let 27 of the 65 swept captions sit within g/4 of the
     usual gap, which dodges the nearness test that 0242 holds the usual gap to.
   - The reach is 96g (about 450 px or 150 ft, about 9 chunks), past which the cover-least branch runs. No swept caption came
     near it: the farthest stops in its fifth chunk.
6. **The cover-least fallback is absent.** 0 of 286 captions reached it, so it is budgeted at 0 (S8). If one does, it costs about
   72 strip queries x (1 seat + about 6.6 cells + about 21 entries + about 8.4 intervals + about 19 compares + the query) = about
   4,100, and up to about 12,400 with both wrap layouts under reading A. One such caption could take a small sheet past its line,
   so the audit should name it as the excess rather than call it waste.
7. **Leader crossings are not owed.** 0330 fixes only where a leader ends (the nearest drawn point, a closed outline before a
   stroke, never a dash gap). No rule says a leader avoids a caption or a building, so `leader_crossing` is budgeted at 0. If the
   GM rules one owed, it costs the cells along each leader x their entries: about 2 cells x 4 entries a leader, about 250 over the 31 leaders of the
   six sheets.
8. **Caption order.** No rule fixes it. Declaration order is counted, and five orders spread a sheet by at most 1.39x (the six summed by 1.09x). This is the
   slack's one source.
9. **The two seated sheets.** `county-magistracy-example` and `ochiba-roundtrip-test` hold their captions already seated, and the
   script ignores those seats. I checked that no element on either sheet is labeled a leader. An unlabeled thin line that is in
   fact a leader would have been filed as an obstacle under its group's kind.
10. **No repair.** Nothing is placed and then moved or dropped, so the budget for moves and drops is 0 (S4).
