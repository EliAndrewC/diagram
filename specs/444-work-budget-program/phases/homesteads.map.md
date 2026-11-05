# The homesteads stage as it stands (feature 444 T30)

Load this file when: you are deriving, planning or porting the homesteads stage - its reads, writes, algorithm, constants, research and repair passes, mapped 2026-11-04 from the Python (an Explore pass; `file:line` as of commit 07ae45d20).

The nucleated path is mapped below. Not read: `track.choose_track_out`, `_sun_corridor_ok`, `_yard_sun_conflict`, `_gardens_sun_ok`, `_wall_on_the_bund`, `_house_on_a_tread`, `_yard_dims`, the overlap registry's `admits`, and the passage walk internals. Where a read's producing stage is inferred from names or comments rather than read, it says so.

Paths: `H` = `/diagram/.clones/diagram-backlog/l7r/diagram/hamletgen/homesteads`, `R` = `/diagram/.clones/diagram-backlog/l7r/diagram/settlement/rolling`, `P` = `/diagram/.clones/diagram-backlog/l7r/diagram/settlement/homestead_parts`.

## Corrections to the brief

- `_place_bundle_nucleated` is in `R/place.py:191`, not `bundle.py`. `bundle.py` holds `_bundle_envelope` (:73), `_bundle_geom` (:80) and `_bundle_layout` (:194).
- `_envelope_blocked` (`R/fit.py:264`), `_parts_fit` (`R/fit.py:309`) and `_site_blocks_rect` (`R/fit.py:245`) are in `fit.py`.
- `try_place` and `_try_place_bundle` are in `settlement/houses.py:446` and `:452`.
- On the nucleated hamlet path `access_corridor` and `route.routed_corridors` are never called. A seat region exists, so `fit._parts_fit` (`R/fit.py:378-382`) calls `SeatRegion.opens` instead. Both calls are kept only for a village roll with no seat region (`R/fit.py:383-387`, `R/access.py:521-528`).
- From `route.py`, only `taut` is used, by `gap_ways._first_admitted` (`R/gap_ways.py:587`). `route.search` is used only by the passage walk (`R/passage.py`).

## 1. READS

**Plan fields**
- `plan.seat` keys `cx, cy, along, out, lat, dep, ladder, offwind` (`H/stages.py:475-499, 305-307`). It is set by `seat_cluster`, stage 4a, per `hamletgen/CLAUDE.md`.
- `plan.spec.households, .seed, .name`; `plan.cluster_shape`; `plan.settlement_form`; `plan.field_archetype`; `plan.manure_form`; `plan.fixtures_min`; `plan.envelope` (field outline); `plan.bamboo` (`H/stages.py:213, 253, 296, 491-492`).
- `plan.settlement_form` is the form switch; `_nucleated` is set from the form in `stage_water_frame` (`H/stages.py:538-541`).

**Settlement attributes from earlier stages** (producing stage inferred, not read)
- Field and ground: `s.field_polys`, `s.block_polys`, `s.hard_polys`, `s.wet_polys`, `s.ellipses`, `s.corridors`, `s.dry_polys` (`H/boundary.py:120-140, 165`; `wood_share.py:173`).
- Water: `s._water_obstacles()`.
- `s.toe_band()`, which is the reed toe laid by hinterland later, so it is derived at seating time (`H/boundary.py:572`).
- Scale and size: `s.bscale`, `s.W`, `s.H`, `s.px()`, `s.ftpx`.
- Knob values: `s.seed`, `s.resolve("byre_form")`.

**Manifest keys read**
- Water and field: `s.M["streams"]`, `["channels"]`, `["moat"]`, `["moat_width"]`, `["dikes"]` (outline), `["dry_plots"]` (`poly`), `["pond"]`, `["crescent_ponds"]`, `["religious"]`, `["shrines"]`, `["torii"]` (`wood_share.py:167-208`, `H/boundary.py:132`). `marsh_ground(s.M)` reads marsh and pond-fringe keys (`H/stages.py:302`, `H/boundary.py:534`).
- `s.M["meta"]` (written, with setdefault).
- Own-written keys read back: `["houses"]`, `["access_corridors"]`, `["access_drawn"]`, `["site_boundary"]`.

**Opt-in state set by this stage's first lines**
- `s.sun_corridor(39 ft)` (`H/stages.py:155`) and `s.west_sun_lane(50 ft)` (`:159`).

