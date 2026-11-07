# T42 brief: what the Rust hamlet driver must reproduce (read from the deleted Python at e660ff77d, 2026-11-07)

Load this file when: you build or change the Rust driver (T42).


All "py:NNN" line numbers below are in the deleted Python at `e660ff77d`; the `.rs` paths are at HEAD. `HamletSpec` and `plan_site` are in `l7r/diagram/hamletgen/plan.py`. The tables are in `consts.py`, `consts_water.py` and `consts_fields.py` in the same directory, plus the grove tables in `settlement/homestead_parts/grove_sides.py`.

## 1. Spec

`HamletSpec` is at plan.py:90-146. Required fields are `name` and `seed`. `households` defaults to 15 and is limited to 10-20 (plan.py:175).

**Fields the six stages read:**
- `down_deg`, `water_flow`, `windward` (default "NW"), `water_sink`, `intake`, `brook_side`
- `cluster_shape`, `settlement_form`, `field_archetype`, `pond_layout`, `dike_crop`, `leftover`
- `pins`, a dict of knob pins (plan.py:146)

**Fields no kept stage reads:** `lane_skeleton`, `lane_web`, `bamboo`, `fixtures_min`, the grove and row fields, `well_siting`, `farm_water`, `manure_form`, `copse_siting`, `kosatsuba_siting`, `byre_form`, `pond_bank`, `plot_size` (read, but only through the roll), `grain_drift`, `woodland_patches`, `harvest_weather`.

**The five pool hamlets** (`pool/hamlets/<n>/<n>.gen.py`, line 25-45, `HamletSpec(...)`, all other fields default):

| Hamlet | Arguments |
|---|---|
| Inashiro | seed=4, households=15, down_deg=90, water_sink="pond", settlement_form="nucleated", fixtures_min={"shrine":1} |
| Kashikawa | seed=3, households=20, down_deg=315, water_sink="offmap", brook_side=-1, bamboo="both", byre_form="yard_shed" |
| Kuwabata | seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry" |
| Mizuguchi | seed=23, households=12, down_deg=0, water_sink="pond", byre_form="courtyard" |
| Sawada | seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys", pins={"paddy_rest":"unsettled"}, harvest_weather="changeable" |

Only Kuwabata is a polder. The other four are `valley_paddy` combs.

## 2. `plan_site` (plan.py:544-672)

**Computed in Python, before stage 1:**
- **Archetype:** `spec.field_archetype`, else `_roll(seed,"field_archetype",ROLLED_ARCHETYPES)`, which is always `valley_paddy`.
- **Pond layout:** `pond_layout` for the dike-pond archetype only (spec value, else rolled from `POND_LAYOUTS=("mosaic","mosaic","grid")`). Every other archetype gets `"grid"`.
- **Windward:** `spec.windward or "NW"`.
- **Water flow:** `spec.water_flow`, else `down_deg`.
- **Flood ground:** `flood_ground` is true for a polder archetype or the `dike_top` form.
- **Acreage:** `target_acres = households * 1.3`.
- **Offtakes:** `offtakes_for(households)` reads `OFFTAKE_LADDER`.
  - Under 11 households: a=(.36,.93), b=(.55).
  - Under 21: a=(.30,.62,.93), b=(.55).
  - Otherwise: a=(.26,.52,.78,.93), b=(.6).
- **Canvas:**
  - `canvas_for(acres, 1.0)`: `span = round(2*sqrt(acres*43560/0.40)/50)*50`.
  - `W = H = round((span*1.44 + 2*seat_room(hh,cluster_shape))/50)*50`, where `FAN_OVERHANG=0.22`.
  - `seat_room = dep + 12 + max(lat, 0.7071*lat + dep + 146)`.
  - `band_extent` (plan.py:383) gives `(dep, lat)`: `asp = {round:2.2, crescent:3, elongated:5, split:3}`; `dep = clamp(sqrt(hh*104²/(asp*π)), 112, 300)`; `lat = clamp(hh*104²/(π*dep), 240, 1100)`.
  - Linear and dispersed forms multiply W and H by `LINEAR_CANVAS=1.0`, which changes nothing.
- **Scale:** `ftpx = 1.0`, so 1 ft is 1 px everywhere. `field_span` is unused by the stages.
- **Rolls through `knob_rng`** (plan.py:324-331, `choices[knob_rng(seed,name).randrange(len)]`):

