# settlement/_geom/ - the geometry helpers as a package

Split from one `settlement/_geom.py` by feature 117 (constitution Principle X clause 13 - the cost being managed is
context-window tokens), by SUBJECT: its plain functions were eight populations (coordinate math, collision predicates,
spatial indexes, a placement memo, caption typography, manifest readers, curves, and a few non-geometry members) that
shared only a positional cut. **Load only the file the task calls for**; this index is the map. `from ._geom import ...`
and `from settlement._geom import ...` resolve exactly as before the split.

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the re-export surface; never add logic here |
| `base.py` | the `Pt` / `Poly` / `Manifest` aliases, the import-time main-tree guard, or the land/crop palette (`LAND`, `PADDY_SHADES`, `FLOODED_SHADES`, `RIPE_SHADES`, `RICE_GREENS`) |
| `primitives.py` | plain coordinate math with no map vocabulary: `point_in_poly`, `seg_closest`, `seg_dist`, `edge_dist`, `segments_cross`, `seg_intersect`, `ring_touches`, `ring_meets_ellipse`, `_signed_area` |
| `overlap.py` | a footprint's corner ring, or whether two regions meet: `rot_rect` / `_rect_ring` (corners), `stroke_quads` (a polyline as polygons), `sat_overlap` / `rects_overlap`, `poly_gap` / `_aabb_gap` / `box_gap` (the three gap MEASURES - know which one your rule is entitled to), `region_blocked` / `quad_hits_poly` / `quad_hits_seg` / `point_quad_dist` (cell-region tests), `_union_area` |
| `indexes.py` | a per-candidate scan is eating a gen: the `boxed_*` bbox prefilters, `PointGrid` (uniform grid, and its `_MAX_SPAN` clamp), `Indexed` (the registry that versions ITSELF rather than being fingerprinted), `indexed_grid`, `boxed_grid`. **Read the two staleness post-mortems here before adding any cache** |
| `seatmemo.py` | `SeatMemo` - the refusal memo behind a dwelling top-up, its measured 64.6%-re-visit rationale, and the `sync()` invariant it ASSERTS instead of assuming. Also read it before wiring the memo into a new gen: below ~a third re-visits it is a pessimization |
| `labels.py` | caption typography: the standoff ladder (`LABEL_MIN_AIR`, `LABEL_AIR_STEP`, `LABEL_AIR_RINGS`, `LABEL_AIR_CAP`), the two caption sizes (`HALL_CAPTION_FS`, `GOVERNOR_CAPTION_FS`), and tilt/box geometry (`label_tilt` the FOLD, `linear_tilt` the CLAMP, `linear_tilt_full`, `label_quad`, `label_aabb`, `tilt_caption_seat`) |
| `ways.py` | what someone could walk or cart along, read off a manifest: `lane_runs`, `way_beds` (the AVOIDANCE list - it carries the village lane network `lane_runs` does not), `lane_through_gate` + `kido_bar_deg` (a kido squares to the WAY, not to the fence), and the crossing constants `PLANK_*` / `LANDING_FT` / `CARRIED_LANDING_FLOOR_FT` |
| `walls.py` | every wall on the map (`wall_runs`, `_box_hits_run`), what closes a ward against one (`ward_interior`, `WARD_BARRED_KINDS`), and the arches that must stand clear of one (`torii_halfbox`, `torii_seat_on_wall`, `torii_wall_conflicts`, `TORII_PITCH_FT`, `TORII_PITCH_MAX_SPANS`) |
| `extents.py` | the DRAWN extent of a recorded feature, read back off the manifest: `paddy_wet_rings` (the water a wellhead may not stand in), `forest_reveal_x` / `forest_frame_span` (what a canvas-filling wood contributes to the crop), and the stable-yard glyph quads `wellhead_quad` / `trough_quad` / `tower_quad` / `rail_quad` (+ `YARD_GLYPH_SLACK`) |
| `curves.py` | making a line or ring look hand-made: `fillet_polyline` (the swept-bend research), `smooth_closed` / `smooth_points` (Catmull-Rom, and why the manifest records the SAMPLED curve), `organic_bbox`, `organic_poly`, `winding` |
| `region.py` | THE REGION (feature 297): the ground a thing may not take, painted ONCE, then read per candidate as array lookups |
| `water_index.py` | a grid over every watercourse segment with each segment's keep-out half-width (feature 138), cached on the settlement and rebuilt when a source list changes length |
| `village.py` | `village_population`, `_VILLAGE_POP_DIST`, `BUNDLE_PITCH_FT` - and see "Placements that look wrong" below before moving them |

