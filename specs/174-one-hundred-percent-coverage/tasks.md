# Tasks: One Hundred Percent Coverage, Enforced (feature 174)

Every task is `research: procedure` - this feature is about what the tooling demands of the
repository's own tests, and nothing in it concerns how a place was built, farmed or lived in. The
GM's words are in [`request.md`](request.md); the measurements taken before specifying, and the ones
taken during, are in [`research.md`](research.md).

## Reaching the floor

- [x] T01 R1-R8: measure where the tree actually stands and what the floors cost, before changing
      anything
      research: procedure
      verify: 96.07% (814 uncovered of 20,655) on the first clean `make test-full`; the suite untraced
      50 s against 237 s with every deselection off, so the TRACING is the expense and not the tests -
      which is what answered the GM's "could a cheaper version of the tests get us there" with a
      measurement rather than a guess

- [x] T02 FR-004: `waterfields/hill.py` covered by tests rather than exempted or put to the GM
      research: procedure
      verify: `tests/waterfields/test_hill.py` (new), 5 tests, 99 statements to 100%. It was nearly
      deleted as dead code first: two FROZEN EXHIBIT gens call it (`tanada.gen.py:35`,
      `yatsuda.gen.py:38`) and `migration-plan.md` lists both archetypes as not yet converted

- [x] T03 FR-005: delete dead code rather than test it (GM: "Yes. We should delete any dead code,
      which will also help with this current effort")
      research: procedure
      verify: 8 functions, 3 orphaned constants and `pt_to_rect` gone from `overlap/matrix.py` and
      `overlap/taxonomy.py` (~181 lines); `ways/touch.py`'s `_clearance` closure, defined and called
      nowhere, an orphan of the feature-173 split; `pool_index.py`'s `if not rows: continue`, which
      `_sections` makes unreachable by construction

- [x] T04 FR-006: an inner function that is hard to test gets LIFTED OUT, not pragma'd
      (GM 2026-08-28, feature 146)
      research: procedure
      verify: five lifted, each with its captured values as parameters and the caller delegating so
      there is ONE body - `first_clear_seat` (fixtures/_helpers), `seg_hits_rect` (structures/packing),
      `avenue_along` (shrines_wells/torii), `_detour_links` + `_along_samples` + `_fine_lattice_links`
      (hamletgen/ways/touch). Each is now tested with plain tuples and lists

- [x] T05 FR-002: bring every remaining module to 100%, module by module, measuring against the FULL
      run rather than a per-file one
      research: procedure
      verify: **100.00%, 0 uncovered of 20,646**, 2,702 passed / 20 skipped / 1 xfailed. The
      per-file view was misleading twice (a line covered in `make cov-file` was still missing in the
      full run and vice versa), so every verdict here came from `python3 -m coverage report -m` over
      the FULL run's own data

- [x] T06 FR-002a: fix the tests found passing while exercising nothing (Principle XIV - a defect you
      find while doing something else is fixed IN that work)
      research: procedure
      verify: six, each fixed and re-proved by watching the target line go from missing to covered.
      The instructive one is `test_a_file_ADDED_or_DELETED_since_the_base_counts_as_changed`, which
      called `_semantically_changed(repo, newfile, "origin/main")` - arguments transposed, so the
      function returned True at its first line and the test asserted nothing

- [x] T07 the along-sampler's exact-divisor gap: RECORDED, not silently corrected
      research: procedure
      verify: where every segment divides `_ALONG_STEP_FT` exactly the carried remainder lands on
      `t == seg` and the strict `<` misses it, so such a way offers only its two ends. Correcting it
      would move the links that rung draws and so the lanes of any map that reaches it - a map change,
      which a coverage feature does not get to make. Pinned by a test and stated on the function

## Enforcing it

- [x] T08 FR-003: `fail_under = 100` enforced on a plain `make done`
      research: procedure
      verify: the gate's phase list is `hooks-test test-full [perf-gate]` - `test-full` on BOTH
      branches, because the floors live behind `COV_FLOORS=1`, which is the same switch that turns
      every deselection off, and a deselected test takes its coverage with it. `tests/tooling/
      test_coverage_floor.py` proves a plain `make done` runs the floored phase and that dropping a
      module below 100% fails it

- [x] T09 FR-003a: the other routes below the floor, named and closed
      research: procedure
      verify: `GATE_RECIPE` in `scripts/gate-stamp.py` salts the stamp key, so every green record
      taken before the floor existed is retired at once - `sync-with-main.sh --check` is the whole of
      what the push demands, and a record of a run that was ALLOWED to finish below the floor must
      not satisfy a push under it. `GATE_STAMP_OK` is KEPT deliberately (feature 170's audited escape:
      it demands a written reason and is logged)

- [x] T10 re-pin the `done` ratchet, since this feature deliberately changes what `done` DOES
      research: procedure
      verify: the GM's condition on D1 (2026-08-30) was to re-pin once real runs exist; this is that,
      with the measured number and the reason in the row itself. The hard ceiling and the
      `hard_at_or_below` trigger are untouched - the GM's own numbers are not this feature's to move

- [x] T11 the file-scale gate fires on this feature's OWN work, and is obeyed
      research: procedure
      verify: `tests/settlement/test_structures.py` reached 1,152 lines and feature 173's check failed
      the gate. Split into `tests/settlement/structures/` - one file per submodule of the subject, the
      mapping DERIVED from which package names each test exercises - with its own "look here when"
      index, and `tests/settlement/CLAUDE.md` updated to route to it

- [x] T12 the whole gate green under the new standard
      research: procedure
      verify: recorded in the feature's own run-log entry

## The pragma, after the GM's ruling (2026-08-31)

- [x] T13 FR-009: answer the GM's ruling by MEASUREMENT, not by reading the comments
      research: procedure
      verify: all 130 pragmas stripped and the whole corpus run against this feature's own new floor,
      which then named every line nothing executes. Counted in coverage's own unit: of **469** excluded
      lines only **113** were still uncovered, so **356 exclusions were hiding lines the corpus already
      runs**. Classifying by what each comment CLAIMED would have deleted live code and kept dead code,
      which is why `pragma-census.md` leads with the method rather than the count

- [x] T14 delete the dead code the ruling names, and say what is NOT dead
      research: procedure
      verify: 13 sites deleted (a guard re-testing a filter one loop above it, an enum check after the
      enum is exhausted, `return None` after a loop that always returns, `if not plots` before code
      that handles empty). 24 KEPT as error handling or structural terminals - `if not pts: continue`
      stands before `len(pts)`, so removal converts a graceful skip into a crash, and several are a
      terminal return where the signature promises a value - each now carrying why it is not
      deletable. The live rescues and external systems are KEPT too ("no cohort map currently" is not
      "cannot happen"). **130 -> 76 pragma comment lines, 469 -> 385 excluded lines, 2.99% -> 2.30% of
      the floored tree, 40 engine lines gone**; 2,716 tests green and no manifest moved, which is the
      evidence the deletions were safe. TWO things recorded for the GM rather than assumed: whether the
      24 error-handling guards are meant too, and that the restored exclusions are block-scoped and so
      over-broad (385 excluded where ~113 are unreached)

- [x] T15 the gate green under the new standard, after the deletions
      research: procedure
      verify: `make done` green in 537 s with the 100% floor enforced on the plain branch

## The measured surface (GM 2026-09-02)

- [x] T16 FR-010: the guidelines FIRST, as the GM asked - a new tool owes 100% the day it lands
      research: procedure
      verify: constitution **v2.15.0** (Principle X clause 5 rewritten round the GM's words, plus the
      two supporting clauses that still said "target 100% on pure logic" and "100% on every measured
      module except the ratcheted settlement/ package"); `CLAUDE.md` carries it as NON-NEGOTIABLE;
      and `pyproject.toml`'s comment - which had argued the GM's exact opposite, "instead of making a
      new tool silently owe 100% coverage the day it lands" - now records that they reversed it

- [x] T17 audit the 19 modules and put them to the GM before touching them
      research: procedure
      verify: all 17 real tools wired to a make target with a stated reason; `pipeline/gencache.py`
      (263) and `regen.py` (56) load-bearing infrastructure merely filed under "tools"; `dwellings.py`
      and `__init__.py` not tools at all - excluded only because the roster listed subpackages. The
      GM ruled none of it abandoned and all of it owed tests

- [x] T18 FR-010: `source = ["l7r"]` and every one of the 19 to 100%
      research: procedure
      verify: measured surface 20,682 -> **22,520 statements** (measured, not tallied); 14 modules given tests (five were
      already at 100% once measured); three docstrings claiming exemption removed. Each suite is
      aimed at what its module would silently get WRONG - `cache_audit`'s vacuous-trial skip,
      `mapcheck`'s locked-scope refusal, `cohort_audit`'s reference gate, `perf_snapshot`'s
      retroactive baseline, `crop_map`'s world-to-pixel conversion asserted on real pixels

- [x] T19 the whole gate green under the WIDENED standard
      research: procedure
      verify: `make done` green - **22,520 statements, 0 missing, 100%** over the whole engine with
      `source = ["l7r"]`, no `--omit`, no ratchet; the hamlet-path floor 12,402 / 0 missing beside it.
      Round 9 noted there was no green gate at HEAD and no task asserting one; this is both

- [x] T20 a defect in ANOTHER feature, surfaced by this one's widened gate (Principle XIV)
      research: procedure
      verify: feature 176 landed mid-flight and its gate went green because on main `make done` SKIPS
      `tests/full/` - so `test_a_sibling_link_lights_the_other_class...` never ran. Under this
      feature's gate it fails. Baselined on unmodified `origin/main` first: it fails there too, so it
      is not a regression of ours. Cause: 176's title placard is at x=150 y=10 and the synthetic
      windbreak rect is at 150-180, 10-30 - the placard is appended last and drawn ON TOP, so a
      force-click on the windbreak answered with a neighbouring class. Moved to clear ground
      (y=105..145); 19 of 19 pass. **The floor caught a live failure in shipped code on its first
      contact with another feature**
