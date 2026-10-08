# settlement/city/ - the provincial-city subsystem as a package

Split from the 1,582-line `settlement/city.py` by feature 113 (constitution Principle X clause 13 -
the cost being managed is context-window tokens). **Load only the file the task calls for**; this
index is the map. `from .city import CityMixin` resolves to this package's `__init__.py`, which composes the
sub-mixins back into one `CityMixin` in the `class Settlement(...)` base list.

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the composition or the re-export mechanism; never add logic here |
| `walls.py` | the defensive shell: `ring_road` (順城街, the follow-the-wall patrol street), `city_wall`, and the two halves it delegates to - the per-gate program (`_draw_gate` -> `_gate_piers` / `_gate_flanking_buildings` / `_gate_tower` / `_gate_caption`) and the curtain's mural towers (`_seat_mural_towers`). Shared vocabulary: `_gapped_ring`, `_tower`, `_wall_walk`, `_wall_perimeter`, `_wall_point_at_arc`, `_wall_arc_of`, `_berm_nudge` |
| `moat.py` | the wet defense and every opening through it: `moat`, `water_gate`, `sluice_gate`, `inwall_drain_outfall`, `moat_flow` |
| `canals.py` | water carried for transport and irrigation rather than defense, and the farmland ring it feeds: `canal`, `towpath`, `farmland_ring`, `_ring_upslope` |
| `waterfront.py` | where the city meets navigable water: `quay`, `aqueduct`, `dock`, `jetty`, `log_boom` |
| `bridges.py` | crossings, from a single span to the footbridge net over a channel system: `bridge`, `bridges`, `channel_footbridges` and the predicates it delegates to (`_widen_for_confluence`, `_deck_clears_its_water`, `_plank_reaches_useful_ground`), plus the module-level plank geometry `_at_arc` / `_deck_quad` / `_quads_overlap` |
| `civic.py` | the governor's mansion - and see below before you "fix" it |
| `crop.py` | the city crop, `crop_city` (`CityCropMixin`; feature 145 moved it out of `core.py`, which every map executes): how much of the city and its country the sheet shows |
| `knobs.py` | the city knob helpers - the machi mouths and the swept moat tap (feature 145 moved them out of `_knobs.py`) |

## The composition mechanism

`CityMixin` has no members of its own. Sub-mixin methods reach each other through `self.` on the
composed `Settlement`, so a cross-submodule call needs no import and the partition can be re-cut
later without touching a call site. There is exactly ONE such call today:

    farmland_ring (canals.py) -> sluice_gate (moat.py)

When decomposing `farmland_ring`, leave that reaching through `self.` - do not "helpfully" add an
import from `moat.py`, which would turn a free re-partition into a breaking one.

The base order in `__init__.py` is source order and is behaviorally irrelevant, because no name is
defined twice. That property is not an accident - it is what
`tests/settlement/test_city.py::test_no_two_city_submixins_define_the_same_name` exists to keep
true, and it has been observed failing (feature 113 tasks.md T016).

## Two placement decisions, so nobody corrects them back

- **`_ring_upslope` lives in `canals.py`, not with `ring_road` in `walls.py`.** The name says ring
  road; the code says otherwise - its only caller is `farmland_ring`. Placement follows the caller.
- **`civic.py` holds one method, on purpose.** `governor_mansion` calls `self.manor(...)` and
  re-keys the record out of `M["manors"]`: it is a STRUCTURE reusing the manor glyph, not city
  infrastructure, so it belongs to none of the five subsystems above. A one-method module is a
  smell, but a module whose index row is a lie is a defect - isolating it keeps every other row
  honest. **Intended follow-up**: fold `civic.py` into `settlement/castle_civic.py`, where it
  topically belongs (it stays under the 1,000-line bar).

## Type checking

The mixin pattern is [`../CLAUDE.md`](../CLAUDE.md)'s, with the TWO-dot path (`from ..core import Settlement`) since
these modules sit one level deeper. Three of `walls.py`'s members are `@staticmethod` and take no `self`.
**`_wall_point_at_arc` imports `Settlement` lazily INSIDE its body** (a runtime class-attribute read that would cycle at
module level): a split that rewrites import paths must rewrite in-body relative imports too, or the line points at a
module that does not exist and fails only at draw time.

## Verifying a change in here

The city wing is exercised by the provincial-city maps and the walled towns - a sweep of the scripted hamlets alone
leaves `city_wall`, `moat`, `farmland_ring` and the whole waterfront module unverified - and by the unit tests that hold
every module here at 100%.

## Long methods left whole, on purpose

`log_boom`, `moat` and `farmland_ring` LOOK long but are short in statements (constitution clause 12 measures
statements, "never raw lines"); a third of their raw length is the researched docstring the record-the-why rule
requires. **Do not "finish the job" by decomposing them** - splitting the code under that prose would duplicate the why
across helpers or let it drift (`specs/113-city-package/research.md` R10).
