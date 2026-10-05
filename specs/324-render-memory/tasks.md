# Tasks: the render's memory (feature 324)

**Input**: plan.md (D1-D4)

## Occasions

- none: no map draws or places anything differently - the picture, PNG and page are byte-identical (spec, Decisions Recorded)

## Tasks

- [x] T01 the baseline: the 324-start bookend on unmodified code (plan, Performance bookends)
      research: rendering
      verify: DONE. 324-start bookend on unmodified code at 8c61b03ae (dev/perf-log, taken before the first engine edit)
- [x] T02 the child stitches a tile at a time; at most TILE_WORKERS tiles at once; at most RENDER_JOBS maps at once; their tests and claims (D1-D4, FR-001 to FR-004)
      research: rendering
      verify: DONE. child stitches a tile at a time; TILE_WORKERS = 3; RENDER_JOBS = 4 and the --jobs help; tests: tile cap counted (red uncapped at 9), default jobs 4 / 2 cores / explicit 7; both files 51 green
- [x] T03 the measurements: the child's and the map's peak and render span on the reference render, the render step's peak and wall time, the byte comparison (SC-001 to SC-004)
      research: rendering
      verify: DONE. child 300 -> 188/190 MB; map peak ~970 -> 571/580 MB; span 2.2 -> 3.2-3.6 s; PNG and page byte-identical; render step 1,725 -> 1,121 MB, p90 737 -> 434 MB, 91 s under load (research.md R3)
- [ ] T04 make done; the 324-end bookend taken alone and the records its band owes; claims owed answered (FR-005, SC-005)
      research: rendering
