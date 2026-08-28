# Research: which automated checks still earn their keep (feature 141)

## R1 - the census (`make check-census`, 2026-08-28)

636 check names in the registry. 231 get a measured verdict from per-stage snapshots of the reference
hamlet and the seed-19 polder; 405 have no scripted executor (town, city, capital and village checks: the
frozen legacy pool is their only subject). Of the 231: 105 keep because a LATER stage rewrites an input
they read; 6 keep because a consumer's behavior branches on them (the re-roll ladder reads
`farmhouses_reach_a_way`; `lanes_form_one_network`, `lanes_reach_something`, `field_ringed`,
`long_ditches_have_a_footbridge`, `paddy_bunds_clear_the_supply_channels` are read by the generator);
25 are vacuous on hamlets (every input absent); 80 pass the mechanical test - their inputs settle at the
stage that placed them - and go to the hand pass. 34 read only derived values and were judged by hand
with them. The ledger (`ledger.md` / `ledger.json`) carries every row.

## R2 - the hand pass over the 80 (the question is the PLACER's behavior)

| class | count | rule |
|---|---|---|
| RETIRE - a hard guarantee (the placer drops or refuses rather than place wrongly) AND an existing placer unit test names the invariant | 15 (14 retired; `structures_clear_of_dry_plots` held - its segment also carries the kept `groves_clear_of_dry_plots`) | FR-002 (a)(b)(c) |
| KEEP - best-effort placer; the check IS the guarantee | 17 | the caption seat (`_best_label_spot`: "the nearest seat wins"), the notice board (`stage_notice` keeps the engine's seat rather than none), the bridges (`bridges.py`: "expect the alignment check to test it"), the belt's clump count, the lonely well, the code-coverage guard `all_ink_is_ruled_on` |
| KEEP - a guarantee by construction is plausible but NO placer test names it (the GM may cut) | 21 + 17 | sizes from the house, quads, windward groves, attached sheds and fixtures, the bamboo tautology, well counts, `no_structure_overlaps` (the GM's example: `_fits` refuses overlap, but the test that names it is a yard/garden test, not a house-vs-house one), `houses_off_corridors`, `wells_clear_of_paddies`, the scatter keep-outs (woodland, groves, commons), z-order at finish, the frame, the sun rules across neighbors, polder parcels |
| LEGACY-FEATURE - vacuous on hamlets though one input exists | 12 | manors, gates, religious, stable troughs, hitching rails, roads, waterworks captions, field ponds |

The 14 retired, each with the placer test that carries it (`ledger.json` `placer_test`): `gardens_present`,
`harvest_yards_present` (a farmhouse with no room for both is DROPPED - `test_farmsteads_drops_a_farmhouse_with_no_*_room`),
`gardens_on_sunny_side`, `harvest_yards_on_sunny_side`, `gardens_clear_of_sheds`, `gardens_clear_of_structures`,
`gardens_clear_of_groves`, `harvest_yards_clear_of_structures`, `harvest_yards_clear_of_paddies`,
`gardens_clear_of_paddies`, `groves_clear_of_paddies`, `groves_clear_of_structures` (the bundle fit's
`*_fits_rejects_*` tests), `dry_plot_seams_shared` (the carve's seam tests), `houses_clear_of_paddies` (since
feature 140 the gate read the placer's own chains - pure same measure; `test_keepouts.py` + the
`_wall_on_the_bund` tests).

## R3 - what was removed, and the numbers

| | before | after |
|---|---|---|
| checks the reference hamlet runs | 232 | **218** |
| check names in the registry | 636 | 622 (14 segments removed; `_seg_0596`'s placement entry retired) |
| check-village unit tests | | -23 |
| fixtures in `pool/regressions/` | 843 | **822** (19 deleted: every fixture whose only fires were retired checks) |
| the unlocked gate | 1 m 45 s cold (140's figure) | 1 m 41 s cold, 3,860 tests - the checks retired were cheap; the win is maintenance and honesty, not seconds (the corpus replay was already served from the cache) |
| scripted negative fixtures | 0 | 4 exemplars (`tests/gate/test_scripted_fixtures.py`), the mechanism for the rest |

## R4 - the trade-offs that remain (for the acceptance conversation)

1. **The 38 "plausible but untested" keeps.** Each is almost certainly a same-measure check; retiring one
   needs a placer test that names its invariant (a few lines each: yard smaller than house, grove on the
   windward face, sheds attached). The GM may cut them wholesale and accept "by construction" without a
   test, or have the tests written - about a day of small tests for all 38.
2. **The 405 legacy-tier checks and 692 legacy fixtures (+53 unscaled).** No scripted map exercises them;
   the fixtures are their only executor and the only thing holding their coverage floor. Options: delete
   now (recover from history when a tier converts; the coverage floor on those segments then needs a
   decision), keep them but only in the full run, or keep as is. My recommendation: delete the fixtures
   and move the checks' segments out of the registry into a `legacy/` package that no gate runs, so the
   floor is not owed on dead code and the rules are not lost.
3. **The 17 best-effort keeps** are the checks that catch second-order effects (the board drift of
   feature 140 was one). They stay unless the placers become guarantees.
4. **Nothing now watches** the 14 retired invariants on a FINISHED map: if a later stage ever starts
   moving a yard or a garden, the placer test will not see it. The census re-run (`make check-census`)
   is the guard: a key that changes after its placer shows up in the ledger.
5. **A held-back segment** (`_seg_0319`) bundles a retired check with a kept one; splitting it is a hand
   edit of the segment body - cheap, but not done blind.
