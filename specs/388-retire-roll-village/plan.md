# Implementation Plan: Retire roll_village

**Branch**: none (main, in the clone) | **Date**: 2026-10-18 | **Spec**: `spec.md`

## Summary

Delete `Settlement.roll_village` (`settlement/rolling/roll.py`), every engine definition only it reached, and their tests;
repoint the prose that names them; drop the 380 carry (FR-004). No shipping map runs any of it, so no map changes (FR-006).

## Technical Context

Python, the engine under `l7r/diagram/`; pytest under `make`. **Single-artifact target**: none is regenerated to prove a
behavior - the deletion changes no shipping map; FR-006 is proven across the whole live pool at once (`make maps`, then
`git diff HEAD` on the manifests is empty) and by the landing cohort.

## Performance bookends

`388-start` taken on unmodified code before the first edit; `388-end` before the push. Removing code no shipping map runs
should move nothing; a flag over the band is mentioned at the landing with its load caveat.

## Constitution Check

- I, II: N/A - no UI in this repository.
- III, IV, V, VII, VIII, IX: N/A - no pool content, no SOURCE block, no in-world prose.
- VI: PASS - each task names its verification; `make maps` (the pool, byte-identical) and `make cohort-landing` stand in for
  the reference-then-pool pair, since nothing is meant to move.
- X: PASS - ruff, pyrefly, the full coverage floor (`make done`); no new behavior, so no red-green test; nothing indexed is added.
- XII: PASS - no rendering decision changes (spec D3); the deleted code's research claims leave the claims index.
- XIII: PASS - the landing cohort refuses a regressed seed; SC-004 holds the soak tier.
- XIV: the defect found (the village soak failure) is resolved by deleting what it tests, per the GM.
- XVI: PASS - the literal reading is the spec's "What it is".

## T01 - the deletion (FR-001, FR-002)

Each name of the spec's closure, confirmed by hand (2026-10-18; method: `grep -rnw <name> l7r pool scripts Makefile
legacy-hand-authored-pool`, every hit read):

| name | where | who else calls it | verdict |
|---|---|---|---|
| `RollVillageMixin`, `roll_village`, `_roll_*`, `_roll_cremation`, `_MarginFrame` | `settlement/rolling/roll.py` | no engine module, no live map; 3 frozen exhibits (Honda, Shimizu, Kikuta) | delete the file; drop the base from `RollingMixin` (the GM's ruling; FR-005) |
| `water_sources_for`, `water_source_anchor` | `settlement/water_source.py` | none (`hamletgen/water/fit.py` names the anchor in prose only) | delete the module and `WaterSourceMixin` from `Settlement`'s bases |
| `edge_seat`, `EdgeGround`, `ANGLES`, `rect_gap`, `rect_samples`, its own `convex_hull`, `STEP_FT` | `settlement/civic_grounds/edge_seat.py` | none (`hamletgen/burial.py` names it in prose; the live callers of `convex_hull` import `_geom/primitives`'s) | delete the module whole |
| `cut_undeckable_lanes`, `CUT_GAP_FT` | `settlement/city/bridges.py` | none | delete |
| `BUNDLE_PITCH_FT` | `settlement/_geom/village.py`, re-exported by `settlement/__init__.py` | none - found by the closure's re-run with re-exports not counted as uses | delete it, its re-export and its test (`test_a_rolled_cluster_band_is_sized_in_REAL_FEET_at_the_map_s_grain`, whose subject is the roller's band) |
| `build_comb`, `crop_to_content`, `cremation_ground` (+ `ROOFED_SHARE`, `cremation_outline`), `PlacerMixin.headman` | `waterfields/comb.py`, `settlement/core.py`, `civic_grounds/funerary.py`, `rolling/place.py` | 13, 11, 7 and 3 frozen exhibits | KEEP (spec D1b, feature 174's precedent) |

`Settlement` keeps a class-level annotation of `_nucleated` on `RollingMixin` (no runtime member): `roll.py` held the one
assignment pyrefly read it by. The closure is run again after the deletion until it names nothing more; any further name
goes through the same table. Tests: every test whose subject is a deleted name goes - the `roll_village` tests in
`tests/settlement/test_rolling.py` (the cremation-seat tests and `_village_with_houses`; the no-cremation-ground test keeps
its pool scan), `tests/gate/settlement/test_rolling.py`, `tests/full/settlement/test_rolling.py`,
`tests/soak/test_village_determinism.py`; `test_houses.py`'s water-source test, `test_city.py`'s undeckable-lanes test,
`test_m8_placers_287.py`'s edge-seat test, `test_geom.py`'s band-pitch test and surface entry, and in
`hamletgen/test_burial.py` `test_rect_gap`, the `test_the_edge_seat_*` tests,
`test_the_ground_stands_beyond_the_last_house_not_in_a_gap_among_them`, `test_convex_hull_of_few_points` and `_seat` (only
the no-ground-of-its-own test stays) - and a file left with no test is removed. The coverage floor then names any line only
the deleted tests reached: it is deleted if nothing reaches it (the same table), else a test is owed.

Verify: `make quick` per step; `make done` green.

## T02 - the prose (FR-003, FR-004)

Repoint, at the point of change, every docstring and comment that names a deleted definition as live: the `roll_village`
mentions in `hamletgen/__init__.py` (the comparison table's middle column becomes "the knob engine", retired),
`hamletgen/cluster.py`, `hamletgen/water/fit.py` (the water-source anchor), `settlement/houses.py`, `settlement/_geom/village.py`
(the band pitch), `settlement/city/bridges.py` (the undeckable-lanes pass), `settlement/structures/fixtures/siting.py`,
`settlement/rolling/__init__.py`, `hamletgen/burial.py` (the edge seat "the village's cremation ground still uses"),
`tests/hamletgen/test_burial.py`'s docstring; the indexes `settlement/CLAUDE.md`, `settlement/rolling/CLAUDE.md`,
`settlement/civic_grounds/CLAUDE.md` (the edge-seat row), `settlement/_geom/CLAUDE.md` (the band pitch), `tests/soak/CLAUDE.md`.
The kept helpers' prose is untouched. The claims index is updated by its own targets (`make claims-owed`, impl-drift,
`make claims-checked`). Feature 380's spec loses its "Carried: from 387" section, and its cremation-ground and burial-ground
items name the code they cited (the roller's cremation seat, the edge seat) as deleted by 388 and readable from git at the
commit before the deletion, their design and rulings unchanged (FR-004). The legacy pool is not touched (FR-005).

Verify: `grep -rn roll_village l7r pool tests` empty (SC-001); `grep -rnwE "edge_seat|water_source_anchor|cut_undeckable_lanes|BUNDLE_PITCH_FT" l7r` names nothing live.

## T03 - measure and land (FR-006, SC-002 - SC-004)

`make maps` and `git diff HEAD -- pool` on the manifests (empty); `make soak` (the village test gone, the rest green);
`make done`; `make perf LABEL=388-end`; `make cohort-landing`; the claims gate; the feature report; the gated push.

Verify: each command's log tail read before the tick.

## Project Structure

Touched: `l7r/diagram/settlement/{rolling,civic_grounds,city}/`, `settlement/{core,water_source,houses}.py`,
`waterfields/comb.py`, `hamletgen/` docstrings, `tests/` (deletions), `specs/380-*/spec.md`, the claims index.

## Complexity Tracking

None.
