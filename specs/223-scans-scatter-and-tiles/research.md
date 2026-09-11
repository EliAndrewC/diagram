# Research - 223 the two remaining scans, the off-map scatter, and the picture in tiles

## R1 - the before (from specs/222 research R2 and the 2026-09-10 profile)

Per pool hamlet after feature 222, seconds: regen 12.2 / 15.9 / 14.3 / 11.3 / 19.3 (inashiro / kashikawa /
kuwabata / mizuguchi / sawada); the stage loop 7.0 / 10.7 / 8.2 / 6.4 / 14.3; the picture + id map, concurrent,
3.35 / 3.21 / 4.10 / 3.35 / 2.81, of which the picture's resvg `--zoom 3` 2.57 / 2.46 / 3.56 / 2.62 / 2.14 and
its encode child 0.77 / 0.74 / 0.54 / 0.73 / 0.67; `drop_offmap` 0.71 / 0.96 / 0.74 / 0.57 / 1.08.

The scans (cProfile of the gen child, 2026-09-10, relative shares): Sawada's `stage_hinterland` 3.7 s, of which
`bamboo_seats` -> `_fits` -> `bamboo_blocked` 9,796 samples, 2.17 million `seg_dist` (52% of the stage
profiled); `place_wells` 1.1-1.3 s on Kashikawa, Kuwabata and Sawada, `_worst_after` 70,416 calls with 1.2
million inner terms on Kuwabata, the sort key evaluating it twice per candidate.

The picture's render: resvg at zoom 3 on Inashiro's file with every blade REMOVED still took 2.43 s (3.81 with
them, 2.86 merged), so the cost is the 26 megapixels (5103 x 5136), not the ink; resvg is single-threaded.
The SVG after 222: 9.37 MB, 259,978 blade subpaths of which ~90% lie outside the viewBox (specs/200 R2).

## R2 - the after (2026-09-11)

The same measurement as 222's R2: each pool gen regenerated alone (`make map GEN="--no-cache ..." PROFILE=1`) from
the clone at commit 3a090121, with a settlement-review's own renders running on the box for part of it (a
modest contention that can only inflate these numbers).

| hamlet | after 222 | after 223 | saved | stages | hinterland | appurtenances |
|---|---|---|---|---|---|---|
| inashiro | 12.2 | 9.6 | 2.6 | 7.0 -> 6.8 | 1.3 -> 1.3 | 0.25 -> 0.18 |
| kashikawa | 15.9 | 11.9 | 4.0 | 10.7 -> 9.2 | 2.4 -> 1.8 | 1.28 -> 0.73 |
| kuwabata | 14.3 | 10.4 | 3.9 | 8.2 -> 7.4 | 1.6 -> 1.4 | 1.12 -> 0.48 |
| mizuguchi | 11.3 | 8.4 | 2.9 | 6.4 -> 5.6 | 1.7 -> 1.1 | 0.18 -> 0.13 |
| sawada | 19.3 | 14.4 | 4.9 | 14.3 -> 11.9 | 3.7 -> 1.8 | 1.17 -> 0.60 |

SC-4 (at least 2 s everywhere, 4 on Sawada): met on every map. SC-1's Sawada hinterland bar of 1.5 s is missed
at 1.8: the bamboo scan is gone from it (its 52% share, R1) and what remains is the commons scatter itself
(`cover.py` `commons`, ~1 s, indexed since feature 218 - the draw count is the cost now) and the coppice
patches. Kuwabata's appurtenances 0.48 s meets its 0.7 bar. Every manifest differs from HEAD only in
`ink_classes`; no stand, well, house, lane, field, water or title moved (the review's manifest diff agrees).

The files: SVG 9.4 -> 3.91 / 4.42 / 3.57 / 3.40 / 4.47 MB (inashiro / kashikawa / kuwabata / mizuguchi /
sawada) - SC-2's 4 MB met on three, missed by under half a megabyte on Kashikawa and Sawada, whose in-frame
scatter is the largest; Inashiro's blade subpaths 259,978 -> 49,465. The page at `RASTER_R` 2: 6.36 / 6.24 /
4.33 / 6.03 / 5.64 MB (7.8-8.9 after 222); SC-3's 6 MB met on three, Inashiro and Kashikawa 0.2-0.4 over.
Inashiro's picture 4.51 MB at 3 -> 2.59 MB at 2.

`RASTER_R` 3 against 2 on Inashiro, both tiled and culled, one run each: regen 10.7 s at 3, 9.6 s at 2; the
page 8.92 MB at 3, 6.36 at 2. The DPR-2 consequence stands as D3 records it.

The phase split (the same marks as 222's R2, a second pass over the five, one at a time, box otherwise idle):

| phase | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| picture thread: 4 resvg tiles in parallel (was one resvg at zoom 3: 2.57 / 2.46 / 3.56 / 2.62 / 2.14) | 0.89 | 0.86 | 1.27 | 0.93 | 0.68 |
| picture thread: PIL decode + stitch + JPEG child (was 0.77 / 0.74 / 0.54 / 0.73 / 0.67) | 0.45 | 0.43 | 0.34 | 0.46 | 0.39 |
| the picture step, the two together (was 3.35 / 3.21 / 4.10 / 3.35 / 2.81 with the id map) | 1.34 | 1.29 | 1.61 | 1.39 | 1.07 |
| finish: `flush_blade_groups` (the cull + merge, new) | 0.17 | 0.21 | 0.16 | 0.14 | 0.23 |
| page: `drop_offmap` (was 0.71 / 0.96 / 0.74 / 0.57 / 1.08) | 0.22 | 0.21 | 0.15 | 0.20 | 0.20 |
| page: `wrap` | 0.21 | 0.15 | 0.16 | 0.20 | 0.13 |
| page: explanations + json blob + data uris | 0.35 | 0.32 | 0.38 | 0.32 | 0.30 |
| PNG render, joined after the .json | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| regen total | 9.7 | 12.1 | 10.3 | 8.4 | 14.3 |

SC-3's picture step under 1.5 s: four of five, Kuwabata 1.61 (its tiles alone 1.27 - the dike-pond map has the
most in-frame ink per tile). SC-2's `drop_offmap` under 0.2 s: Kuwabata 0.15, the other four 0.20-0.22 - what
remains is the pass over every classed string, not the blades. The four tiles at `RASTER_R` 2 take 0.7-1.3 s
where one process at 3 took 2.1-3.6: the two levers compound (the pixels 44%, the parallelism ~2.5x on four
cores), and the parse overhead D4 priced (each tile parses the ~4 MB document) is inside those numbers.
