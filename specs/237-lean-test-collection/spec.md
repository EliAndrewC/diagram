# Feature 237 - collect only what the run can execute

**Status**: IMPLEMENTED. `spec-fidelity` FAITHFUL at round 3 of the initial acceptance (round 1 CHANGES REQUIRED on seven findings - the request record, FR-002's empty-list case, FR-010's count and its derived guard, FR-007 extended to the two test modules that import shapely, the marginal figure separated from the cumulative one, FR-008's criterion, and FR-010's bookend run with an increase made non-waiverable; round 2 CHANGES REQUIRED on five stale-text findings). AMENDED mid-implementation with D8, FR-003's second clause and SC-007, on a counter reset to zero by the GM's own ruling: round 1 CHANGES REQUIRED on five (D8's error direction, two docstrings, the criterion, the task), round 2 CHANGES REQUIRED on two more stale comments at the point of change. Verified: `make done` green at 400 MiB and 41.3 s (`research.md` R11), the pool byte-identical, and the perf bookends adjudicated by `perf-audit` (R12). AMENDED again 2026-09-13 with FR-011, SC-008 and D9 (numpy and PIL, the GM asking for numpy on this feature's own measurement), on a counter reset again: round 1 CHANGES REQUIRED on five - FR-009's contradiction, the four-item count in the Summary and D7, R10's stale closing claim, PIL disclosed as the session's own scope, and this line; round 2 CHANGES REQUIRED on four more - R9's paragraph, the DERIVED GUARD's own docstring crediting PIL to the GM, FR-011's title and the task heading, and D9's estimate replaced by a measurement (numpy 69 MiB of the 83, PIL 14); round 3 CHANGES REQUIRED on one - a paragraph inserted inside R14's table, orphaning two of its three rows.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - why xdist workers must all collect the same thing, what
collection costs here, the sharding experiment that failed, the data-as-Python hypothesis tested, and
where the test-module megabytes actually are.
**Predecessors**: 207 (the incremental gate, the plan and the selection plugin), 206 (the browser skip,
*"this is about saving memory, not saving time"*), 221 (the worker count measured at ten), 208 (the
raster's memory spikes), 216/219 (the gate rolls only what the floor needs).

## Summary

A gate's collection costs 922 MiB at ten workers and is paid in full whether or not a test runs - 53% of
the whole run's peak (R3). Every worker collects the entire tree because xdist dispatches work by
integer index into a collection all workers must share, which is documented design and was refused
upstream when someone tried to change it (R1). Arguments are the one lever xdist leaves: paths and node
ids restrict collection BEFORE import, while `-k`, `-m` and `--deselect` filter after it, and every
worker is handed the controller's argv verbatim so restricting it keeps the protocol satisfied.

So this feature does five things: it restricts a gate's arguments to the modules its plan can reach, stops pinning the collected items, defers the import-time work that all ten workers pay and one worker needs, imports `shapely` in the worker that uses it rather than in all ten, and - added by the GM mid-implementation once the measurement was in - does the same for `numpy` in the two tools that hold it, which turned out to be the larger half (FR-011, R14). Two things it deliberately does not do: change the worker count (the GM's ruling, and it is already tuned by
measurement), and shard the gate into concurrent runs - that was measured and came out 94 MiB WORSE,
because the duplication is per worker and ten workers are ten copies whichever way they are grouped
(R4).

What it is NOT is the fix the GM expected, and the difference is recorded because it reverses an
intuition: the test tree holds no large data written as Python. 2,513 KiB of source, of which 40 KiB is
module-level literals and 9 KiB is eight-or-more-element literals inside functions; the map data is
already rolled at run time or read from disk (R5). The mechanism the GM described - module-level work
paid by every worker, better deferred until a test needs it - is real and worth about 13 MiB per worker,
but its payload is one module parsing the whole tree's AST at import time and one heavyweight library
import, not data (R6).

## Functional requirements

- **FR-001 The plan names the modules it can reach, derived without collecting.** `Plan` gains a
  `paths` list: the modules of `affected_tests`, every entry of `changed_test_modules`, and the modules
  of every baseline test whose fixture closure intersects `affected_fixtures` - the closures being in
  `tests.json` already, so nothing is circular and no import is needed to compute it. The list is a
  SUPERSET of the modules `keep_set` will keep, by construction, and that property is tested rather
  than asserted in prose.
