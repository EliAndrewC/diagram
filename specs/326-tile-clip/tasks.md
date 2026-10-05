# Tasks: each tile its own part of the map (feature 326)

**Input**: plan.md (D1-D5)

## Occasions

- none: no map draws or places anything differently - the picture is visually identical, measured (spec, Decisions Recorded)

## Tasks

- [x] T01 the clip per tile (tile_doc) and its tests (D1, D4, FR-001, SC-001)
      research: rendering
      verify: DONE. tile_doc trims classed lines to the tile window by drop_offmap; render_tile builds each document in its worker; tests: the clip drops outside / keeps inside / leaves unclassed, the synthetic tiled picture equals its single render; raster tests 26 green
- [x] T02 the grid measured (4x4 to 7x7 against 3x3) and, by Amendment 1, kept at 3x3; the clipped-against-unclipped A/B; feature 223's note corrected (D2, D5, FR-002, FR-005, SC-002, SC-005)
      research: rendering
      verify: DONE. grids 4x4-7x7 measured against 3x3 (R2); kept 3x3 by amendment 1; A/B clipped 371/365 MB vs unclipped 551/528, span 3.57/3.37 vs 3.13/3.22 s; TILE_MPX note corrected (R3, R4)
- [x] T03 visual identity over every live pool map's picture: clipped tiles against unclipped, each difference counted and bisected, recorded (D3, FR-003, SC-003)
      research: rendering
      verify: DONE. pool: 6 of 11 maps one tile, 3 identical, 2 differ by 34 and 29 channel values at most 10 levels - bisected to anti-aliasing on trimmed paths, visually identical as the GM accepted (R4)
- [ ] T04 make done; both bookends back to back in an arranged window and the records their band owes; claims owed answered (FR-004, SC-004)
      research: rendering
