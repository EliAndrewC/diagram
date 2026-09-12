# Research - 226 the site boundary, and the seats proposed from it

## R1 - the before (2026-09-12, the per-house profile in dev/performance.md)

| per house | inashiro | kuwabata | sawada |
|---|---|---|---|
| candidate seats proposed (`try_place`) | 3 | 10 | 2 |
| positions tested (`_fits_any_side`) | 419 | 1,686 | 363 |
| rectangles tested (`_rect_blocked`) | 1,090 | 2,755 | 848 |
| chord side tests (`chain_violated`) | 7,778 | 13,075 | 6,424 |
| hard-ground scans (`_hard_clear`) | 1,234 | 2,090 | 1,006 |
| rotated-corner gap tests (`poly_gap`) | 396 | 802 | 283 |

The stage: 1.0 / 2.3 / 2.3 s real (15 / 16 / 19 houses). What a rectangle is tested against: `block_polys`
(every dry hem plot, the pond's box, Kuwabata's pond mosaic), the paddy's chords (5 points), the water courses,
and the hard ground (every dry plot again, every marsh, every ditch segment as a quad - 29 + 114 + 2 on
Inashiro); then the standing houses by rotated-corner gap, the sun corridors, the treads and the bund-wall
corners. 24 of Inashiro's 39 proposed seats failed every one of the spiral's 181 offsets.

## R2 - the after (2026-09-12, the pool at the landing commit; `make map --no-cache PROFILE=1`, `meta.seat_search`, `site_boundary`)

| per house | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| households seated (first roll) | 15/15 | 20/20 | 16/16 | 12/12 | 19/19 |
| candidate seats pre-tested | 4.3 | 4.8 | 7.0 | 2.5 | 1.6 |
| placer calls | 1.5 | 1.5 | 1.8 | 1.1 | 1.3 |
| positions the fit test saw | 55 | 62 | 105 | 28 | 46 |
| rectangles judged | 194 | 220 | 387 | 113 | 163 |
| lattice rounds (`rounds`; over 4 = the rescue ran) | 4 | 4 | 4 | 4 | 4 |
| stage_homesteads, s (after 225: 1.0 / 1.3 / 2.3 / 0.8 / 1.0) | 0.25 | 0.38 | 0.58 | 0.14 | 0.26 |
| regen, s (after 225: 8.7 / 10.6 / 7.5 / 5.9 / 10.5) | 8.1 | 9.4 | 7.4 | 6.0 | 10.6 |

The boundary the fit test was asked against, per map - chords / outline rings (vertices) / holes / water segments /
registered-corridor segments: Inashiro 7 / 3 (667) / 0 / 5 / 3; Kashikawa 10 / 3 (654) / 0 / 5 / 3; Kuwabata 7 / 1
(230) / 1 / 0 / 0; Mizuguchi 8 / 3 (627) / 0 / 5 / 3; Sawada 7 / 3 (657) / 0 / 5 / 3. So the CHORDS, the water and
the corridors are the "relatively small number of line segments" the GM asked for - 13 to 22 per map - and the
union rings are outlines of a few hundred vertices asked by containment through a `RingIndex`, not segments; the
settlement-review asked that the record say so rather than claim a handful. Before the cover test dropped the
segments the cultivated ground already refuses, the water set was 86-119 per map.

Against R1: Inashiro 419 positions per house -> 55, Kuwabata 1,686 -> 105, Sawada 363 -> 46; Kuwabata's 157
proposals for 16 houses -> 112 pre-tested candidates and 28 placer calls; the stage from 1.0-2.3 s to 0.14-0.58 s.
SC-1 (under 0.25 s) is met on Mizuguchi and Inashiro and missed on Kashikawa (0.38), Sawada (0.26) and Kuwabata
(0.58 - the mosaic's 230-vertex ring with its hole, and 7 candidates per house); SC-2's 12 candidates per house is
met on every pool map, its 2 placer calls too, and its positions (the spiral's offsets included) are 28-105 - the
six-ring spiral is 30 px of offsets per placer call, and a seat the placer refuses outright still walks them.

**The quota-short path, measured (SC-2's second case).** No pool map reaches the rescue rounds (`rounds` 4 on all
five). Of the 48 cohort seeds one does: seed 25 (crescent, T, 20 households, fall 225), whose crescent has the
reed-marsh toe across its wet half - 14 of 20 seated without the rescue once the toe was in the boundary, 20 of 20
with it, at 13.4 candidates and 98 positions per house over six rounds on the kept roll (`meta.seat_search`:
268 / 31 / 1,963 / 5,467 / rounds 6), against 12.4 candidates and 1,566 positions on the same seed under the old
cloud (the NODEDUPE toggle run, 2026-09-12).

**The cohort.** 48 of 48 pass with `households_seated` reported (the audit counted stranded houses only before this
feature). Two seeds regressed under the first cut and were fixed by measurement, each toggle rolled in isolation:
seed 11 (one stranded house) passed under ANY of three perturbations - the old fifteen-ring spiral, the envelope
front row, no lattice dedupe - a chance failure, cured by the re-roll drawing a fresh lattice (the salt); seed 25
passed under none of them and needed the rescue rounds' width and free guesses. Both pass at attempt 2 now.

**The bookends** (`make perf LABEL=226-start` in a worktree at main's tip c5c67f38, `226-end` at the landing):
total 27.8 -> 27.7 s (-0.4%); seed 25 +8.0% (band 1) - the bookend times each seed's FIRST roll, and the re-seated
layout's first roll strands two farmhouses that the web's straggler routine pays its recorded 240-routing-call bill
for (web 1.66 -> 2.75 s on that roll; the homesteads stage 1.12 -> 0.25); the kept map's web is 0.43 s and the
whole generate 14.5 s against main's 35 (four rolls). Explained with `make perf-explain`; the `perf-audit` agent's
confirmation is in dev/perf-log/.

**What moved and why (D4, D6):** every pool layout re-packed - the seats come from the chains at the pitch, so the
front rank fronts the paddy by more (houses within 165 px: 10 -> 12, 15 -> 16, 8 -> 9, 10 -> 11, 11 -> 14) and
Kuwabata's lone outlier farmhouse is gone; the `_hard_clear` sweep fix alone moves a rectangle's verdict by a few
tenths of a pixel; the belt re-rolled on every map for its 39 ft southern strip (Kashikawa's beds shaded from the
south 7 of 22 -> 0; main had 2 of 26).