**Registries read**
- `s.placed`: placed homestead bboxes, indexed by `_reach_index(self.placed, "placed_reach")` (`R/place.py:341`).
- `s._pending_farmsteads`.
- `s.standing.reserved`: read by `reserve_the_seating` and `Settlement.admits`, which the registry check `bundle_admitted` asks (`R/lot.py:275`).
- `s._seed`, `s._hjit(x, y, salt)`, `knob_rng`.

## 2. WRITES

**Manifest**
- `M["meta"]["house_bearing_deg"]` (`H/stages.py:78`).
- `M["site_boundary"]` = `{chords, water, corridors, rings, holes}` and `["window"]` (`H/boundary.py:590`, `H/stages.py:801`).
- `M["access_corridors"]`: one record per leg, `{pts, of?}`, first leg carrying `of` (`R/access.py:806`).
- `M["access_drawn"]`: legs the drawn run has that the reserved run lacks (`R/access.py:816-822`).
- `M["houses"]` records `{x, y, w, h, kind, rot, role, shed, shed_side, wealth, geom}` (`houses.py:530`).
  - `geom` holds `bbox`, `boxes{house, yard, gardens, shed, byre, well, fixtures}`, `turn`, `opens`, `access`, `passage`, `wood`.
  - Later keys are `byre` and `well_pocket` (`R/lot.py:193`), `fixtures` and `wood_share{seats, r, ft2}`.
  - `reached_across`, `passage_depth`, `passage`, `passage_kind` appear for passage and pinch households.
- `M["way_out_track"]` and `M["way_out_gate"]` (`H/stages.py:224-225`).
- `M["meta"]` keys: `houses_taken_back`, `seat_margin`, `built_share`, `passage_share`, `seat_off_wind`, `seat_search`, `passage_revoked`, `pinch_passages`, `passage_reached`, `cluster_shape`, `cluster_aspect_drawn`, `cluster_seeding` ("grown"), `house_quarter_turns`.
  - `meta.dispersed_seating` is written on the dispersed path only.
- The `Indexed` list is rebuilt: `M["houses"] = Indexed([on_dike ones] + survivors)` (`R/farmsteads.py:142`).
- Drawing writes from `farmsteads`: `M["groves"]` (empty on the nucleated path), yards, gardens, houses via `_attach_yard`, `_attach_garden` and `house` (`R/farmsteads.py:111-116`).

**Plan**
- `plan.cluster_shape` is overwritten with the resolved shape (`:215`).
- `plan.seat` is replaced on a margin-ladder step (`:305`).
- `plan.placed = s.farmsteads()` (the survivor count, `:254`).

**Settlement state left for later stages**
- Left standing:
  - `s.placed` (homestead bboxes).
  - `s.standing.reserved` corridor strips (at `ACCESS_HALF_FT` = 7 ft) and wood seats, which every later placer keeps off (`:333-344`).
  - `s.hard_polys`, which now holds the toe (`H/boundary.py:573-574`).
  - `s.standing` holds from `hold_laid_parts`.
  - `s._house_bearing`, `s._bearing_follow`, `s._household_bamboo`, `s._fixture_forms`, `s._byre_form`, `s._byre_pockets`.
- Cleared at the end (`:230-241`): `_site_chains`, `_site_corridors`, `_free_ground`, `_access`, `_corridor_ground`, `_corridor_tree`, `_corridor_drawn`, `_wood`, `_way_out_anchor`, `_way_out_bearing`, `_seat_region`, `_unreachable`, `_lots`.
- `_byre_form` and the pockets survive so `draft_byres` can draw the stalls.

**Later readers (verified by grep)**
- `way_out_track` is read by `ways/track.py:82` and `ways/tree.py:100`.
- `access_corridors` is read by `ways/tree.py:76` and `ways/last_resort.py`.
- Also read: `way_out_gate`, `wells.py:770` (lanes and corridors), `fixtures` and `well_pocket` (`stage_appurtenances`), `wood_share.seats` (copse plant, belt).
- `site_boundary` is read for the walk-through plate.

## 3. THE ALGORITHM

