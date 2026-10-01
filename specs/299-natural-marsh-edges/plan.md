# Plan - feature 299, natural marsh edges

**Spec**: [spec.md](spec.md) - **Request**: [request.md](request.md) - **Research**: [research.md](research.md)

## Design

### A. The shaped outline (`settlement/land/outline.py`, new; called from `marsh()` in `land/wet.py`)

`natural_outline(poly, seed, bs)`: the laid ring as a shapely polygon; ROUNDED by `buffer(-r).buffer(r)` (convex corners become
arcs, nothing is added), `r` halved until the rounding keeps 85% of the area, then cut to the laid polygon; WAVED by moving
points every 8 ft along the rounded ring inward by a depth `D * (0.5 + 0.5 * w)`, `w` the mean of three sines whose lengths are
fitted to whole waves round the ring (so it closes without a step) and whose lengths and phases are rolled from the seed;
the waved polygon cut to the rounded one, its largest piece kept (the rounded one where waving would lose half the area).
The shaped ring is simplified to 1 ft (`SIMPLIFY_FT`) - unsimplified, a large marsh carried about a thousand vertices that
every reader of the marsh walks (the title pocket's box test made Sawada's ground-cover stage 0.45 -> 0.8-1.1 s), and that box
test asks each polygon by row (`RingIndex`, the exact verdict). `marsh()` shapes every role but `pond_fringe`, before `_clipped_to_open_ground` and `drawn_ground`, seeded by
`scope_seed(map seed, "marsh_outline", (role, the ring's first point))`.

### A2. The pond cuts the marsh as its ellipse (`wet.pond_cut`)

The pond's no-build block is a box round its ellipse, kept to stop buildings standing on water; cut from the marsh it left a pale
rectangle round the oval pond (the plan review, BLOCKED round 1). The marsh and its reeds' bare ground are cut by the ellipse
in its place; every other block is kept.

### B. The scrub keeps off the shaped marsh (`hinterland` in `land/cover.py`)

Once a marsh is recorded the scrub is handed no laid toe band (`commons` reads every recorded marsh itself), so the ground the
marsh gives up is scrub, and the two meet.

### C. The fringe and the overlays (`land/tiles.py`, `settlement/finish.py`)

`flush_covers` computes every cover's shape first; then for each scrub (marsh) shape the band within `FRINGE_FT / 2` of any marsh
(scrub) shape is cut out and drawn with the `fringe` tile in the cover's own slot and class; the rest is drawn with its base tile
and, over it, its overlay (`OVERLAYS`: grass -> `grass-clumps` at `OVERLAY_TILE_FT` (97 ft), reed -> `reed-clumps` at
`REED_OVERLAY_TILE_FT` (197 ft, larger than `REED_TILE_FT`)). The reed base tile
grows to `REED_TILE_FT` with an even haze (research R1). `cover_path` writes one even-odd path.

### D. Record, tests, measurement

Research entries 125 (the scrub-marsh edge) and 050 (the scrub's look) and the marsh entries that describe its drawing say what is
drawn; `record-format` on each, `entry-drift` where owed. Tests: the shaping (within the laid ring, no run along it, a pond
fringe untouched), the fringe (only where the two meet), the overlays (each base path has its overlay), Inashiro's manifest
(SC-001), the gate test of feature 298 extended. The pool regenerated and timed against the base.

## Decisions (for the plan review)

| id | decision | class |
|---|---|---|
| D1 | Rounding radius 60 ft, wave 0-40 ft over 180-480 ft (targets 40 ft across, 10-25 ft) | calibration departure, research R1 |
| D2 | The wave is inward-only, cut to the laid outline | within FR-002 |
| D3 | The scrub reads the recorded marsh rather than the laid band once a marsh exists | mechanism for FR-003's meeting |
| D4 | The reed base tile at 128 ft with an even haze | calibration (FR-004's varied look), research R1 |
| D6 | The pond cuts the marsh as its ellipse, not its building box; the SC-001 test's pond allowance is the ellipse and its reed ring | FR-001's cut-outs follow their feature |
| D5 | The overlay in the base tiles' colors, 3 clumps per 97 ft tile, the same density per area on the reed overlay's 197 ft tile | calibration, research R1 |
