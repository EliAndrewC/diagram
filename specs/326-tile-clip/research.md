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
