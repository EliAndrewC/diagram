# Research - 225 the marks culled, the pad tightened, the opacity folded, the rows clipped

## R1 - the before, and where a tile's time goes (2026-09-11)

After feature 224 (its R2), per pool hamlet: the picture's four tiles 0.97 / 0.83 / 1.26 / 1.00 / 0.69 s
(inashiro / kashikawa / kuwabata / mizuguchi / sawada), `drop_offmap` 0.17 / 0.12 / 0.10 / 0.17 / 0.12,
`wrap` 0.21 / 0.15 / 0.16 / 0.21 / 0.13, the hinterland stage 0.61-0.70, the SVG 2.52 / 1.98 / 2.03 / 2.43 /
1.86 MB, regen 8.5 / 10.3 / 9.5 / 7.9 / 13.1. The review of 224 counted 2,146 of Inashiro's 3,684 brush dots
(58%) drawn outside the view - the pad's ring.

**The tile's time is not the pixels.** On Inashiro's page document (2.5 MB, 6,970 elements, resvg 0.45,
`--serif-family "DejaVu Serif"`): the full render at zoom 2 (11.6 Mpx) 1.34-1.39 s; the same document at zoom
0.02 (parse and tree, a tiny raster) 0.09 s; a quarter tile at zoom 2 (2.9 Mpx) 0.74 s - 55% of the full for a
quarter of the pixels. Stripping the invisible hit ink (1,328 elements, 0.18 MB) changed nothing (1.37 / 0.73).
Then, one thing removed at a time (full / quarter): the blade groups 1.20 / 0.69; the four group opacities 1.19 /
0.68; the 30 `clip-path`s 1.17 / **0.44**; pattern fills n/a (none on the page); **every element `opacity` and
`fill-opacity` 0.79 / 0.38**. Per family, the fill-opacity of the marsh tint alone 1.30 / 0.74 - so the cost
was element `opacity`, not fill opacity: 958 crop-row `<line>`s carry `opacity="0.8"`, 203 crown circles
`opacity="0.55"`, 15 + 15 + 17 rects, 14 paths. Folding it into the one paint's own opacity - `opacity` ->
`stroke-opacity` on a stroke-only line, -> `fill-opacity` on a fill-only circle, -> `stroke-opacity` on a
`fill="none"` shape - took the full render 1.35 -> 1.02 and the quarter 0.75 -> 0.44, with 36 element opacities
left (the two-paint elements). The same pixels: for a single primitive with one paint the two attributes are the
same operation; resvg composites `opacity` through a layer.

The clip paths are the dry hem's: `landuse.py` draws the tea fringe's and the vegetable ground's rows as
full-width horizontal lines inside a `<g clip-path="url(#...)">` per plot (29 on Inashiro's file), each a
layer in resvg. A row is a horizontal line and a plot is a convex quadrilateral, so the row's ends are its two
intersections with the plot's edges.

## R2 - the after (2026-09-11)

The same measurement as 224's R2 (the phase marks in a detached worktree of the feature's commit, each pool gen
alone, the box otherwise idle):

| phase | inashiro | kashikawa | kuwabata | mizuguchi | sawada |
|---|---|---|---|---|---|
| the picture's four tiles (was 0.97 / 0.83 / 1.26 / 1.00 / 0.69) | 0.51 | 0.60 | 0.66 | 0.47 | 0.48 |
| the encode child (was 0.44 / 0.45 / 0.33 / 0.45 / 0.39) | 0.45 | 0.45 | 0.35 | 0.44 | 0.40 |
| `drop_offmap` (was 0.17 / 0.12 / 0.10 / 0.17 / 0.12) | 0.15 | 0.12 | 0.08 | 0.17 | 0.10 |
| `wrap` (was 0.21 / 0.15 / 0.16 / 0.21 / 0.13) | 0.21 | 0.15 | 0.17 | 0.20 | 0.13 |
| `stage_hinterland` (was 0.61 / 0.62 / 0.60 / 0.63 / 0.63) | 0.57 | 0.56 | 0.64 | 0.59 | 0.61 |
| `flush_blade_groups` (the marks too now) | 0.07 | 0.05 | 0.05 | 0.07 | 0.05 |
| regen total (was 8.5 / 10.3 / 9.5 / 7.9 / 13.1) | 8.2 | 10.2 | 9.2 | 7.0 | 12.4 |

The file: 2.27 / 1.75 / 1.67 / 2.11 / 1.54 MB (was 2.52 / 1.98 / 2.03 / 2.43 / 1.86); Inashiro's clips 30 -> 1
(the pad base), its element opacities 1,237 -> 17. The tiles halved on three maps and fell 30-40% on the other
two - the fold and the cut did what R1's experiments said; the encode child did not move (it never depended on the
document). The bookends: 225-end vs 225-start -1.4% on the reference's stage total, band 0. The second 48-map
cohort at the 40 px pad: 48 of 48, no breach; the pool's tightest side 39.7-40.2 px on every map.

**The bars, mostly missed, reported.** SC-1's tiles under 0.6 s: Inashiro, Mizuguchi and Sawada; Kashikawa 0.60,
Kuwabata 0.66 (its mulberry-dike bank clips, one per pond, are the layers left, D-noted in FR-004). SC-2's
`drop_offmap` + `wrap` under 0.2 s: none - 0.23-0.37; the per-string scans are the residual and the marks' cull
took only a hundredth or two off them, because the page's own drop had already removed what the writer now
removes, and the merge's precheck rarely fires (nearly every classed string holds two or more elements). SC-3's
SVG under 1.5 MB: none - 1.54-2.27 - and the hinterland under 0.55 s: none - 0.56-0.64: the 120 -> 40 pad took
the ring's throws away and the stage moved 0.02-0.06 s, so the ring was never the stage's cost; what remains is
the in-frame throws' keep-out tests and the coppice and bamboo scans. SC-4's 0.8 s per map: Mizuguchi 0.9, the
rest 0.1-0.7. The four items bought 0.1-0.9 s per map; what is left of a regen is the stage loop (the field's
comb 1.8-3.7 s, the homesteads 1.0-2.5, the web up to 2.1, the track ~1) and the picture's ~1 s.
