# Feature 237 - tasks

Spec IN IMPLEMENTATION: `spec-fidelity` round 1 CHANGES REQUIRED (seven findings, all taken), round 2 CHANGES REQUIRED (five stale-text findings, all taken), round 3 dispatched. No engine line was written before round 1 returned (constitution XVI). Every
task is classified `research: rendering` or `research: physical`. **NOTHING here is physical**: this
feature is about what a test run loads into memory, not about how a place was built, farmed or lived
in. Every measurement it rests on is in `research.md` R1 to R9 and was taken before the spec was
written.

## Phase 1 - the paths (item 1: FR-001 to FR-005)

- [ ] T01 `Plan` gains `paths: list[str]`, derived in `plan()` from the plan's own inputs with NO
      collection: the modules of `affected_tests`, every `changed_test_modules` entry, and the modules
      of every baseline test whose closure in `tests.json` intersects `affected_fixtures` (FR-001).
      research: rendering
- [ ] T02 `incremental paths` prints them space-separated, empty on a full run, and on an incremental
      plan with nothing to run prints a path that HOLDS NO TESTS rather than nothing - a fallback to the
      trees there would pay the whole 922 MiB collection to run nothing, which is the item inverted. The
      gate's `test` recipe reads it into a shell variable AFTER `incremental plan` has run and passes it
      as pytest's positional arguments. It must be a shell variable, not `$(shell ...)`: the whole recipe is one
      line, so a make-time expansion would run before the plan exists (FR-002).
      research: rendering
- [ ] T03 `tests.json.next` is not written by a restricted run. `save-baseline` ALREADY refuses on an
      incremental run ("the baseline stays the last full run"), so the promotion half is in place -
      this task is the write half plus the test that pins both, because the invariant is now load
      bearing rather than merely true (FR-004).
      research: rendering
- [ ] T04 The fixture graph survives a restricted run: a full run persists `fixture_dependents` in the
      baseline, and `merge` reads the baseline's graph unioned with this run's. **This fixes a
      PRE-EXISTING defect** (Principle XIV): the graph is already partial on any run carrying
      `--ignore` (`FULL_TREE_IGNORE`, `BROWSER_SKIP`), so a fixture whose upstream changed already
      keeps stale contexts for dependents in an ignored tree (FR-005, `research.md` R7).
      research: rendering
- [ ] T05 Tests: the derived path set covers every module `keep_set` keeps over the recorded plans; a
      changed test module absent from the baseline is still collected; the two-consecutive-incremental
      case (the second selects the same small set, not near-everything); a fixture's dependents in an
      uncollected module have their contexts dropped (SC-001, SC-003).
      research: rendering

## Phase 2 - the pinned items (item 2: FR-006)

- [ ] T06 `remember_all` stores `{nodeid: fixture_ids(it)}` and the graph edges instead of
      `list(items)`; `_all_items` goes. Record AT THE POINT OF CHANGE why it exists at all -
      `ROLL_DESELECT` and `TIER_SELECT` deselect by marker even on a full run, so the items list at
      write time is already short of the baseline the next plan needs, and the code does not say so
      today (FR-006).
      research: rendering

## Phase 3 - the deferred imports (item 3: FR-007)

- [ ] T07 `tests/test_package_surfaces.py`: the whole-tree AST census moves into a session-scoped
      fixture. **Its parametrization is derived from the census**
      (`@pytest.mark.parametrize("module", sorted({m for _, m, _ in _IMPORTS}))`), and a fixture cannot
      drive `parametrize`, so the shape changes: ONE test that checks every module and reports every
      offending module together. That keeps the diagnostic the parametrization was for - the docstring
      says it exists so a failure names the package - while removing 8.7 MiB from every worker that
      does not run it (FR-007, R6).
      research: rendering
- [ ] T08 `import coverage` moves inside the tests that use it in `tests/tools/test_hamlet_floor.py`
      and `tests/tools/test_roll_audit.py` (4.2 MiB, R6), and the module-level shapely import in
      `tests/waterfields/test_geoms.py` and `test_seams.py` moves into the tests that use it - without
      which Phase 4 saves nothing on a full gate, because collecting `tests/waterfields` imports
      shapely into all ten workers whatever the engine does. `tests/soak/test_seatings.py` keeps its
      module-level `mock` import with the reason recorded beside it: `norecursedirs` holds `soak` out
      of every ordinary run, so no gate pays it (FR-007).
      research: rendering

## Phase 4 - shapely (item 4: FR-010)

- [ ] T09 One lazy accessor per module for the SEVEN engine import sites - `settlement/land/wet.py`,
      `hamletgen/homesteads/boundary.py`, `waterfields/comb.py`, and `waterfields/seams/close.py`,
      `geoms.py`, `plots.py`, `pockets.py` (`banks.py` matches a grep for the word and holds no
      import). Annotations keep the real names through a `TYPE_CHECKING`
      import, so the type checker loses nothing; the runtime constructors come from the accessor, and
      a function that calls one in a loop hoists it ONCE outside the loop. No `import` statement goes
      inside a per-plot, per-seam or per-candidate function (FR-010, D6).
      research: rendering
- [ ] T10 Two tests that ask the PROCESS, not the source: after importing the whole engine `shapely` is
      absent from `sys.modules` and present after a geometry call (SC-005); and a DERIVED guard that
      fails on any module-level shapely import under `l7r/` outside an accessor, because a hand list is
      how FR-010 first said eight sites instead of seven (features 169, 185 and 190 paid for that
      lesson).
      research: rendering

## Phase 5 - the verdict (FR-008, FR-009, SC-002, SC-006)

- [ ] T11 Measure: the collection-only peak at ten workers and a real incremental gate's peak, before
      and after, with the PSS harness R3 used; the per-worker import attribution re-run; and the
      MARGINAL shapely-only figure, since R9's 16.3 MiB is shapely plus numpy and numpy arrives through
      `tests/tools` regardless (FR-009). Record every
      number in `research.md` whichever way it comes out, including an item that did not pay.
      research: rendering
- [ ] T12 `make perf LABEL=237-end`, then `make perf-report AGAINST=237-start`: FR-010's acceptance. An
      increase on the total or on ANY seed is NOT waiverable for this item - the remedy is that the
      offending site goes back to a module-level import and the remaining sites stand (FR-010). The
      `perf-audit` agent is the DIAGNOSIS when a band of 1 or more is reported, never the exit: the item
      was approved as a memory saving, and a slower map is not a trade the GM was offered. The `-start`
      bookend was taken on unmodified code before Phase 1 began.
      research: rendering
- [ ] T13 `make done` green (the 100% floor over the merged coverage), `make hooks-test` green, the
      worker count still pinned at ten (FR-008), and the spec's Status line updated with the review
      history.
      research: rendering
