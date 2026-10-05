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

## R3 - The final code (after T02)

Observed 2026-10-05, method: the 50 ms sampler over the same rendered 20-household hamlet, two runs: peak 571 / 580 MB (983 /
962 MB before, R1), the picture child 188 / 190 MB (300 MB before), at most five resvg processes alive (eleven before: three
tiles, the PNG render and the id map), the render span 3.60 / 3.21 s (2.14 / 2.19 s before) - the first run includes the
changed modules' first import. The PNG and the page are byte-identical to the baseline run's (`cmp`, string equality).
SC-001 (child at least 80 MB lower: 111 MB) and SC-002 (map peak at least 300 MB lower: ~395 MB; span at most +1.5 s:
+1.0 to +1.4 s) hold; the span's first run came within 0.1 s of its bound.

Observed 2026-10-05, method: the 100 ms sampler over `make render-sync` (the 11 live maps regenerated, the new default of four
generators): peak 1,121 MB, p90 434 MB, 91 s - against 1,725 MB, p90 737 MB, 60 s for the unmodified code at 22 (R1). The load
average rose from 2.4 to 6.8 during the run (the container's other sessions), which the wall time carries; the prototype's
4-job run on a quieter machine was 72 s (R2). SC-003 holds.

## R4 - The bookends (2026-10-05)

Observed 2026-10-05, method: `make perf-gate` and alternated `make perf-profile` runs - the first 324-end, taken at load 7-8.5
while another session ran headless-Chromium modal checks in the container, read band 3 (every roll stage grown, +17% to +41% at
10 and 20 households). The snapshot times only the roll's stages, which feature 324 does not touch. The control
(`measurements.json` `perf-control-324-stage-calls`): the homesteads and web stages make the same calls on the base engine and
the clone (3,403,625 and 3,082,225 primitive calls), the clone no slower. The end bookend is re-taken once the container is quiet.

## R5 - The bookends that landed (2026-10-05)

Observed 2026-10-05, method: `make perf` and `make perf-gate` back to back in a window the other session in the container held
clear - the 324-start re-taken retroactively in /tmp/base324 at 8c61b03ae (060216Z), the 324-end right after (060545Z): band 0
at 10/20/40 households (-27.2 / -23.0 / -8.1%), band 3 on seed 4 at 15 households alone (+23.7%, field). The load fell from 13
to 4 across the pair; the unmodified engine itself read 48% slower at 06:02 than at 04:21. Explained with the controls
(`perf-control-324-stage-calls`, `perf-control-324-roll-ab`); perf-audit confirmed it consistent and audited it justified,
re-running seed 4 six times alternated (6.05 s on both); the GM signed off, 2026-10-05. The two earlier 324-end bookends,
taken under other sessions' load, measured that load and are not committed.
