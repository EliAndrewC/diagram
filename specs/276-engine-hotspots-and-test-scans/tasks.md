# Tasks - feature 276, engine hotspots and test scans

Spec: [`spec.md`](spec.md) (FAITHFUL, round 3). Plan: [`plan.md`](plan.md) (D1-D19). Research: [`research.md`](research.md).
Order: F's harness target first (so every after-figure is taken the same way), then A and B (test side, US1), then C
(US2), D (US3), E (US4), each proved on its tests and on Inashiro before the pool, then the sweep and the records.

## Setup

- [ ] T01 `make h276` runs `harness.py` into a JSON; `measurements.json` entries name it as their `command` (D17)
      research: rendering

## US1 - the slow tests stop redoing work (P1)

- [x] T02 [US1] `tests/_engine_ast.py`: the content-keyed parse cache, the `PARSES` counter, `walked()`, `engine_modules()` with a needle (D1)
      research: rendering
      verify: DONE. tests/_engine_ast.py: content-keyed parse cache, PARSES counter, walked(), engine_modules() with needles and opt-in skip_broken, module_level(); tests/test_engine_ast.py green
- [x] T03 [US1] The four AST tests read from it, each scan lifted to a function, each with its needle (D2): `tests/test_memory.py`, `tests/hamletgen/test_driver.py`, `tests/test_package_surfaces.py`, `tests/settlement/test_water_ways.py`
      research: rendering
      verify: DONE. the four tests read the shared parse with identifier/keyword needles (heavy names, STAGES, del, diagram), each scan lifted to a function; their files green (87 passed)
- [x] T04 [US1] `tests/test_engine_ast.py`: one parse per file across the four; each scan flags a planted offender (D3); SC-001 by the harness (`measure.py`)
      research: rendering
      verify: DONE. tests/test_engine_ast.py: one parse per file across the four scans (non-vacuous overlap asserted), planted offenders caught by all three lifted scans, broken files raise unless skip_broken
- [x] T05 [P] [US1] Record tests: the cached id table, the `.md` prefilter (D4) in `tests/interactive/test_record.py`; the joined corpus and the word-set lookup with its equality test (D5) in `tests/interactive/test_record_format.py`; planted-violation tests (D6); SC-001a by the harness (`measure.py`)
      research: rendering
      verify: DONE. test_record.py: _ids_of content-keyed, .md prefilter in both token scans, broken_links and md_token_hits lifted with planted tests; test_record_format.py: bounded_words set + stands_in with an equality test over every boundary case (a flawed lookbehind caught: oku/ugi); 45 + 3 green

## US2 - a house is seated without testing a hundred wrong places first (P1)

- [x] T06 [US2] The placed-house index: `M["houses"]` and `placed` as `Indexed` (`settlement/core.py`, `settlement/rolling/farmsteads.py`), every per-candidate scan in `settlement/rolling/fit.py` answered from an `indexed_grid`; the equality tests against the linear forms (D7)
      research: rendering
      verify: DONE. M[houses] and placed Indexed (core.py, farmsteads.py rebinds, _solve_homestead bumps on its in-place move); every per-candidate scan in fit.py from houses_meeting / the placed reach index; test_the_house_and_placed_indexes_answer_every_fit_rule_as_the_scans_did (both paths, 400 candidates, 40+ houses) + the moved-record test green
- [x] T07 [US2] The static ground index: `SiteCorridors` vertex and hole grids in `hamletgen/homesteads/boundary.py`; the equality test (D8)
      research: rendering
      verify: DONE. SiteCorridors: a vertex grid per ring, a hole grid, one grid lookup per rectangle; test_the_indexed_hit_points_answer_as_the_linear_scan_did (1,800 random rectangles over rings with holes) green
- [x] T08 [US2] The free-ground index (D9): static surely-taken cells where a site boundary is installed (empty otherwise) plus the placed boxes added as each bundle lands (D7's grid); asked first for every spiral offset and every `_slide` step (dispersed) and, on the nucleated path, for the placed-box hits and the static ground only where the loop judges ground; the dispersed pre-screen behind it (D9a); in `settlement/rolling/place.py`, `settlement/rolling/fit.py` and `hamletgen/homesteads/boundary.py`; the same-seat tests on both paths, including the whole-envelope-clear, side-on-taken-ground case
      research: rendering
      verify: DONE. FreeGround (static surely-taken cells where a boundary is installed) + the placed index; _seat_refused and _bundle_refused ahead of every spiral offset and slide step (dispersed); nucleated prune only where the loop judges ground; test_the_free_ground_changes_no_seat (both paths, rescue + toy, all pre-screens off vs on), the envelope-clear case, and the surely-taken cells refused by the real ground test - all green; plan review 4 CLEAR
- [x] T09 [US2] The unraked bundle template with the rake per candidate, and the household-rolled yard, garden jitter and bed split, in `settlement/rolling/bundle.py` / `homestead_parts/yards.py` (D10); SC-002 and SC-003 by the harness on both paths
      research: rendering
      verify: DONE. _bundle_geom = the unraked _bundle_layout built once per household and size, moved and raked per seat; yard, garden jitter and bed split rolled at the household seat; dispersed rescue 2.718 s -> 0.352 s with 46781 -> 128 full fit tests, 240 seeds 29372 -> 304, per house flat on both paths (harness scratch runs; after-figures recorded at T18)
- [x] T09a [US2] `_toy_hamlet` sets the placer's own nucleated switch; the spur test says it wants a dispersed cluster (D20)
      research: rendering
      verify: DONE. _toy_hamlet sets s._nucleated from its plan; the spur test asks for a dispersed cluster explicitly; hamletgen 511 green
- [ ] T10 [US2] Inashiro regenerated (`make map`); its houses, form and yards read against `pool-before.json`
      research: rendering

## US3 - a comb field closes its seams in a fraction of the time (P2)

- [ ] T11 [US3] Compute once (D11) and batch (D12) in `waterfields/seams/plots.py` and `close.py`
      research: rendering
- [ ] T12 [US3] Touched cells in `_plant` per connected piece of each row, the diagonal-sliver and two-piece-row tests (D13); re-profile and treat the next heaviest step (D14); SC-004 by the harness (`measure.py`)
      research: rendering
- [ ] T13 [US3] Inashiro regenerated; its paddy, flooded and dry-plot counts against `pool-before.json`
      research: rendering

## US4 - a track is routed without re-scanning the map per candidate (P3)

- [ ] T14 [US4] `PathChecker` in `hamletgen/ways/checks.py`, used by `hamletgen/ways/track.py` (D15); the equality test over Inashiro's candidate paths (D16); SC-005 by the harness (`measure.py`)
      research: rendering
- [ ] T15 [US4] Inashiro regenerated; its lanes against `pool-before.json`
      research: rendering

## Across the pool, and the records

- [ ] T16 `make done` green (every live pool map regenerated, 100% coverage); FR-006's counts for all five hamlets against `pool-before.json`, recorded in research
      research: rendering
- [ ] T17 The after-cohort `make cohort N=24` against research R7's baseline; every newly failing seed diagnosed
      research: rendering
- [ ] T18 `make perf LABEL=276-end`, `make perf-report AGAINST=276-start`; the after-figures in `measurements.json` and research; `make quick ALL=1` and `make done` wall time
      research: rendering
- [ ] T19 `dev/performance.md` gains the three shapes with their measurements (D19)
      research: rendering
