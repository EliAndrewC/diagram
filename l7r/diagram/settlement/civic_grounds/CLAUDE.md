# settlement/civic_grounds/ - the civic-grounds subsystem as a package

Split from one `settlement/civic_grounds.py` by feature 115 (constitution Principle X clause 13 - the cost being
managed is context-window tokens). **Load only the file the task calls for**; this index is the map.
`from .civic_grounds import CivicGroundsMixin` still resolves.

**This package was never ONE subsystem.** The file was a RESIDUE BUCKET - unrelated subsystems feature 025 left in one
file - so its modules are grouped by **what a session comes here to change**, not by theme, and are deliberately uneven
in size.

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the composition itself; never add logic here |
| `funerary.py` | ground given over to the DEAD: `cemetery` (parish rectangle vs organic common ground - the Louzeyuan-vs-Japan distinction lives in its docstring), `mausoleum`, `cremation_ground`, `ossuary`, and `_ward_fence_cap`, the ward-fence predicate `mausoleum` sites against |
| `justice.py` | ground given over to PUNISHMENT: `punishment_spot` (the in-settlement post/stocks), `execution_ground` (the outside-the-settlement siting rules - road, boundary, outcast side), and `boundary_marker` |
| `civic.py` | institutional and COMMERCIAL works - what a domain builds because it administers and trades, as opposed to what its inhabitants build to live: `granary`, `merchant_storehouses`, `merchant_residences`, `district`, `terrace`, and `precinct_interior` (the sovereign temple precinct's interior program) |
| `lodging.py` | where travelers and their ANIMALS stop: `flophouse`, `inn`, `stables`, `animal_ground`, `flush_stable_yards` (the deferred draw that puts the yards on the map last, at crop time, when the map is complete), plus the way-bearing helpers `_way_bearing_near` and `_way_seat_near` |
| `stable_yard.py` | the working YARD around a gate stables, as STAGES: the beaten-earth scatter, the road-parallel rail, the interior rails, the trough cluster and its well, the dung heaps. **Read its module docstring - the stages table and the RNG rules - BEFORE editing it** |
| `edge_seat.py` | a SEAT AT THE SETTLEMENT'S EDGE for a ground that must stand apart from the houses (feature 273): beyond the last house, clear of houses and wells by its own distance, out of the water by the caller's bank margin - how a village's cremation ground is placed |
| `_yardctx.py` | `_YardCtx` - one yard's shared state (keep-outs, the wall, prior yards' rails/troughs/heaps, the candidate ring) and the six predicates every stage tests against (`clear`, `take`, `rail_rec`, `draw_hitch`, `rail_clear_of_heaps`, `glyph_free`). Not a mixin; it is constructed per yard |

## Composition, and why it is in `__init__.py`

`CivicGroundsMixin` is
`class CivicGroundsMixin(FuneraryGroundsMixin, JusticeGroundsMixin, CivicWorksMixin, LodgingMixin, StableYardMixin)`
with no members of its own. It exists ONLY so `core.py` keeps its single import and
`CivicGroundsMixin` keeps its position in the `class Settlement(...)` base list - which means the
partition here can be re-cut later without touching `core.py`.

**Cross-submodule calls need no import.** Every sub-mixin is a base of the same `Settlement`, so
`self.cemetery(...)` from `civic.py` resolves through the MRO wherever the caller's text lives. Two
such calls exist here by design, and both are intentional rather than accidents of the cut:

| from | to | call |
|---|---|---|
| `civic.py` | `funerary.py` | `precinct_interior` -> `cemetery` (the precinct claims its own graveyard) |
| `lodging.py` | `stable_yard.py` | `flush_stable_yards` -> `_stable_yard` |

Two members are also reached from OUTSIDE the package through `self.`, which is why neither is as
private as its underscore suggests: `structures/compounds.py` calls `self._ward_fence_cap(...)`, and
`trades.py` calls `self._way_bearing_near(...)`.

## Three placements you will want to "fix" - each is deliberate

### `_ward_fence_cap` is in `funerary.py`, not with the ward fences

It reads like a ward-fence utility and its natural home is beside the ward fences in
`water_ways/`. It is here because `mausoleum` is its caller inside this package, and **placement
follows the caller** (feature 113's `_ring_upslope` precedent). Its external consumer
(`structures/compounds.py`) reaches it through the composed `Settlement` either way, so its
placement costs that consumer nothing.

Moving it to `water_ways/` is a PARENT-level move - a separate change, a named follow-up rather than an oversight.

### `precinct_interior` is in `civic.py`, not with the shrines

It draws a sovereign temple precinct's interior program - abbot's residence, order administration,
library, two monk dormitories, kitchen/refectory - so thematically it is religious ground and its
natural eventual home is beside the shrines in `shrines_wells/`. It sits in `civic.py` as the
institutional-works member for the same parent-level-move reason as above.

Two things to know if you touch it: it calls `self.cemetery` across the module boundary (normal, see
the table above), and its **only consumer in the entire tree is the frozen Shiro Daika exhibit**, which nothing runs by
default - so a change to it is verified by rolling that map by hand.

### `_stable_yard` has a module to itself

A module holding one private method (and its stages) reads oddly beside its siblings; folding it into `lodging.py`
beside its caller would move the grab-bag problem rather than solve it.

## The stable yard

The stages table and THE RNG RULES live in `stable_yard.py`'s module docstring, beside the code they govern. In one
line: the yard draws from the global stream inside one seed bracket in `_stable_yard`, so stage order is draw order -
read the docstring before moving anything.

## The next seam, decided in advance

If `stable_yard.py` grows, the next seam is **furniture** (the litter, both rail passes, the heaps) versus **water**
(the trough cluster and its dug well) - the water stage is the only one that reaches outside the yard for a recorded
well, and the largest. `tests/settlement/test_civic_grounds.py` becomes a package mirroring this one when it nears the
1,000-line bar.

Monkeypatching: patch the DEFINING module (`settlement._geom.rail_quad`, never `settlement.civic_grounds.rail_quad`) -
the rule is [`../CLAUDE.md`](../CLAUDE.md)'s.

## The guard, and what it is for

`tests/settlement/test_civic_grounds.py` holds the 22 pre-split members as a SUBSET of what the
composed class exposes, a second test holds that no two sub-mixins define the same name, and a third
holds that all 22 resolve on `Settlement` itself. Both breakage classes were proven to fire before
the guard was trusted (feature 115 T007/T017).

- **Subset, not equality** - so the decomposition's added private stages need no bookkeeping. The
  direction that HIDES is a member going missing: an addition is visible in review, while a
  subtraction surfaces only when whichever generator happens to call it runs - and for
  `precinct_interior` that is one frozen exhibit nobody runs by default.
- **The census admits attributes, not just callables**, even though this class has none today. A
  constant is as easy to lose in a split as a method and much easier to overlook.
- **`_way_seat_near` is LIVE.** It has no consumer outside the package and a cross-file census that
  excludes the defining file reports it deletable - feature 115's own pre-spec census did exactly
  that and proposed deleting it. `_way_bearing_near` calls it, one line. Any dead-member pass here
  MUST count intra-file callers.
