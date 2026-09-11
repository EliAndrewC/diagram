# Plan - 222 faster renders and an indexed title scan

Spec: [`spec.md`](spec.md). Engine code throughout (`settlement/land/cover.py`, `settlement/land/wet.py`,
`interactive/raster.py`, `interactive/page.py`, `settlement/finish.py`, `settlement/_geom/indexes.py`,
`pipeline/rollcache.py`, `tools/scatter_audit.py`), so the GATED route and a green `make done`.

## Constitution Check

- I/II not applicable (no webapp). VI: `make done` once at the end; the motivating maps first (`make
  map` on Kuwabata for FR-004, Inashiro for FR-001/2/3), then the pool by `make maps`. X clause 15: the
  overlap check this touches (the title-pocket scan) moves onto the existing index family; the plan says
  how it is indexed (D4). X clause 5: every new line is covered (the thread path by the existing
  `renders` test, the index by unit tests against the linear oracle, the JPEG by the raster tests). XII:
  every decision is recorded (D1-D5); no physical research - all rendering. XIII: no regression; the
  moved manifests are diagnosed (ink census counts only). XIV: FR-005 fixes the found defect. XVI: the
  spec is reviewed against the request before implementation; D1 is put to the reviewer explicitly.

## Order

1. FR-004 the index (`indexes.py` `BoxObstacles`, `finish.py` `_title_obstacles`/`_box_clear`), unit
   tests against `_box_clear`'s old body kept as the oracle; `make map` Kuwabata, byte-identical manifest.
2. FR-001 the blade groups (`cover.py`, `wet.py` call `merge_primitives`; `scatter_audit.py` and
   `test_wet_ground._marks` read `M x,y`); `make map` Inashiro; the SVG size and the ink census.
3. FR-002 the JPEG (`raster.py` `picture`/the child/`data_uri` mime; tests; `placement_stages.py` note).
4. FR-003 the concurrency (`finish.py`, `page.py` `render_page`).
5. FR-005 the forwarded stderr (`rollcache._in_child`) and a test that a child's stderr reaches the
   parent's under the flag.
6. R2: the five hamlets timed as in R1; `make done`; the pool; land.
