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
| households seated (roll attempt) | 15/15 (1) | 20/20 (1) | 16/16 (1) | 12/12 (1) | 19/19 (1) |
| placer calls | 21 | 27 | 25 | 15 | 25 |
| ENVELOPE TESTS per placer call (at most nine) | 2.6 | 4.2 | 5.0 | 3.5 | 3.1 |
| RECTANGLE TESTS per house, every test counted (226: 113-387) | 7 | 11 | 16 | 9 | 8 |
| candidates per house (226: 1.6-7.0) | 1.4 | 1.4 | 1.6 | 1.2 | 1.3 |
| front row seated / rounds behind | 7 / 2 | 9 / 2 | 2 / 5 | 6 / 2 | 7 / 3 |
| nearest house to the field outline, px / within 165 | 44 / 7 | 47 / 12 | 135 / 3 | 37 / 7 | 60 / 6 |
| homestead-to-homestead GAP, median / worst px | 31 / 106 | 8 / 32 | 4 / 19 | 19 / 68 | 20 / 161 |
| drawn aspect (rolled shape, honored?) | 2.49 (crescent, yes) | 2.79 (elongated, no) | 1.86 (round, yes) | 2.31 (round, no) | 1.43 (round, yes) |
| windbreak / copse clumps | 197 / 88 | 240 / 110 | 112 / 56 | 168 / 20 | 249 / 235 |
| gardens split into two beds / garden sides | 2 / {'W': 10, 'S': 2, 'E': 3} | 3 / {'E': 15, 'W': 2, 'S': 3} | 2 / {'W': 6, 'E': 10} | 2 / {'S': 2, 'W': 4, 'E': 6} | 4 / {'E': 9, 'W': 9, 'S': 1} |

Two counters, named apart (the review's nitpick) - and one cost outside both: the front row's ground push asks the
boundary once per front seat at proposal time, before any placer call, and is not in `meta.seat_search`. ENVELOPE
TESTS are the rectangles the placer asks per call (the union, then each configuration's own box and its one computed
move); RECTANGLE TESTS per house count every rectangle any test asked and are the figure to set against 226's
113-387. A placer call is a fixed handful of rectangles against 26 to 60 positions of the full battery before (R1),
and no call walks.

**Is the cluster one settlement? Read the FOOTPRINTS.** The review's second pass measured connected components on a
165 px CENTRE link and read the pool as fragmented. This engine's own rule is that a gap verdict reads footprints
and never centres (`dev/placement.md`, "CENTER vs FOOTPRINT"), and the houses are now separated by exactly the yards
and gardens between them: homestead to homestead the median gap is 4 to 31 px. Kashikawa's is 8 px - the
fabric is continuous. What the centre link was measuring is a rank standing one homestead's depth behind another,
which is what a rank IS.

**The gardens.** Every homestead has one; 13 of 82 split into two beds, in three forms; the sides are
{'W': 31, 'S': 8, 'E': 43} pool-wide against 0 west before the tie-break was made positional (main: 6 west of 82).

**What the reviews changed, in order.** First pass: the reed-marsh toe was not in the boundary and three maps
recorded a structure inside it; the belt's southern sun strip was 22 px against the 39 ft a farmhouse owes the same
bed. Second pass: the notice board's frame test admitted a board 30 px outside the view and Sawada's shipped
undrawn; the anchored board ranked by distance to its anchor alone; the garden's west side had gone to zero; the
ranks compounded a step behind whoever stood in front; the pitch fell into one bucket. Each is fixed at the point of
change. Cohort seed 39 then stranded a farmhouse because the ranks abutted at four pixels and no alley could thread
them - the rank step leaves `MIN_WEB_GAP` now, and the cohort is 48 of 48.

**The bookends** (`make perf LABEL=227-start` in a worktree at origin/main, `227-end` at the landing): total 29.4 ->
22.6 s (-23.1%), every seed faster (4 -12.9%, 25 -45.7%, 39 -18.0%, 47 -8.9%), band 0, nothing owed.

A first `227-end` was taken one commit EARLY and read band 1 on seed 4 (+8.1%, the notice stage +1.1 s). The
explanation written for it credited the board's new frame test - and the `perf-audit` agent refused it as
INCONSISTENT on the ground that the diff between the two bookends is docstrings only: the footprint inset and the
band-then-traffic reordering both land in the commit AFTER the measured end state, so the explanation credited a fix
that postdated its own measurement, and the 1.1 s it described was the per-candidate traffic count that the same
commit removed. Re-taken at the reviewed commit the pair is band 0. The lesson is the agent's: a bookend binds to a
commit, so take the end one AFTER the last change it is meant to measure - and a band explained by a fix that is not
in the measured range is not explained at all.

The gardens BEFORE (the pool at feature 226's landing, the bed forms read from each house's `geom.gardens`: two beds
on opposite walls = flanking, one above the other = stacked, side by side otherwise):

| | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| gardens before (houses / with a garden / one bed / flanking / stacked / side by side) | 15 / 15 / 13 / 0 / 0 / 2 | 20 / 20 / 17 / 2 / 0 / 1 | 16 / 16 / 11 / 2 / 1 / 2 | 12 / 12 / 10 / 2 / 0 / 0 | 19 / 19 / 18 / 0 / 1 / 0 |
