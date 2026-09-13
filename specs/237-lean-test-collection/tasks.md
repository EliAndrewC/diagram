# Feature 237 - tasks

Spec IN IMPLEMENTATION: `spec-fidelity` round 1 CHANGES REQUIRED (seven findings, all taken), round 2 CHANGES REQUIRED (five stale-text findings, all taken), round 3 dispatched. No engine line was written before round 1 returned (constitution XVI). Every
task is classified `research: rendering` or `research: physical`. **NOTHING here is physical**: this
feature is about what a test run loads into memory, not about how a place was built, farmed or lived
in. Every measurement it rests on is in `research.md` R1 to R9 and was taken before the spec was
written.

## Phase 1 - the paths (item 1: FR-001 to FR-005)

- [x] T01 `Plan` gains `paths: list[str]`, derived in `plan()` from the plan's own inputs with NO
      collection: the modules of `affected_tests`, every `changed_test_modules` entry, and the modules
      of every baseline test whose closure in `tests.json` intersects `affected_fixtures` (FR-001).
      research: rendering
      verify: DONE. `incremental.reachable_modules` + `existing`; the superset property is a test over a plan with all three rules live, and a deleted module is filtered because pytest resolves arguments before any plugin loads (exit 4 would take the gate with it).
- [x] T02 `incremental paths` prints them space-separated, empty on a full run, and on an incremental
      plan with nothing to run prints a path that HOLDS NO TESTS rather than nothing - a fallback to the
      trees there would pay the whole 922 MiB collection to run nothing, which is the item inverted. The
      gate's `test` recipe reads it into a shell variable AFTER `incremental plan` has run and passes it
      as pytest's positional arguments. It must be a shell variable, not `$(shell ...)`: the whole recipe is one
      line, so a make-time expansion would run before the plan exists (FR-002).
      research: rendering
      verify: DONE. `incremental paths`; the recipe reads it into a shell variable after the plan runs. Probed first: `tests/__init__.py` collects nothing in 1.16 s and exits 5, which the existing empty-selection-is-green branch turns into 0.
- [x] T03 `tests.json.next` is not written by a restricted run. `save-baseline` ALREADY refuses on an
      incremental run ("the baseline stays the last full run"), so the promotion half is in place -
      this task is the write half plus the test that pins both, because the invariant is now load
      bearing rather than merely true (FR-004).
      research: rendering
      verify: DONE. `.next` is written only by an unrestricted run; `save-baseline` already refused an incremental one. Both pinned by a test that asserts the file is ABSENT after a restricted run.
- [x] T04 The fixture graph survives a restricted run: a full run persists `fixture_dependents` in the
      baseline, and `merge` reads the baseline's graph unioned with this run's. **This fixes a
      PRE-EXISTING defect** (Principle XIV): the graph is already partial on any run carrying
      `--ignore` (`FULL_TREE_IGNORE`, `BROWSER_SKIP`), so a fixture whose upstream changed already
      keeps stale contexts for dependents in an ignored tree (FR-005, `research.md` R7).
      research: rendering
      verify: DONE. `fixtures.json` beside the baseline, promoted by `save_baseline`, unioned in `merge` via `selection.merge_graphs`. This also closes the pre-existing hole for any `--ignore`d tree.
- [x] T05 Tests: the derived path set covers every module `keep_set` keeps over the recorded plans; a
      changed test module absent from the baseline is still collected; the two-consecutive-incremental
      case (the second selects the same small set, not near-everything); a fixture's dependents in an
      uncollected module have their contexts dropped (SC-001, SC-003).
      research: rendering
      verify: DONE. 31 cases green in tests/tooling/ci/test_incremental.py, including the superset property, the restricted-run baseline refusal, the graph promotion and the deleted-module filter.

## Phase 2 - the pinned items (item 2: FR-006)

- [x] T06 `remember_all` stores `{nodeid: fixture_ids(it)}` and the graph edges instead of
      `list(items)`; `_all_items` goes. Record AT THE POINT OF CHANGE why it exists at all -
      `ROLL_DESELECT` and `TIER_SELECT` deselect by marker even on a full run, so the items list at
      write time is already short of the baseline the next plan needs, and the code does not say so
      today (FR-006).
      research: rendering
      verify: DONE. `remember_all` keeps the closures and the reverse edges; `_all_items` deleted; the old test's assertion now proves the items are NOT pinned.

