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

## R2 - the after

(filled at T07)
