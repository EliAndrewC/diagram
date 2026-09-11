# Plan - 223 the two remaining scans, the off-map scatter, and the picture in tiles

Spec: [`spec.md`](spec.md). Engine code (`hinterland/bamboo.py`, `homesteads/wells.py`,
`settlement/land/cover.py`, `land/wet.py`, `settlement/finish.py`, `_geom/indexes.py`, `interactive/raster.py`),
so the GATED route and a green `make done`.

## Constitution Check

VI: motivating maps first (Sawada for FR-001, Kuwabata for FR-002, Inashiro for FR-003/FR-004), then the pool.
X clause 15: the two scans move onto the index family; the plan says how (FR-001, `BambooObstacles`). X clause 5:
every new line covered (index and key tests against the oracles, the flush by the finish tests, the tiles by a
forced split). XII: every decision recorded (D1-D5); rendering only. XIII: no regression; the moved manifests
diagnosed. XVI: the spec reviewed against the request; D3 put to the reviewer.

## Order

1. FR-001 (`BambooObstacles`, `bamboo_seats`), oracle test; `make map` Sawada byte-identical.
2. FR-002 (the memoized key), a test that the order is the linear form's on a synthetic pool; Kuwabata.
3. FR-003 (the deferred buckets, `flush_blade_groups`, the two readers); Inashiro; the SVG size.
4. FR-004 (`picture` in tiles, the stitch in the child); the identity test; Inashiro.
5. FR-005 the `RASTER_R` 2 measurement.
6. R2 in the phase-marked worktree; `make done`; the pool; the review; land.
