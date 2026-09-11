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

## R2 - the after

(filled at T05)
