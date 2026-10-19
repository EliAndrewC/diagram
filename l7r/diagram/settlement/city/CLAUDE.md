# settlement/city/ - the provincial-city subsystem as a package

Split from the 1,582-line `settlement/city.py` by feature 113 (constitution Principle X clause 13 -
the cost being managed is context-window tokens). **Load only the file the task calls for**; this
index is the map. `from .city import CityMixin` resolves to this package's `__init__.py`, which composes the
sub-mixins back into one `CityMixin` in the `class Settlement(...)` base list.

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the composition or the re-export mechanism; never add logic here |
| `moat.py` | the openings through the wet defense: `sluice_gate`, `inwall_drain_outfall` |
| `bridges.py` | crossings, from a single span to the footbridge net over a channel system: `bridge`, `bridges`, `channel_footbridges` and the predicates it delegates to (`_widen_for_confluence`, `_deck_clears_its_water`, `_plank_reaches_useful_ground`), plus the module-level plank geometry `_at_arc` / `_deck_quad` / `_quads_overlap` |
| `knobs.py` | the city knob helper - the machi mouths (`machi_mouths`; feature 145 moved it out of `_knobs.py`) |

Feature 392 retired the code only the frozen legacy maps called (the waterfront, the governor's mansion, the city crop,
the wall and its gapped ring, the canals, the moat itself and the swept moat tap); the commit before it holds it.

## The composition mechanism

`CityMixin` is `class CityMixin(MoatMixin, BridgesMixin)` with no members of its own.
Sub-mixin methods reach each other through `self.` on the composed `Settlement`, so a cross-submodule call needs no
import and the partition can be re-cut later without touching a call site - leave such a call reaching through
`self.`; do not "helpfully" add an import, which would turn a free re-partition into a breaking one.

The base order in `__init__.py` is source order and is behaviorally irrelevant, because no name is
defined twice. That property is not an accident - it is what
`tests/settlement/test_city.py::test_no_two_city_submixins_define_the_same_name` exists to keep
true, and it has been observed failing (feature 113 tasks.md T016).

## Type checking

The mixin pattern is [`../CLAUDE.md`](../CLAUDE.md)'s, with the TWO-dot path (`from ..core import Settlement`) since
these modules sit one level deeper. A split that rewrites import paths must rewrite any in-body relative imports too,
or the line points at a module that does not exist and fails only at draw time.

## Verifying a change in here

The members here are reached from outside the package (`land/dikes.py` -> `sluice_gate`, `fields/comb.py` -> `inwall_drain_outfall`, the hamlet ways and water -> the bridges) and held by the
unit tests that hold every module here at 100%.
