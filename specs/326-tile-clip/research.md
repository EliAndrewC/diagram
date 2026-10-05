# Research: each tile its own part of the map (feature 326)

## R1 - The standalone measurement (2026-10-05, before this feature)

Observed 2026-10-05, method: a one-shot test running resvg per tile under `/usr/bin/time -f %M` on the PNG's SVG of a rendered
20-household hamlet (seed 4), with text removed as the picture removes it; "clipped" is `raster.drop_offmap` applied line by
line against the tile's box. Every clipped 3 x 3 tile was byte-identical to the full-document tile.

| grid (observed 2026-10-05, method: as above) | per tile, full | per tile, clipped | total tile CPU, full -> clipped |
|---|---|---|---|
| 1 x 1 | 331 MB | 331 MB | 2.5 s |
| 3 x 3 | 103 MB | mean 79 MB (60-93) | 5.3 -> 4.3 s |
| 5 x 5 | mean 68 MB (max 94) | mean 52 MB (max 84) | 8.7 -> 6.5 s |

Observed 2026-10-05, method: resvg on a one-rect SVG, with and without `--skip-system-fonts` - 4.5 MB either way, so the fonts are
not the per-tile cost: most of a tile's memory scales with its pixels, the most likely cause the full-canvas layers resvg
allocates for semi-transparent groups (feature 225 found layers dominate its time); clipping removes elements, not those layers,
which is why smaller tiles are the larger lever.

Observed 2026-10-05, method: reading `page.py` `write_html` - the picture is rendered from the page's own text (`raster.picture(
raster.without_text("\n".join(wrapped)))`), one record string a line, a classed string wrapped in `<g class="f ...">`; the page
already clips classed strings to the whole viewBox (`drop_offmap`, feature 200) and leaves the sheet and unclassed strings whole.
The standalone measurement clipped the PNG's SVG instead, so the pipeline's own numbers are taken in T03.

## R2 - The grids in the pipeline (2026-10-05, after T01)

Observed 2026-10-05, method: the 50 ms process-tree sampler over the rendered 20-household hamlet (seed 4), `TILE_MPX` set to give
each grid, two interleaved rounds, load 3-5 (the container's other session working):

| grid, clipped (observed 2026-10-05, method: as above) | peak | render span |
|---|---|---|
| 3 x 3 | 367 / 372 MB | 3.51 / 4.51 s |
| 4 x 4 | 363 / 352 MB | 7.85 / 4.90 s |
| 5 x 5 | 350 / 349 MB | 6.03 / 5.98 s |
| 6 x 6 | 352 / 348 MB | 7.88 / 6.91 s |
| 7 x 7 | 350 / 352 MB | 9.53 / 11.02 s |

Observed 2026-10-05, method: the same sampler, unclipped against clipped 3 x 3 alternated on a normal machine (each run ~9.5 s):
unclipped peak 551 / 528 MB, span 3.13 / 3.22 s; clipped peak 371 / 365 MB, span 3.57 / 3.37 s. With the clip the peak is set by the
generator process and the stitch child, not the tiles, so finer grids save 10-20 MB more and every one breaks the 3.81 s span bound.

## R3 - What tiling and clipping do to the pixels (2026-10-05)

Observed 2026-10-05, method: a one-shot test on the picture's own input text (captured from that render), each grid's tiles
stitched in-process and compared with the single render: the clipped and unclipped tiles give the same canvas at 3 x 3, 4 x 4 and
5 x 5 - the clip changes no pixel. Tiling itself does: 4,319 pixels differ from the single render at 3 x 3 (6,037 at 4 x 4, 7,765 at
5 x 5), 482 of them within 2 px of a seam; by level 1: 2,344, 2: 1,108, 3: 206, ..., none above 39. Feature 223's note that the
stitched picture "is the single render pixel for pixel" held only on its test's tiny synthetic page. A new grid moves these
differences, so a grid change cannot leave the picture byte-identical to today's. The clip cost (`tile_doc` in Python, measured in
the same test): 0.89 s for 9 tiles, 1.47 s for 16, 2.04 s for 25.

## R4 - The pool, clipped against unclipped (2026-10-05)

Observed 2026-10-05, method: every live pool map's picture input captured during a `make render-sync` in the clone, each rendered
from clipped and from unclipped tiles and the JPEGs compared byte for byte: 6 of the 11 render as one tile (nothing clipped); of
the 5 tiled, 3 identical and 2 different. Bisecting the changed lines found the cause in both: a classed line whose far subpaths
the clip trimmed (a woodland-commons blob path; a perimeter dike's planted group) - not a lost element: the tile's pixels against
the unclipped tile's differ in 34 and 29 channel values of 20+ million pixels, at most 10 and 4 levels. Trimming a path moves
resvg's anti-aliasing slightly.

Observed 2026-10-05, method: the same check with WHOLE-line clipping (a classed line dropped only when nothing of it survives the
off-map rule, otherwise kept untouched): all 5 tiled maps byte-identical; on the reference render, peak 420 / 393 MB against
537 / 533 MB unclipped (about 130 MB less, against trimming's about 170 MB), render span 4.36 / 3.99 s against 3.25 / 3.82 s
under load. The GM chose trimming (Amendment 2): visually identical, the larger saving.

## R5 - The bookends (2026-10-05)

Observed 2026-10-05, method: `make perf` in /tmp/base326 at the pre-feature commit b8b20e690 and `make perf-gate` in the clone,
back to back in a window the container's other session held clear (load 4.5 -> 1.5 across the pair): band 3 - 15 households
+15.6% (seeds 39 and 47 +27% / +29%), 10 households +14.9%, but 20 households -15.5% and 40 households -19.6%. The snapshot
times only the roll's stages, which feature 326 does not touch (raster.py). Control (`measurements.json`
`perf-control-326-roll-ab`): the two seeds that crossed, whole roll alternated base and clone - 4.0 / 3.8 against 3.8 / 3.8 s and
4.1 / 4.2 against 4.2 / 4.1 s. The pair's spread is the machine, both ways, as feature 324 found (its R5).