## The surface is DERIVED, not maintained

`__init__.py` is star imports plus an aliased block, and nothing else - Principle X clause 14
(feature 027's idiom).
An 89-name import roster would restate what the submodules already declare, and would go stale the
first time a member moved.

**`import *` does NOT carry underscore names**, so all seven private members are re-exported by the
`as`-alias block. This is not a formality: the surface census caught `_VILLAGE_POP_DIST` missing from
that block the first time it ran, on a package that imported cleanly and passed every other test.
**If you move a private member between submodules, fix its alias line in the same edit.**

## The two guards, and what they are for

`tests/settlement/test_geom.py` holds them, and both were proven red before they were trusted
(`specs/117-geom-package/contracts/surface.md`):

- **The surface census** - all 89 pre-split names still resolve on `settlement._geom`, as a SUBSET
  assertion so a later helper needs no bookkeeping. A dropped member gives a package that imports
  cleanly, type-checks cleanly, and fails only when whichever caller needs it happens to run.
- **The shadowing guard** - no name is defined in two submodules. This one is specific to a
  star-import surface and has no counterpart in the mixin splits: `from .a import *` followed by
  `from .b import *` silently keeps `b`'s binding and leaves `a`'s implementation dead, with no error
  from Python, ruff or the type checker. A mixin at least keeps a duplicate reachable through the MRO.

A third test reads `base.py` for the bare `_assert_not_main_tree()` call. That call is the one
UNNAMED top-level statement in the pre-split file - the single member a name-keyed partition can drop
- and its failure mode is silence, because every test already runs inside a session clone.

## Layering, so the package stays acyclic

    base  <-  primitives  <-  overlap  <-  { indexes, labels, ways, walls, extents, curves }

`region.py` imports only `base`, `water_index.py` only `base` and `primitives`; `seatmemo.py` and `village.py` import
nothing from the package. No submodule imports from a module to
its right. **Respect the order when adding a member** - and note that Python 3.14 evaluates
annotations lazily (PEP 649), so an annotation-only reference is NOT an import dependency and a cycle
invented to satisfy one is a cycle for nothing. `indexed_grid` annotating `PointGrid` ~140 lines
before it is defined is the live example. The type checker catches the reverse error - a name used in
an annotation that no submodule imports.

## Placements that look wrong - each is deliberate

### `base.py` holds two things that are not geometry

The import-time main-tree guard and the drawing palette. Neither belongs in a geometry package on
subject grounds; both are what everything else needs FIRST (`core.py` imports `LAND` from here), and
the guard must run on ANY import of the package - which it does, because every submodule's star
import in `__init__.py` reaches this one, so there is no import path that bypasses it.

### `walls.py` holds torii predicates, and `shrines_wells/torii.py` exists

At THIS level an arch has exactly one geometric rule - it may not stand in a wall - and both
predicates are computed from `wall_runs()`. Filing them with the arches would put them in a module
that cannot see the walls they are about. The arch GLYPH, the avenue count, the stride, the threshold
and the wall-dodging are all `settlement/shrines_wells/torii.py` and were not touched.

### `village.py` is a module of its own

A village population roll and a homestead-bundle pitch are not geometry; feature 025's positional cut put them here, and
they sit isolated in one module (read by `rolling/`, `homestead_parts/`, `shrines_wells/` and the hamlet's ways) so a
move is a one-file change. **Moving them is a separate change with its own verification** - do not fold it into
something else.

### `seatmemo.py` is one class in one file

Not a size decision. `SeatMemo` is its own subject (it remembers ANSWERS, not geometry) with a long
measured rationale attached, and a session working on the indexes next door almost never touches it.

## If a module grows: the seams, decided in advance

- **`indexes.py`**: the `boxed_*` prefilters and the index CLASSES are independent - the prefilters take a list, the
  classes own a structure. Cut there (`prefilter.py`) when the file nears the 1,000-line bar.
- **`walls.py`**: the wall/ward half and the torii half touch only through `wall_runs()`. Cut there if the torii rule
  gains more than clearance.
- **`overlap.py`**: the corner CONSTRUCTORS (`rot_rect`, `_rect_ring`, `stroke_quads`) are the reusable half, the
  predicates the rest.

Monkeypatching a name here: patch the DEFINING submodule (`settlement._geom.primitives.seg_dist`), never
`settlement._geom` - the rule is in [`../CLAUDE.md`](../CLAUDE.md).