### 3.0 Stage driver (`H/stages.py:81`)
```
sun_corridor(39); west_sun_lane(50)
placed, cloud = seat_every_household
declare_cluster_shape -> meta, plan.cluster_shape
if _access and _way_out_bearing:
    track = chose_the_track
    M.way_out_track/gate
    for leg in near_the_cluster(track, px(45)): _access.add(leg)
meta.passage_revoked, pinch = lay_the_ways
clear seating state
plan.placed = farmsteads
hold_laid_parts
reserve_the_seating
meta.house_quarter_turns = count of |rot - bearing| > 45
```

`seat_every_household` (`:274`):
```
mark = seating_mark
_seat_households (dispersed trial deep-copy skipped on nucleated)
if placed == 0: walk margin ladder (only when NO house stands)
    skip rungs without a dry exit
    unseat_to(mark)
    reseat
if placed < want: raise SiteRefused
```
- Nothing seated is ever taken back; `houses_taken_back` stays 0.
- The ladder applies only when a margin seated zero houses, for example when `exit_bearing` returns None (`:571-572`).

### 3.1 `_seat_households_as` setup, nucleated (`:446`)
```
install_site_boundary
face_the_houses
_seat_region = None
household_byre_form
install_wood_shares(HOMESTEAD_WOOD_FT2[0]=6000 ft2, reach 90 ft, ACCESS_HALF 7 ft)
fixture_forms, fixture_quota + retirement_quota
_lots = HouseholdLots
_seat_search = {candidates, placer_calls, positions, rects, rounds}
_house_max = (46*1.35, 28*1.10) ft
bound = 1.15 * hypot(lat, dep)   # band_extent(households, cluster_shape, 162 ft)
```
Corridor setup:
- `_corridor_ground`, `_corridor_tree` (`seating_judge`) and `_corridor_drawn` (`seating_drawn`) are installed.
- `_out = exit_bearing(seat, out, length = 1.5*bound + 100)` tries turns 0, ±15 ... ±90 degrees and takes the first line `lawful_ground` admits (`R/access.py:220-236`). None means return 0 and refuse the margin.
- `_access = AccessTree(px(7 ft))` starts EMPTY. Its `routed` flag is True, but `access_corridor` is never called here.
- `_way_out_anchor` is the three points center, center + out*bound, center + out*length (`:583`).
- `_seat_region = SeatRegion(seating_window)`.
- Passage share: `passage_share(seed)` is rolled in 0..0.25. `_passage_left = floor(share * households)`.
- If `byre_form == detached_commons`, the shared-shed pockets are reserved (`reserve_commons_byres`).

### 3.2 Boundary and rasterization (`H/boundary.py`)
`install_site_boundary` (`:556`):
- The toe polygon is appended to `s.hard_polys` once.
- `site_boundary(seat)` returns `chains` (paddy), `water` and `registered` segments, and `rings` and `holes` (everything else).

`site_boundary` construction (`:92`):
- **Paddy chains:** for each field polygon with at least 4 vertices, `facing_chains(poly, seat, FIELD_KEEPOUT_EPS = 3 px)`. These are simplified chords facing the seat, capped at `FACING_CHORD_CAP = 12`; the tolerance is multiplied by 1.5 until the cap holds (`primitives.py:367-380`).
- **Blob members**, unioned with shapely into one outline with holes:
  - `block_polys`;
  - `hard_polys`, `wet_polys` and `dry_plots`, each buffered by `TILT_ALLOWANCE_PX * bscale` (2 px);
  - `s.ellipses` as 24-gon polygons (`ELLIPSE_SIDES = 24`);
  - members under 1 px^2 are dropped.
- **Segment sets:** `water` is `_water_obstacles()` segments at their half-width + 5. `registered` is `s.corridors` segments at their clearance. A segment fully covered by `(fields ∪ blob).buffer(clr)` is dropped.

`SiteCorridors` (`:180`) indexes these in `PointGrid(128)` cells. Each ring also carries a vertex `PointGrid(32)`, and the holes carry a `PointGrid(128)` of boxes.
- `hit_points` asks the water set at all 9 points, and the rings by containment or vertex-in-rectangle.
- `hit_center` asks the registered set at the center only.