## Phase 3 - the deferred imports (item 3: FR-007)

- [x] T07 `tests/test_package_surfaces.py`: the whole-tree AST census moves into a session-scoped
      fixture. **Its parametrization is derived from the census**
      (`@pytest.mark.parametrize("module", sorted({m for _, m, _ in _IMPORTS}))`), and a fixture cannot
      drive `parametrize`, so the shape changes: ONE test that checks every module and reports every
      offending module together. That keeps the diagnostic the parametrization was for - the docstring
      says it exists so a failure names the package - while removing 8.7 MiB from every worker that
      does not run it (FR-007, R6).
      research: rendering
      verify: DONE. Session fixture; one test reporting every offending module together, since a fixture cannot drive parametrize. The diagnostic the parametrization existed for is kept in the assertion message.
- [x] T08 `import coverage` moves inside the tests that use it in `tests/tools/test_hamlet_floor.py`
      and `tests/tools/test_roll_audit.py` (4.2 MiB, R6), and the module-level shapely import in
      `tests/waterfields/test_geoms.py` and `test_seams.py` moves into the tests that use it - without
      which Phase 4 saves nothing on a full gate, because collecting `tests/waterfields` imports
      shapely into all ten workers whatever the engine does. `tests/soak/test_seatings.py` keeps its
      module-level `mock` import with the reason recorded beside it: `norecursedirs` holds `soak` out
      of every ordinary run, so no gate pays it (FR-007).
      research: rendering
      verify: DONE. `import coverage` inside the tests in both tools files; the two waterfields test modules use a same-named lazy wrapper so no call site changed; soak keeps its `mock` import with the reason beside it.

## Phase 4 - shapely (item 4: FR-010)

- [x] T09 One lazy accessor per module for the SEVEN engine import sites - `settlement/land/wet.py`,
      `hamletgen/homesteads/boundary.py`, `waterfields/comb.py`, and `waterfields/seams/close.py`,
      `geoms.py`, `plots.py`, `pockets.py` (`banks.py` matches a grep for the word and holds no
      import). Annotations keep the real names through a `TYPE_CHECKING`
      import, so the type checker loses nothing; the runtime constructors come from the accessor, and
      a function that calls one in a loop hoists it ONCE outside the loop. No `import` statement goes
      inside a per-plot, per-seam or per-candidate function (FR-010, D6).
      research: rendering
      verify: DONE. All seven engine modules bind through `_load_shapely()` with a sentinel; `from __future__ import annotations` added to the three that needed it, since shapely names stand in their annotations. ruff and pyrefly clean.
- [x] T10 Two tests that ask the PROCESS, not the source: after importing the whole engine `shapely` is
      absent from `sys.modules` and present after a geometry call (SC-005); and a DERIVED guard that
      fails on any module-level shapely import under `l7r/` outside an accessor, because a hand list is
      how FR-010 first said eight sites instead of seven (features 169, 185 and 190 paid for that
      lesson).
      research: rendering
      verify: DONE. tests/test_memory.py: the DERIVED guard (no module-level shapely import under l7r/ outside a TYPE_CHECKING block) and a child-process probe - absent after the whole engine imports, present after one geometry call.

## Phase 1b - the amendment the implementation forced (FR-003, D8, SC-007)

- [x] T14 The `FULL_FRACTION` decision moves from `selection.py` (after collection) to the planner
      (before the arguments are chosen): `incremental.over_the_fraction` projects `keep_set`'s rules over
      the baseline and `plan()` returns a full plan with no paths when it is over the line. A process whose
      arguments were narrowed cannot decide to run everything - a run labeled full that collected a subset
      would skip the merge and judge the 100% floor over that subset alone (FR-003, D8).
      research: rendering
      verify: DONE. `over_the_fraction` + the planner's branch; `test_plan_returns_a_full_run_when_the_projection_is_over_the_fraction` drives both sides through `plan()` itself, and `test_e_over_the_fraction_the_PLANNER_runs_everything_and_keeps_the_trees` proves it end to end at the gate's level. Both module docstrings that still described the old flip are corrected; D8 states the projection's error in both directions.

