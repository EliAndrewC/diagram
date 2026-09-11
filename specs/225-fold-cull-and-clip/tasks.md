# Tasks - 225 the marks culled, the pad tightened, the opacity folded, the rows clipped

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review FAITHFUL; research R1 (the resvg experiments)
      research: rendering
      verify: DONE. FAITHFUL at round 1 of 5; R1 with the resvg experiments
- [x] T02 FR-003 the opacity fold at finish with its test; FR-005 the merge's precheck; `make map` Inashiro; the tile times
      research: rendering
      verify: DONE. `fold_element_opacity` in finish.py over every record string (stroke-only, fill-only, fill=none, single-subpath path; declines two paints, a paint opacity present, multi-subpath, groups) with its test; `merge_primitives` returns under two elements before the scan; Inashiro's file: 17 element opacities left of 1,237
- [x] T03 FR-001 the marks deferred and flushed with the blades; FR-002 the pad; the pool; the 48-map cohort
      research: rendering
      verify: DONE. `_mark_groups` (dots, pines, tint, glints with extents) flushed into their slot at finish by drop_offmap's rule beside the blades; `SCATTER_PAD` 40 with the argument at the constant; the four pre-finish readers flush first; the pool: the tightest side 39.7-40.2 px, no breach; the 48-map cohort 48 of 48
- [x] T04 FR-004 the rows cut to their plot where convex; Inashiro; the pool
      research: rendering
      verify: DONE. `line_cuts` (general) and `row_cuts` (horizontal) in landuse.py; `_draw_furrows` (the comb's 29 clips on Inashiro) and `_rows_cut_to_plot` (the tea fringe, the vegetable ground) write cut rows, the clip kept for a plot a row meets other than twice; tests; Inashiro's file 30 -> 1 clip; Kuwabata's records move only in draw-position indexes (three veg clips gone)
- [x] T05 FR-006/FR-007: R2; `make done`; the settlement-review; spec IMPLEMENTED; land
      research: rendering
      verify: DONE. R2 (the phase split, the bars mostly missed and named, the bookends band 0); the 48-map cohort 48 of 48 at the 40 px pad; `make done` green (3,550 tests, 100%); settlement-review pass x5 with its records applied; spec IMPLEMENTED; landing under 222 D5's first route (nothing placed moved)
