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

## R2 - the after

(filled at T07)