- **FR-002 An incremental gate is given those paths as positional arguments**, and an EMPTY list collects nothing rather than everything. `make test-full` passes the derived list where it passes the trees today; a full run passes the trees exactly as now. Nothing else about the invocation changes - same worker count, same `--dist`, same ignores. The empty case is the one that matters most and is the easiest to get backwards: `plan()` returns an INCREMENTAL plan with no affected tests, fixtures or modules when nothing the baseline exercised has changed, so a fallback to the trees there would pay the whole 922 MiB collection (R3) in order to run nothing. The arguments in that case name a path that holds no tests, so the selection plugin still records its result, the existing empty-selection-is-green branch still fires, and the merge and the floors still run.
- **FR-003 Deselection remains the authority on what runs, and the FULL-RUN decision moves to the
  planner.** The arguments restrict what is IMPORTED; `keep_set` still decides which collected tests
  execute, unchanged. Two layers on purpose: if they ever disagree the deselection wins, and because
  FR-001's set is a superset the disagreement can only be in the safe direction. What does NOT survive is
  the post-collection flip: `selection.py` used to turn a run FULL when the selection came out over
  `FULL_FRACTION`, and a process whose arguments were already narrowed cannot make that choice - a run
  labeled full that collected a subset would skip the merge and judge the 100% floor over that subset
  alone. So the planner makes it, before the arguments are chosen, by projecting the same four rules over
  the baseline (D8).
- **FR-004 The baseline is written only by a run that collected everything.** `selection.py` writes
  `tests.json.next` only when the run was not restricted; a restricted run leaves the previous
  `tests.json` in place, which `save_baseline` already does when the file is absent. Without this the
  next plan would see every unselected module's tests as new and run almost all of them (R7).
- **FR-005 The fixture graph survives a restricted run.** `fixture_dependents` is persisted in the
  baseline by a full run and `merge` reads the baseline's graph unioned with this run's, so a changed
  fixture's dependents in unselected modules still have their stale contexts dropped. This is the one
  correctness defect a naive path restriction would introduce, and it is a coverage defect rather than
  a selection one (R7).
- **FR-006 No `Item` is pinned for the baseline's sake.** `remember_all` stores
  `{nodeid: fixture_ids(it)}` and the graph edges instead of `list(items)`, and `_all_items` goes with
  it. It exists because `ROLL_DESELECT` and `TIER_SELECT` deselect by marker even on a full run, so the
  items list at write time is short of what the baseline needs - that reason is recorded at the point of
  change, since the code does not currently say it.
- **FR-007 Import-time work is deferred to the worker that needs it.** `tests/test_package_surfaces.py` computes its whole-tree AST census inside a session-scoped fixture rather than at module level (8.7 MiB, R6); `import coverage` moves inside the tests that use it in `tests/tools/test_hamlet_floor.py` and `test_roll_audit.py` (4.2 MiB, R6); and the module-level `from shapely.geometry import Polygon` in `tests/waterfields/test_geoms.py` and `tests/waterfields/test_seams.py` moves into the tests that use it, WITHOUT which FR-010 saves nothing on a full gate, because a run that collects `tests/waterfields` imports shapely into all ten workers whatever the engine does (`spec-fidelity` round 1, finding 4). `tests/soak/test_seatings.py` keeps its module-level `mock` import, with the
  reason recorded: `norecursedirs` holds `soak` out of every ordinary run, so no gate pays it.
- **FR-008 The worker count is untouched**, by the GM's ruling, and `tests/tooling/test_worker_count.py`
  keeps pinning ten.
- **FR-009 The change is measured, not asserted.** The collection peak and the gate peak are measured
  before and after with the PSS harness this feature's research used, and the numbers are recorded in
  `research.md` whichever way they come out - including if an item turns out not to pay. It records the
  MARGINAL shapely figure as well as the cumulative one: R9's 16.3 MiB is shapely plus the `numpy` it
  drags in, and `numpy` also arrives through `tools/page_lit.py` and `tools/picture_diff.py`, so any run
  collecting `tests/tools` holds it regardless (`spec-fidelity` round 1, finding 5). Deferring
  numpy in those two tools was recorded here as a further lever this feature had NOT taken, with the figure
  left for the GM to price; they asked for it on 2026-09-13 and FR-011 takes it.
- **FR-011 `numpy` is imported by the worker that uses it, the same way - and `PIL` with it, on the
  session's judgment rather than the GM's request** (the GM asked for numpy, 2026-09-13: *"I do indeed want
  you to do the same thing for numpy which we already did for shapely"*; PIL rides along and **D9** states
  what that was worth and how to reverse it).
  The two engine tools that hold them - `tools/page_lit.py` and `tools/picture_diff.py` - bind both through
  one `_load_arrays()` per module, and the three test modules that import them at module level
  (`tests/tools/test_page_lit.py`, `test_picture_diff.py`, `tests/interactive/test_raster.py`) import them
  inside the tests that use them, because `np` and `Image` are reached by ATTRIBUTE and a same-named
  wrapper cannot stand in for a module. The derived guard of FR-010 widens to all three libraries rather
  than gaining a second copy. This is the lever FR-009 recorded as not taken, and it is the larger half:
  it is what held the whole-tree collection peak at 922 MiB while every part of it shrank (R14).
