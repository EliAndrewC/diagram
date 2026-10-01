# Plan - feature 298, tiled ground cover

**Spec**: [spec.md](spec.md) - **Request**: [request.md](request.md)

## Technical context

Python 3.14, numpy, shapely, the settlement engine's record streams (`settlement/core.py`: `add` appends to `self.out`, with a
parallel `out_cls`), and the finish's splices (`settlement/finish.py`: blocks inserted at recorded indexes, highest first). The
existing `<pattern>` fills (`drycrop`, `fallow`, `core._header`) are the precedent; resvg, the page's rasterizer and browsers all
render them.

## Constitution check

- X.15 (build the blocked ground once): each zone's bare ground is built ONCE as a shape from the keep-outs the scatter already
  files (`KeepoutGrid`), not tested per point - the per-point throw is what goes.
- XII (decisions recorded): the three covers are map drawing conventions; the record entries that describe the glyphs are edited
  (research/vegetation, research/water) and the modals' prose (`interactive/classes/greenery.py`) checked by `entry-drift`.
- XIII (no regressions): the base worktree `/tmp/base298` at the commit before this feature's code is the baseline;
  measured before/after back to back.
- XIV: a defect found on the way is fixed in the work.

## Design

### A. The cover tiles (`settlement/land/tiles.py`, new)

`cover_pattern(kind, bs) -> (id, svg)`: one `<pattern patternUnits="userSpaceOnUse">` per kind and scale, its glyphs laid once
from a fixed seed with the scatter's own glyph shapes, colors, stroke and density per area:

| kind | tile | glyphs per tile (the scatter's density) |
|---|---|---|
| `grass` | 64 x 64 ft x `bs` | a throw per 74 sq ft: ~55, 14% brush dots (`#94A063`, r 1.5-2.4), the rest three-bladed tufts (`#A7A860`, 0.8 wide, 2.4-4.2 long, +/-0.45 rad) |
| `reed` | 64 x 64 ft x `bs` | a tint per 360 sq ft (`#9FBBAE`, 0.14), a tuft per 150 sq ft: 12% glints (`#C2D6CE` ellipses), the rest four near-vertical reeds (`#6E9377`, 0.8 wide, 4-7 long, +/-0.2 rad) |
| `bamboo` | 4 x 7 ft wide, 4 rows of 0.86 x 7 ft, x `bs` | the stand's own jittered grid (`bamboo_stand`), one `bamboo_mark` per seat |

A glyph whose extent crosses the tile's edge is drawn again at the opposite edge, so the tile is seamless. The tile has no
background: the land shows between the glyphs as it does between today's.

### B. The cover zones (record at the scatter, draw at the finish)

`Settlement._covers: list[Cover]` - `kind`, `cls`, the zone's ring, and its bare ground as a shapely geometry. Recorded where the
scatter was:

- **`commons`** (every role that threw blades: commons, grazing, pasture - pasture keeps its unclassed ink as today): the bare
  ground is `KeepoutGrid.shape()` of `_commons_keep(...)` (new method: the union of every filed keep-out at its pad - rings
  buffered by their pad, segment corridors by their half-width, rects, circles), every marsh's ground (`marsh_ground`), the
  crescent ponds and the pond. `grass_scatter`'s throw goes; the scraggly pines stay as they are (thrown, tested, culled).
- **`marsh`**: the zone is the drawn ground (`drawn`), the bare ground the marsh's `KeepoutGrid` shape at the tuft's pads (dike
  crests, pond banks, watercourses, crescents, pond). `_throw`, `offer_rethrow`, `throw_again` and the hinterland's
  `throw_to_the_view` registry go; the marsh files no scatter frame.
- **`_cull_cover_in(ring)`** (a clearing swept later): adds the ring to every waiting cover's bare ground, in place of culling
  blades.

`flush_covers()` (in `finish()`, where `flush_blade_groups` ran): each cover's shape = ring minus bare ground, clipped to the view
plus `OFFMAP_MARGIN`; an empty shape draws nothing. `_header` RESERVES the slots right after the land `<rect>` - the tiles'
`<defs>`, then the scrub, a pasture's (unclassed, as its blades were) and the marsh - and the flush writes each cover's `<path
fill-rule="evenodd" fill="url(#...)">` into its class's slot: below everything else (FR-004), and with no splice, so no recorded
z index shifts. Grass before reed, so a marsh's fill is above any scrub fill (they do not overlap by construction). Each scrub cover's shape is recorded on its commons record
(`cover`, rings rounded to 1 decimal) for the page.

`_blade_groups`, `flush_blade_groups`, `_blade_starts` and their consumers go: nothing else threw blades. `_mark_groups` stays
(the pines, woodland crowns).

### C. Bamboo stands (`homestead_parts/stands.py`)

`bamboo_stand` draws one `<path>` of the stand's ring filled with the `bamboo` tile inside its `<g class="bamboo">`, at its
present place in the stack; `marks` stays the count of the grid's seats inside the ring (the record's reader, the stand's size
in marks). The windbreak grove's culms (`groves._draw_grove`) are untouched (FR-006).

### D. The page

- `HIT_FROM_MARKS` and `marks_region` go: the scrub's hit region is its recorded cover shape (`HIT_REGIONS` reads `commons[].cover`
  for the scrub roles) - which is exactly the ground the GM asked the highlight to keep to (blank village ground is not in it).
- The `premerged` blade path in `render_page` goes.
- The census: each cover path carries its class, so no new unclassed ink.
- The modals (`interactive/classes/greenery.py`) say the cover is a repeating pattern.

### E. Tools, tests, docs, record

- `tools/scatter_audit.py`: the blade, dot and reed families retire (nothing to parse); pine and crown stay.
- Tests: the blade/reed/dot tests are rewritten against the covers (a cover per zone, its shape leaves out a clearing, the tile is
  seamless and at the stated density, the block is right after the land); the re-throw tests retire with the re-throw.
- `tools/placement_stages.py`: its watermark list names `_covers` in place of `_blade_groups`.
- `dev/performance.md`: the blade-merge section gets a closing note; research/vegetation and research/water entries that describe
  the glyphs say the cover is a tiled pattern (a map drawing convention); `entry-drift` on each modal written from them.

### F. Measurement

`stagemin.sh` (best of three per stage, `make map PROFILE=1`), the base and the clone back to back on the five pool hamlets, and
the file sizes - into `measurements.md` with dates, methods and loads.

## Decisions (for the plan review)

| id | decision | class |
|---|---|---|
| D1 | Tile size 64 ft (grass, reed); bamboo the stand's grid | map drawing convention; the GM does not mind repetition |
| D2 | The density per area is the scatter's interior density (no feather) | the same look inside a zone |
| D3 | Bare ground left out of the shape by geometry, not only by layering | FR-005; the GM's fallback "lay that down as its own rendered thing" is not needed where the bare ground is never painted |
| D4 | Bamboo fill stays at the stand's place in the stack | it draws exactly where today's marks draw, so nothing over or under a stand changes |
| D5 | Pasture's cover stays unclassed, as its blades were | no new class without its explanation |