`FreeGround` (`:274`):
- Cell is `FREE_GROUND_CELL = 8 px`, on the canvas grid, rasterized over `seating_window`.
- `seating_window` is the seat plus or minus `r = px(2 * 162 * sqrt(households / pi))`, snapped to 8 px and clipped to the canvas (`:551`).
- The union is: each chain chord as a field-side strip of depth `2 * window diagonal`, plus (rings minus holes), plus water `LineString.buffer(clr)`.
- Taken cells are those contained in the union shrunk by 0.5 px. Clear cells are those disjoint from the union grown by 0.5 px. The rest (edge cells) are asked exactly.
- 8x8-cell blocks are tested first (`_BLOCK_CELLS = 8`).
- Cells beyond the window are decided lazily by the same two tests (`_cell_beyond`, `decide_beyond`).
- The registered corridors are not rasterized.
- `rect_refused` asks 9 points against taken cells (`:482`).

`UnreachableGround` (`:489`): `web_hard_ground` (envelope and crops at 3 ft gap, toe, wet) grown by its gap, eroded by `WEB_REACH_FT + 1 = 101 ft`. `refuses` is one point test.

### 3.3 `SeatRegion` (`H/region.py`)
- Cell 8 px, FreeGround's own grid, two `Region` rasters over the window.
- `buildable` holds FreeGround's taken cells, corridor strips at the 7 ft half-width, and the wood seats as radius-1 circles.
- `lane` holds the taken cells plus the water courses painted at `clr - GROW*cell`, and wood seats.
- The reach flood (`_reached`): lane taken cells grown by one cell (`LaneGround`, 8-neighbor), free cells labeled 4-connected (`scipy.ndimage.label`), seeded from the tree segments if any, else from `anchor_in_window` (the way-out anchor stretch past the band).
- The flood is cached and recomputed after each house or corridor change.
- `offer(pts)` is true where at least one of the 4 garden-side envelopes at the smallest house (`LENGTH_FACTORS[0]`, `DEPTH_FACTORS[0]`, unturned, no parts) is clear in `buildable`. The box is shrunk by one cell, and the yard box must touch a reachable cell via a summed-area table. Seats whose boxes leave the window are offered unjudged.
- `opens(geom)` is the same yard-touches-reach test, with the yard grown by `half + cell`.
- The seated homesteads are NOT painted (research R15 says it is slower).

### 3.4 Growth (`H/growth.py:373`)
```
if no houses:
    seats = free_seats(seat center, field=plan.envelope)   # capacity.py:73
        grid pitch 100/3 ft, canvas inset 6 px, drop FreeGround-taken points
        drop points within 50 px of a house
        sort by (round(dist/pitch), field distance, x, y)
    seats = region.offer(seats)
    offer_seats(seats, 0, 1, DRY_SPELL=400)    # 400 offers in a row seating none ends it
```
First house: the free ground nearest the seat center.

Next houses:
```
heap = []; seen = {}; level = 0
while placed < want:
    ndir, rings = grow_level(level)
    for rec in houses[done:]:
        reach = footprint(rec)
        for k in 0..ndir:
            ang = 360/ndir*k + (hjit(hx,hy,300+k)-0.5)*2*(12*8/ndir) deg
            far = 1 + hjit(hx,hy,400+k)*0.12
            base = seat_toward(h, reach, guess, ang, gap)
            for ring in rings:
                q = h + (base-h)*far*ring
                queue if key=(round(q/10)) unseen and on canvas
        if passage_left>0 and crossable(rec): queue tight seats
            yard-side directions only (within 90 deg of the yard bearing)
            at TIGHT_GAP_PX = 2 px, unjittered in distance
    if heap empty:
        if level >= 3 and nothing queued: break   # ground is full
        level += 1; done = 0; continue
    pop key = (int(d // px(20 ft)), field_distance, d)   # ring 20 ft, field breaks ties
    settled_seat(...)       # up to SETTLE_TRIES = 4 moves
    skip if None or within BUNDLE_PITCH*0.5 of a house
    _grown_keep = keeps_its_distance AND keeps_every_gap
    try_place(q, "plain")
```
- `GROW_LEVELS = ((8, (1.0,)), (12, (1.0, 1.5)), (16, (1.25, 1.75, 2.0)))`; past the table it is 16 directions on one ring of `2.0 + 0.5*(level-2)`.
- `footprint` is the bbox, plus wood seats plus a 12 px clump, plus the south sun `px(39 + 2 ft)` below the yard and each bed.
- `grow_gap = px(MIN_WEB_GAP = 18 ft) + TIGHT_GAP_PX = 2`.
- `settled_seat` rolls the full household envelope at the candidate through `household_reach`, which runs `household_parts` then `_bundle_envelope`. It first asks `seat_refused` (house box via `_house_box_refused`, plus `FreeGround.rect_refused`).
- A tight seat needs the passage budget. It is spent when a tight seat is admitted; `_tight_of` is set to `{rec, land, own, gap: 2}`.
- Loop count is roughly one pop per queued seat (the code comment cites 448 queued and 194 offered for 15 households).

