# Research: a leaner site build and a faster clip (feature 327)

## R1 - The starting point (2026-10-04/05, from features 323 and 326)

Observed 2026-10-04, method: tracemalloc over `site.build(RESEARCH_DIR)` (feature 323 research.md R1, R3): the result 2,698 files,
72.6 M characters, 148 MB held - 69.1 M characters at two bytes each (132 MB), because every page carries text past Latin-1; the
build's traced peak 236 MB after feature 323.

Observed 2026-10-05, method: a one-shot test timing `tile_doc` over the reference render's picture text (feature 326 research.md
R3): 0.89 s for 9 tiles, 1.47 s for 16, 2.04 s for 25 - each tile re-parses every classed line. Observed 2026-10-05, method: the
50 ms process-tree sampler, clipped against unclipped 3 x 3 alternated (feature 326 research.md R2): clipped span 3.57 / 3.37 s
against 3.13 / 3.22 s unclipped, peak 371 / 365 MB.

## R2 - The site held as UTF-8 (2026-10-05, after T01)

Observed 2026-10-05, method: tracemalloc over `site.build(RESEARCH_DIR)` in a one-shot test, every file compared with main's
`research/site/` (built at 06fea4766, the same record): with `SiteFiles` alone the pages held 71 MB (148 MB before) but the build's
peak rose 236 -> 249 MB - the single page was still joined as 42 MB of text and then encoded, the text and its bytes alive
together. With the single page's pieces linked and encoded one at a time and the bytes joined (`site_pages.shell_utf8`), the
traced peak is 165 MB and 84 MB is held at the end (pages 71 MB); all 2,698 files byte-identical to main's.

## R3 - The clip parsed once (2026-10-05, after T02)

Observed 2026-10-05, method: process CPU time in a one-shot test on the reference render's picture text, three runs: the 9 tiles
re-parsing every line 0.82 / 0.82 / 0.92 s; parsing once 0.08 s plus nine assemblies 0.03 s (0.11-0.12 s); the 9 tile documents
identical. Every tiled live pool picture (5 of 11) byte-identical between parsing once and per tile.

Observed 2026-10-05, method: the 50 ms process-tree sampler over the rendered 20-household hamlet, old raster.py (06fea4766)
against new, alternated: the span fell (3.45 -> 3.22 s mean over the first two rounds) but the peak ROSE - old 372 / 374 / 358 /
381 / 382 MB, new 392 / 436 / 384 / 467 / 422 MB. At each peak the resvg processes held 236-246 MB (old) against 253-336 MB (new):
with the clip no longer staggering the tiles, the three tile renders started together and overlapped the PNG and the id map. The
prepared form itself is 6.7 MB (5,860 subpaths, 9,097 shapes).

Observed 2026-10-05, method: the same, with one cap shared by every resvg launch in the process (`RESVG_SLOTS`), old against new
alternated over five rounds: old peak 411 / 359 / 380 / 359 / 364 MB (mean 374.6), span 3.41 / 3.34 / 3.51 / 3.45 / 4.05 s (mean
3.55); new with four slots peak 362 / 356 / 397 / 387 / 351 MB (mean 370.6), span 3.14 / 3.36 / 3.16 / 3.17 / 3.24 s (mean 3.21);
three slots measured 364 / 349 MB, 3.19 / 3.26 s. The PNG and the page byte-identical to the old code's.
