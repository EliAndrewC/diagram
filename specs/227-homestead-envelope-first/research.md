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

## R2 - the after

(filled at T04/T06)

The gardens BEFORE (the pool at feature 226's landing, the bed forms read from each house's `geom.gardens`: two beds
on opposite walls = flanking, one above the other = stacked, side by side otherwise):

| | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| gardens before (houses / with a garden / one bed / flanking / stacked / side by side) | 15 / 15 / 13 / 0 / 0 / 2 | 20 / 20 / 17 / 2 / 0 / 1 | 16 / 16 / 11 / 2 / 1 / 2 | 12 / 12 / 10 / 2 / 0 / 0 | 19 / 19 / 18 / 0 / 1 / 0 |
