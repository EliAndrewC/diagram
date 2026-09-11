# Feature 225 - the marks culled, the pad tightened, the opacity folded, the rows clipped

**Status**: IMPLEMENTED 2026-09-11 (the picture's tiles 0.7-1.3 s -> 0.5-0.7; Inashiro's clips 30 -> 1 and element opacities 1,237 -> 17; the SVG 1.9-2.6 -> 1.5-2.3 MB; regen 7.9-13.1 -> 7.0-12.4; the bookends band 0 - research R2). `spec-fidelity` round 1 FAITHFUL. Most bars missed and reported in R2: the tiles' 0.6 s on two maps, `drop_offmap` + `wrap` under 0.2 s on none (0.23-0.37, the per-string scans), the SVG's 1.5 MB and the hinterland's 0.55 s on none, SC-4's 0.8 s on one map of five. The 48-map cohort 48 of 48 at the 40 px pad.
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - R1 the before, with the
resvg experiments that found where a tile's time goes; R2 the after. **Predecessors**: 224 (the predicted frame,
the breach record, the cohort), 223 (the blades culled at finish, the tiles), 222 (`merge_lines`), 200/199 (the
page's raster and the merge).

## Summary

The three items 224 left, as listed. Item 1, the ring of marks the pad keeps: the scatter's dots, pines, tints and
glints are culled at finish the way the blades already are, and the lateral pad shrinks from 120 px to 40 by
224's own enumeration. Item 2, the picture's tiles: the experiments (R1) found a tile's time is not the pixels
but translucency layers and clip paths - element `opacity` on 1,237 single-paint elements (a layer each in
resvg) and the dry hem's 30 `clipPath`s - so element opacity is folded into the paint's own opacity where that
is the same picture, and the hem's rows are cut to their plot at write time instead of by a clip. Item 3, the
per-string scans: fewer elements reach them after item 1, and a string with under two primitives skips the
merge's scan. Each is measured.

## Functional requirements

- **FR-001 The scatter's marks are culled at finish like the blades.** `land/cover.py` `commons` (the grass
  branch: brush dots and pines) and `land/wet.py` `marsh` (the wet tint discs and the glints) write their marks
  into the record stream at scatter time; ~90% lay outside the frame until 224 clipped the throw, and the 120 px
  ring the pad keeps still holds 58% of Inashiro's dots. Each mark is now kept as (its extent, its string) in a
  deferred group with a placeholder at the draw position, and `finish()` writes the group with `drop_offmap`'s
  rule (kept unless wholly outside the viewBox plus `OFFMAP_MARGIN`), exactly as `flush_blade_groups` does -
  one flush for both kinds. The woodland branch's crowns are recorded features and stay as they are. The page's
  own `drop_offmap` then finds nothing more to drop from those groups.
- **FR-002 The lateral pad is 40 px.** `SCATTER_PAD` 120 -> 40: 224's R3 enumerated every hard feature placed
  after the hinterland and found none that grows the crop laterally, so the pad's only job laterally is to let a
  mark centered just outside the view still paint into it - the widest mark is the wet tint at 28 px radius.
  `TITLE_BAND_ALLOWANCE` stays 140 on the north. The breach record, the pool test, the cohort and the report
  line are the guard; the 48-map cohort is run again (R2).
- **FR-003 Element opacity is folded into the paint's opacity where the picture is the same.** An element with
  ONE paint - a stroke-only `<line>`, a fill-only `<circle>`/`<ellipse>`/`<rect>`/`<polygon>`, a stroke-only
  shape with `fill="none"`, a single-subpath `<path>` with one paint - draws the same pixels under
  `stroke-opacity`/`fill-opacity` as under `opacity`, but resvg (and a browser) composites `opacity` through a
  layer and folds the paint opacity into the paint. Measured on Inashiro's page document (R1): a full render at
  zoom 2 1.35 -> 1.02 s, a quarter tile 0.75 -> 0.44 s. `finish()` folds the attribute on every such element in
  the body before writing (one regex pass; an element with both paints, a `stroke-opacity`/`fill-opacity` already
  present, or a multi-subpath path is left alone), so the SVG, the PNG, the picture, the id map and the browser
  all read the folded form; a test holds the fold to the rule and the review diffs the renders.