### 3.5 Placer, per offered seat (`R/place.py:191`, `houses.py:452`)
```
_try_place_bundle:
    household_parts -> lot k = count of "plain" houses seated
        sizes: px(46)*L, px(28)*D; kura flag, byre flag, fixtures
    _place_bundle sets _household_seat = (x, y)  # layout rolls key on the seat offered
    _place_bundle_nucleated(x, y, hw, hh, shed)
```
1. `placer_calls++`, `positions++`.
2. `_house_box_refused(_house_box)` returns None for:
   - the canvas margin (6 px);
   - `tree.covers_box`;
   - two or more placed boxes within 2 px.
3. `_at[side] = _bundle_geom(...)` for the four sides `_NUC_SIDES = (SE, SW, E, W)`. The union envelope is `_env`. `_union_clear` is `not FreeGround.rect_refused(_env) and _envelope_blocked(_env) is None`.
4. If `_tight_of` is set and not `landlocked(layouts)`, return None.
5. For each side (rank 0 to 3):
   - If the union is blocked, test the side's own box with `rect_refused`, then `_envelope_blocked`.
   - `_envelope_blocked` (`R/fit.py:264`) tests the canvas margin (6 px), `self.bound`, `_rect_blocked` (nine-point `_site_blocks_rect`), `tree.covers_box`, and the placed-box index. The placed-box index is a `_reach_index` over `s.placed` (cell size not read), queried with margin 2 px; it returns the one overlapping box, or True for two or more.
   - On exactly one overlap, apply ONE computed move: shift along the smaller-overlap axis by (overlap + 2 px) away from that neighbor, rebuild the geometry, and re-test. `_grown_keep` must hold or the move is refused.
   - If the seat is unmoved, ask `region.opens(geom)` once per seat.
   - Run `_parts_fit`.
   - Score: `(sum(_garden_shaded), rank // 2, hand)`. The hand is `(rank % 2) XOR (hjit(cx, cy, 12) < 0.5)`. The lowest score wins.

The nine points are the 4 corners, 4 edge midpoints and center (`R/fit.py:256`). `_site_blocks_rect` asks chains at gap 0 only for points not in a `point_clear` cell. A rectangle needs one point in a taken cell to be refused outright.

`_parts_fit` order (`R/fit.py:309-431`):
1. `geom["unlaid"]` refused.
2. `wood.covers_a_seat`.
3. `_sun_corridor_ok`, `_yard_sun_conflict`, `_gardens_sun_ok`, `_persimmon_sun_conflict`.
4. Way of its own: `region.opens(geom)`, or for a tight seat `passage_of` and not `opens`.
5. `_wall_on_the_bund`.
6. `_parts_across_stream`.
7. Farmstead boxes and fixtures against `_rect_hits` of field polygons (persimmon by a 4 ft trunk box).
8. Beds off every ditch (`_rect_on_water`).
9. `bundle_admitted` (registry, `s.admits` per part).
10. `_house_on_a_tread`, `_house_too_near_a_neighbor`, `_house_unreachable`.
11. `wood.share(geom, turn, tree.segs)`; None refuses the seat.

On success `try_place` appends `geom["bbox"]` to `s.placed`, then calls `reserve_way`, then `record_parts` (`wood.commit`), then appends the record to `M["houses"]` and `_pending_farmsteads` (`houses.py:529-546`).

