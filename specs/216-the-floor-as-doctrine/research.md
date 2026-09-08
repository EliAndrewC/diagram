# Research - 216 the floor as doctrine

## R1. The four sites, and what each needs

From 215's audit (`specs/215-the-floor-itself/research.md` R1): Woodland-shrink reaches 0 lines nothing else
does; Clamped 3 (`hamletgen/sink.py` 285-287, the pond-to-off-map fallback); Polder 19 0 alone (the two polders
together 3, all in `hamletgen/water.py`, two of them reached by either polder); the three seatings TEN together
(LaneOnly 4: `ways/route.py` 174-176, `ways/touch.py` 465; OneHouse 5: `hinterland/stages.py` 83,
`homesteads/wells.py` 311-314, `ways/web.py` 221; CloudOnly alone 0; and one line two of the three share that nothing outside them reaches - the gate's floor names it). A reference roll's stage times (perf snapshot,
seed 4): field 5.8 s, hinterland 8.0 s, windbreak 7.4 s of 24.4 s; homesteads 0.95 s. The seating tests read only
what the homestead pass decided, so a partial roll to that pass costs the field stage once (~6 s) and the three
seatings a second each, against three full rolls of ~24 s.

**The probes (2026-09-08, before implementation).** The woodland band cannot be swept on the pool's loaded manifest
(`open_ground_patches` needs the field stage's plan state: `min() of an empty sequence`), so it runs on the hinterland
unit tests' stub site, which does return parcels. The three seatings on copies of one partial roll: the LINEAR seed-5
state (prefix to the homestead pass 3.3 s) holds the cloud's assertions (10 placed, `cluster_seeding` cloud, the
shape honored) and LaneOnly's and OneHouse's counts, but the frontage offers 0 seats until the TRACK stage has drawn
the connector - so each variant runs the homestead pass and the track (about a second each). The nucleated seed-7
state (prefix 11 s) offers no connector seats at all, so the linear one is the base.

## R2. Measured after (2026-09-08)

**The census, on the green full gate** (`f216-done4`, INCREMENTAL=0 by the gate's own choice - a non-module file under
`tests/` changed):

    roll census: 3 roll(s) of 3 spec(s); 11 request(s) served from a shared roll; roster 3 row(s)
      Inashiro seed=4: 1 roll(s), attempts 1, 26s - rostered; requested by test_a_map_is_immune_to_an_upstream_change_in_the_number_of_
      Polder seed=12: 1 roll(s), attempts 1, 64s - rostered; requested by test_a_rolled_cohort_passes_the_whole_gate
      Seatings seed=5: 1 roll(s), attempts 4, 17s - rostered; requested by test_the_cluster_seeds_cloud_still_seats_a_hamlet_when_the_r
      stand-in stage rolls (stub-excepted modules, no map): 19, 2.4s in all
      pool gen: five, all served from the gen cache, not rolled

The Seatings row's four attempts are the one child's prefix roll and its three seated variants (spec D2). SC-001 holds.
Cold (the run before, where `ways/web.py` had changed and every pool gen re-rolled): 9 rolls of 8 specs, the five pool
gens among them - the shipped maps' rolls, which the gate reads rather than repeats (feature 215).

**The gate**: 143 s whole (`make done`: lint, types, hooks-test skipped as fresh, test-full, the floors, the census);
pytest 123 s, 3,471 passed, 2 skipped; the engine floor 23,260 statements at 100%, the hamlet-path floor 13,011 at 100%.
Feature 215's landing measured 165 s with 9 rolls; the difference is the six rolls that are gone, less the seatings'
partial roll that is new.

**Four gate runs to green, and what each caught** - three of them by the census, which is the mechanism working:

1. Two test failures and nine uncovered lines: `roll_audit` had no `OPERATIONS` row; the fan-out still named the
   retired `rolls.KINK`; and nine engine lines only the retired rolls had reached (`ways/serve.py` 498, `ways/web.py`
   181 and 446-454, `hamletgen/driver.py` 436-437, `tools/roll_audit.py` 89). Each is a direct unit test now; the
   collapsed-lane cleanup was lifted out of `stage_web` (`_drop_collapsed`) to be one. **The audit tool's own test
   found its root one level short** (`parents[5]` lands on `.claude/`; six is the repository) - the silent-depth
   failure the skill's CLAUDE.md warns about, caught before the target had ever been run.
2. `Cohort-43 seed=43 ... NOT IN THE ROSTER; requested by test_make_soak_refuses_rather_than_reporting_a_vacuous_green`:
   the soak tooling test ran the real `make soak` and returned early once the tree had content - so the first time
   `tests/soak/` held a test, the gate rolled it. The target reads `SOAK_DIR` now and the test proves the refusal on
   an empty fixture in under a second; a second test pins that the recipe honors the override.
3. Two findings at once. `Seatings seed=5 was rolled 2 times` by two tests of one module: `keyed_to(child=)` passed
   no `share=True`, so the FULL run's bypass stored the child's record and served nobody - two xdist workers reaching
   the module fixture each rolled (the run before had happened to schedule all three tests on one worker). And
   `test_a_rolled_cohort_passes_the_whole_gate ... excepted as a stub-stage module, but its roll of Polder seed=12
   took 62s` beside `roster row Polder seed=12 was not rolled`: the verdict bucketed every record from a stub-excepted
   module as a stand-in stage, so a CHILD roll the fan-out merely requested first (under worksteal the requester
   varies run to run) was a 62 s "stub" and the Polder row went unrolled. A stub is an in-process record now
   (`pid == worker`); a child roll is judged by the roster whoever asks. Both have unit tests.
4. Green, above.

**`make roll-audit` on the landed baseline** (the first run of the target found its recipe dead: `$(RUN)` carries its
own `@`, and a `: "..." ; \` continuation ahead of it put `@python3` mid-command - one recipe line now):

```
roll audit: 13 rolling context(s) (>= 2000 engine lines each); per context, the engine lines NO other context reaches
   5204 unique of   5570  
        overlap/taxonomy.py:282, tools/pack_audit/checks.py:138, citybudget.py:100, settlement/__init__.py:98, tools/pack_audit/parse.py:96, interactive/page.py:95
     21 unique of   6771  fixture:tests/gate/test_no_feature_overlaps.py::polder
        settlement/fields/comb.py:11, hamletgen/water.py:9, hamletgen/ways/clearance.py:1
     17 unique of   7474  tests/full/test_villages.py::test_a_map_is_immune_to_an_upstream_change_in_the_number_of_random_draw
        pipeline/rollcache.py:17
     15 unique of   4077  tests/full/settlement/test_rolling.py::test_pinned_knob_is_byte_identical_across_regens_and_rejects_
        settlement/rolling/roll.py:15
     11 unique of   7476  tests/full/test_villages.py::test_village_passes_gate[mizuguchi.gen.py]|run
        settlement/water_ways/lanes.py:9, hamletgen/ways/serve.py:1, hamletgen/ways/sweeps.py:1
     11 unique of   7457  tests/full/test_villages.py::test_village_passes_gate[sawada.gen.py]|run
        hamletgen/ways/route.py:3, hamletgen/sink.py:2, hamletgen/ways/touch.py:2, settlement/shrines_wells/byres.py:2, settlement/water_ways/lanes.py:2
     10 unique of   6401  tests/gate/hamletgen/test_driver.py::test_a_rolled_cohort_passes_the_whole_gate|run
        pipeline/rollcache.py:7, hamletgen/water.py:3
      5 unique of   7501  tests/full/test_villages.py::test_village_passes_gate[kashikawa.gen.py]|run
        hamletgen/ways/web.py:2, settlement/structures/fixtures/siting.py:2, hamletgen/ways/serve.py:1
      2 unique of   3953  tests/gate/settlement/test_rolling.py::test_roll_village_stream_fed_with_a_pinned_water_source|run
        settlement/rolling/roll.py:2
      1 unique of   3854  fixture:tests/gate/hamletgen/test_homesteads.py::seatings
        hamletgen/homesteads/seats.py:1
      1 unique of   4073  tests/full/settlement/test_rolling.py::test_roll_village_is_deterministic_and_seed_varies_the_combin
        settlement/_geom/water_index.py:1
      0 unique of   7523  tests/full/hamletgen/test_driver.py::test_the_cli_reports_a_single_hamlet|run
      0 unique of   3985  tests/gate/settlement/test_rolling.py::test_roll_village_honors_a_pinned_knob|run
```

Read against the roster: the empty context (the module-level lines every import executes) is the first row; the three
rostered rolls are the polder fixture (21 unique lines: the comb fields, `hamletgen/water.py`), the immune test's
perturbed reference (17, all in `rollcache.py` - the `extra_draws` machinery itself), and the seatings (1 line of
`homesteads/seats.py`). The pool sweep's five gen children carry 5-11 unique lines each - Sawada 11, Mizuguchi 11,
Kashikawa 5 - and the fan-out's Polder request 10 more (`rollcache.py` 7, `water.py` 3): the shipped maps are the
coverage, exactly as 215 found. The two zero rows are served requests, not rolls. Nothing here is a candidate for
another cut without moving a shipped map's lines; the next packing question is a tier question.