| Knob | Table |
|---|---|
| `fan_aspect` | (0.88, 0.95, 1.0, 1.08, 1.16) |
| `head_lead` | (80, 105, 130) |
| `dike_crop` | (mulberry×3, fruit×2, tea) |
| `leftover` | (rice, pond) |
| `fry_form` | (none×3, fry_village) |
| `woodland_patches` | (2,3,3,4) |

- `dike_crop`, `leftover` and `fry_form` roll only for the dike-pond. They are otherwise "mulberry", "rice" and "none".
- `pyrand.rs` provides `knob_rng`: SHA-256 of `"{seed}\0{name}"`, first 8 bytes as the MT19937 seed.

**From Rust (`rust/phases/src/water_frame.rs`, `roll_plan` / `stage_water_frame`):** the fall and 21 knobs.
- **Call:** `stage_water_frame(seed, windward, cardinal=archetype in POLDER, fall_pinned=spec.down_deg is not None, forms, knobs)`.
- **Fall:** drawn from `admitted(windward, cardinal)` with `knob_rng(seed,"down_deg")`. A pinned fall passes through unchanged.
- **`knobs`:** a list of `(name, n_forms, pinned, branch)`.
- **Pins:** a pinned knob takes the spec value. Off-branch knobs take table[0], except `row_line`, which is "edge" on flood ground. `settlement_form` always rolls first.

**Order and branches** (py:461-483): `settlement_form`, `cluster_shape`, `water_sink`, `lane_skeleton`, `lane_web`, `bamboo`, `grove_sides`, `grove_flank`, `row_line`, `row_sides`, `row_water`, `row_shelter`, `well_siting`, `farm_water`, `manure_form`, `copse_siting`, `kosatsuba_siting`, `plot_size`, `grain_drift`, `intake`, `brook_side`.
- **Branch codes:**
  - `intake` and `brook_side` use "brook". That means "all" unless the archetype is a polder, then "off".
  - `row_*` is "linear".
  - `farm_water` is "dispersed".
  - `grove_*` is "not_nucleated".
  - `lane_web` is "not_dispersed".
  - All others are "all".
  - `row_line` goes "off" on flood ground.

**Tables** (consts*.py lines in parentheses; weights are repeated entries):
- `SETTLEMENT_FORMS` = nucleated×5, dispersed×3, linear×2 (consts.py:511)
- `CLUSTER_SHAPES` = (round, round, elongated, crescent) (consts.py:335)
- `SINKS` = (pond, pond, offmap) (consts_water.py:174)
- `LANE_SKELETONS` = (spine, T, Y, cross); `LANE_WEBS` = (alleys, back_lane)
- `BAMBOO_FORMS` = (homestead, homestead, thicket, both, none) (consts.py:566)
- `GROVE_SIDES` = (2,2,2,2,2,3,3,3,4,4); `GROVE_SIDES_FLOOD` = (2)×15 + (3)×9 + (4)×16; `GROVE_FLANKS` = (-1, 1)
- `ROW_LINES` = (street, edge); `ROW_SIDES` = (one, both); `ROW_WATERS` = (own, shared); `ROW_SHELTERS` = (own_grove, sheltered)
- `WELL_SITINGS` = (lane, cluster); `FARM_WATERS` = (channel, well); `MANURE_FORMS` = (heap, pit)
- `COPSE_SITINGS` = (among_the_houses); `KOSATSUBA_SITINGS` = (frontage)
- `PLOT_SIZES` = (small_irregular, medium, medium, large_block)
- `GRAIN_DRIFTS` = (-8,-4,0,0,4,8)
- `INTAKE_FORMS` = (weir, open) (consts_water.py:19)
- `BROOK_FLANKS` = (1, -1) (consts_water.py:29)

**These tables are not in `l7r/diagram/knobs.json`.** That file is the settlement knob registry only (forms, default, weights, typing-rule source). It holds none of the hamletgen consts. Its `bamboo` has 4 forms against the 5-entry roll table. The driver must embed the tables above.

**Only these plan fields reach the six stages:**
- `down_deg`, `water_flow`, `windward` / `wind`, `water_sink`, `cluster_shape`
- `plot_size`, `intake`, `brook_side`
- `fan_aspect`, `head_lead`, `offtakes_a/b`
- `W`, `H`, `ftpx`
- `field_archetype`, `pond_layout`, `dike_crop`, `leftover`, `fry_form`