### 3.6 Parts layout (`R/bundle.py:194`)
- House: `px(46)*LENGTH_FACTORS[i]` by `px(28)*DEPTH_FACTORS[i]` from the size ladder, with `LENGTH_FACTORS = (0.85, 1.35)` and `DEPTH_FACTORS = (0.90, 1.10)`. Rung k goes to household k; the ladder is shuffled by seed. Aspect cap 2.7.
- Gap between house and yard or garden: `px(3)`.
- Yard: `_yard_dims(hw, hh, seat)`, a rolled area (not read), centered on the south front.
- Garden: `0.48*hw` by `0.85*hh`, jittered up by `hjit(3)` and `hjit(4)` times 0.25, capped at 44 by 34 ft.
- Sides: SE, SW (south corners), E, W walls. Beds split with probability 0.26: flank (E and W), stacked (south only), or side by side.
- Kura: a north annex, `kura_rect`, when `lot[2]`. Share `KURA_SHARE = 0.125` by count, dealt to the largest houses first.
- Byre: `byre_part` on the flank away from the garden, `BYRE_FT = (16.12, 10.92)`, gap `YARD_SHED_GAP_FT[0] = 6 ft`, when `lot[3]` and the byre form is a household form.
- Fixtures (`lay_fixtures`, `fixture_seats.py`): kinds from the lot, in the order retirement, bath, woodpile, privy, manure, coop, shrine, grave, persimmon. Wall gap 3.5 ft, outward step 8 ft up to 24 steps. The bath is joined to the house. The wood shed stands a ken off a wall. Sizes are rolled per household.
- No grove and no well pocket on the nucleated bundle.
- Rake: each part is carried round the house center by `_house_rot` (common bearing within 11.25 degrees of south, plus MarginBearing, plus a spread of at most 30 degrees). `boxes` are the turned axis-aligned boxes. `bbox` is the union of all parts.
- Template cache keyed on `(hw, hh, side, shed, nucleated, seat, byre, fixtures)`.

Wood share (`P/wood_share.py:332`):
- Lattice of `SEAT_PITCH_BS = 11*sqrt(2)` times `bscale`, within `reach = 90 ft`, sorted by `LATERAL_WEIGHT * u^2 + (v - 0.7*reach)^2` (behind the house first).
- A seat is kept when `seat_barred` is false and its crown (radius `clump/2`, clump 22 bscale, raster cell `2*bscale`) adds fresh cells.
- Stop when crown coverage is at least 6,000 ft2. If it is never reached, return None and the seat is refused.
- Keep-outs: `copse_keepouts` from the house parts. `bars` and `seats` are `PointGrid(64)`.
- `lane_gap = corridor half + max(0.45*clump + 4, crown_reach) + 0.5`.
- Seats are barred by canvas, reach, own keep-outs, other homesteads' keep-outs, hard ground (`ground_blocks`), a stream between seat and house, and corridors.

### 3.7 Corridors and ways (nucleated)
While houses are seated, nothing of a way exists. `reserve_way` (`houses.py:543`) reserves nothing on this path (`passage.reserve_way` is for a passage, not read).

After the last house:
```
track = chose_the_track        # seated_parts stands in for undrawn farmsteads
for leg in near_the_cluster(track, px(JOIN_FAR_FT = 45)): _access.add(leg)
```
- `seated_parts` makes polygons of each house, yard, well, shed, byre, gardens and fixtures, plus octagons of the lane reach round the wood seats (`H/household_ways.py:61-85`).
- The search itself is in `ways/track.choose_track_out`, which I did not read.

`lay_the_ways` (`R/gap_ways.py:439`):
```
L = lane_layers(placed boxes, tree segs)
    cell 5 px, margin 160 px, clipped to canvas
    cover = homestead boxes grown by 7 ft
    site = wood seats by lane_gap + FreeGround taken + edge cells asked exactly
flood: Dijkstra from tree segs, 8-way, step weight 1 + 3*(blocked share within 3 cells), no corner cutting
       stops 400 px past the last homestead's ring
for each house sorted by nearest flood distance:
    _way_for: pop own bbox from placed
        doors = doors_of (forecourt, far edge, two flank doors)
        way_out searches from doors over the household's own open cells, 8-way
        up to GAP_TRIES = 6 distinct exits (18 if knotted); exits within 4 cells of a pick are skipped
        per exit, 3 lay layers: join near (25 ft), join far (45 ft), run on to the way out
        foot gathered onto a junction within 25 ft (KNOT_FT)
        run pulled taut (taut, at most GAP_LEGS = 12 legs, hairpin at 140 degrees)
        admitted = fixtures_clear, parts_clear, lawful_leg, tree_admits (the lane law)
    first admitted: reserve (add legs to tree, M["access_corridors"])
household with none: pinch across nearest reached household's yard
```
Reserve details:
- `access.reserve` (`R/access.py:800`) adds each leg to the tree and records it.
- Drawn legs the reserved run lacks are barred with `tree.bar`, and recorded in `access_drawn`.

