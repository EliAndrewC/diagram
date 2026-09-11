# Feature 223 - the two remaining scans, the off-map scatter, and the picture in tiles

**Status**: IMPLEMENTED 2026-09-11 (regen per pool hamlet 11-19 s -> 8-14 s; Sawada's hinterland 3.7 -> 1.8 s, the appurtenances 1.1-1.3 -> 0.5-0.7; the SVG 9.4 -> 3.4-4.5 MB; the picture step 2.8-4.1 -> 1.1-1.6 s as four parallel tiles at `RASTER_R` 2, the page 7.8-8.9 -> 4.3-6.4 MB - research R2). `spec-fidelity` round 1 CHANGES REQUIRED (FR-005 had declined `RASTER_R` on a consequence the GM "did not weigh"; rewritten as the item with the DPR-2 cost priced in D3), round 2 FAITHFUL. Misses reported, not chased: SC-1's Sawada hinterland 1.8 against 1.5 (the scatter's own draw count is what remains), SC-2's 4 MB on Kashikawa and Sawada by under half a megabyte and `drop_offmap` 0.20-0.22 against 0.2 on four maps, SC-3's picture step on Kuwabata 1.61 against 1.5 and the page on Inashiro and Kashikawa 0.2-0.4 MB over 6. `make done` green (3,527 tests, 100% over 23,690 statements).
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - R1 the before (from
specs/222 R2 and the 2026-09-10 profile), R2 the after. **Predecessors**: 222 (the four levers before these;
`merge_lines`, `BoxObstacles`, the JPEG, the concurrent renders), 218 (the scatter's `KeepoutGrid`), 200 (the
picture, `RASTER_R`, the id map), 199 (the tiles the page paints).

## Summary

The GM approved the four items feature 222 left and asked whether anything can be done about the picture's
render time. All four items are done as listed: the bamboo seat scan indexed, the wells' minimax key computed once, the
off-map scatter no longer written, and `RASTER_R` lowered to 2 with its retina consequence priced (D3). The
fifth thing answers the question: the picture is rendered as pixel-aligned
tiles by parallel resvg processes and stitched, which is the same pixels in about a third of the wall time.

## Functional requirements

- **FR-001 The bamboo seat scan is indexed.** `hamletgen/hinterland/bamboo.py` `bamboo_seats` tests fifteen
  sample points per candidate rect against every house-class rect, every lane segment and every polygon edge
  by `bamboo_blocked` - 2.2 million `seg_dist` calls for 9,796 samples on Sawada, 52% of its hinterland
  stage. The lists are built once per call and never change during the scan, so they go into an index built
  once (`BambooObstacles` beside the other indexes in `settlement/_geom/indexes.py`: the rects in a
  `PointGrid` by their padded boxes, the lane segments in a `PointGrid` by boxes inflated by each lane's
  half-width, each polygon as a `RingIndex` with its pad) and each sample asks the index by the same tests
  `bamboo_blocked` makes: a padded rect containing the point, a lane segment within its half-width, a polygon
  containing the point or an edge within its pad, then the margin, the pocket and the pond as today.
  `bamboo_blocked` stays as the oracle; a test holds the index to it on random samples; every stand seats
  where it seated.
- **FR-002 The wells' minimax key is computed once per candidate.** `hamletgen/homesteads/wells.py`'s sort
  key evaluates `_worst_after(c)` and `_extent_added(c)` twice each per candidate, and `_worst_after` re-derives
  every needy house's distance to the standing wells on every call (70,416 calls, 1.2 million terms on
  Kuwabata). The per-house distance to the nearest standing well is computed once each time the pool is
  sorted (the standing wells do not change during a sort), and each candidate's key tuple once, memoized for
  that sort. The numbers are the same numbers, so the order (a stable sort on equal keys) is the same order
  and every well stands where it stood.
- **FR-003 The off-map scatter is not written.** The commons' grass and the marsh's reeds are scattered over
  the whole parcel, and ~90% of the blades lie outside the frame the map is cropped to (specs/200 R2); the
  page drops them (`raster.drop_offmap`, 0.6-1.1 s per map), the file carries them (9.4 MB after 222), and
  the PNG's resvg parses them. The crop is not known when the scatter runs (`stage_frame` follows the
  hinterland), so the two buckets are DEFERRED the way the tree canopies are: the writer adds a placeholder
  at the group's draw position and keeps the blades, and `finish()` - where the view is known - flushes each
  group with exactly `drop_offmap`'s predicate (a blade kept unless it lies wholly outside the viewBox
  plus `OFFMAP_MARGIN`, judged on the same formatted coordinates) and `merge_lines`. The page's own
  `drop_offmap` then finds nothing further to drop from a classed group, so the page is unchanged there; an
  unclassed bucket (a pasture's), which the page never judged, loses its off-map blades on the page too, invisible
  by construction; the SVG and
  the PNG lose ink that the viewBox clipped anyway - invisible by construction. A map with no view keeps
  every blade. The two blade-root readers (`tools/scatter_audit.py`, `tests/settlement/test_wet_ground.py`)
  read the flushed groups.
- **FR-004 The picture is rendered in tiles, in parallel.** `interactive/raster.py` `picture` renders the
  page's SVG once at `RASTER_R` in one resvg process - 2.1-3.6 s per hamlet, and resvg is single-threaded on
  a 22-core box. The picture is split into an n x n grid of PIXEL-ALIGNED tiles (n = the smallest count that
  puts each tile under `TILE_MPX` megapixels - 2 x 2 on every hamlet today, 1 on a page under the bar such as
  the tests' tiny one), each tile rendered by its own resvg process from the same document with the tile's
  viewBox (`--zoom` unchanged, so each tile's pixel grid is the whole picture's), all in parallel, and the
  encode child pastes them into one image before the JPEG. A pixel-aligned tile renders every pixel from
  the same geometry the whole render does, so the stitched picture is the single render pixel for pixel;
  a test compares the two on a forced 2 x 2 split, and the settlement-review diffs them on the pool. The id
  map (zoom 1, 0.3 s) and the PNG (already hidden under the page's work) stay single renders.
- **FR-005 `RASTER_R` is lowered to 2.** `interactive/raster.py`'s `RASTER_R` becomes 2.0, its note recording
  the measurement (the picture step and the page size at 2 against 3 on the five hamlets, R2) and the
  consequence specs/200 R4 recorded - that a DPR-2 screen's opening view of Kuwabata is then past the switch
  scale (screen scale 1.31 x 2 = 2.62 > 2), so such a reader sees the vector page at its opening view and gets
  the picture only zoomed out from it - and naming the one-line reversal. The change is reported to the GM
  with those numbers when the implementation works, per Principle XVI.
- **FR-006 Measured before and after, per hamlet**, the way 222's R2 measured (the same phase marks), with
  the stage profile for the two indexed scans and the tile count, tile render times and stitch time for the
  picture.
- **FR-007 Verification.** `make done` green; the pool regenerated; the manifests differ only in the ink
  census counts (fewer tiles where the off-map blades went); the renders diffed against main's by the
  settlement-review.

## Success criteria

- SC-1 Sawada's `stage_hinterland` under 1.5 s (3.7 s before); Kuwabata's `stage_appurtenances` under 0.7 s
  (1.1 s); no stand, well, house, lane, field, water or title moves on any pool map.
- SC-2 A pool hamlet's SVG under 4 MB (9.4 MB after 222); the page's `drop_offmap` under 0.2 s (0.6-1.1).
- SC-3 The picture step under 1.5 s on every hamlet at `RASTER_R` 2 (2.8-4.1 s after 222 at 3), the stitched
  picture identical to the single render at the same resolution, and the page under 6 MB (7.8-8.9 MB after 222).
- SC-4 Regeneration per pool hamlet down by at least 2 s on every map and 4 s on Sawada (11-19 s after 222).

## Decisions Recorded

- **D1 The off-map cull happens at `finish`, not at scatter time.** The scatter could clip to the content box
  plus the frame's maximum margin instead, and nothing would need deferring - but the crop is decided later
  (`stage_frame`, and `crop_hugs_content` caps its margin at 56 px only for the scripted tier), and a clip
  guessed a few pixels tight would leave a bare strip inside the frame: a visible defect for an invisible
  saving. Deferring costs a placeholder and one flush, the pattern `flush_tree_stands` already uses.
- **D2 The tiles are pixel-aligned on the WHOLE picture's grid.** A tile's viewBox origin is the whole
  picture's origin plus a whole number of picture pixels over `RASTER_R`, and its size a whole number of
  pixels, so resvg rasterizes each tile's pixel from the same geometry-to-pixel mapping the single render
  uses; a stroke crossing a seam is drawn in both tiles with the same coverage on each side. Anything else
  (a tile grid in map units, a margin trimmed after) would resample. Measured, not assumed: the test and the
  review compare the two renders.
- **D3 `RASTER_R` 2, with the DPR-2 cost priced and recorded.** Specs/200 R4 chose 3 over 2 because at 2 a
  DPR-2 screen's opening view of Kuwabata (screen scale 1.31 x 2) is past the switch scale: such a reader's
  first view is the vector page, the paint cost feature 200 exists to remove, and the picture serves them only
  when they zoom out. At 2 the picture has 44% of the pixels (Inashiro 3402 x 3424 = 11.6 Mpx against 26.2),
  so the resvg render, the decode, the JPEG and the page's bytes all fall by roughly that. The GM approved the
  item as listed and their pattern for a visible change to this picture is feature 222's - make it, look, reverse
  it in one line if bad - so it is made; the alternative declined is keeping 3 for retina readers at the full
  render cost. The reversal is `RASTER_R = 3.0`.
- **D4 The tile count follows the pixel area, not the core count.** Each resvg process parses the whole
  document (~0.3 s), so tiles cost parse time in proportion; `TILE_MPX` = 8 puts a hamlet at 2 x 2 and a
  provincial city at 3 x 3, which is where the parse overhead and the raster saving balance on the numbers
  measured (R2), and it is a constant a later measurement can move.
- **D5 The moved manifests land under the two routes 222 D5 set**: ink-census-only changes under the GM's
  2026-08-29 ruling; anything that moves a placed thing is named to the GM (SC-1 says nothing does).

## Review history

- Round 1 (2026-09-11): CHANGES REQUIRED. FR-005/D3 declined an approved item on a consequence the GM "did not
  weigh" - completing the GM's thought, the failure XVI names; the faithful requirement is the item as listed, the
  DPR-2 cost recorded as the priced consequence with the one-line reversal, per feature 222's own pattern. The
  Summary and SC-3 carried the same carve-out. FR-004 faithful to the question (a question whose answer is work);
  nothing else beyond the request. Applied.
- Round 2 (2026-09-11): FAITHFUL - both items closed, nothing added; the SC-1 aside (stricter than the byte-identity ruling) noted.
- settlement-review (2026-09-11), over a snapshot of the rendered pool beside the detached gate: pass on all five - three
  PNGs byte-identical to main's, two within 6 px at a channel delta of 1; the edge-band blade ink pixel-identical (no
  bare strip); the tile seams statistically invisible against an independent single-process re-render; the picture at
  2 px per map px indistinguishable at its display scale; `bamboo_stands` and `wells` byte-identical. Acted on: a notes
  entry per map, `ink_census` and `scatter_audit` say the file now holds on-frame blades only, `flush_blade_groups`
  names the case where a culled bucket under `TILE_MIN` becomes one path, and a fractional zoom renders single (a
  guard with a test) so the pixel-alignment premise cannot be broken by a one-line `RASTER_R` change.
- perf-audit not owed: the bookends read band 0 (223-end vs 223-start -8.3% on the reference's stage total).