- **FR-004 The dry hem's rows are cut to their plot at write time.** The 29 clips on Inashiro are the comb's own
  dry-plot rows (`fields/comb.py`, lines at the field's angle inside a `<g clip-path>` per plot); the tea fringe's
  and the vegetable ground's rows (`fields/landuse.py`, horizontal) are the same construction on the maps that
  carry them. Each clip costs resvg a layer: removing them took a quarter tile 0.74 -> 0.44 s (R1). A row is a
  line and a plot a convex polygon, so the row's ends are the line's two crossings of the polygon's edges and the
  clip is not needed (`line_cuts`, and `row_cuts` for the horizontal case); a plot that is not convex (a row that
  meets its edges other than twice) keeps the clip. The
  difference is at a row's ends where a plot's edge is slanted - a butt cap where the clip cut along the slant, a
  sliver under a stroke width - within the GM's 2026-09-08 ruling; the review looks. The mulberry-dike
  bank clip (`landuse.py` `_cid("mb")`, one per dike POND - Kuwabata's ponds, whose tile is the slowest) is
  measured in R2 and left as it is in this feature: its clip is a rounded bank outline, not a convex row cut.
- **FR-005 The page's per-string scans.** `wrap`'s `merge_primitives` scans every classed string for primitives
  before deciding there is nothing to merge; a string with fewer than two self-closing elements (a C-speed count)
  returns at once. `drop_offmap` is re-measured after FR-001 removed most of what it walked; further work on it
  is reported, not done, if the number is under 0.1 s.
- **FR-006 Measured before and after, per hamlet** (224's phase marks): the picture's tiles, `drop_offmap`,
  `wrap`, the flush, the hinterland stage, the SVG size, the regen total; the cohort's verdict.
- **FR-007 Verification.** `make done` green; the pool regenerated; a settlement-review of the five maps (the
  texture re-rolls again under FR-002; the rows' ends under FR-004; the folded opacity under FR-003).

## Success criteria

- SC-1 The picture's tiles under 0.6 s on every hamlet (0.7-1.3 after 224) and the PNG render (single, 2600 px)
  at least 25% faster.
- SC-2 `drop_offmap` + `wrap` together under 0.2 s on every hamlet (0.25-0.38 after 224).
- SC-3 A pool hamlet's SVG under 1.5 MB (1.9-2.6); the hinterland stage under 0.55 s (0.6-0.7).
- SC-4 Regeneration per pool hamlet down by at least 0.8 s on every map (7.7-13.1 after 224); no breach on any
  pool map or cohort seed.

## Decisions Recorded

- **D1 The fold is a finish-time pass, not an emitter sweep.** Six emitters write element `opacity` on a line and
  more on other shapes; a sweep would miss one and a rule at one place cannot. The pass is exact by SVG's own
  semantics for a single-paint primitive and declines everything else.
- **D2 40 px laterally, by 224's enumeration and the widest mark.** The pad's lateral purpose after R3 is only
  the mark radius; 40 covers the 28 px tint with room. The north keeps the band allowance. A later placer that
  grows the crop laterally after the hinterland breaks the premise, and the breach machinery says so.
- **D3 The rows are cut geometrically only where the plot is convex.** Two intersections per row is the convex
  case and the only one the cut is exact for; a concave plot keeps its clip rather than get a wrong cut.
- **D4 The moved manifests land under 222 D5's routes**; the texture re-rolls (224 D1) and the review judges.

## Review history

- Round 1 (2026-09-11): FAITHFUL - FR-003/FR-004 the only available way to do item 2 (the cost is in the document, not the tiling); FR-002 the item itself (the pad is what keeps the ring), argued from 224 R3; nothing beyond the three. Asides: name `drop_offmap`'s number and decision in the report; SC-1's PNG and SC-3's size are consequences, a miss there is a reported miss.