### 3.8 Farmsteads (`R/farmsteads.py:50`)
Under `rng_scope("farmsteads")`:
- Groves for every pending record (none on nucleated).
- `_relax_gardens_south`.
- Then per record: `_attach_yard`, `_attach_garden`, `house`.
- Then grove arms (none).

## 4. CONSTANTS and their Research claims

- `SUN_CORRIDOR_FT = 39`: research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html.
- `WEST_SUN_FT = 50`: 0038.
- `SEATING_GROUND_FT = 162` (0285), `COPSE_HOUSE_REACH_FT = 90` (0036), `HOMESTEAD_WOOD_FT2` min 6,000 (0036).
- `BUNDLE_PITCH = 100`: no claim label read.
- `FORM_BOUND`: 1.15 nucleated; GUESS, `H/stages.py:63`.
- `CLUSTER_DRAWN_ASPECT`: round (1, 2), crescent and split (1.9, 4.2), elongated (2.8, 12). GUESS (`H/seat_geometry.py:82`).
- `COMMON_BEARING_DEG = 11.25`: 0029.
- `BEARING_SPREAD_DEG = 30`: not read. The code says "held under 30 degrees" (`H/stages.py:72`).
- `ACCESS_HALF_FT = 7`: DEVIATION on 0246 (`R/access.py:34`).
- `EXIT_TURNS_DEG`: GUESS.
- `TREAD_HALF_FT` 1.5, `TREAD_WALL_FT` 3 (0081), `PART_MARGIN_FT` 0.5 (GUESS).
- `WEB_FABRIC_GAP` 7 (DEVIATION on 0246), `MIN_WEB_GAP` 18 (0081 and 0246), `WEB_CROP_GAP` 3 (0081), `WEB_HARD_GAP` 8 (GUESS), `WEB_REACH_FT` 100 (GUESS).
- `FIELD_KEEPOUT_EPS = 3 px`: cited as feature 140 research R3 (not a questions page).
- Growth:
  - `GROW_JITTER_DEG` 12 and `GROW_JITTER_FRAC` 0.12: GUESS.
  - `GROW_LEVELS`: GUESS.
  - `TIE_RING_FT` 20: GUESS.
  - `TIGHT_GAP_PX` 2 (0081, 0246).
  - `TIGHT_BEARING_DEG` 90 (0246).
  - `WOOD_CLUMP_PX` 12 and `SETTLE_TRIES` 4: unlabeled code comments.
- `DRY_SPELL` 400 and `FREE_SEAT_STEP` 1/3: feature 306 heuristic, "seat search NONE".
- Boundary and region: `ELLIPSE_SIDES` 24, `TILT_ALLOWANCE_PX` 2, `FREE_GROUND_CELL` 8, `SEAT_REGION_CELL` 8, `SiteCorridors` cell 128, vertex grid 32. All "NONE (plumbing)".
- Lot:
  - `LENGTH_FACTORS` (0.85, 1.35) and `DEPTH_FACTORS` (0.90, 1.10): 0029.
  - `KURA_SHARE` 0.125: 0040.
  - `FARMHOUSE_MAX_ASPECT` 2.7: 0029.
- Wood: `COPSE_CLUMP_BS` 22 (0036), `FOCUS_DEPTH` 0.7 (0036 plus "ours"), `LATERAL_WEIGHT` 2 (GUESS), `EAST_LANE_FT` 50 (0038), `BAR_MARGIN_PX` 0.5.
- Fixtures (`P/fixture_seats.py`): `WALL_GAP_FT` 3.5 and `STEP_FT` 8 (GUESS), `FIXTURE_ORDER` (GUESS), `PRIVY_*` (0047), `PRIVY_SUNNY_SHARE` 0.727, `BATH_*` (0044), `PERSIMMON_*` (0046).
- Gap ways (`R/gap_ways.py`):
  - `GAP_CELL` 5, `GAP_MARGIN_PX` 160, `FLOOD_PAST_PX` 400, `RING_CELLS` 4, `CENTER_CELLS` 3, `GAP_TRIES` 6: NONE (breadth, measured).
  - `CENTER_WEIGHT` 3: GUESS.
  - `KNOTTED_TRIES` 3: 0081.
  - `GAP_LEGS` 12: 0081 and NONE.
  - `JOIN_FT` 25 and `JOIN_FAR_FT` 45: GUESS.
  - `KNOT_FT` 25 and `KNOT_MARGIN` 1.0: 0081.
