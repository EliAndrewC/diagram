# Research - 227 the homestead's envelope first, and the page from the code

## R1 - where a placer call's positions come from (2026-09-12, a temporary probe in `_place_bundle_nucleated` and `_slide_nuc`, one roll each)

| | Inashiro spec (seed 4) | Kuwabata spec (seed 21) |
|---|---|---|
| placer calls | 23 | 19 |
| houses seated | 15 | 16 |
| positions in the spiral | 699 | 339 |
| positions sliding toward the paddy | 99 | 110 |
| positions sliding along the neighbors | 32 | 49 |
| rectangles per position | 3.5 | 4.2 |

On the Inashiro roll 8 of 23 calls seated nothing and each walked all 73 offsets with the full battery; the 15
that seated used about 8 positions each. The pre-test (feature 226) asks the SMALLEST house's box; the placer
asks the house, the yard, a kura and a garden on one of four sides as separate rectangles, plus the eave gap,
the wall rule and the sun corridors - so a seat the house fits and the homestead does not costs 73 offsets
before it is refused. The 2 px slides: no recorded reason (commit ed0e884e); the stop is whichever of the rules
fires first and stepping avoided computing the clearance to each.

## R2 - the after (2026-09-12, the pool re-rolled under the envelope-first placer; `meta.seat_search`)

| per house (pool, first roll) | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| households seated | 15/15 | 20/20 | 16/16 | 12/12 | 19/19 |
| placer calls | 28 | 41 | 58 | 27 | 36 |
| rectangles per placer call (the union, the boxes, the moves) | 5.1 | 4.5 | 5.1 | 4.6 | 4.5 |
| part layouts judged per call | 1.9 | 1.9 | 1.3 | 2.5 | 2.1 |
| rectangles judged per house (226: 113-387) | 19 | 19 | 37 | 20 | 17 |
| candidates per house (226: 1.6-7.0) | 1.9 | 2.0 | 3.6 | 2.2 | 1.9 |
| front row seated / rounds behind | 8 / 1 | 9 / 2 | 0 / 4 | 5 / 2 | 6 / 2 |
| drawn aspect (rolled shape, honored?) | 2.95 (crescent, yes) | 2.67 (elongated, no) | 2.4 (round, no) | 2.22 (round, no) | 1.57 (round, yes) |
| gardens: houses / with a garden / one bed / flanking / stacked / side by side | 15 / 15 / 11 / 1 / 0 / 3 | 20 / 20 / 17 / 2 / 0 / 1 | 16 / 16 / 14 / 0 / 1 / 1 | 12 / 12 / 7 / 2 / 2 / 1 | 19 / 19 / 17 / 0 / 1 / 1 |

What the numbers say. A placer call is a fixed handful of rectangles now - the union of the configurations, then
each configuration's own box and at most one computed move each - against 26 to 60 positions of the full battery
per call before (R1); rectangles judged per house fell from 113-387 to 16-37, and no call walks. The dike mosaic
(Kuwabata) still refuses most seats between its ponds - 3.6 candidates per house against 1.9-2.2 elsewhere - which
is the ground, not the search: every seat there is at most nine rectangles. Every pool map seats its quota on the
first roll; the 48-seed cohort passes 48 of 48 (`households_seated` and `farmhouses_reach_a_way`), after two seeds
taught the proposer what a placer without a spiral needs - seed 25 the per-configuration fallback, seed 8 the ranks
proposed behind every standing house with the sun corridor in the rank step. Every homestead has its garden; the
bed splits are 13 of 82 before and 16 of 82 after, in three forms both times.

The rolled shapes: two of five bind inside their band, three stand within 0.4 of it (Kuwabata 2.4 on a round's
1.0-2.0, Mizuguchi 2.22, Kashikawa 2.67 on an elongated's 2.8-12) - D8's measured factor, and the GM's call at
acceptance (three of five were unhonored before this feature too, at 226's landing).

The gardens BEFORE (the pool at feature 226's landing, the bed forms read from each house's `geom.gardens`: two beds
on opposite walls = flanking, one above the other = stacked, side by side otherwise):

| | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| gardens before (houses / with a garden / one bed / flanking / stacked / side by side) | 15 / 15 / 13 / 0 / 0 / 2 | 20 / 20 / 17 / 2 / 0 / 1 | 16 / 16 / 11 / 2 / 1 / 2 | 12 / 12 / 10 / 2 / 0 / 0 | 19 / 19 / 18 / 0 / 1 / 0 |
