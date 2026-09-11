# Research - 222 faster renders and an indexed title scan

## R1 - the before (2026-09-10, session `diagram-performance`)

The full profile is the last section of `.claude/skills/diagram/dev/performance.md`. The rows this
feature acts on, seconds per pool hamlet, one `make map GEN="--no-cache ..."` each on an idle 22-core
box:

| phase | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| engine stages (`build`) | 6.9 | 10.4 | 16.6 | 6.3 | 14.4 |
| of which `stage_hinterland` | 1.3 | 2.4 | 10.0 | 1.7 | 3.7 |
| page picture: resvg `--zoom 3` + lossless WebP | 7.8 | 7.1 | 6.5 | 6.9 | 6.4 |
| PNG render: resvg 2600 px | 2.1 | 3.0 | 2.7 | 2.0 | 2.4 |
| page: id map (resvg zoom 1) | 0.3 | 0.2 | 0.3 | 0.3 | 0.2 |
| page text: `drop_offmap` | 0.7 | 1.0 | 0.8 | 0.6 | 1.1 |
| regen total (child) | 19.3 | 23.0 | 27.9 | 17.3 | 25.6 |

The picture split (Inashiro): resvg zoom 3 render + PNG encode 2.5 s; PIL decode + lossless WebP child
5.2 s. Encoders on the same 5103 x 5136 picture: lossless WebP method 0, 4.12 s, 3.87 MB; lossy WebP q90,
0.93 s, 2.32 MB; JPEG q90 4:2:0, 0.10 s, 3.58 MB; JPEG q90 4:4:4, 0.15 s, 4.56 MB; JPEG q95 4:4:4, 0.18 s,
6.39 MB; PIL decode 0.41 s. The picture's alpha channel is 255 everywhere.

The SVG (Inashiro): 16.39 MB, 268,156 `<line>` (14.56 MB) - 211,374 in the commons grass bucket, 48,604 in
the marsh reed bucket - 18,325 circles, 2,027 polygons, 235 paths. resvg on it: 2600 px 2.13 s; with each
blade group merged into one path (9.37 MB) 1.17 s; with the blades removed (2.57 MB) 0.89 s. Zoom 3: 3.81 /
2.86 / 2.43 s.

Kuwabata's hinterland under cProfile: `title_pocket` -> `_blank_label_spot` -> `_box_clear` 4,027 calls,
16.4 million `segments_cross` pairs, 34 million `ccw`, 24.2 of the stage's 27.8 profiled seconds.

## R2 - the after (2026-09-11)

The same measurement as R1: each pool gen regenerated alone (`make map GEN="--no-cache ..." PROFILE=1`) on an
otherwise idle box, from the clone at commit 5373772e. Regeneration totals (the child, as `regen` reports):

| hamlet | before (R1) | after | saved |
|---|---|---|---|
| inashiro | 19.3 | 12.2 | 7.1 |
| kashikawa | 23.0 | 16.0 | 7.0 |
| kuwabata | 27.9 | 14.1 | 13.8 |
| mizuguchi | 17.3 | 11.4 | 5.9 |
| sawada | 25.6 | 19.2 | 6.4 |

SC-4 asked at least 6 s on every map and 12 on Kuwabata: Kuwabata 13.8; Mizuguchi 5.9, a tenth of a second
under the bar on a single run - reported as the miss it is, not reached for (the reviewer's own condition).

Stage totals: Inashiro 6.9 -> 7.0 s, Kashikawa 10.4 -> 10.7, Kuwabata 16.6 -> 8.2 (hinterland 10.0 -> 1.6),
Mizuguchi 6.3 -> 6.4, Sawada 14.4 -> 14.3 - so the writer's merge (`merge_lines`) costs nothing the stage
profile can see, where the first cut (calling `merge_primitives` on the written lines) had cost 1.9 s of the
hinterland stage on Inashiro.

The file: Inashiro's SVG 16.39 -> 9.37 MB (268,156 `<line>` -> 119 `<path>` in 10 blade groups holding
259,978 subpaths); resvg on the tiled file at 2600 px 1.18 s (2.13 before), zoom 3 2.81 s (3.81); the page
7.79 -> 8.92 MB (the JPEG at 4:4:4 is a megabyte larger than the lossless WebP, D2); the PNG unchanged in size.

The pool: every manifest differs from HEAD only in `ink_classes` (the census counts paths where it counted
lines); no `title`, `meta.title_band` or view moved on any of the five, so FR-008 changed no shipped map and
D5's first route covers all of them.

The phase split, the same marks as R1's (a second pass over the same five, one at a time):

| phase | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| engine stages (the stage profile) | 7.0 | 10.7 | 8.2 | 6.4 | 14.3 |
| page: picture + id map, concurrent (was 6.4-7.8 + 0.2-0.3 in sequence) | 3.35 | 3.21 | 4.10 | 3.35 | 2.81 |
| of which the picture thread: resvg `--zoom 3` | 2.57 | 2.46 | 3.56 | 2.62 | 2.14 |
| of which the picture thread: PIL decode + JPEG child (was 2.9-5.2) | 0.77 | 0.74 | 0.54 | 0.73 | 0.67 |
| PNG render (resvg 2600), joined after the .json (was 2.0-3.0 in sequence) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| page text: `drop_offmap` | 0.71 | 0.96 | 0.74 | 0.57 | 1.08 |
| page text: `wrap` (was 0.25-0.47) | 0.21 | 0.14 | 0.16 | 0.20 | 0.14 |
| page: explanations + json blob + data uris | 0.35 | 0.35 | 0.40 | 0.34 | 0.32 |
| page: hit regions | 0.11 | 0.07 | 0.03 | 0.10 | 0.05 |
| `gencache.store` | 0.10 | 0.11 | 0.12 | 0.11 | 0.10 |
| regen total | 12.2 | 15.9 | 14.3 | 11.3 | 19.3 |

The PNG's join is 0.00 s everywhere: started as the .svg lands, resvg's 2600 px pass finishes under the page's
own work every time, so the three renders now cost the wall clock what the slowest one does. SC-2 asked the
picture step under 3.5 s on every map: four of five; Kuwabata's is 4.10 because its resvg render alone is
3.56 s (the dike-pond map has the most non-blade ink). The encode itself is 0.15 s (R1); the child that holds
it - spawn, PIL decode, JPEG - is 0.54-0.77 s, against the 2.9-5.2 s lossless child. The JPEG's gain against
the GM's "about four seconds": 2.2-4.4 s per map on the child alone.

What is left, for the record (out of scope here): `drop_offmap` at 0.6-1.1 s walks the 260,000 blade
subpaths to discard the ~90% outside the viewBox - the writer could clip the scatter to the frame's content
box when it scatters, which would also take the resvg passes and the file down again; the resvg zoom-3 render
at 2.1-3.6 s is the largest remaining step of the page, and `RASTER_R` 2 would take it to ~45%.