- **FR-010 `shapely` is imported by the worker that uses it, through one accessor per module.** The
  SEVEN engine modules that import it at module level - `settlement/land/wet.py`,
  `hamletgen/homesteads/boundary.py`, `waterfields/comb.py`, and `waterfields/seams/close.py`,
  `geoms.py`, `plots.py`, `pockets.py` - each get ONE module-level lazy accessor that imports on first
  use and caches what it needs; no `import` statement goes inside a function that runs per plot, per
  seam or per candidate, because both forms defer the cost and only one of them is free afterwards (D6).
  The SET IS DERIVED, not kept as a list here: a test fails on any module-level shapely import under
  `l7r/` outside the accessor, because a hand-enumerated surface is the failure this repository has
  already paid for in features 169, 185 and 190 - and a hand list is how this requirement first said
  eight (`spec-fidelity` round 1, finding 3).
  **Its acceptance is the perf bookend and an increase is NOT waiverable.** `make perf LABEL=237-start`
  was taken on unmodified code before any of this landed; `make perf LABEL=237-end` and `make perf-report
  AGAINST=237-start` run on the same machine with this feature's delta as the only change. The local
  band-1 line is 0.0%, so any increase on the total or on any seed trips `perf_review.py --check` at
  push. Under the standing ladder such an increase is dischargeable with a written explanation and a
  `perf-audit` confirmation; for FR-010 it is not, because the item was approved as a memory saving and
  a slower map is not a trade the GM was offered: the offending site keeps its module-level import and
  the remaining sites stand (finding 7).

## Success criteria

- **SC-001** (FR-001, FR-003) On a corpus of recorded plans, the derived path set covers every module
  `keep_set` keeps, and a plan whose `changed_test_modules` names a file that does not exist in the
  baseline still collects it - a new test file is always reachable.
- **SC-002** (FR-002, FR-009) An incremental gate over a narrow plan shows a collection peak below the
  whole-tree figure in R3, measured the same way; the gate stays green and the 100% floor still passes
  over the merged coverage.
- **SC-003** (FR-004, FR-005) Two consecutive incremental gates: the second selects the same small set
  as the first rather than near-everything (proving the baseline was not shrunk), and a fixture changed
  in the first run has its dependents' contexts dropped even when those dependents live in modules the
  run did not collect.
- **SC-004** (FR-006, FR-007) The per-worker import measurement in R6 re-run: the three named items no
  longer appear in it, and `tests/test_package_surfaces.py`'s own test still fails when a surface is
  broken (the check is deferred, not weakened).
- **SC-005** (FR-007, FR-010) `shapely` is absent from `sys.modules` after the whole engine is imported
  and after a collection-only run of the full tree - asked of the PROCESS, not of the source - and
  present the moment a geometry call is made; and `make perf-report AGAINST=237-start` reports no
  increase on the total or on any seed. The first clause needs FR-007's two test modules as well as
  FR-010's seven engine ones, which is why it names both: with the engine alone it would pass a
  restricted run and fail every full gate.
- **SC-007** (FR-003) A plan whose baseline projection is over `FULL_FRACTION` comes out `full` with NO
  paths, so the run collects the trees and records a baseline; and a restricted run never reports itself
  full, whatever its selection comes to.
- **SC-008** (FR-011) After the whole engine is imported, `numpy` and `PIL` are absent from `sys.modules`
  along with `shapely`, asked of the process; a whole-tree collection-only run at ten workers peaks BELOW
  the 922 MiB R3 measured before this feature; and `make page-lit` and `make picture-diff` still work.
- **SC-006** (FR-008, spec-wide) `make done` and `make hooks-test` green, `make quick` unchanged in
  scope, and `tests/tooling/test_worker_count.py` still pinning ten workers - the one item this
  feature is forbidden to move.

## Decisions Recorded

- **D1 - paths, not a plugin.** Every sharding plugin in the ecosystem filters in
  `pytest_collection_modifyitems` and therefore pays the whole collection (R2); the only mechanism that
  skips the import is an argument, which is what home-assistant uses at scale. Declined with it:
  `pytest-split`, `pytest-shard`, `pytest-test-groups`, `--dist each`, `--maxschedchunk`, per-worker
  `--tx` environments, `pytest-run-parallel`, and waiting for upstream.
- **D2 - concurrent shards measured and rejected** (R4): 1,836 MiB against 1,742 for one run. Recorded
  because it was the GM's own stated worst case and because the reason generalizes - worker count, not
  run count, is what multiplies the import.
