# Research: grow outward, never restart (feature 318)

Probes run from the session's scratchpad (`spread318.py`, `order318.py`, `refusals318.py`, `prof318.py`), each on the clone and on
main's detached worktree at the 318-start commit, CPU seconds of the homestead stage (`time.process_time`), one process at a time,
all on 2026-10-03 on this host (one-shot measurements, not re-run; each figure is the probe's single run).

## R1 - Nearest the field first needs every direction offered at once (plan D4 amended)

Reference spec (Inashiro's: nucleated, pond sink) at 40 households, the bookend seeds; mean / farthest house-to-field distance
(ft, to the field's facing chains), homestead stage seconds:

| tree | seed 4 | seed 25 | seed 39 | seed 47 | stage s (sum) |
|---|---|---|---|---|---|
| main (700 ft reach, radius bound, 3 levels) | 443 / 698 | 421 / 691 | 429 / 692 | 416 / 698 | 21.5 |
| no reach, 3 levels (8, 12, 16 directions) | 637 / 978 | 400 / 653 | 585 / 919 | 442 / 733 | - |
| no reach, 16 directions x rings 1.0-2.0 in quarters | 405 / 692 | 361 / 565 | 386 / 619 | 352 / 596 | 44.6 |
| no reach, 12 directions x 1.0 / 1.5 / 2.0 | 429 / 689 | 362 / 611 | 421 / 647 | 374 / 657 | 29.6 |
| no reach, 16 directions x 1.0 / 1.5 / 2.0, jitter unscaled | 370 / 604 | 389 / 630 | 425 / 634 | 339 / 539 | 31.2 |
| **chosen: 16 directions x 1.0 / 1.5 / 2.0, jitter scaled** | **384 / 607** | **367 / 580** | **394 / 605** | **355 / 539** | **32.7** |
Observed 2026-10-03, method: `spread318.py` over the four cells, one process at a time on each tree.

Why the three levels failed: the heap pops the nearest-the-field seat first (popped keys 92, 108, 108, 119 ft on seed 4), but those
seats are refused, and with no radius the eight-direction level never runs dry - houses seated 231, 364, 511, ... 957 ft from
the field in turn. Main reached its near-field gaps only after its radius emptied level 0 and the 12- and 16-direction levels ran.
Observed 2026-10-03, method: `order318.py` (the heap's popped keys and each seated house's field distance, in order).

Every chosen cell seats on margin 1 at growth level 0; no house taken back; aspects 2.84-4.06, each inside its declared shape's band
(crescent or elongated); built share 0.238-0.313 (main 0.224-0.318).

## R2 - Seed 18 and the small seeds

| cell | tree | margin | farthest from first house | mean / farthest to field | built share | stage s |
|---|---|---|---|---|---|---|
| cohort 18 (15 hh) | main | 12 | 640 | 447 / 696 | 0.237 | 18.67 |
| cohort 18 | chosen | 1 | 686 | 562 / 817 | 0.361 | 2.39 |
| ref 15 hh seed 8 | main | 1 | 534 | 354 / 671 | 0.289 | 1.46 |
| ref 15 hh seed 8 | chosen | 1 | 627 | 241 / 397 | 0.282 | 2.64 |
| cohort 7 (17 hh) | main | 1 | 556 | 442 / 658 | 0.280 | 1.19 |
| cohort 7 | chosen | 1 | 747 | 282 / 434 | 0.229 | 2.10 |

Seed 18 is the spec's narrow strip: on its first margin it grows along and away from the field (farthest 817 ft), where main threw
eleven margins away and seated the twelfth. The row villages (cohort 3, 11) are unchanged (the growth does not seat them). Observed 2026-10-03, method:
`spread318.py`.

## R3 - Where the small seeds' extra time goes

Reference 15 households seed 8, the offers the growth made and why each was refused:

| tree | offers | seated | envelope or seat refused | refused before the corridor (wood, sun) | no corridor | refused after |
|---|---|---|---|---|---|---|
| main | 71 | 15 | 28 | 15 | 13 | 0 |
| chosen | 202 | 15 | 108 | 40 | 34 | 6 |

The seats nearest the field are more often hemmed in by the paddy and the standing houses; the envelope refusals are cheap, and
the cost is the corridor searches that find no way (2.5 s of `access_corridor` across 238 calls). The cost is the order the GM
asked for (the nearest-the-field option tried first); it is measured at the bookends and carried through the perf records. Observed 2026-10-03, method: `refusals318.py` and
`prof318.py` (cProfile of the homestead stage).

## R4 - Option A, the ways laid in the gaps (Amendments 2 and 3), the scratch prototype

Observed 2026-10-03, method: the scratch prototype (in-memory patches of the clone at a241afe7f: no per-seat search, the 20 ft
gap, the ring tie-break, a gap pass at the seating's end), each stage's process time on the reference at 15 households (seeds 4,
25, 39, 47) and cohort seeds 2, 7, 8, 9 and 10.
- Laid after the seating by the corridor router as it is (one search per house against the growing tree): 2-9 houses a map
  unreached. The grid found a route from both doors every time; the taut pull refused it - its own beds and fixtures, which the
  router's grid does not keep off, and at most 5 legs. Laying in the seating's order, or 9 legs, mended one map of nine.
- A gap pass (one flood over lane ground from the way out, a local way out of each homestead, traced along the flood): the
  failures were then the whole tree's lane law - the doubled band (`tree_shadows`) in 10 of 14, a new way running beside an
  older one in the same gap. Joining an older way at a T within 25 ft mended them.
- The raster's open test must be the corridor's own (the site's uncertain cells asked exactly): with the free-ground raster's
  surely-taken cells alone, the taut pull refused a leg in 8 of 18 failures.
- Padding the homestead boxes by most of a cell closed the gaps (20 ft gap less two 7 ft half-widths leaves 6 ft): every house
  but a few found no way out. Unpadded, with no diagonal cutting a blocked corner: 5 of 9 maps reached every house.
- Up to six distinct exits a house: 6 of 9. Cell 5 px: 8 of 9 (cell 6 px: 7 of 9; 4 px: 6 of 9 and 0.3 s more).
- Cost, homesteads stage summed over the nine: main 9.85 s; the tie-break alone 9.96 s; option A 14.38 s (the pass 0.5-0.9 s a
  map: the flood about 0.4, the site's uncertain cells 0.15, the local searches and the lane law 0.2). The per-seat search it
  replaces was about 0.25 s a map on main; the +11.9% of the first amendment was the field-first order, not the search.
