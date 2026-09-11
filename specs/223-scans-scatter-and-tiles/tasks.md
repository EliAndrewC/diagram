# Tasks - 223 the two remaining scans, the off-map scatter, and the picture in tiles

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [ ] T01 spec-fidelity review FAITHFUL (D3 put to it explicitly); research R1
      research: rendering
- [x] T02 FR-001 `BambooObstacles` + the sampler on it; oracle test; `make map` Sawada byte-identical
      research: rendering
      verify: DONE. `BambooObstacles` (rects/lanes in PointGrids, polygons as RingIndex + point_in_poly) + `bamboo_blocked_indexed`; oracle test on 4,000 random points; Sawada hinterland 3.7 -> 1.8 s, manifest byte-identical
- [x] T03 FR-002 the wells key once per candidate; order test; `make map` Kuwabata byte-identical
      research: rendering
      verify: DONE. the standing-well walks once per sort, `_key` once per candidate, `worst_after` lifted and held to the nested form; Kuwabata appurtenances 1.1 -> 0.5 s, manifest byte-identical
- [x] T04 FR-003 the blade buckets deferred and flushed at finish with drop_offmap's predicate; the two readers; `make map` Inashiro; the SVG size
      research: rendering
      verify: DONE. `_blade_groups` on the Settlement, the two buckets add a placeholder, `flush_blade_groups` at finish culls by drop_offmap's rule and merges; the three pre-finish readers flush first; unit test; Inashiro SVG 9.37 -> 3.91 MB, blades 259,978 -> 49,465
- [x] T05 FR-004 the picture in pixel-aligned tiles, parallel, stitched in the child; the identity test; `make map` Inashiro
      research: rendering
      verify: DONE. `tile_count`/`tile_boxes`/the parallel tiles in `picture`, the stitch in the encode child; `test_a_tiled_picture_is_the_single_render` (2 x 2 and 3 x 3 byte-identical to the single render)
- [x] T06 FR-005 `RASTER_R` lowered to 2; the picture step and page size at 2 against 3 measured; the DPR-2 consequence and the reversal in the note and the report
      research: rendering
      verify: DONE. `RASTER_R = 2.0` with the note (the DPR-2 cost, the one-line reversal); Inashiro 10.7 -> 9.6 s, page 8.92 -> 6.36 MB, picture 4.51 -> 2.59 MB; R2
- [x] T07 FR-006/FR-007: R2; `make done` green; the pool; the settlement-review's diff; spec IMPLEMENTED; land under D5
      research: rendering
      verify: DONE. R2 (totals and the phase split, the misses named); `make done` green (the full run 3,527 passed and the incremental re-run after the review records 302, 100% over 23,692 statements); the pool regenerated with manifests differing only in `ink_classes`; settlement-review pass x5 with its records applied; the bookends band 0; spec IMPLEMENTED; landing under D5's first route (nothing placed moved)