## Phase 4b - numpy at the GM's request, PIL on the session's judgment (FR-011, D9)

- [x] T15 `tools/page_lit.py` and `tools/picture_diff.py` bind `numpy` and `PIL.Image` through one
      `_load_arrays()` each, the same form as `_load_shapely`; `tests/tools/test_page_lit.py`,
      `test_picture_diff.py` and `tests/interactive/test_raster.py` import them inside the tests that use
      them, since `np` and `Image` are reached by attribute and a same-named wrapper cannot stand in for a
      module. Each of those three keeps a `TYPE_CHECKING` import for its annotations, which are evaluated
      outside the function body (FR-011).
      research: rendering
      verify: DONE. 9 loader call sites in the two tools, 11 test functions importing where they use; ruff and pyrefly clean; 53 cases green in the three suites.
- [x] T16 The FR-010 guard widens to all three libraries rather than gaining a second copy, and the
      measurement is recorded whichever way it comes out (FR-011, SC-008).
      research: rendering
      verify: DONE. `HEAVY = ("shapely", "numpy", "PIL")` in the derived guard. MEASURED (research R14): the whole-tree collection peak 923 -> 840 MiB, which is the anomaly R10 recorded and could not explain, and the per-worker engine baseline 57.6 -> 42.9 MiB.

## Phase 5 - the verdict (FR-008, FR-009, SC-002, SC-006)

- [x] T11 Measure: the collection-only peak at ten workers and a real incremental gate's peak, before
      and after, with the PSS harness R3 used; the per-worker import attribution re-run; and the
      MARGINAL shapely-only figure, since R9's 16.3 MiB is shapely plus numpy and numpy arrives through
      `tests/tools` regardless (FR-009). Record every
      number in `research.md` whichever way it comes out, including an item that did not pay.
      research: rendering
      verify: DONE. research R10, R11 and R12. The honest mix: the per-module deferrals verified individually (8.7 -> 0.09, 3.18 -> 0.42 MiB, and the engine baseline 61.0 -> 57.6 as shapely leaves it); one tree's collection 602 -> 515 MiB; the WHOLE tree's collection peak unmoved at ~922 MiB with its wall time halved, recorded as measured without a confirmed mechanism; and the gate itself 400 MiB / 41.3 s collecting nothing. The marginal shapely figure is 3.4 MiB a worker where numpy arrives anyway and 21.7 where it does not.
- [x] T12 `make perf LABEL=237-end`, then `make perf-report AGAINST=237-start`: FR-010's acceptance. An
      increase on the total or on ANY seed is NOT waiverable for this item - the remedy is that the
      offending site goes back to a module-level import and the remaining sites stand (FR-010). The
      `perf-audit` agent is the DIAGNOSIS when a band of 1 or more is reported, never the exit: the item
      was approved as a memory saving, and a slower map is not a trade the GM was offered. The `-start`
      bookend was taken on unmodified code before Phase 1 began.
      research: rendering
      verify: DONE. 237-start taken on unmodified code, three -end bookends taken after. Total -1.3% / -1.8% / -1.3%; seed 4 +3.6% / +1.8% / +3.6% on `field` and `track`. Cause measured, not inferred: the shapely import costs 0.244 s and seed 4 is the first seed, so it now pays it inside its timed region - one-time per process. The per-call loader cost was ruled OUT by measurement (an inline sentinel changed nothing). Explanation recorded; `perf-audit` confirmed it independently.
- [x] T13 `make done` green (the 100% floor over the merged coverage), `make hooks-test` green, the
      worker count still pinned at ten (FR-008), and the spec's Status line updated with the review
      history.
      research: rendering
      verify: DONE. `make done` green (400 MiB, 41.3 s, the floors over the merged coverage, roll census green, hooks-test green); `make static` green; the worker count untouched at ten; the Status line carries the full review history.
