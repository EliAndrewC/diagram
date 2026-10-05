# Research: the render's memory (feature 324)

## R1 - Where a rendered map's memory goes (2026-10-05, before this feature)

Observed 2026-10-05, method: a process-tree RSS sampler at 50 ms over `make hamlet ARGS="--name MemTest --seed 4 --households 20
--out <dir>"` (rendered), two runs: peak 983 / 962 MB, the render span 2.14 / 2.19 s. At the peak eleven resvg processes run at
once - ten picture tiles at ~100 MB each (`raster.picture` starts every tile at once, `ThreadPoolExecutor(max_workers=len(boxes))`,
and every tile parses the whole SVG, so a tile's memory is the document's, not its pixels') and the id map (~80 MB). After them
the picture child (`raster._PICTURE_CHILD`) climbs to 300 MB: it opens every tile, and `convert('RGB')` loads each one and keeps
it in its dict until the end.

Observed 2026-10-05, method: the same sampler at 100 ms over `make render-sync` in the clone, the pool's 11 live maps
regenerated: peak 1,725 MB (17 resvg, 5 generators), p90 737 MB, 60 s; `render_cache.regen_pool` runs `os.cpu_count()` (22)
generators at once.

## R2 - The prototype (2026-10-05)

Observed 2026-10-05, method: the same sampler, two runs a variant, the hamlet above; the tile cap through a temporary
environment variable, the child decoding, pasting and closing each tile in turn:

| variant (observed 2026-10-05, method: the sampler) | peak | picture child | render span |
|---|---|---|---|
| the child alone | 1,106 / 1,083 MB | 177 / 187 MB | 2.22 / 2.23 s |
| child + 4 tiles at once | 643 / 627 MB | 191 / 185 MB | 3.20 / 3.20 s |
| child + 3 tiles at once | 542 / 538 MB | 191 / 190 MB | 3.21 / 3.15 s |
| child + 2 tiles at once | 456 / 441 MB | 184 / 185 MB | 4.35 / 4.28 s |

Observed 2026-10-05, method: `cmp` and string equality - the PNG and the page from the 2-tile variant are byte-identical to the
baseline's.

Observed 2026-10-05, method: the 100 ms sampler over `make render-sync` with the child and 3 tiles, the 11 maps regenerated each
time: 22 jobs peak 1,459 MB, p90 889 MB, 57 s; `--jobs 4` peak 1,219 MB, p90 448 MB, 72 s.

Not taken (it is not a straightforward change): giving each tile only the elements inside its box - `drop_offmap` works on the
page's element strings before the SVG is assembled, and the tiles are cut from the assembled text.
