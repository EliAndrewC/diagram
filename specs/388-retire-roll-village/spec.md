# Feature Specification: Retire roll_village - delete the old knob engine nothing ships from

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=388-retire-roll-village`)

**Created**: 2026-10-18

**Status**: Done 2026-10-18 - T01-T03 ticked: make done green, make maps clean (pool unchanged), make soak 9 passed, cohort-landing 54/54, bookends 18.9 -> 18.8 s, claims none owed; spec FAITHFUL (round 6), plan CLEAR; the GM review lands open

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
2. **What only it reached**: every engine definition whose only caller was in `roll.py` - no other engine module, no
   live pool map and no frozen legacy exhibit calls it (measured 2026-10-18 by a name-level closure over `l7r/` and `pool/`,
   code tokens only, iterated to a fixpoint, re-exports (`X as X`) not counted as uses; the script is
   `specs/388-retire-roll-village/closure.py`; every name then grepped in `legacy-hand-authored-pool/`): `water_sources_for`,
   `water_source_anchor` (with `settlement/water_source.py` and its mixin), `civic_grounds/edge_seat.py` whole (`edge_seat`,
   `EdgeGround`, `ANGLES`, `rect_gap`, `rect_samples`, and - names the closure cannot see because they are also defined
   elsewhere - its own `convex_hull` and `STEP_FT`), `cut_undeckable_lanes` (with `CUT_GAP_FT`) and `BUNDLE_PITCH_FT`.
   **Kept, because a frozen exhibit calls it** (the precedent of feature 174, `tests/waterfields/test_hill.py`: a legacy
   exhibit's call keeps an engine builder): `build_comb` (13 exhibits), `crop_to_content` (11), `cremation_ground` (7, with
   `ROOFED_SHARE` and `cremation_outline`) and `PlacerMixin.headman` (3). Deleting them would leave 17 more exhibit scripts unrunnable
   to delete four small helpers; deleting `roll_village` itself leaves the 3 that call it (FR-005).
3. **Its tests**: every test whose SUBJECT is (1) or (2) - deleted, not ported (FR-002).

## Requirements

- **FR-001**: `roll_village` and everything in "What it is" (2) are deleted from the engine. A name the plan finds still
  reached by shipping code (a pool map, the scripted hamlet, a Mode A sheet, the page) is kept, and the plan says who reaches it.
- **FR-002**: A test goes with the code it tests: a test whose SUBJECT is deleted code is deleted, and a test file left
  empty is removed. This reaches one scripted-hamlet test file, `tests/hamletgen/test_burial.py`: `test_rect_gap`, the
  `test_the_edge_seat_*` tests, `test_the_ground_stands_beyond_the_last_house_not_in_a_gap_among_them` (it tests the seat
  through `_seat`), `test_convex_hull_of_few_points` (it tests `edge_seat.py`'s own hull) and the `_seat` helper go; only
  `test_a_hamlet_draws_no_ground_of_its_own_and_records_where_its_dead_lie` stays, and the docstring stops naming the edge
  seat as live. A test that mixes a deleted subject with a live one keeps the live part (the pool scan in
  `test_rolling.py`'s no-cremation-ground test). The kept helpers' tests stay as they are. The `rolls_map` marker lists in
  `tests/test_markers.py` drop `roll_village`.
- **FR-003**: Prose that describes `roll_village` or the closure's names as live is updated where it stands: the package indexes
  (`settlement/CLAUDE.md`, `settlement/rolling/CLAUDE.md`, `settlement/civic_grounds/CLAUDE.md`, `waterfields/CLAUDE.md`,
  `tests/soak/CLAUDE.md`), the module and function docstrings that cite them (`hamletgen/__init__.py`, `hamletgen/cluster.py`,
  `hamletgen/burial.py` - "which the village's cremation ground still uses" -, `hamletgen/water/fit.py`, `settlement/houses.py`,
  `settlement/_geom/village.py`, `settlement/city/bridges.py`, `settlement/structures/fixtures/siting.py`) and the research claims index entries for the deleted code (the claims tooling
  regenerates or drops them). Specs are history and keep their words - except feature 380's, a live placeholder (FR-004).
- **FR-004**: The village soak failure is NOT carried: the "Carried: from 387" section of feature 380's spec is removed (the
  GM: "not even move it into the 384 backlog"). Feature 380's two items that cite deleted code are reworded where they stand:
  the cremation ground ("already drawn by the roller's village tier ... The village generator reuses it") and the burial
  ground ("seated through `settlement/civic_grounds/edge_seat.py`") name that code as deleted by feature 388 and readable from
  git at the commit before the deletion. Their design and the GM's rulings keep their words; the village tier builds the seat
  anew or recovers it from git - nothing is owed to the deleted code.
- **FR-005**: The frozen legacy maps are NOT edited: the legacy pool is frozen, its maps exhibits that are never
  regenerated. The three drawn with `roll_village` (`legacy-hand-authored-pool/hamlets/honda`, `.../shimizu`,
  `legacy-hand-authored-pool/villages/kikuta`) keep their `.gen.py` words and simply no longer run; their manifests, renders
  and pages are untouched. Every other exhibit still runs: no other name it calls is deleted ("What it is" (2), kept).
- **FR-006**: No shipping map changes: the deletion removes only code no shipping map runs.

## Success Criteria

- **SC-001** (FR-001, FR-003, FR-005): `grep -rn roll_village l7r pool tests` finds nothing (the legacy pool and `specs/` excepted, FR-005), and no engine docstring, comment or package index names
  a deleted definition as live (FR-001, FR-003).
- **SC-002** (FR-001, FR-002): `make done` is green - the full-coverage floor over the engine, ruff, pyrefly, and every test - with the
  deleted code gone (FR-001, FR-002).
- **SC-003**: The landing cohort (`make cohort-landing`) regresses no seed against main (FR-006), and the pool hamlets regenerate
  byte-identical (FR-006; `git diff HEAD` on their manifests after `make maps` is empty).
- **SC-004**: `make soak` no longer contains the village test, and every soak test left in it passes as on main (FR-002).
- **SC-005** (FR-004): Feature 380's spec has no "Carried: from 387" section, and its cremation-ground and burial-ground items name
  the deleted code as deleted by 388 with the commit that still holds it (FR-004).

## Decisions Recorded

- **D1 - a test follows its subject**: a test of deleted code goes with it (FR-002); none is ported to the scripted
  hamlet, which draws none of it. Who chose: the GM ("just delete it").
- **D1b - the exhibits' helpers stay** ("What it is" (2)): four helpers lost their last ENGINE caller with the roller but
  are still called by frozen exhibits. Feature 174 ruled that such a call keeps a builder; deleting them would make 17 more
  exhibit scripts unrunnable, which the GM did not ask for. Alternative priced: delete them too and repoint their tests
  through test helpers (tried 2026-10-18 - 40-odd files of churn, and the waterfields surface census then failed on the
  exhibits' imports). Who chose: the session, on that precedent; reported to the GM.
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