- Passage: `PASSAGE_SHARE_BAND` (0, 0.25) GUESS, `PASSAGE_CHAIN` 2 GUESS, `PASSAGE_ADJOIN_FT` 1 GUESS, `WALK_STEP_PX` 4 NONE.
- Route (only `taut` used here): `ROUTE_REACH_PX` 320, `ROUTE_LEGS` 5, `ROUTE_STEP_PX` 12, `ROUTE_WEIGHT` 1.5.
- Stage: `RANK_DEPTH_JITTER` 0.25 (dispersed only).

## 5. Research pages cited

- 0001: every declared household is drawn, or the site is refused.
- 0004: households per house; no house taken back.
- 0028: farmstead fixtures by quota; the storehouse and sheds go to the larger houses first.
- 0029: farmhouse size ladder, common bearing, the homestead turning as one piece, nearest the seat first, nearer the field as tie-break.
- 0030: the headman keeps an ordinary yard and garden.
- 0031: cluster shapes; the grown irregular cluster; position along the field margin; the scattered line on dispersed.
- 0032: no house refused for distance from the fields; the built share reported.
- 0033: row village (not detailed here).
- 0035: the brook; a farmstead stays on one bank; one bank or both.
- 0036: the homestead wood (6,000 ft2, 90 ft reach); no lane through a grove.
- 0037: threshing yard.
- 0038: sun corridor 39 ft, west lane 50 ft, garden side by sun, 50 ft crown clearance.
- 0039: garden size and splitting.
- 0040: kura one farm in eight.
- 0043: wood shed dealt to larger houses.
- 0044, 0046, 0047: bath, persimmon, privy.
- 0048: byre forms, the shared-shed count 0.22.
- 0058: no house on the toe marsh.
- 0071: the dooryard copse clump and its keep-outs.
- 0074: copse off the marsh.
- 0075: bamboo.
- 0081: village lanes: gaps between plots, joins and knots at 25 ft, tread 3 ft off walls, lane law.
- 0196: wells.
- 0246: the central page: houses before lanes, the ways laid in the gaps, the threading gap, passage across a neighbor's yard.
- 0285: the 162 ft seating ground.

## 6. Repair passes and retry loops

Placed, then moved or removed:
- **One computed move in the placer** (`R/place.py:273-292`): a seat overlapping one neighbor is shifted by overlap + 2 px and re-tested; refused if `_grown_keep` fails.
- **Pushed seat across the brook** (`H/stages.py:384-423`, `_ground_push`, `_tries`). This is on the front-row path, which the grown nucleated path skips (`for _rung in () if _grown`).
- **`settled_seat`**: up to 4 outward moves until the household's rolled envelope clears.
- **`_relax_gardens_south`** (`R/farmsteads.py:183`): moves a drawn bed south in 4*bscale steps up to `bed height + house height + 6` when a neighbor's grove shades its east. It is a no-op on nucleated, which has no groves.
- **`gap_ways._way_for`**: pops the household's own bbox from `placed` while searching, then re-inserts it (`R/gap_ways.py:519-577`). This is temporary, not a repair.
- **Passage revoke**: a tight-seat household later given a real way has `reached_across`, `passage_depth` and `passage` popped and `meta.passage_revoked` incremented (`R/gap_ways.py:483-486`).
- **`unseat_to(mark)`** on the margin ladder, only when no house stands, so no house is ever removed (`:304`).
- **`reserve_the_seating`** and `hold_laid_parts` re-register at the end (bookkeeping, not repair).

Retry and fallback loops:
- Margin ladder: `for margin in ladder if placed == 0`.
- Growth levels widen on a dry heap, ending when a level queues nothing new.
- `FreeGround`'s facing-chains tolerance grows by 1.5 until at most 12 chords.
- The wood share is re-asked with the new corridor standing when a corridor runs over a seat (`R/fit.py:426-427`). This applies only to the corridor-search path.
- Gap-way exits: 6 tries, extended to 18 if only knotted feet are found; a knotted fallback is kept.
- Exit bearing: 13 turns from 0 to ±90 degrees.
- Pinch: a household with no admitted way is reached across the nearest reached household's yard.
- `DRY_SPELL = 400` applies only to the first-house `offer_seats` call (the dispersed exhaustive pass uses it too).
