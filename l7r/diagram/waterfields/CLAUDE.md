# waterfields/ - the water-first field engine as a package

Split from one `waterfields.py` by feature 110 (constitution Principle X
clause 13: files stay at human scale - the cost being managed is context-window tokens). **Load
only the file the task calls for**; this index is the map. `import waterfields` still exposes
the whole consumed surface via `__init__.py` (star-import re-exports per clause 14 / the 027
mechanism, plus an aliased block for the externally-consumed underscore names; guard:
`tests/waterfields/test_surface.py`) - never add logic to the `__init__`.

The engine's doctrine (THE INVERSION - fields grow around the water network; the warp-thread
march; slope as a knob) lives in the `__init__.py` docstring and `research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.html` (and its rules at research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html).

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the engine doctrine docstring or the re-export mechanism; never logic |
| `frame.py` | the contour(u)/fall(f) frame (`_Frame`), warp-thread state (`_Thread`), the march constants (`DF`, `GAP`, `DRAIN_W_*`, `BANK_MARGIN`), the channel TAPER LAW (`taper_w` - width goes as sqrt(discharge), so w SQUARED interpolates; shared by every consumer of a local width, and the one place to change it), or pure geometry (`_at_f`, `_f_at_u`, `_seg_x`, `_seg_d`, `_pip`, `_poly_perim`, `_signed_area`, `_poly_area`, `_dug_polyline`, `_point_along`, `_drain_bank`, `_miter_normals`) |
| `palette.py` | colors (`_RICE_GREEN`, `RICE_GREENS`, `FLOODED`, `RIPE_GOLD`, `BUND`, `AZE`, `BEAN_GREEN`), the real-feet paddy-cell calibration (`PADDY_CELL_ACRES`, `paddy_grain`), `aze_w`, `organic_parcel`, `DRY_CROPS` |
| `banks.py` | how plots hem to canals and ditches: `polyline_cum`, `drain_bank_clearance`, `supply_bank_clearance`, `floor_overhang`, `hem_to_bank`, `hem_on_paddy`, `_TOE_MIN_THICKNESS`, `_TOE_MIN_APEX`, `pointed_ring`, `dedup_ring`, `round_channel_joints`, and `jog_steps` / `jog_vertices` (a wall that steps sideways and carries on parallel to itself) |
| `comb.py` | `build_comb` = `finish_comb(carve_comb(...))` - the water-first comb builder: the carve lays the skeleton (pond sluice, head-race, supply canals, thread march, offtakes, drain) and the planted region; the finish lays the plots (`partition`, `settle`, `tint`), the dry hem and the beans |
| `hem.py` | the comb's DRY HEM, split out of `comb.py` at its 1,000-line bar (feature 287, W36): `_comb_dry_and_beans` (the hem and the bund beans), `fan_toe_hem` / `toe_cut` (where a fan's dry band lies, the `fan_middle` knob; 269 B07), and `middle_reserve` / `middle_stretch` (the WHOLE wild middle, laid to the canvas edge off the paddy and the drawn strip, nearest the toe first, for the coarse-grain top-up in `settlement/fields/grain.py`) |
| `carve.py` | `_bnd` / `_root_f` (where a sector's threads run at a fall - the partition's bounds), `_dry_fields` (the dry-crop hem tiling), `_bund_beans` (azemame bead accents). The plot carve that lived here was retired by feature 302 |
| `partition.py` | the comb's plots BY CONSTRUCTION (feature 302): `planted_region` (the envelope less its water and the ground it cannot command - its area is the acreage the fit scores), `Sectors` (each sector's lattice: rows with the wander, columns with the wobble, thinning where it narrows, the outer strip's lattice) and `cut` (every bund noded at once and `polygonize`d) - and the shared-bund research (*aze*) |
| `settle.py` | the partition held to the ring rules at construction: snapped to the recorded grid, judged once (`verdict`), staircases split, failing cells merged across their longest shared bund (opened, clusters grow), the rest left bare |
| `tint.py` | the low ground and the water tint: `mark_low` (the carve's `low` and FLOODED sample, set from where a plot lies) and `judge_tint` (the tint's six clauses and the promotion, moved from `close_seams`) |
| `furrows.py` | the dry hem's row directions, set tract by tract (`tract_ways`, `furrow_turn`, the `TRACT_*` figures; 269 B06) - what `_dry_fields` asks for each column's heading - and the rule itself (`tract_seams`, the finished-map judge lifted) with its repair across both bands (`settle_tract_seams`; feature 287, W35) |
| `trunks.py` | the comb's trunks as the rules read them (feature 287, W13-W15): `outfall_rise` (the collector discharges downhill), `sharpest_turn` and `DRAIN_MIN_LEG` (no hook into the outfall), `end_anchored` / `anchor_trunk_ends` (no main or collector end in bare ground) - split out of `comb.py`, which sits at the 1,000-line bar |
| `ring_rules.py` | every rule a finished paddy ring keeps, one predicate each (feature 287, M1), and `fan_context` - the context the gate reads off the manifest, built from the engine's channels; the width and dart rules are recorded and NOT enforced (the research contradicts both) |
| `seams/` | what is left of the seam pass after feature 302 - a PACKAGE with its own [`CLAUDE.md`](seams/CLAUDE.md): `pockets.py` (`_water`, `_outside_command` - the planted region is cut from them), `close.py` (`hold_ring_rules`, the re-hold after a grave cut, and `_split_steps`), `geoms.py` |
| `twins.py` | TWO WATERCOURSES DO NOT RUN SIDE BY SIDE (feature 294 B4): a delivery that would run parallel to another watercourse is dropped (`drop_twin_deliveries`, called by `comb.py`) |
| `polder.py` | `build_polder` (dike-and-drain reclamation) |
| `hill.py` | `build_terraces` (contour terraces) and `build_ribbon` (valley ribbon paddies), the hill-rice engines - out of `polder.py` (feature 145) because `FIELD_ARCHETYPES` deliberately holds neither, so the hamlet floor (100% on every module a hamlet roll executes) judges only what a hamlet draws |

No module imports one that imports it: `frame` is the leaf, `comb` composes the rest. The former mega-functions
(`build_comb`, `build_polder`, `_carve`) are named sequential stage functions - each stage takes its state as parameters
and returns what the next stage needs, so the pipeline reads top-down in the builder body. The star import in
`__init__.py` keeps every name importable from `waterfields`.
