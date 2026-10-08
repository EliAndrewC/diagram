# land/ - the land-surface subsystem

Split from one `settlement/land.py` by feature 120 (constitution Principle X clause 13). **Load only the submodule
your task calls for**; this index is the map. `LandMixin` composes the whole surface, so the split is invisible above
it.

This package was a **residue bucket, not a chain**: unrelated land subsystems that feature 025's positional cut left
adjacent. The partition is therefore by SUBJECT, and the test of it is that a real
task stays inside one module.

## Look here when

| file | look here when |
|---|---|
| `dikes.py` | you are changing the polder **perimeter dike** - its varying width, its willow/mulberry planted rows, its sluice notches, the `crest` it records - or `dike_top_houses`, the single-file village that stands on that crest. They are one module because the second reads the first's crest and skips its sluice gaps |
| `wet.py` | you are changing **wet ground**: the `marsh` glyph and its four roles (`toe` / `pond_fringe` / `defense` / `waterside`), `toe_band` (the contour band that decides where the toe lies), `trim_off_marsh` (walking a way's ends back to dry ground), or `surface_water_dist` - the module-level predicate shared by the gate and by `hamletgen.place_wells` |
| `cover.py` | you are changing **dry ground cover**: `commons` (the feathered scatter - woodland / pasture / scrub by `role`), `hinterland` (the composer that picks the toe side, lays the ring strips and fills interior voids), or `_clear_ground` / `reserve_clearing` (the swept verge the scatters must skip) |
| `tiles.py` | you are changing how a **ground cover that stands for an area** is drawn (feature 298): the grass, reed and bamboo tiles (`<pattern>`s of the scatters' own glyphs at their density, seamless), `Cover` (a zone, its class and its bare ground, recorded by `commons` / `marsh` and drawn by `Settlement.flush_covers` in the slots `_header` reserves right above the land), `cover_rings` |
| `outline.py` | a MARSH'S NATURAL OUTLINE (feature 299): rounded corners and a slow irregular wave along the edges of a marsh laid as straight strips |
| `nearring.py` | you are changing **near-ring farmland** at town or city scale: `near_ring_cropland` (the dry hatake + garden quilt, with its density tiers) or `near_ring_paddy` (wet-rice basins, placed only where legitimately watered, with the moat intake and the city farm rings) |
| `__init__.py` | you need the composed `LandMixin` or the `surface_water_dist` re-export; never add logic here |

## The three things worth knowing before you edit

**`toe_band` is derived, not drawn, and that is deliberate.** It was factored out of `hinterland` in
2026-08-12 so a WAY could ask where the wet ground will be while it still has a choice of route -
`hinterland` lays the marsh late, after the structures. Deriving that in two places is the trap the
engine's rules call *"placement and its test must read the SAME source"*, so there is ONE derivation
and both callers use it. If you need the toe earlier still, call `toe_band` earlier; do not
re-derive it.

**Two corrections are baked into that band, and both were expensive.** It is a CONTOUR band
perpendicular to the fall, not an axis-aligned box - a rectangle is only an honest contour at a
0/90/180/270 fall, and at a diagonal it slices across the slope and swallows the drain. And its
WIDTH comes from the ground the fan waters, never from the canvas: an alluvial fan's spring line
follows the FAN's toe and a floodplain's backswamp is bounded by its levees, so wet ground is
FEATURE-bounded in both landforms (`research/questions/0057-marshes-and-wetlands-shitchi.html`). The
canvas-wide version was never a decision - it arrived as a side effect - and three separate pieces
of work built on it before anyone checked. That story is
[`dev/decisions.md`](../../../../dev/decisions.md), "A side effect is not a rule".

**The swept verge lives with the scatters that skip it, and the ordering is the rule.** A scatter
only skips clearings that EXIST when it runs, which is why `reserve_clearing` is there at all: a
precinct dropped in after `hinterland` must reserve its ground FIRST or the scrub covers it.
`scatter_respects_swept_clearings` checks exactly that, reading the `seq` ordinal `_clear_ground`
records.

## The one cross-submodule call

`hinterland` (cover.py) reaches `self.toe_band(...)` and `self.marsh(...)` in wet.py. It needs no
import: both are on the composed `Settlement`, which is what lets this partition be re-cut later
without touching `core.py`.

The farmstead helpers (`_attach_grove`, `_find_appurtenances`, `_farmstead_nudges`) are farmstead plumbing, not land
surfaces: they live in [`../homestead_parts/farmstead.py`](../homestead_parts/farmstead.py).

The mixin and monkeypatching rules are [`../CLAUDE.md`](../CLAUDE.md)'s: the two-dot `from ..core import Settlement`
here, a new submodule's mixin added to `LandMixin`'s bases and a row to the table above, and a module-level name
patched where it is defined (`settlement.land.wet.surface_water_dist`, not `settlement.land.surface_water_dist`).
