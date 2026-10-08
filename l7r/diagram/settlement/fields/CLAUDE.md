# settlement/fields/ - the field subsystem as a package

Split from the 1,511-line `settlement/fields.py` by feature 112 (constitution Principle X clause 13
- the cost being managed is context-window tokens). **Load only the file the task calls for**; this
index is the map. `from .fields import FieldsMixin` still resolves.

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the composition itself; never add logic here |
| `paddy.py` | wet and dry field BODIES and the plot geometry they quilt themselves from: `paddy_field`, `water_field`, `fallow_field`, plot splitting (`_paddy_plots`, `_split_convex`), tax-free plots, the paddy surface render, crop rows, and the resting plot (`PADDY_REST`, `rest_plots`, `resting_plots`, `rest_basin` - 269 B01; the comb draws its resting basins through the same two methods). Also the module-level WATER FRAME (`_uf_u` / `_uf_f` / `_uf_xy`) - the contour/fall transforms, pure and shared |
| `comb.py` | the comb-field builder and only it: `draw_comb_field` and its eight `_comb_*` steps (hem, paddies, beads, source, ditches, the field record, the ditch records, the hairline source channel), plus `comb_base_fill`, `bund_junctions`, `_draw_furrows` |
| `grain.py` | where a hamlet's coarse grain grows (feature 287, W36; research/contents.json#fields 0011): the `winter_crop` knob (barley on the drained paddy, or none), the need per household, and `top_up` - the placer that tops a wild fan's dry band up from the middle's reserve, which `comb.py`'s `_coarse_grain_top_up` calls |
| `outfall.py` | the comb's drain outfall run and the channel rule (`runs_downhill`, `outfall_run` curving out of the collector at most 55 degrees a turn) - lifted out of `comb.py` at the 1,000-line bar (feature 328), re-exported there |
| `landuse.py` | the land-use overlay pass - mulberry-and-fishpond, lotus, hill tea: `apply_land_use` and its four `_landuse_*` steps (tea fringe, wholesale leftovers, one converted plot, the dike-pond sluices), plus `_mulberry_rows`, `_pick_overlay_plots` |
| `features.py` | anything that is NOT rice: the feature-012 in-field pond / rock outcrop / grave island with their archetype-matrix constants, and every standing-water glyph (`pond`, `crescent_pond`, `_rounded_pond`) |

## Composition, and why it is in `__init__.py`

`FieldsMixin` is `class FieldsMixin(PaddyMixin, CombMixin, LandUseMixin, FieldFeaturesMixin)` with
no members of its own. It exists ONLY so `core.py` keeps its single import and `FieldsMixin` keeps
its position in the `class Settlement(...)` base list - which means the partition here can be
re-cut later without touching `core.py`.

**Cross-submodule calls need no import.** Every sub-mixin is a base of the same `Settlement`, so
`self._paddy_surface(...)` resolves through the MRO wherever the caller's text lives. The engine
already relies on this from outside the package too: `settlement/land/nearring.py` calls
`self._draw_furrows(...)`, which is defined in `comb.py`.

**Two members deliberately do NOT live with their primary caller.** Both are recorded so nobody
"fixes" them back:

- **`_paddy_surface` is in `paddy.py`** though `apply_land_use` (in `landuse.py`) is one of its
  three callers. It renders the paddy SURFACE; the overlay is a consumer of paddy rendering, not a
  co-owner of it.
- **`_rounded_pond` is in `features.py`** though its ONLY caller is `apply_land_use`. It is a pond
  glyph, and a reader looking for how a pond is drawn must find all four pond drawers in one place.

## The guard, and what it is for

`tests/settlement/test_fields.py::test_no_pre_split_fields_member_was_lost_in_the_move` holds the
24 pre-split members as a SUBSET of what the composed class exposes, and
`test_no_two_fields_submixins_define_the_same_name` holds that no two sub-mixins define the same
member. Both were proven to fire before being trusted (feature 112 T005).

Two things about the shape of that pair:

- **Subset, not equality** - so adding a method here needs no bookkeeping. The direction that HIDES is a member going
  missing: an addition is visible in review, while a subtraction surfaces only when whichever
  generator calls it happens to run.
- **The collision half is the one that is easy to under-rate**: a member defined by two sub-mixins
  produces a working import, a clean type check, and one silently dead implementation, because
  MRO just picks the first base.

## The class body is not only methods

`features.py` carries three class-level tuples - `_PADDY_POND_KINDS`, `_PADDY_ROCK_KINDS`,
`_PADDY_GRAVE_KINDS` - the feature-012 archetype matrix saying which field kinds get which in-field
feature. The surface guard cannot see attributes, so
`test_feature_012_archetype_constants_survived_the_split` covers them separately. Any future
re-partition of this package must move class attributes as deliberately as methods.

Monkeypatching: patch the DEFINING module (`settlement._geom.point_in_poly`, never `settlement.fields.point_in_poly`) -
the rule is [`../CLAUDE.md`](../CLAUDE.md)'s.

## `water_field`

`water_field` is the longest method left here, and its body says why at the point of the decision: what remains is
coupled through `uline`, a closure over the lateral boundaries that both the plot-carving loop and the lateral draw call.
**The next move there is to give the water frame a small object, not to lengthen a parameter list.** It is the v1 field
builder, superseded by `waterfields/` for rebuilt maps, so it is not where new work should go.
