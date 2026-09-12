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

## R2 - the after (2026-09-12, the pool at the landing; `meta.seat_search`, the manifests)

| per house (pool, the kept roll) | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| households seated (roll attempt) | 15/15 (1) | 20/20 (1) | 16/16 (1) | 12/12 (1) | 19/19 (5) |
| placer calls | 19 | 26 | 35 | 16 | 25 |
| ENVELOPE TESTS per placer call (the union, the boxes, the moves) | 2.9 | 2.8 | 4.2 | 2.2 | 3.5 |
| part layouts judged per call | 2.9 | 3.0 | 2.0 | 3.2 | 3.0 |
| RECTANGLE TESTS per house, every test counted (226: 113-387) | 7 | 7 | 18 | 6 | 9 |
| candidates per house (226: 1.6-7.0) | 1.3 | 1.3 | 2.2 | 1.3 | 1.3 |
| front row seated / rounds behind | 7 / 2 | 9 / 2 | 2 / 5 | 6 / 2 | 7 / 3 |
| nearest house to the field outline, px / houses within 165 | 44 / 5 | 47 / 8 | 118 / 5 | 37 / 9 | 60 / 6 |
| drawn aspect (rolled shape, honored?) | 2.42 (crescent, yes) | 2.88 (elongated, yes) | 2.02 (round, no) | 2.61 (round, no) | 1.71 (round, yes) |
| windbreak clumps / copse clumps | 163 / 82 | 219 / 119 | 34 / 95 | 172 / 32 | 231 / 202 |
| gardens: houses / with a garden / one bed / flanking / stacked / side by side | 15 / 15 / 12 / 2 / 0 / 1 | 20 / 20 / 17 / 3 / 0 / 0 | 16 / 16 / 13 / 2 / 1 / 0 | 12 / 12 / 11 / 1 / 0 / 0 | 19 / 19 / 16 / 1 / 0 / 2 |

Two counters, named apart (the review's nitpick) - and one cost outside both: the front row's ground push asks the
boundary once per front seat at proposal time, before any placer call, and is not in `meta.seat_search`. ENVELOPE TESTS are the rectangles the placer asks per call - the
union, then each configuration's own box and its one move - at most nine, 4.5-5.1 measured; RECTANGLE TESTS per house
count every rectangle any test asked, the proposer's ground push included, and are the figure to set against 226's
113-387. A placer call is a fixed handful of rectangles now against 26 to 60 positions of the full battery before (R1),
and no call walks.

What the numbers say. Every pool map seats its quota; four on the first roll, Sawada on its fifth (the driver's
re-roll after stranded farmhouses, a pre-existing mechanism - each earlier roll seated 19 and stranded one). The
48-seed cohort passes 48 of 48 with `households_seated` and `farmhouses_reach_a_way`. The dike mosaic (Kuwabata) is
the hard case throughout: its dike heads offer two front seats, refused until the seat was pushed past the dike's bank
by the outline's measured reach plus a footpath's room; its cluster stands 118 px from the crop's outline
(the yard between the house and the bank, the bank itself, the path's room), against 63 under feature 226 and the 60 px
the reference roll is held to - the polder's geometry, not the search, and the GM's to judge; its windbreak seats
34 clumps where the houses now stand in the ground it held. Every homestead has its garden; 13 of 82 split, in three
forms (13 of 82 before).

The rolled shapes: three of five bind inside their band; Mizuguchi's round draws 2.61 against 1.0-2.0 and
Kuwabata's 2.02 - D8's measured factor, the GM's call at acceptance (three of five were unhonored at 226's landing).

The lessons, each a cohort seed or a review finding, recorded at the point of change in `homesteads/stages.py`:
a placer that takes the seat it is given needs seats that fit by construction (the ranks behind the standing
houses, not a deduped cloud); the front row's standoff counts the homestead's core toward the chord (the
garden's side is chosen later); where the outline lies beyond the chord the seat is pushed once by the measured
reach plus a footpath's room; the along-the-field seats are a fallback, or the clusters string out; the rescue
offers them first.

The gardens BEFORE (the pool at feature 226's landing, the bed forms read from each house's `geom.gardens`: two beds
on opposite walls = flanking, one above the other = stacked, side by side otherwise):

| | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| gardens before (houses / with a garden / one bed / flanking / stacked / side by side) | 15 / 15 / 13 / 0 / 0 / 2 | 20 / 20 / 17 / 2 / 0 / 1 | 16 / 16 / 11 / 2 / 1 / 2 | 12 / 12 / 10 / 2 / 0 / 0 | 19 / 19 / 18 / 0 / 1 / 0 |
