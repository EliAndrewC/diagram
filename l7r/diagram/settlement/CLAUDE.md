# settlement/ - the Mode B drawing engine as a package

Split from one 16,016-line `settlement.py` by feature 025 (constitution Principle X clause 13 - the cost being managed is
context-window tokens). **Load only the file the task calls for**; this index is the map. `import settlement` still
exposes the full surface via `__init__.py`, and `settlement.Settlement` is one class whose methods are grouped into
subsystem MIXIN classes composed in `core.py`, so class-level monkeypatching and subclassing behave as on one class.

Two invariants the split does NOT touch:

- **DRAW ORDER is a runtime contract.** Features are layered by the record streams (`add` / `add_top` / `add_wall`, in
  `core.py`) and assembled by `finish()` (in `finish.py`); the DRAW ORDER map is
  [`dev/placement.md`](../../../dev/placement.md). The mixin grouping changes where a method's TEXT lives, never when it
  runs.
- **Knob doctrine** (feature 005): knobs are rolled via `scope_seed`/`knob_rng` in `_knobs.py`; a knob's value depends
  only on (map seed, knob name), never on draw order.

## Look here when

Each subpackage carries its own `CLAUDE.md` index: read it, then load one module.

| file | look here when |
|---|---|
| `__init__.py` | you need the re-export list or the import-time main-tree guard; never add logic here |
| [`_geom/`](_geom/CLAUDE.md) | geometry and spatial predicates: primitives, overlap and gap tests, the spatial indexes, captions' standoff, ways, walls, extents, curves |
| `_knobs.py` | the knob engine (`Knob`, `register_knob`, `resolve_knob`, `scope_seed`, `knob_rng`, layout validators, `skeleton_layout`) and roll/size helpers (`roll_torii_count`, `execution_ground_ft`, wall/bridge/moat/crop helpers) |
| `core.py` | `class Settlement(...)` itself: `__init__`, the record streams (`add`/`add_top`/`add_wall`/`add_label`, each with a `cls=` feature class for the interactive page - feature 134 - plus `add_parts` and the `feature()` scope), meta/header, knob resolve + rng scoping, viewport/crop |
| [`fields/`](fields/CLAUDE.md) | the fields: paddy and dry field bodies, the comb builder, land-use overlays, in-field features |
| [`water_ways/`](water_ways/CLAUDE.md) | focal features, water and its clipping, lanes, streets, kido, wards |
| `town_ways.py` | the TOWN-tier ways and focal features - `market`, `ancestral_hall`, `water_mouth`, `alley` (`TownWaysMixin`) |
| [`shrines_wells/`](shrines_wells/CLAUDE.md) | shrines, torii, wells and the ground that may take one, `open_seat`, byres, tree stands and the forest |
| [`structures/`](structures/CLAUDE.md) | compounds, roads and pasture, urban buildings, servant ranges, the packing engines, caption plumbing, civic fixtures |
| `trades.py` | trade works: brewery, dye yard, lumber, oil press, pawnshop, bathhouses, farrier, kiln, charcoal yard, refining forge, tanning yard, border lines |
| [`homestead_parts/`](homestead_parts/CLAUDE.md) | threshing yards, gardens, groves, stands and keepouts |
| `farm_fixtures.py` | the small things on a farmstead: privy, wood shed, manure heap, bath room, chicken coop, the household shrine, the persimmon (feature 133), each at true size |
| [`land/`](land/CLAUDE.md) | the land surface: the polder dike, marsh and wet ground, the commons and hinterland scatter, near-ring cropland |
| [`civic_grounds/`](civic_grounds/CLAUDE.md) | funerary and justice grounds, civic buildings, lodging, the stable yard |
| [`city/`](city/CLAUDE.md) | the provincial city: walls, moat, canals, waterfront, bridges, the governor's mansion, its crop and knobs |
| `castle_civic.py` | castle, ministries, dojos + martial halls + hanko, the caption/label-spot engine, forest patches, freestanding walls, flower fields |
| `houses.py` | house drawing + placement machinery (corridors, keepouts, treads, `_fits`, frontage), `try_place`, cluster seeds, plot texture |
| `hard_ground.py` | the hard no-build ground (`_hard_ground`: crop, pond, bog, a field's own ditches, read from the manifest) and the footprint test against it (`_hard_clear`, from `_hard_index`'s box grid) (`HardGroundMixin`) |
| `water_source.py` | where a field's water comes in: the gravity-feedable source positions and the sluice point a named one resolves to (`WaterSourceMixin`; out of `houses.py` at the 1,000-line bar, feature 328) |
| [`rolling/`](rolling/CLAUDE.md) | the rolling / homestead-solver CHAIN: `roll_village` and its stages, the settlement-form seeds, the bundle, fit, place and the deferred flush |
| `see_through.py` | the marks drawn below solid opacity, each with its class, its faintest and why (feature 294); the gate holds every shipped map to this table |
| `finish.py` | labels, `finish()` (layer assembly + svg write + the ink census and the interactive `.html`, feature 134), `render_png` |
| `title.py` | the title placard: its size (`placard_size`, `placard_height` - the one formula the hamlet's title pocket and band allowance derive from), its seat, the band grown for it, the blank-spot search and the title-clearance test |

**Other-tier code does not live where a hamlet roll runs** (feature 145): a function only a town or city runs goes in a
module a hamlet roll does not execute (`town_ways.py`, `structures/urban_fixtures.py`, `city/crop.py`, `city/knobs.py`,
`shrines_wells/forest.py`), so the hamlet floor judges only what a hamlet draws.

## Mixins and type checking (every mixin package under `settlement/`)

Every mixin method is annotated `self: "Settlement"` with `from .core import Settlement` (or the right relative depth)
under `TYPE_CHECKING` - that is what lets pyrefly, with the mypy-strict rule set, resolve cross-subsystem attribute
access with zero runtime import cycle. When adding a method to a mixin, keep that pattern; when adding a new subsystem
file, add its mixin to the `class Settlement(...)` bases in `core.py` and a row to its package's index.

## Monkeypatching a module-level name (every package under `settlement/`)

Submodules bind helper names at import (`from ._geom import poly_gap`), so patching `settlement.poly_gap` does not
reach a mixin that already imported it - patch the DEFINING submodule (e.g. `settlement._geom.overlap.poly_gap`, not
`settlement._geom.poly_gap`; each package index says which submodule defines what) or, for anything reached via
`self.`, patch `settlement.Settlement` (class-level patching is unaffected by the splits).

## Coverage

Every module of this package that a scripted hamlet roll executes owes 100% - the set is DERIVED from the roll cache's
records (`hamlet_floor --list`; `tools/hamlet_floor.py` carries the why) and held by the gate's FULL run. The package is
under the same single 100% floor as the whole engine on a plain `make done` (feature 174 retired the old 94% ratchet).