The other rolls (`lane_*`, `bamboo`, `grove_*`, `row_*`, `well_siting`, `farm_water`, `manure_form`, `copse_siting`, `kosatsuba_siting`, `grain_drift`, `woodland_patches`) only fill the manifest meta (`water/skeleton.py:65-120`). Each draw is independent by knob name, so they can be rolled for the manifest without affecting the rest.

## 3. Doors

**Stage 1, `water_frame`.** Python wrote only meta: `generated_by`, `name`, `scale="hamlet"`, `ftpx`, `households`, `water_flow`, `down_deg`, `windward`, `wind_source`, the rolled forms, and `intake` / `brook_side` (None on a polder). It also set `water_kind="stream"`.

**Stage 2, `field`** (`field/py.rs`; `field_stage.py`). The pure-Rust entries are `field::build::build(&FieldIn)` and, for the polder, `polder::polder`, `dike::dike`, `polder::outfall`, `polder::rest`, `landuse::{inset,convert}`.
- **`FieldIn`** (build.rs:49):
  - `seed`, `households`, `down_deg`, `aspect=fan_aspect`.
  - `center=(W/2,H/2)`, `canvas=(W,H)`, `brook_side` as f64.
  - `brook` = (`head_lead`, `OFFTAKE_DEG` 35, `BROOK_TAP_RUN` 70, `BROOK_SLEW` 22, `BROOK_SKIRT` 34, `BROOK_WANDER` 10, `station` 20, `w` 5.25). `BROOK_WANDER_STEP` is not passed.
  - `offtakes`.
  - `weir` = (`WEIR_HALF`, 30, `{fence:1.5, gabion:2, frame:5, crib:5}`), with `WEIR_HALF = 5.25/2/cos30° + 1`.
  - `row_ft = lattice::row_ft_for(plot_size)` (40 small, 60 large, else 48); `cell = row_ft*31`.
  - `knobs`.
