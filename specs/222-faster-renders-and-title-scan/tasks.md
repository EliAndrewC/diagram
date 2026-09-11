# Tasks - 222 faster renders and an indexed title scan

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review FAITHFUL (D1 put to it explicitly); research R1 (the before, from the profile)
      research: rendering
      verify: DONE. FAITHFUL at round 1 of 5 (D1 legitimate, FR-005 faithful); R1 written from the 2026-09-10 profile; FR-008 added and put to round 2
- [x] T02 FR-004 the title-pocket index: `BoxObstacles` in `_geom/indexes.py`, `_title_obstacles` returns it, `_box_clear` asks it; unit tests against the linear oracle; `make map` Kuwabata byte-identical; FR-008 the duplicate block removed and the pool's moved titles measured
      research: rendering
      verify: DONE. `BoxObstacles` + `box_clear_brute` in `_geom/indexes.py`; `_title_obstacles` returns the index, `_box_clear` asks it; oracle tests (3,000 random boxes, a real manifest sweep); Kuwabata hinterland 10.0 s -> 1.6 s, manifest byte-identical; the duplicate block removed - `make maps`: no title moved on any of the five (manifests differ only in `ink_classes`)
- [x] T03 FR-001 blade groups as merged paths in `cover.py` and `wet.py`; `scatter_audit.py` and `test_wet_ground._marks` read `M x,y`; `make map` Inashiro; the SVG size
      research: rendering
      verify: DONE. `merge_lines` (the writer's merge from the coordinates; `merge_primitives` parsed back cost 1.9 s of the stage) in cover.py and wet.py, held to `merge_primitives`' bytes by a test; scatter_audit + test_wet_ground read `M x,y`; Inashiro SVG 16.39 -> 9.37 MB, resvg 2600 px 2.13 -> 1.18 s on the tiled file
- [x] T04 FR-002 the JPEG picture: `raster.py` child + mime; the raster and finish tests; the `placement_stages.py` note
      research: rendering
      verify: DONE. `PICTURE_FORMAT/QUALITY/SUBSAMPLING/MIME` + `_PICTURE_CHILD` + `encode_picture` in raster.py, the mime in page.py; tests updated; the note names the three lines that reverse it
- [x] T05 FR-003 the three renders concurrent in `finish()` and `render_page`; outputs byte-identical
      research: rendering
      verify: DONE. `finish()` submits `render_png` to a thread after the .svg and joins it after the .json; `render_page` runs the picture and the id map in two threads; outputs unchanged (the pool's manifests differ only in `ink_classes`)
- [x] T06 FR-005 the child's stderr forwarded under `L7R_STAGE_PROFILE`; a test
      research: rendering
      verify: DONE. `rollcache._in_child` forwards the child's stderr under `L7R_STAGE_PROFILE`; `make map ... PROFILE=1` prints the stage profile; a test drives a child that writes to stderr with and without the flag
- [x] T07 FR-006/FR-007: R2 the five hamlets timed as R1; `make done` green; the pool regenerated; spec IMPLEMENTED; land under D5
      research: rendering
      verify: DONE. R2 (totals and the phase split, the misses named); `make done` green (3,521 passed, 100% over 23,615 statements, roll census 5 of 5); the pool regenerated with manifests differing only in `ink_classes`; settlement-review over the five renders and the JPEG pictures logged in each map's notes; spec IMPLEMENTED; landing