- **D3 - the baseline is a full run's to write.** The alternative, reconstructing the unselected
  modules' entries from the previous `tests.json`, was declined: it would make the baseline a merge of
  two runs' collections with no single run having ever seen the whole set, which is exactly the
  property the plan's "is this test new" question depends on.
- **D4 - the expected cause was absent, and that is recorded rather than quietly dropped** (R5, R6, R8).
  The GM's hypothesis was that test modules hold map data as Python literals; the tree holds 40 KiB of
  module-level literals in 2,513 KiB of source, and the maps come from rolls and from disk. The shape
  of the fix they described was right and is FR-007; its payload is import-time computation and a
  library import.
- **D5 - the worker count stays at ten** (FR-008), the GM's explicit instruction, against a measured
  trade of 1.14 GiB at eight workers and 45.2 s versus 1.39 GiB at ten and 40.3 s.
- **D6 - one accessor per module, never an `import` in a hot function** (FR-010). Both forms defer the
  cost; only one of them is free afterward. Every one of the seven sites is called per plot or per seam,
  and an `import` statement re-enters `__import__` on each call, so the lever that saves 16 MiB would
  have been paid back in a slower gate and slower maps. The accessor resolves once and is a local lookup
  from then on.
- **D7 - the four original items are one feature on purpose** (the fifth, FR-011, was added by the GM on the strength of this feature's own measurement, and belongs with them for the same reason).** They share a single measurement (the PSS harness
  in R3) and a single acceptance (the collection peak), and three of the four are meaningless to verify
  apart: a path restriction that does not defer the import-time work still pays R6's 13 MiB, and
  deferring imports without restricting the paths still collects everything. The GM asked for them
  together.
- **D8 - the fraction is decided before collection, not after it** (FR-003; AMENDED 2026-09-13, mid
  implementation, on a review counter reset to zero by the GM's own ruling). This was not in the spec the
  review accepted, and the code is what found it: the first implementation kept `selection.py`'s flip and
  simply refused it on a restricted run, which left the knob dead on the only plan that could ever reach
  it, and two existing tests went red saying so. The flip's purpose - "most of the suite is selected
  anyway, so run everything and record a fresh baseline" - requires collecting everything, which is
  precisely what the arguments have already foreclosed by then. So `incremental.over_the_fraction`
  projects `keep_set`'s rules over the BASELINE and the planner returns a full plan (no paths) when the
  projection is over the line. What this costs, stated rather than discovered later, and it errs in BOTH
  directions. It UNDERCOUNTS by tests that do not exist yet: `over_the_fraction` passes the baseline as the
  collection, so `keep_set`'s "not in the baseline" rule cannot fire, and a new test is invisible to the
  projection though it is still collected and run (its module changed, so git reports it). A plan near the
  line therefore runs incrementally instead of fully, which is safe because an incremental run merges over
  the baseline while a full run replaces it. And it OVERCOUNTS by baseline tests that no longer exist:
  `existing()` strips a deleted module from the ARGUMENTS but leaves it in `changed_test_modules`, so
  `keep_set`'s module rule counts every one of its baseline tests as reached - retiring a large test module
  can therefore flip the gate to a full run on tests nobody will collect. That is safe for a different
  reason, and the difference matters to whoever meets it: not that incremental merges, but that a full run
  is always CORRECT, merely slower - the cost is one full gate paid for tests that were retired. The
  denominator moved with it, from `len(collected)` to `len(baseline_tests)`. Making the error
  one-directional by dropping deleted modules from `changed_test_modules` as well is a change to what flips
  the gate, so it is left for the GM to price rather than taken here.
- **D9 - PIL was deferred alongside numpy, and that is the session's judgment rather than the GM's
  request** (`spec-fidelity` on the FR-011 amendment, finding 4). The GM asked for numpy: *"do the same
  thing for numpy which we already did for shapely"*. `PIL` is a separate library with its own cost, and it
  is separable - `tests/interactive/test_raster.py` imported PIL and no numpy at all, so the "same import
  block" argument that covers the other four files does not cover that one. What it is worth: **2.3 MiB a
  worker**, against numpy's 17.9 (R9). What reversing it would cost, MEASURED after the review asked for the
  figure rather than estimated: with numpy deferred and PIL put back at module level in the two tools, the
  whole tree collects at 854 MiB against 840 with both deferred - so of the 83 MiB the pair saves, **numpy is
  69 MiB and PIL is 14** (R14).
  Why it was taken: in four of the five files the two imports are adjacent lines feeding the same functions,
  the guard reads one list, and splitting them would leave a module half-deferred. It is disclosed here
  rather than folded into the request so the GM can reverse it in one commit if they would rather only the
  thing they asked for moved.