- **Knobs are a Python-side computation.** `_knob_tables` (py:71-90) rolls each knob in Python with `roll_knob(seed,name,len(forms),weights)` and passes `(name,[pin],[],pin)`. The Rust `rolled()` (build.rs:166) can instead take forms plus weights.
  - Order: `town_nearness`, `winter_crop`, `fan_middle`, `paddy_rest`, `plot_regularity`, `weir_form`, `intake_place`, `intake_siting`, then `("intake",[plan.intake],[],plan.intake)`. `grave_form` is not in the registry and is skipped.
  - Forms and weights (`knobs.json`):
    - `town_nearness`: near, far, even.
    - `winter_crop`: barley, none, [.5,.5].
    - `fan_middle`: wild, cleared, [.75,.25].
    - `paddy_rest`: settled, unsettled, [.8,.2].
    - `plot_regularity`: only "organic" survives. The typing rule needs `field_origin=="planned"`, which hamlets never set.
    - `weir_form`: fence, gabion, frame, crib, even.
    - `intake_place`: shoulder, center.
    - `intake_siting`: bend, straight.
  - A spec pin (`spec.pins`, such as Sawada's `paddy_rest`) overrides. `winter_crop`'s typing and weight rules read `grain_*` meta that is absent at this stage, so the knob's own weights apply.
- **Outputs** (`field_dict`): `knobs`, `grain` (drawn, need, room), and per field:
  - `ring`, `fork`, `foot`, `brook`, `brook_drawn`, `intake`, `weir`
  - `plots` (ring, stats, row, col, state, drain_side), `plots_box`, `channels` (role, pts, w, w_tail)
  - `beans`, `hem`, `pond`, `grave`
- **Manifest keys written** (py:169-336): `fields` (`name = "<name>-paddies"`, `outline`, `bbox`, `vis_bbox`, `plots`, `drain_hem`, `plot_rings`, `bund_beans`, `cell`, `down_deg`, `fork`), `field_ditches`, `channels`, `weirs`, `wet_plots`, `flooded_plots`, `field_ponds`, `field_graves`, `streams` (via `s.stream`), and meta (`field_archetype`, `winter_crop`, `water_source`, `coarse_grain_*`, and so on).
- **Plan fields set:** `plan.brook = f["brook"]`, `plan.envelope = outline`, `plan.hem_in = {**hem, ring, field}`.
- **Polder (Kuwabata)** (py:358-520):
  - Rolls `paddy_rest` and `dikepond_split` (forms 0.6, 0.4, 0.7, 0.5, 0.3, even; default 0.6) in Python.
  - Calls `stage_polder(seed, hh, dikepond, layout, down, center, aspect, canvas, rest=="unsettled", (split, leftover, fry_form, dike_crop))`.
  - Writes `fields`, `field_ditches`, `channels` (feeder and outfall), `dikes`, `planted_trees`, `dikeponds`, `land_use`.
  - Name is `"<name>-polder"`. No hem, no sink.

**Stage 3, `sink`.** Pure entry: `sink::sink(&SinkIn, &mut dyn Stations)`. `Vec<Pt>` implements `Stations`.
- **Inputs:** `pond = water_sink=="pond"`, `canvas`, `fall`, `flow_deg = water_flow`, `outline`, `drain` (the `field_ditches` entry with role "drain"), the drawn brook (`brook_drawn`), `brook_w = 5.25`, `run_w = chan_px(5.5, GRAIN=2.0) = max(1.5, 5.5) = 5.5`, `resting` (rings of plots with state "rest"), `reed_ft = 44`, `join_trunk = 150`.
- **Skipped:** it does nothing on a polder, because the drain name check fails.
- **Outputs:** `form`, `run`, `to`, `pond` ((cx,cy),rx,ry), `reeds`, `confluence`.
- **Manifest keys written** (py:100-124): `pond`, `meta.pond_role="drainage"`, `block_polys` (pond box + 10), `channels` (run record with w=2.5, `to` kind, field), `meta.water_sink`.
- **Plan fields set:** `plan.sink_pond`, `plan.sink_brook = run`, `plan.confluence`, `plan.water_sink = form`.
- **Refusal:** `SinkRefused` is returned as an `Err`.

**Stage 4a, `seat`.** Pure entry: `seat::seat(&SeatIn)`.
- **Inputs** (seat_stage.py:36-55):
  - `canvas`, `fall`, `wind` (`WIND_VECTORS[windward]`: N (0,-1), NE (.7071,-.7071), and so on), `back_min_dot = 0.7071`, `outline`, `band = band_extent(hh, cluster_shape)`.
  - `plots = []`, because the dry plots are laid after the seat.
  - `toe`, `reeds` (`wet`), `brook = plan.brook`, `walls`, `lines`, `streams`, `ford = (160, 30, 20)`.
- **Python-only inputs that must be ported:**
  - `toe_band()`: wet.py:642-748, about 60 lines. `pad=90`, `bleed=120`, a cross-slope station step of `max(24,pad/3)`, a three-station running max, and flank curves at `t^1.6`. It reads `field_polys` and the fan points.
  - `exit_walls`: cluster.py:23. Walls are the toe and the reeds, each grown 8 ft by `ring_offset(w, 8, 0)` (Python-only), at margin 0. Also the envelope at margin 0, and the pond as a 16-gon of radius `max(rx,ry)` at margin 80. Lines are the sink run's segments plus `plan.watercourses`.
  - `lines` from the manifest: `field_ditches` (the non-head channels), `channels` (head race, then the sink run record), and `drawn_channels` segments. The last are the filleted, mouth-clipped strokes, which are Python-only (`fillet_polyline`, `_clip_to_pond` / `_clip_to_stream`).
  - `streams`: the `stations` of each stream record, which is `brook`.
  - `reeds` as the drawn marsh ring: pond reeds minus field, dry and water (`drawn_ground`, Python-only). Use `out.reeds` directly as an approximation.
- **Outputs:** `frames` (cx, cy, along, out, lat, dep, anchor, offwind), the chosen one first and the ladder after it; `fords`; `stream_segs`.
- **Manifest and plan:** `meta.brook_fords`, `meta.seat_offwind`, `meta.lane_skeleton`, `plan.seat`, and `plan.watercourses = ditches + stream_segs + drawn`.
- **Draws nothing.**

**Stage 4b, `hem`.** Entry: `hem::lay(&HemIn, ring, water, keep)`.
- **Inputs:** the field's `hem` fields (`line`, `out`, `down`, `bounds`, `seed`), `ring = fan ring`, and `water` as `(a, b, w)` segments from `f.water.segs` / `f.water.widths`.
- **`keep`:** `settlement_ground(seat)` (hem_stage.py:40-49). A quad from `anchor ± along*lat`, extended by `out*(12 + 2*dep + 146)`.
- **Outputs:** `dry` (poly, crop, theta, tract) and `grain` (drawn, room).
- **Manifest keys:** `dry_plots` (`tract = "<field>:<n>"`), `meta.coarse_grain_dry_acres` and `coarse_grain_room_acres` (rounded to 2 places), plus `dry_polys` and `block_polys`. A polder (`hem_in` is None) lays none.

**Stage 4c, `waterward`.** Entry: `waterward::fringe(dikes, cut, cut_hw, depth, canvas, fall, seat_out)`.
- **Inputs:**
  - `dikes = [(M.dikes.outline, M.dikes.gaps)]`, where `outline = outer + reversed(inner)`.
  - `cut = max(dike w_max)`, `cut_hw = 15`, `depth = 280`, `canvas`, `fall`, `seat_out = plan.seat["out"]`.
- **Outputs:** `flanks` and `strips`. The strips are drawn as "waterside" marsh, and `meta.waterward = flanks`.
- **Skipped:** it does nothing unless the archetype is a polder with dikes.
- **Python-only extra:** `reserve_sty_seat` (pondstock.py). It draws nothing and can be dropped.

## 4. Drawing

**Conventions:**
- 1 px = 1 ft, with an SVG `<svg viewBox="0 0 W H">`.
- The sheet is a rect `LAND #EFE3C2`.
- The crop is a `viewBox` of `(ox,oy,w,h)`. The Python crop was `content_view(boxes, extras, CROP_MARGIN=48, W, H)` clamped to the canvas. `frame_for` also reserves the confluence ±75 ft (`BROOK_JOIN_TRUNK*0.5`) and a polder's reed-strip extent. For the driver, use the bbox of the drawn content plus 48.
- The title and scalebar belong to `stage_frame` / `stage_labels`, not these six stages.

**Draw order (a single z-ordered list):**

1. **Field floor (`comb_base_fill`, drawing.py:24).**
   - Polygon of the fan `ring`, fill `_RICE_GREEN #A6C398`, no stroke.
   - Clipped to the plots' box, as `<clipPath><rect>` of `plots_box`.
2. **Grave ground.** Fill `MOUND #CFC6B4`. Only when a grave is present.
3. **Paddies (`ink.paddies`).**
   - Each plot is a polygon with `stroke-linejoin round`, stroke `AZE #6E4520`, width `aze_w(1.0) = max(1.5, 0.5) = 1.5`.
   - Fill by state: green `#A6C398`, wet `FLOODED #93B7AC`, flooded `POND_WATER #9CB4C8`, gold `RIPE_GOLD #C9BA79`.
   - A "rest" plot is a polygon with fill `REST_GRASS #C8CF92` and the same bund stroke. It also gets small tufts: a "^" path in `REST_TUFT #8FA05E`, 0.8 wide. There are `max(3, area/900)` of them, and the RNG is seeded `int(|cx|*7 + |cy|*13)`.
4. **Dry plots (`ink.dry_plots`; drawn in the hem stage).**
   - Polygon with fill `CROP_FILL` (barley #C9B57A, millet #C29A55, buckwheat #D9CFC0, soy #8DAA6A).
   - Stroke `#A98C58`, width 1.4, round join.
   - Furrow lines in `CROP_FURROW` (barley #9C8650, millet #8E6E36, buckwheat #A8574A, soy #5E7A44). They sit 5 px apart across the plot, at angle `theta`, clipped to the plot, with stroke width 0.8 and opacity 0.8 (`_draw_furrows`, drawing.py:85).
5. **Water block.** It is one block, composited at the end by `_water_block` (finish.py:658), in this order:
   1. Pond rims (stroke `#5C7488`, width 2.4).
   2. A `<g opacity=.85>` of all beds, with the pond fill (`#9CB4C8`) last.
   3. A `<g opacity=.55>` of the sheens.
   - **Brook:** bed stroke `#9CB4C8`, width 5.25, round caps and joins. Sheen stroke `#B6CAD8`, width `max(2, 0.35*w)` rounded, butt cap.
   - **Ditches (`field_channel`):** stroke by role. Supply is `SUPPLY_HUE #6C9CBE`; the drain and the sink run are `DRAIN_HUE #4F7186`.
     - Width runs `w → w_tail` with `taper_pieces`, one segment per piece. Each piece has the width `sqrt(w0² + (w1² - w0²)*t)` at its arc-length midpoint (`taper_w`).
     - Round caps and joins. Bends are rounded with `fillet_polyline(pts, 2.5*max(w))`: quadratic, 6 steps, cut-back capped at 0.35 of each leg, corners under 8° left alone.
     - If `|w1-w0| < 0.2`, one path.
   - **Sink run width:** 5.5. It is the drainage-ditch class.
   - **Pond (sink):** ellipse fill `#9CB4C8`, rim `#5C7488` width 2.4, sheen ellipse (rx-12, ry-10) in `#B6CAD8` width 1.
   - A simple implementation can emit these directly without the clipping.
6. **Beans.** `<g opacity=.85>` of circles of radius 1.5, fill `BEAN_GREEN #2F6B35`. The runs are first filtered by `ink.settle` / `beans::settle` against the segs and ponds (`settle_runs`).
7. **Weir.** Polygon fill `#7A6A52`, stroke `#4E4232`, width 0.6.
8. **Pocket pond** (valley and polder).
   - Outer ellipse (rx+2.5, ry+2.5) with fill FLOODED and stroke AZE, width 2.2.
   - Water ellipse in `#9CB4C8` with stroke `#5C7488`, width 1.2.
   - Sheen ellipse in `#B6CAD8`, width 0.9.
   - Eight reed ticks in `#7FA040`, width 1.1, opacity .9.
9. **Grave.**
   - Mound ellipse (rx 6.5, ry 4.5) with fill `#CFC6B4` and stroke `#8C8470`, width 1.2.
   - Two stones `(−2, .5, 3)` and `(1.5, 2.5, 2.2)`: rect width 1.8, fill `#9AA1A4`, stroke `#5A584F`, width .5.
10. **Marsh** (pond reeds and waterside strips). This is the engine's reed-tile cover (tiles.py). Approximate it with a polygon in a pale wet reed tint, with sparse `#7FA040` reed ticks. Nothing in the six stages' logic depends on it.
11. **Polder (Kuwabata)** (ink.py:200-262, `ink.dike` / `dikeponds`).
    - **Dike band:** fill `DIKE_EARTH #B79B68`, edge `#9C8150` width 1, `evenodd`.
    - **Crowns:** `CROWN_FILL` (willow #6E8B4A, mulberry #87A45C, fruit #7C9A54, tea #5E7C40), opacity .92, or .9 for the bank crop.
    - **Sluice gates:** 8×8 rect, fill `#8C7A5A`, stroke `#5A4A32`, width .8.
    - **Bank:** `BANK_FILL #A9AE7C` ring with `AZE` stroke.
    - **Pond water:** `#9CB4C8` (nursery water `#A7B3AE`) with a `#5C7488` rim, width 1.
    - **Tea hedges:** polyline, stroke `#5E7C40`, width 3.
    - **Rice parcels:** the green paddy fill with the bund stroke, plus a jittered grid of shoots 4.5 apart. `paddy.py` draws these (`_paddy_surface`), and the hamlet's layer `s.add_paddy` is always drawn beneath the water block.
    - **Polder plot fill:** polygons use `FILL[state]` with AZE at 1.5.

## 5. What needs porting from deleted Python

- The knob registry (typing and weights). The `knobs.json` forms and weights are enough; there is no `Knob.allowed` logic to port beyond `plot_regularity` collapsing to "organic".
- The `hamletgen` tables listed in section 2, plus the constants in section 3.
- `canvas_for`, `band_extent`, `seat_room`, `offtakes_for`, `settlement_ground`, and `WIND_VECTORS`.
- `toe_band` and `ring_offset` (the seat's inputs).
- `fillet_polyline`, `taper_pieces`, `taper_w`, and the clip-to-pond/stream mouths (needed for the seat's `drawn_channels` lines). These need only approximate fidelity.
- The SVG writer: palette constants, the water-block compositing, and the reed and marsh tile (or a simplification).
- The crop box (bbox plus 48).
- The manifest assembly, including the `s.px(...)` width conversions (identity at ftpx=1). The per-stage keys are listed in section 3.
