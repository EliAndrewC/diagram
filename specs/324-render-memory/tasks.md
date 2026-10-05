# Tasks: the render's memory (feature 324)

**Input**: plan.md (D1-D4)

## Occasions

- none: no map draws or places anything differently - the picture, PNG and page are byte-identical (spec, Decisions Recorded)

## Tasks

- [ ] T01 the baseline: the 324-start bookend on unmodified code (plan, Performance bookends)
      research: rendering
- [ ] T02 the child stitches a tile at a time; at most TILE_WORKERS tiles at once; at most RENDER_JOBS maps at once; their tests and claims (D1-D4, FR-001 to FR-004)
      research: rendering
- [ ] T03 the measurements: the child's and the map's peak and render span on the reference render, the render step's peak and wall time, the byte comparison (SC-001 to SC-004)
      research: rendering
- [ ] T04 make done; the 324-end bookend taken alone and the records its band owes; claims owed answered (FR-005, SC-005)
      research: rendering
