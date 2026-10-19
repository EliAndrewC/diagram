# settlement/structures/ - the structures subsystem as a package

Split from one `settlement/structures.py` by feature 114 (constitution Principle X clause 13 - the cost being managed is
context-window tokens). **Load only the file the task calls for**; this index is the map.
`from .structures import StructuresMixin` still resolves.

**This package was never ONE subsystem.** `structures.py` was feature 025's RESIDUE BUCKET - whatever was neither
field, nor way, nor homestead, nor funerary ground - so the modules are grouped by **what a session comes here to
change**, not by theme, and are deliberately uneven in size. A partition tuned for equal files would have to cut a
cluster that no task cuts.

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the composition itself; never add logic here |
| `ground.py` | `road` (a bordered roadbed + its no-build corridor, `ROAD_W_FT`) and `_finish_road_label`. A member that does NOT belong to this subsystem at all - see "Two placements you will want to fix" below |
| `urban.py` | the generic urban BUILDING: the `URBAN` palette (fill/edge/footprint by caste and role) and `building` itself - the one seat every frontage and top-up funnels through, and where the samurai-ward refusal lives |
| `captions.py` | **the LABEL PHASE** (`place_labels`, feature 157 - the last phase of every settlement's generation, its drain order, its one-row dispatch table, and `discard_queued_label` for a feature that is placed and then withdrawn), the ONE placer's settlement adaptor (`_draw_seated_caption`, `label_obstacles`, feature 266), and the boxes a caption must miss (`label_blocker_quads`, `tree_crown_discs`) |
| [`fixtures/`](fixtures/CLAUDE.md) | public street furniture: the kosatsuba notice board, its water and lane clearance probes, and its placement pass (`place_kosatsuba`). Read its index, then load one file |

## Composition, and why it is in `__init__.py`

`StructuresMixin` is
`class StructuresMixin(GroundMixin, UrbanBuildingMixin, CaptionProbesMixin, PublicFixturesMixin)`
with no members of its own. It exists ONLY so `core.py` keeps its single import and `StructuresMixin`
keeps its position in the `class Settlement(...)` base list - which means the partition here can be
re-cut later without touching `core.py`.

**Cross-submodule calls need no import.** Every sub-mixin is a base of the same `Settlement`, so
`self.label_obstacles(...)` from `fixtures/siting.py` resolves through the MRO wherever the caller's text lives.

| from | to | call |
|---|---|---|
| `fixtures/siting.py` | `captions.py` | `place_kosatsuba` -> `label_obstacles`, `tree_crown_discs` (its caption proved by the one placer, feature 287) |

Feature 392 retired the code only the frozen legacy maps called (the compounds, the packing engines, the servant ranges,
the city fixtures and the caption siting probes); the commit before it holds it.

## Two placements you will want to "fix" - each is deliberate

### `road` is in a module of its own because it does not belong HERE

`road` belongs with `water_ways/`'s ways (lanes, streets, alleys, kido). It is in this package only because feature
025's cut put it here. Moving it is a separate change of its own (a member moved between parent-level mixins); isolating
it makes the eventual move a one-file change plus one row of this table.

What the module legitimately IS, so it is not merely a leftovers drawer: `road` draws an unbuilt GROUND SURFACE that
reserves placement rather than a structure that occupies it - it appends a corridor and records no footprint the overlap
matrix treats as solid.

### `captions.py` and `place_caption` - DECIDED by feature 266

There is ONE caption placer, `l7r/diagram/labels/`, owned by neither mode (the GM, 2026-09-27: *"one placer for all
labels"*). `captions.py` is its settlement ADAPTOR - `_draw_seated_caption` places and draws, `label_obstacles` builds
the index once per phase - and `place_caption` in `castle_civic.py` is only a subject request that queues into it. The
standoff ladder that used to live in `castle_civic.py` is gone, so the old question of where the seat engine belongs
no longer has two answers.
