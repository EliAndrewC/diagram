# Feature Specification: Retire roll_village - delete the old knob engine nothing ships from

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=388-retire-roll-village`)

**Created**: 2026-10-18

**Status**: Draft

**Approved**: the GM, 2026-10-18, "I think if nothing ships from it then we should just delete it now and not even move it into the 384 backlog."

**Affects**: hamlet

**Input**: `request.md` - the GM's question, the session's answer and the GM's ruling, verbatim.

## Why

`Settlement.roll_village` (feature 005) rolls a hamlet-scale map from a seed. The scripted hamlet generator (`hamletgen/`)
replaced it: no map in `pool/` calls it (measured 2026-10-18; method: `grep -rl roll_village pool` - none). Only tests call
it, and one of them (`tests/soak/test_village_determinism.py`, run only by `make soak`) has failed on main since `221a9a08e`
(feature 328 wave 78), unnoticed because nothing ships from the code it tests. The GM's condition, "if nothing ships from it",
holds; the instruction is to delete it now, and NOT to carry the failure anywhere.

## What "it" is, read literally

1. **`roll_village`**: `l7r/diagram/settlement/rolling/roll.py` whole - `RollVillageMixin`, its seven `_roll_*` stages,
   `_roll_cremation` and `_MarginFrame` - and its place in `RollingMixin`'s bases.
2. **What only it reached**: every engine definition whose only production caller was in `roll.py` (measured 2026-10-18 by a
   name-level closure over `l7r/` and `pool/`, code tokens only, iterated to a fixpoint; the script is
   `specs/388-retire-roll-village/closure.py`): `water_sources_for`, `water_source_anchor`, `crop_to_content`,
   `cremation_ground` (with `ROOFED_SHARE`, `cremation_outline`), `civic_grounds/edge_seat.py`'s `edge_seat`, `EdgeGround`,
   `ANGLES`, `rect_gap`, `rect_samples`, `cut_undeckable_lanes` (with `CUT_GAP_FT`), `PlacerMixin.headman` and `build_comb`.
   Code with no production caller is not shipping, so it is part of "it"; the plan confirms each name before it goes.
3. **Its tests**: every test that calls (1) or (2) - deleted, not ported.

## Requirements

- **FR-001**: `roll_village` and everything in "What it is" (2) are deleted from the engine. A name the plan finds still
  reached by shipping code (a pool map, the scripted hamlet, a Mode A sheet, the page) is kept, and the plan says who reaches it.
- **FR-002**: Their tests are deleted; a test file left empty is removed. The `rolls_map` marker lists in
  `tests/test_markers.py` drop `roll_village`.
- **FR-003**: Prose that describes `roll_village` as live is updated where it stands: the package indexes
  (`settlement/CLAUDE.md`, `settlement/rolling/CLAUDE.md`), the module and function docstrings that cite it
  (`hamletgen/__init__.py`, `hamletgen/cluster.py`, `settlement/houses.py`, `settlement/_geom/village.py`,
  `settlement/city/bridges.py`, `settlement/structures/fixtures/siting.py`) and the research claims index entries for the
  deleted code (the claims tooling regenerates or drops them). Specs are history and keep their words.
- **FR-004**: The village soak failure is NOT carried: the "Carried: from 387" section of feature 380's spec is removed (the
  GM: "not even move it into the 384 backlog"). Feature 380's placeholder gains one line naming the commit before this
  feature's deletion, so the village tier can read the old cremation-ground seat (research 0238) from git if it wants it - a
  pointer, not an owed item.
- **FR-005**: The frozen legacy maps that were drawn with `roll_village` (`legacy-hand-authored-pool/hamlets/honda`,
  `.../shimizu`, `legacy-hand-authored-pool/villages/kikuta`) are NOT edited: the legacy pool is frozen, its maps exhibits
  that are never regenerated, so their `.gen.py` keep their words and simply no longer run. Their manifests, renders and
  pages are untouched.
- **FR-006**: No shipping map changes: the deletion removes only code no shipping map runs.

## Success Criteria

- **SC-001**: `grep -rn roll_village l7r pool tests` finds nothing (the legacy pool and `specs/` excepted, FR-005).
- **SC-002**: `make done` is green - the 100% coverage floor over the engine, ruff, pyrefly, and every test - with the
  deleted code gone.
- **SC-003**: The landing cohort (`make cohort-landing`) regresses no seed against main, and the pool hamlets regenerate
  byte-identical (FR-006; `git diff HEAD` on their manifests after `make maps` is empty).
- **SC-004**: `make soak` no longer contains the village test, and every soak test left in it passes as on main.

## Decisions Recorded

- **D1 - delete, not port**: the tests of deleted code go with it (FR-002); none is ported to the scripted hamlet, because the
  scripted hamlet's own tests already cover what it draws. Who chose: the GM ("just delete it").
- **D2 - the legacy `.gen.py` files stay as written** (FR-005): editing frozen exhibits is a hand-map edit; leaving a call to
  a deleted method in a file nothing runs costs nothing. Alternative priced: rewrite their headers to say the engine is gone -
  rejected as an edit to frozen files the GM has not asked for.
- **D3 - no research changes**: this feature removes code, so no rendering decision changes and no map draws anything new.
  The research pages the deleted docstrings cited (0031, 0084, 0190, 0238) keep their words; the claims of the deleted code
  leave the claims index.

## Assumptions

- "Nothing ships from it" means no map under `pool/` - the live pool - runs it. The legacy pool is frozen and never runs.
- The closure in "What it is" (2) is a name-level measurement; the gate's coverage floor and its import of every module are the
  check that it missed nothing reached and deleted nothing live.
