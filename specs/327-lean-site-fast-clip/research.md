# Research: a leaner site build and a faster clip (feature 327)

## R1 - The starting point (2026-10-04/05, from features 323 and 326)

Observed 2026-10-04, method: tracemalloc over `site.build(RESEARCH_DIR)` (feature 323 research.md R1, R3): the result 2,698 files,
72.6 M characters, 148 MB held - 69.1 M characters at two bytes each (132 MB), because every page carries text past Latin-1; the
build's traced peak 236 MB after feature 323.

Observed 2026-10-05, method: a one-shot test timing `tile_doc` over the reference render's picture text (feature 326 research.md
R3): 0.89 s for 9 tiles, 1.47 s for 16, 2.04 s for 25 - each tile re-parses every classed line. Observed 2026-10-05, method: the
50 ms process-tree sampler, clipped against unclipped 3 x 3 alternated (feature 326 research.md R2): clipped span 3.57 / 3.37 s
against 3.13 / 3.22 s unclipped, peak 371 / 365 MB.
