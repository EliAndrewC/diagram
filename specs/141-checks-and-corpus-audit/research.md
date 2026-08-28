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

## R5 - the GM's cut (2026-08-28): *"I think we should cut all of the things you described in (1) and (2)"*

Applied in one pass (`cut-plan.json`, `cut-done.json`): the 39 checks of (1) - the "plausible but untested"
keeps and the held-back one - and the 442 of (2) - every check no scripted map exercises, plus the 25 vacuous
on hamlets and the 12 legacy-feature ones. A segment went when every check it carried was cut; a segment that
also WRITES a value a kept check needs stayed as a writer (36 such - their checks still evaluate, vacuously
on a hamlet; the list is in `cut-done.json`); the 7 segments that bundle a kept hamlet check with cut ones
(the headman, the kosatsuba family, the windbreak family, `households_consistent`, `cluster_abuts_fields`,
`wells_among_dwellings`, the byre form) stayed whole - the GM's (5) resolved: `_seg_0319` went entirely
because `groves_clear_of_dry_plots` was in (1). Every derivation only those segments needed went with them
(479). The legacy tiers' fixtures went in full (village, town, city, capital); the hamlet-tier and unscaled
fixtures were trimmed of cut names and deleted when nothing was left to fire.

| | opened | after T03 | after the GM's cut |
|---|---|---|---|
| segment functions | 1,405 | 1,391 | **595** (20,837 lines of `check_village`) |
| check names | 636 | 622 | **237** |
| checks the reference hamlet runs | 232 | 218 | **149** |
| fixtures in `pool/regressions/` | 843 | 822 | **190** |
| tests the unlocked gate runs | 3,898 | 3,860 | **2,455** |
| unlocked `make done`, cold | 1 m 45 s | 1 m 41 s | **48 s** (test phase 16 s) |

What the sweep touched beyond the segments: 736 + 4 check tests and three legacy-structure tests removed
(the `tier_town` / `tier_city` check trees are nearly empty now); the ratchet table in the check-village
builders lost 7 rows; the cohort pin lost seed 22 (`field_ringed`, cut) and the gate pin seed 44
(`houses_clear_of_paddies`, retired in T03); the tripwire pin is unchanged; two placement entries in the
registry retired; the frozen registry rows and check-name fixture rewritten. Live code that still names a
cut check as a string: the overlap policy's fire-tower rows in `common_02` (kept as writers), and the frozen
legacy pool gens' waivers (never run).

The census after the cut (`ledger-after.md`, 237 names): 126 keep on the measured test (a later stage changes
an input, or the generator reads it); 27 are mechanical candidates that the hand pass keeps as best-effort
placers' guarantees (captions, the board, the bridges, the belt's count, the lonely well, the ink guard) or
that ride in a kept segment; and 84 cut-class checks are STILL EVALUATED because they ride in the 36
writer segments and 7 mixed segments (they pass vacuously on a hamlet - a manor no hamlet has). Splitting
those is the hand edit (5) named before, now 84 check calls across 43 segments; the ledger names each.

**The (5) edit, done (2026-08-28, the same day):** every `check("<cut name>", ...)` call inside a kept segment was
removed and a stub left in its place - 85 calls across 25 files; the 9 that remain are the ones whose name is built
at run time (`f"{scale}_has_kosatsuba"`, the headman family) and the two stream anchors a writer segment carries.
The reference hamlet now runs **136 checks** (232 at the feature's opening); the registry names 153, of which 126
keep on the measured test, 17 are best-effort placers' guarantees, 10 are the run-time-named residue. The
frozen check-name roster is regenerated from the live registry; the corpus stands at what those checks can fire.
