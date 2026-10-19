# settlement/shrines_wells/ - the shrines/wells subsystem as a package

Split from one `settlement/shrines_wells.py` by feature 116 (constitution Principle X clause 13 - the cost being
managed is context-window tokens). **Load only the file the task calls for**; this index is the map.
`from .shrines_wells import ShrinesWellsMixin` still resolves.

**This package was never ONE subsystem, and its NAME concedes it** - the only module in the engine joined by an `and`.
Feature 025's positional cut left unrelated subsystems sharing a file (religious halls, torii avenues, the well
subsystem, a general seat-finding API, draft byres, woodland stands), so the modules are grouped by **what a session
comes here to change**, not by theme, and are deliberately uneven in size.

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the composition itself; never add logic here |
| `shrines.py` | a shrine's GLYPH: `shrine` (the simple glyph) |
| `torii.py` | the torii arches: `_torii` (one true-scale arch), `torii_path` / `torii_even` (hand-placed ascents), and the module-level `torii_plan_svg` |
| `wellground.py` | **whether a patch of ground may take a wellhead at all**, and the cost of asking: `_well_ground_clear` (the predicate), `_build_well_index` / `_well_index` (the three `PointGrid`s), `frozen_terrain` (the per-pass freeze that asserts its own invariant), `_terrain_fingerprint`, `_wet_toe_keepout` (the reed toe, derived before the reeds are drawn), `_in_scrub_cover` (the grazed-waste refusal). **The hub - read the perf notes here before touching any of it** |
| `wells.py` | the wellhead GLYPH and how many wells a map gets and where: `well`, `_well_vr` (the drawn extent placement must predict), `well_at` (place one if the spot is clear), `place_wells` / `_place_wells` (the neighborhood grid + coverage pass) |
| `seats.py` | the general "where can a `w` x `h` feature stand?" API: `open_seat` (asks the real `_fits` at the moment of placement) and `_footprint_clear` (the whole-footprint test against the BOUND only, deliberately). Nothing to do with shrines or wells - see "Three placements you will want to fix" below |
| `byres.py` | the draft-animal byre: `_draw_byre` (the open-fronted stall glyph) and `draft_byres` (the house-driven pass: since 269 B16 the beast lives with its household - the inner stable's arm against the farmhouse or the outer stable's own shed in the yard, on about half the households; the old shared shed on the commons is the rare `detached_commons` roll, a labeled guess) |
| `woods.py` | how a wood is DRAWN - a stand of individual trees, never a terrain wash: `flush_tree_stands` / `_draw_stand` (the deferred canopy, drawn at crop time against the complete map), `_stand_fringe` (thicket-masked advance growth on the cut-over margin), `_crowns`, `_fringe_blocked` |

## Composition, and why it is in `__init__.py`

`ShrinesWellsMixin` is
`class ShrinesWellsMixin(ShrineHallsMixin, ToriiAvenueMixin, WellGroundMixin, WellsMixin, OpenSeatMixin, DraftByresMixin, TreeStandsMixin)`
with no members of its own. It exists ONLY so `core.py` keeps its single import and
`ShrinesWellsMixin` keeps its position in the `class Settlement(...)` base list - which means the
partition here can be re-cut later without touching `core.py`.

**Cross-submodule calls need no import.** Every sub-mixin is a base of the same `Settlement`, so
`self._well_ground_clear(...)` from `wells.py` resolves through the MRO wherever the caller's text
lives. The engine already relies on this from outside the package too: `hamletgen/homesteads/wells.py` calls
`self._well_ground_clear`, `self._in_scrub_cover` and `self.frozen_terrain`; `rolling/`, `homestead_parts/` and
`hamletgen/` read `self._well_vr`; `core.py` and `finish.py` call `self.flush_tree_stands`.

**`wellground.py` is the hub**, which is the shape a well-cut partition should have - two of the
other six call into it and it calls out to none of them:

| from | to | call |
|---|---|---|
| `wells.py` | `wellground.py` | `well_at` -> `_in_scrub_cover`, `_well_ground_clear`; `_place_wells` -> both; `place_wells` -> `frozen_terrain` |
| `seats.py` | `wellground.py` | `open_seat(well=True)` -> `_in_scrub_cover` |

Feature 392 retired the code only the frozen legacy maps called (the shrine halls and the small shrine, the hill, the torii
avenue, the farm and shrine wells, the tree-stand queue and the canvas-filling forest); the commit before it holds it.

## One placement you will want to "fix" - it is deliberate

### `seats.py` and `byres.py` hold members that do not belong in this package at all

`open_seat` + `_footprint_clear` are a general placement API (how to use it: [`dev/diagnostics.md`](../../../../dev/diagnostics.md),
"Ask the ENGINE where a feature fits"); its home is `houses.py`, beside the `_fits` it delegates to. `_draw_byre` +
`draft_byres` are a homestead appurtenance and belong with `homestead_parts/`. Both are here only because feature 025's
positional cut put them here, each in an isolated module so the eventual move - a separate change of its own - is a
one-file change.

## If a module grows: the seams, decided in advance

- **`woods.py`**: the crown primitives (`_crowns`, `_fringe_blocked`) are the reusable half, the
  stand policy the rest. No reason to cut today.

Monkeypatching: patch the DEFINING submodule (`settlement._geom.point_in_poly`, or `settlement.shrines_wells.<module>`
for a member of this package) - the rule is [`../CLAUDE.md`](../CLAUDE.md)'s.

## The guard that makes the split safe

`tests/settlement/test_shrines_wells.py` holds the composed-surface guard: every pre-split name
still live on the composed class (a SUBSET assertion, so a later helper needs no bookkeeping), no two
sub-mixins defining the same name (MRO would silently orphan one), all of them resolving on
`Settlement` itself, and `frozen_terrain` still being a context manager - the decorator
being the one thing a slice can drop while leaving the NAME in place, so the surface census alone
cannot see it. Both surface assertions were proven red before they were trusted; the contract and its
red proofs are in `specs/116-shrines-wells-package/contracts/mixin-surface.md`.
