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

Each name of the spec's closure, confirmed by hand (2026-10-18; method: `grep -rnw <name> l7r pool scripts Makefile`, every
hit read):

| name | where | production code that calls it, other than `roll.py` | verdict |
|---|---|---|---|
| `RollVillageMixin`, `roll_village`, `_roll_*`, `_roll_cremation`, `_MarginFrame` | `settlement/rolling/roll.py` | none | delete the file; drop the base from `RollingMixin` |
| `water_sources_for`, `water_source_anchor` | `settlement/water_source.py` | none (`hamletgen/water/fit.py` names `water_source_anchor` in prose only) | delete |
| `crop_to_content` | `settlement/core.py` | none - the scripted hamlet crops through `content_view` / `crop_to_view` (`hamletgen/hinterland/frame.py`); 15 docstrings and comments name it | delete; repoint the prose (T02) |
| `cremation_ground`, `ROOFED_SHARE`, `cremation_outline` | `settlement/civic_grounds/funerary.py` | none | delete |
| `edge_seat`, `EdgeGround`, `ANGLES`, `rect_gap`, `rect_samples` | `settlement/civic_grounds/edge_seat.py` | none (`hamletgen/burial.py` names it in prose: the hamlet draws no burial ground) | delete the definitions; the module goes if nothing is left in it |
| `cut_undeckable_lanes`, `CUT_GAP_FT` | `settlement/city/bridges.py` | none | delete |
| `PlacerMixin.headman` | `settlement/rolling/place.py` | none (the word "headman" elsewhere is the role, not the method) | delete |
| `build_comb` | `waterfields/comb.py` | none - the scripted hamlet calls `carve_comb` and `finish_comb` (`hamletgen/water/fit.py`); 20-odd docstrings name it as the comb builder | delete the wrapper; its docstring (the comb layout, `grain`) moves onto `carve_comb`; repoint the prose (T02) |

The closure is run again after the deletion (`closure.py` with the newly deleted files) until it names nothing more; any
further name goes through the same table before it is deleted. Tests: every test of a deleted name goes (the
`roll_village` tests in `tests/settlement/test_rolling.py`, `tests/gate/settlement/test_rolling.py`,
`tests/full/settlement/test_rolling.py`, `tests/soak/test_village_determinism.py`; the tests of the closure names in
`test_houses.py`, `test_crop_framing.py`, `test_civic_grounds.py`, `tier_city/.../test_civic_grounds.py`,
`hamletgen/test_burial.py`, `test_city.py`, `test_villages.py`, `test_caption_paths.py`, `test_map_vocabulary.py` and the
composed-surface guard's member list), and a file left with no test is removed. The coverage floor then names any line only
the deleted tests reached: it is deleted if no shipping code reaches it (the same table), else a test is owed.

Verify: `make quick` per step; `make done` green.

## T02 - the prose (FR-003, FR-004)

Repoint, at the point of change, every docstring and comment that names a deleted definition as live: `crop_to_content` ->
the crop (`content_view` / `crop_to_view`); `build_comb` -> `carve_comb` / `finish_comb`; `roll_village` mentions in
`hamletgen/__init__.py` (the comparison table loses its middle column), `hamletgen/cluster.py`, `settlement/houses.py`,
`settlement/_geom/village.py`, `settlement/city/bridges.py`, `settlement/structures/fixtures/siting.py`; the indexes
`settlement/CLAUDE.md`, `settlement/rolling/CLAUDE.md`, `settlement/civic_grounds/CLAUDE.md`, `waterfields/CLAUDE.md`. The
claims index (`dev/claims-index.json`, `dev/claims-deferred.json`) is rebuilt by its own target. Feature 380's spec loses its
"Carried: from 387" section and gains the one-line pointer (FR-004). The legacy pool is not touched (FR-005).

Verify: `grep -rn roll_village l7r pool tests` empty (SC-001); `grep -rnw "crop_to_content\|build_comb" l7r` empty.

## T03 - measure and land (FR-006, SC-002 - SC-004)

`make maps` and `git diff HEAD -- pool` on the manifests (empty); `make soak` (the village test gone, the rest green);
`make done`; `make perf LABEL=388-end`; `make cohort-landing`; the claims gate; the feature report; the gated push.

Verify: each command's log tail read before the tick.

## Project Structure

Touched: `l7r/diagram/settlement/{rolling,civic_grounds,city}/`, `settlement/{core,water_source,houses}.py`,
`waterfields/comb.py`, `hamletgen/` docstrings, `tests/` (deletions), `specs/380-*/spec.md`, the claims index.

## Complexity Tracking

None.
