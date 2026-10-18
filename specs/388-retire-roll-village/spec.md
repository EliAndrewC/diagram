# Feature Specification: Retire roll_village - delete the old knob engine nothing ships from

**Feature Branch**: none (main, in the clone; `SPECIFY_FEATURE=388-retire-roll-village`)

**Created**: 2026-10-18

**Status**: Amendment 1 in progress (the four helpers). As first landed: Done 2026-10-18 - T01-T03 ticked: make done green, make maps clean (pool unchanged), make soak 9 passed, cohort-landing 54/54, bookends 18.9 -> 18.8 s, claims none owed; spec FAITHFUL (round 6), plan CLEAR; the GM review lands open

**Approved**: the GM, 2026-10-18, "I think if nothing ships from it then we should just delete it now and not even move it into the 384 backlog."

**Amendment 1 approved**: the GM, 2026-10-18, "I believe that the frozen maps do not need to stay runnable, and therefore the four helpers can go too."

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
   **Amendment 1 - the four helpers only frozen exhibits call go too** (the GM: "the frozen maps do not need to stay
   runnable"): `build_comb` (13 exhibit scripts), `crop_to_content` (11), `cremation_ground` (7, with `ROOFED_SHARE` and
   `cremation_outline`) and `PlacerMixin.headman` (3). As first landed they were kept on feature 174's precedent (an
   exhibit's call keeps a builder); the GM's ruling retires that precedent for these four. `make dead-closure` with the four
   cut (2026-10-18) names nothing else newly dead.
3. **Its tests**: every test whose SUBJECT is (1) or (2) - deleted, not ported; a test of shipping code that reached it
   through a deleted one-call wrapper is repointed to the live pair (FR-002, amendment 1).

## Requirements

- **FR-001**: `roll_village` and everything in "What it is" (2) are deleted from the engine. A name the plan finds still
  reached by shipping code (a pool map, the scripted hamlet, a Mode A sheet, the page) is kept, and the plan says who reaches it.
- **FR-002**: A test goes with the code it tests: a test whose SUBJECT is deleted code is deleted, and a test file left
  empty is removed. This reaches one scripted-hamlet test file, `tests/hamletgen/test_burial.py`: `test_rect_gap`, the
  `test_the_edge_seat_*` tests, `test_the_ground_stands_beyond_the_last_house_not_in_a_gap_among_them` (it tests the seat
  through `_seat`), `test_convex_hull_of_few_points` (it tests `edge_seat.py`'s own hull) and the `_seat` helper go; only
  `test_a_hamlet_draws_no_ground_of_its_own_and_records_where_its_dead_lie` stays, and the docstring stops naming the edge
  seat as live. A test that mixes a deleted subject with a live one keeps the live part (the pool scan in
  `test_rolling.py`'s no-cremation-ground test). The `rolls_map` marker lists in `tests/test_markers.py` drop
  `roll_village`. **Amendment 1**: the tests of `cremation_ground` and `headman` go (their subjects are deleted); a test of
  SHIPPING code that reached it through a deleted one-call wrapper keeps its subject and calls the live pair the scripted
  hamlet calls - the comb tests that laid a field with `build_comb` call `finish_comb(carve_comb(...))` through one test
  helper, the frame tests that cropped with `crop_to_content` call `crop_to_view(content_view(...))` through one test
  helper - and a test of a wrapper ITSELF (carve-then-finish equals the wrapper) loses that clause. The surface censuses that
  scan the legacy pool for consumers (`tests/waterfields/test_surface.py`, `tests/hamletgen/test_surface.py`) stop scanning
  it: a frozen exhibit is no longer a consumer the engine must resolve.
- **FR-003**: Prose that describes `roll_village` or the closure's names as live is updated where it stands: the package indexes
  (`settlement/CLAUDE.md`, `settlement/rolling/CLAUDE.md`, `settlement/civic_grounds/CLAUDE.md`, `waterfields/CLAUDE.md`,
  `tests/soak/CLAUDE.md`), the module and function docstrings that cite them (`hamletgen/__init__.py`, `hamletgen/cluster.py`,
  `hamletgen/burial.py` - "which the village's cremation ground still uses" -, `hamletgen/water/fit.py`, `settlement/houses.py`,
  `settlement/_geom/village.py`, `settlement/city/bridges.py`, `settlement/structures/fixtures/siting.py`) and the research claims index entries for the deleted code (the claims tooling
  regenerates or drops them). Specs are history and keep their words - except feature 380's, a live placeholder (FR-004).
  **Amendment 1**: the same for the four helpers - every docstring, comment and index naming `build_comb`, `crop_to_content`,
  `cremation_ground` or `headman` (the method) as live is repointed: the comb builder's account moves onto `carve_comb`, the
  crop's frame rule onto `content_view`, and the prose names those.
- **FR-004**: The village soak failure is NOT carried: the "Carried: from 387" section of feature 380's spec is removed (the
  GM: "not even move it into the 384 backlog"). Feature 380's two items that cite deleted code are reworded where they stand:
  the cremation ground ("already drawn by the roller's village tier ... The village generator reuses it") and the burial
  ground ("seated through `settlement/civic_grounds/edge_seat.py`") name that code as deleted by feature 388 and readable from
  git at the commit before the deletion. Their design and the GM's rulings keep their words; the village tier builds the seat
  anew or recovers it from git - nothing is owed to the deleted code.
- **FR-005**: The frozen legacy maps are NOT edited: the legacy pool is frozen, its maps exhibits that are never
  regenerated. The three drawn with `roll_village` (`legacy-hand-authored-pool/hamlets/honda`, `.../shimizu`,
  `legacy-hand-authored-pool/villages/kikuta`) keep their `.gen.py` words and simply no longer run; their manifests, renders
  and pages are untouched. **Amendment 1**: the same holds for every exhibit that calls one of the four helpers - 18 scripts
  in all stop running, and none is edited (D2).
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

- **SC-006** (FR-001, FR-002, FR-003, amendment 1): no engine module defines or calls `build_comb`, `crop_to_content`,
  `cremation_ground` or `PlacerMixin.headman`; `make dead-closure BASE=<the commit before the amendment>` names nothing NEWLY
  DEAD and no PINNED test, and its STILL CALLED lines name only frozen exhibits.
## Decisions Recorded

- **D1 - a test follows its subject**: a test of deleted code goes with it (FR-002); none is ported to the scripted
  hamlet, which draws none of it. Who chose: the GM ("just delete it").
- **D1b - the exhibits' helpers go (amendment 1)**: as first landed the four were kept on feature 174's precedent; the GM
  ruled the frozen maps need not stay runnable ("especially if it streamlines our code base and reduces our support
  surface"), so they go, their tests of shipping code repointed (FR-002). Who chose: the GM.
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
