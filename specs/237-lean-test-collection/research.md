# Research - feature 237, lean test collection

## R1 - why every xdist worker collects the whole suite

It is documented design, not an accident, and it cannot be turned off. `docs/how-it-works.rst` in the
xdist 3.8.0 sdist: *"workers at this point perform a full test collection, sending back the collected
test-ids back to the controller which does not perform any collection itself ... it converts the list
of test-ids into a list of simple indexes ... the controller can now tell one of the workers to just
execute test index 3 instead of passing the full test id."*

In the source: `dsession.py` returns early from collection on the controller (`# prohibit collection of
test items in controller process`); `LoadScheduling.schedule()` calls
`_check_nodes_have_same_collection()` and logs `**Different tests collected, aborting run**` on a
mismatch, then `self.pending[:] = range(len(self.collection))`; `loadscope.py` converts nodeids back to
indexes per worker, and `loadgroup` inherits it. Dispatch is therefore BY INDEX into a collection every
worker must share.

The CHANGELOG records the indexes as a bug fix (1.10, pytest issue 419: nodeids are not unique for
parametrized duplicates), and the one PR that tried to skip per-worker collection was closed unmerged -
bluetech: *"how can a node execute a test (Item) it hasn't collected?"*; RonnyPfannschmidt: *"it is a
completely unacceptable no go as shedulers currently talk in terms of indexes into the collection"*.

**What this leaves.** Arguments (paths and node ids) restrict `Session.collect` BEFORE import; `-k`,
`-m` and `--deselect` filter after it. Arguments apply identically to every worker, because a worker is
handed the controller's argv verbatim (`workermanage.py`: `args = [str(x) for x in
self.config.invocation_params.args or ()]`), so restricting them keeps the protocol satisfied. There is
no per-worker argument and no supported way for one worker to collect less than another.

## R2 - the ecosystem: every shard plugin filters AFTER collection

Read from their sdists rather than their READMEs. `pytest-split` (`--splits/--group`), `pytest-shard`
(`--num-shards/--shard-id`) and `pytest-test-groups` all do their work in
`pytest_collection_modifyitems` with `items[:] = <subset>` plus `pytest_deselected`. They balance CI
wall clock across machines and save no memory at all. `--dist each` is worse (every worker runs
everything); `--maxschedchunk` and per-worker `--tx` environments do not touch collection;
`pytest-run-parallel` says in its own README that it is not an xdist alternative.

Upstream will not fix it: the TIME cost is xdist issue 353, open since 2018 and reopened by a
maintainer (*"reopened as structural issues on our side have clearly been demonstrated"*), nothing
implemented in eight years; the MEMORY cost of duplicated collection has never been filed against
xdist, which has no memory or performance label. One layer down, pytest issue 619 has been open since
2014 with `help wanted` - *"149150 test functions ... takes 1.26GB ... about 8KB per test"* - and
nicoddemus: *"In general pytest has been optimized for efficiency rather than memory usage."*

Of the large projects, **home-assistant** is the only one that solves it, and it solves it by PATHS: a
`split_tests.py` job writes ten buckets and each matrix job is given only its own bucket's paths, so no
worker ever collects 80k tests. Its stated reason is wall-clock balance; there is no memory rationale
anywhere in its CI config. pandas and numpy/scipy run xdist over the whole suite. sentry shards 22 ways
by hashing nodeids after collection. django collects once in the parent and forks, but django is not
pytest. So: the problem is real and general, the fix is paths, and nobody has packaged it.

## R3 - what collection costs here, measured

Memory is measured as the sum of PSS over a run's own process tree, sampled at 0.4 s
(`scratchpad/shard2.py`). PSS divides shared pages among the processes mapping them, so the sum over a
tree is an honest total, and - unlike the container's cgroup counter - a concurrent gate in another
session cannot inflate it.

**Collection only (a `-k` that matches nothing), 10 workers:**

| scope | peak | per worker |
|---|---|---|
| whole tree | 922 MiB | 92 MiB |
| one tree (`tests/settlement`) | 602 MiB | 60 MiB |
| one module | 356 MiB | 36 MiB |

A full run over the whole tree peaks at 1,742 MiB, so **collection is 53% of the gate's peak, and it is
paid whether or not a single test runs.**

**The per-worker budget** (RSS checkpoints in one process, which agree with the table above to within
a megabyte): 13.8 MiB interpreter; +12.1 pytest; +9.9 xdist, coverage and pytest-cov (36 MiB is the
floor, matching the one-module row exactly); +29.8 for 221 engine modules; +28.0 for 270 test modules.
Items themselves are ~2-3 KiB each (3,753 items, under 10 MiB), which matches pytest PR 14766's own
benchmark of 2,860 B/item and is well under issue 619's 8 KiB. Nothing about the per-item cost is
anomalous; the cost is importing 491 Python modules into ten processes.

## R4 - sharding into concurrent runs: measured and REJECTED

One 10-worker run over the whole tree against two concurrent 5-worker runs over halves:

| | peak | wall |
|---|---|---|
| one run, 10 workers, whole tree | 1,742 MiB | 25.6 s |
| two runs, 5 workers each, halves | 1,836 MiB | 18.1 s |

Splitting cost **94 MiB more**. The duplication is per WORKER, not per run: ten workers are ten copies
whichever way they are grouped, each half still imports the engine (30 of the 92 MiB), and a second
controller is added. The wall-clock column is noisy - another session was running tests during the
first row - and is not the reason for the verdict. This closes the GM's own worst case (*"ten different
test suites"*) by measurement rather than by argument.

## R5 - the data-as-Python hypothesis, tested

The GM's hypothesis: the test modules hold large map data written as Python, so every worker loads it.

An AST scan of the whole tree (`scratchpad/litscan.py`): **275 modules, 2,513 KiB of source.**
Module-level assignments whose value is a literal total **40 KiB, 1.6% of the source**; the largest
single block in the repository is 7.2 KiB (a guard census table in
`tests/tooling/test_guard_firing_log.py`), then 5.6 KiB (`tests/test_villages.py`) and 3.2 KiB
(`tests/test_citybudget.py`). Literals of eight or more elements inside function bodies - the
fixture-returning-a-dict shape - add **9 KiB**. There is no megabyte-scale data structure written as
Python anywhere in the tree.

The map data is already on disk and already lazy: maps are ROLLED at run time and shared through the
roll cache, and the fixed data is read from the pool manifests, from `tests/fixtures` (544 KiB) and
from nine JSON and CSV files.

## R6 - where the test-module megabytes actually are

Each test module imported into a live process after the engine is in (`scratchpad/impcost.py`): **232
modules, 20.5 MiB, mean 91 KiB, 8.6x the source size** - the ordinary CPython ratio of code objects,
function objects and class dicts to source. The largest SOURCE files are among the cheapest:
`tests/interactive/test_page.py` is 57.4 KiB of source and costs 0.11 MiB; `tests/settlement/test_fields.py`
is 48.1 KiB and costs 0.09 MiB.

Two thirds of the total is three modules doing work AT IMPORT TIME, each re-measured in a fresh process
(`scratchpad/one.py`, `two.py`):

| module | cost | what it is |
|---|---|---|
| `tests/test_package_surfaces.py` | 8.7 MiB | module-level `_IMPORTS = _from_imports()`, which `ast.parse`s every `.py` in the skill |
| `tests/tools/test_hamlet_floor.py`, `test_roll_audit.py` | 4.2 MiB | `import coverage` at module level |
| `tests/soak/test_seatings.py` | 3.5 MiB | `from unittest import mock` at module level - the only one in the tree |

The package-surfaces global RETAINS almost nothing (`_IMPORTS` holds 1,314 small tuples); the 8.7 MiB is
the transient AST of the whole skill, freed but never returned to the OS, so the arena growth lasts for
that worker's life. The soak module is not collected by an ordinary run (`norecursedirs` carries
`soak`), so its 3.5 MiB is never paid at the gate - which leaves **about 13 MiB per worker, about 130
MiB at ten workers**, in two items.

## R7 - what restricting the arguments breaks, and what it does not

**Already safe, checked in the code rather than assumed.**

- A change to any non-test-module file under `tests/` - a conftest, `_scope.py`, a helper, `fixtures/` -
  already forces a FULL run (`plan()`'s `ch.other_tests` branch), as does a change to a line that runs
  at import time (`import_time_change`). So an incremental run is by definition one where no shared
  fixture moved, and restricting the paths cannot hide one.
- `stale_tests` already keys on the modules that were actually collected, and its docstring says why:
  *"A module not collected at all (an `--ignore`, the browser package under a fresh stamp) keeps its
  tests' contexts: nothing about them changed."* The mechanism was built for `--ignore`, and a path
  restriction is the same decision at finer granularity.

**Genuinely breaks, and this is the work.**

1. `save_baseline` runs after any green floor phase and promotes `tests.json.next`, which
   `selection.py` writes from THIS run's collection. Restricted, that list is short, so the next
   plan's `baseline_tests` would be missing the unselected modules' tests and `keep_set` would treat
   every one of them as new - one narrow run followed by a near-full one.
2. `result.json`'s `fixture_dependents` feeds `fixture_closure` in `merge`. Partial on a restricted
   run, so a changed fixture's dependents in unselected modules would keep their stale contexts. That
   is a coverage-correctness defect, not a selection one, and it is the reason FR-005 exists.

**Why `remember_all` exists at all**, which the code does not say: `ROLL_DESELECT` and `TIER_SELECT`
deselect by MARKER even on a full run, so the items list at write time is already short of the baseline
the next plan needs. That is what `session._l7r_all_items = list(items)` is for - and it pins every
collected `Item` on every worker to do it, when its one consumer needs `{nodeid: fixture_ids(it)}`.

## R8 - are there individually enormous functions? No, and the sweep is exhaustive

The GM's remaining question: a fixture whose body is a large literal is not a module-level assignment
and could have evaded R5. So every function in the repository was ranked two ways
(`scratchpad/fnsize.py`) - by source span, and by what its COMPILED code object costs, which is
`len(co_code)` plus the recursive size of `co_consts` with nested code objects counted as their own
rows. The second measure is the one that matters: a literal inside a function body lives in that
function's constants and is paid at import.

| tree | code objects | bytecode | constants | largest single object | functions over 8 KiB of source |
|---|---|---|---|---|---|
| `tests/` | 7,136 | 1.34 MiB | 3.28 MiB | 14.0 KiB (a module body) | **0 of 3,405** |
| `l7r/` | 5,222 | 1.54 MiB | 2.79 MiB | 37.6 KiB (`overlap/taxonomy.py`'s module body) | 58 of 1,760 |

Not one function in the test tree exceeds 8 KiB of source; the largest is 5.8 KiB, and the largest
function-level constant block is 6.1 KiB. The engine's 58 large functions are large in STATEMENTS, not
data - `_draw_board_caption` is 43.4 KiB of source and does not reach the top ten by code plus
constants. The one real data table in the repository is `overlap/taxonomy.py`, at 37.6 KiB.

So the whole repository compiles to about 9 MiB while importing it costs about 50 MiB of RSS. The
factor of five is the runtime objects Python builds around the code - function objects, class objects,
type and module dicts, annotations, closures - and it is ordinary.

## R9 - what a worker's 92 MiB is actually made of

Measured as cumulative RSS in one process (`scratchpad/libs.py`, `eng.py`), which is where the answer to
*"it is not normal for unit tests to take this much RAM"* turns out to be:

| component | MiB | whose |
|---|---|---|
| bare interpreter | 9.4 | - |
| `pytest` | 16.1 | third party |
| `coverage` + `pytest-cov` | 9.9 | third party |
| **`shapely`** (which pulls `numpy`) | **16.3** | third party, via 9 of our files - 7 engine, 2 test |
| `PIL` | 2.3 | third party, via 2 tools |
| our 182 engine modules | 10.4 | ours |
| our ~230 test modules | ~17-20 | ours, 13 of it R6's three items |

**44.6 MiB per worker is third-party code imported before a line of ours runs**, against ~28 MiB for
all 412 of our own modules. The tests are not the expensive part and never were.

`shapely` is the interesting row: 16.3 MiB from SEVEN module-level import sites in the engine -
`settlement/land/wet.py`, `hamletgen/homesteads/boundary.py`, `waterfields/comb.py` and FOUR of
`waterfields/seams/*` (`close.py`, `geoms.py`, `plots.py`, `pockets.py`) - every one of them geometry
that a run only touches when it builds a map. (`waterfields/banks.py` answers a grep for the word and
holds no import: its `ring_solidity` docstring explains that it is hand-rolled INSTEAD of shapely.)
Two TEST modules import it at module level as well - `tests/waterfields/test_geoms.py` and
`test_seams.py` - and they are the half that decides whether this pays on a full gate: a run that
collects `tests/waterfields` imports shapely into all ten workers whatever the engine does.

**And 16.3 MiB is the CUMULATIVE figure, shapely plus the `numpy` it drags in.** `numpy` alone is 13.25
MiB, and `tools/page_lit.py` and `tools/picture_diff.py` import it at module level while
`tests/tools/test_page_lit.py` and `test_picture_diff.py` import those, so any run collecting
`tests/tools` holds numpy regardless of what the geometry modules do. The MARGINAL shapely-only saving
is therefore smaller than 16.3 and is measured rather than asserted (the spec's FR-009). Deferring
numpy in those two tools is a further lever, recorded here and not taken: the GM approved the shapely
accessor.

A collection imports the module, so before this feature all ten workers paid shapely whether or not they
ran a geometry test. Deferring the import moves that cost to the workers that execute the code, and the
FORM matters: every one of the seven engine sites is on a per-plot or per-seam path, so an `import`
statement inside one of those functions would re-enter `__import__` on every invocation and pay the
memory back in time. So the deferral is ONE module-level lazy accessor per module, resolved once and a
local lookup afterwards (the spec's FR-010 and D6), with the perf bookend as its acceptance: the local
band-1 line is 0.0%, and for this item an increase is not waiverable - the offending site goes back to a
module-level import.

## R10 - what it cost before, measured the same way twice

Every figure here is the sum of PSS over the run's own process tree, sampled at 0.4 s
(`scratchpad/shard2.py`, `peak.py`), so a concurrent gate in another session cannot inflate it.

**Before, on unmodified engine code.** `make test-full` passes `INCREMENTAL=0` unless `FROM_DONE` is set,
so this is a FULL run and not the narrow case - the incremental path belongs to `make done`. Stated here
because the first reading of this number assumed otherwise:

| | peak | wall |
|---|---|---|
| `make test-full` (a full run), before | 3,124 MiB | 66.0 s |

It collected all 3,753 tests across ten workers and paid the coverage tracer and the floors. A full run is
also the shape this feature helps LEAST, by construction: it collects everything on purpose, so only the
deferred imports (FR-007, FR-010) can move it, never the restriction.

**The pool is byte-identical.** `make maps` regenerated every shipped hamlet clean and `git status pool/`
reports nothing: no manifest, no render and no page moved, which is the evidence that the shapely deferral
(FR-010) changed the geometry in no way at all. It is also why this feature owes no `settlement-review`
(feature 231's rule: a review is owed when a pool map's LAYOUT moved).

**After, the same instrument.** Full run against full run, and a third full run at 3,169 MiB to show the
spread - which is the point: at this scale the run-to-run variance is larger than what the deferred imports
can save on a shape that collects everything anyway.

| | peak | wall |
|---|---|---|
| `make test-full` (full), before | 3,124 MiB | 66.0 s |
| `make test-full` (full), after | 2,897 MiB | 48.2 s |
| `make test-full` (full), after, again | 3,169 MiB | 48.8 s |

**COLLECTION ONLY, which is the low-noise instrument** (a `-k` matching nothing, ten workers, identical
before and after, sampled at 0.1 s and again at 0.4 s with the same answer):

| scope | before | after |
|---|---|---|
| whole tree | 922 MiB, 9.1 s | **923 MiB, 4.5 s** |
| one tree (`tests/settlement`) | 602 MiB | **515 MiB** |
| one module | 356 MiB | 366 MiB |

Two things to read honestly here. The per-module deferrals are VERIFIED individually, in a fresh process
each: `tests/test_package_surfaces` 7.40 -> 0.09 MiB, `tests/tools/test_hamlet_floor` 3.18 -> 0.42 MiB, and
the engine baseline itself 61.0 -> 57.6 MiB as shapely leaves it. But the whole-tree collection PEAK did not
move, and its wall time halved. I do not have a confirmed mechanism for the peak holding at ~922 MiB while
the parts that compose it each shrank, and it is recorded as measured rather than explained away: three test
modules still import numpy at module level (`tests/interactive/test_raster.py`,
`tests/tools/test_page_lit.py`, `test_picture_diff.py`), which is 17.9 MiB a worker that a whole-tree
collection pays regardless. **R14 tested that suspect and it was right** - the anomaly is closed, and a
reader who stops here should not carry it away as open.

Which is the feature's own argument, arrived at from the other side: the way to stop paying for the whole
tree is to stop collecting the whole tree. One module's collection is 366 MiB against 923, and one tree's is
515 - so what an incremental gate pays is set by its REACH, which is exactly what FR-001 derives.

**And the marginal shapely figure FR-009 asks for, which changes the emphasis.** Measured by import
order in one process (`scratchpad/libs.py`): `numpy` first costs 17.91 MiB and `shapely` then adds only
**3.39 MiB**; `shapely` first costs 21.71 MiB because it pulls numpy in with it. So what deferring
shapely is worth depends on whether numpy arrives anyway:

- on a run that collects `tests/tools` - every full gate - `tools/page_lit.py` and `tools/picture_diff.py`
  import numpy at module level, so the marginal saving is about **3.4 MiB a worker**;
- on a restricted run that collects neither, it is the whole **21.7 MiB a worker**.

Which means the lever this feature had not taken AT THE TIME OF THIS MEASUREMENT - deferring numpy in those
two tools - is the larger half on a full gate. It was recorded here for the GM to price rather than taken on
a session's own judgment, and they asked for it the same day: **R14 takes it, and closes the anomaly this
section leaves open.**

## R11 - the gate itself, which is the number that matters

`make test-full` passes `INCREMENTAL=0` unless `FROM_DONE` is set, so the restriction only ever applies
under `make done`. Measured there, on the cheapest real shape - a clone whose engine content the baseline
already covers:

| | peak | wall | what it did |
|---|---|---|---|
| `make done`, after | **400 MiB** | **41.3 s** | `gate: INCREMENTAL - nothing the baseline exercised has changed`, 0 of 0 tests, green |

Four hundred megabytes is the WHOLE gate - lint, the type check, `hooks-test`, the selection, the merge,
all three coverage floors and the roll census - against 923 MiB for the collection alone that the same
shape used to pay before it ran anything. There is no before-measurement of this exact shape on the old
code, and the reason is worth recording rather than papering over: the first "before" run was taken with
`make test-full`, which forces a full run, so it measured the shape this feature helps least. The
comparison that is sound is the one above against the collection-only figure, which was measured on
unmodified code (R3) and again after (R10) with the same instrument.

## R12 - the perf bookends, and the one seed that got slower

`make perf LABEL=237-start` was taken on unmodified code before any of this landed; three independent
`-end` bookends were taken afterwards on identical code:

| | seed 4 | seed 25 | seed 39 | seed 47 | TOTAL |
|---|---|---|---|---|---|
| 237-end | +3.6% | -2.0% | -6.0% | -1.4% | -1.3% |
| 237-end2 | +1.8% | -4.0% | -6.0% | +0.0% | -1.8% |
| 237-end3 | +3.6% | +0.0% | -8.0% | -1.4% | -1.3% |

A fourth `-end` taken at the final commit reads seed 4 +1.8%, seed 25 -4.0%, seed 39 -8.0%, seed 47 -2.8%,
TOTAL **-3.1%**.

The total is faster every time and ONE STAGE on ONE SEED is consistently slower. The `perf-audit` agent
established the sharper form of this, and it is better evidence than the session's own: seed 4's `field` is
the only GROWING stage whose delta keeps its sign across the bookends - 1.82 s -> 1.92 / 1.90 / 1.92 / 1.88,
so **+0.06 to +0.10 s** - while every other mover that grows flips sign between runs, which is noise (seed 4's
`track` went -0.01 / +0.02 / +0.05, so the session's first explanation named it wrongly and the record was
corrected). Two DECREASES hold their sign as well - seed 39's `track` at about -0.12 and seed 47's `field`
from -0.06 to -0.19 - and both are improvements, so neither weakens the attribution of the one increase.
Residual outside the stages is zero to within rounding, so the seed's rise IS that stage. The delta shrank
from +0.10 to +0.06 when `geoms.py`'s sentinel was fixed, which is the direction that fix predicts: its two
import statements had been re-entering `__import__` on every construction.

**The cause is mechanical and measured, not inferred.** `field` is the paddy-fan stage - `waterfields/comb.py`
and `seams/` - which is the geometry that loads shapely; the only other shapely-touching stage,
`homesteads`, is 0.08 s and too small to hide it. A cold `import shapely.geometry, shapely.ops` measures
0.14 s warm and 0.24 s cold on this machine, against an observed +0.09 s net of the same stage running 0.04
to 0.14 s FASTER on the other three seeds. Seed 4 is the FIRST seed the snapshot runs
(`perf_snapshot.DEFAULT_SEEDS = (4, 25, 39, 47)`, one process, no reordering), and FR-010 moved the import
out of module import time and into first use - so the first seed of a process now pays it inside its timed
region. One-time per process, not per map, which is exactly why the other three seeds are faster.

Two candidates were **ruled out by measurement rather than by argument**, and the second was reverted.

The per-call loader cost is invisible in this data. The audit found the decisive case: seed 47's `field` is
4.63 s, the heaviest geometry in the set - the most plots, the most seams, the most `PlotGeoms` and
`GeomTree` constructions - and it went DOWN on every bookend (-0.06 / -0.08 / -0.11). At the commit it
audited, `geoms.py` was moreover calling its loader UNCONDITIONALLY on every construction, which is the
strongest form of the cost, and it still could not be seen.

So the inline sentinel at each call site - `if not _SHAPELY_LOADED: _load_shapely()`, to save the call
itself - was REVERTED. It left the slow seed at +3.6%, unchanged, and it cost the 100% floor: with several
call sites in a module, only the first one to run executes its `_load_shapely()` line and the rest are
unreachable. The coverage floor failed on precisely those lines, and in doing so it found a real defect
behind them - `geoms.py`'s loader declared the sentinel and returned on it but never SET it, so the guard
never engaged and its two import statements re-ran on every construction. Both are recorded at the point of
change so the lever is not pulled again.

## R13 - the trap a lazily bound name sets for a test, and which check caught it

A name bound on FIRST USE does not exist as a module attribute until something uses it, so
`monkeypatch.setattr(wet, "ShapelyPolygon", _boom)` raises `AttributeError` - unless some earlier test in
the same worker happened to run the geometry first. Two tests in `tests/settlement/test_wet_ground.py` do
exactly that patch, and the full gate **passed** while `make quick` **failed**: in the gate one worker had
already loaded shapely, in quick's smaller selection none had. An order-dependent pass is worse than a clean
failure, and it was the CHEAPER check that exposed it.

The fix is local and explicit - the test calls `wet._load_shapely()` before patching, with the reason beside
it - and it is safe because the loader's sentinel means a later call from inside the placer returns without
rebinding, so the patch survives. Worth knowing before deferring any other module-level import: every test
that patches the deferred name needs the loader to have run, and the gate will not tell you which ones.

## R14 - numpy was what held the whole-tree collection peak, and deferring it is the larger half

R10 recorded an anomaly honestly rather than explaining it: every part of the whole-tree collection shrank
and the PEAK did not move (922 MiB before, 923 after). R10 also named the suspect - three test modules
still importing `numpy` at module level - without testing it. The GM asked for the numpy deferral on
2026-09-13, and it settles the question:

| collection only, ten workers | before the feature | after FR-007/FR-010 | after FR-011 (numpy, PIL) |
|---|---|---|---|
| whole tree | 922 MiB, 9.1 s | 923 MiB, 4.5 s | **840 MiB, 3.9 s** |
| one tree (`tests/settlement`) | 602 MiB | 515 MiB | 516 MiB |
| one module | 356 MiB | 366 MiB | 366 MiB |

And per worker, measured the same way as R6: the engine baseline - pytest plus every engine module - falls
from **57.6 MiB to 42.9 MiB**, because `numpy` (17.9) and `PIL` (2.3) no longer arrive with it.

One reconciliation a reader will otherwise try and fail to make: 20.2 MiB a worker times ten workers is not
the 83 MiB the peak fell by, and nothing is wrong with either figure. The per-worker numbers are
single-process RSS checkpoints (R3, R6); the peaks are summed PSS, which divides a shared library's pages
among the processes mapping them. Ten workers importing the same numpy do not cost ten private copies of it.

So the mechanism behind R10's anomaly was this: `tools/page_lit.py` and `tools/picture_diff.py` imported
numpy at module level, `tests/tools/test_page_lit.py` and `test_picture_diff.py` imported those tools, and
`tests/interactive/test_raster.py` imported PIL - so ANY run that collected the whole tree paid numpy
regardless of what the geometry did. That is why deferring shapely alone moved the one-tree case and not the
whole-tree case, and why the marginal shapely figure (R10) was 3.4 MiB where numpy arrived anyway against
21.7 where it did not.

The form differs between the engine and the tests, and the reason is worth keeping: `np` and `Image` are
reached by ATTRIBUTE (`np.array`, `Image.open`), so the same-named-wrapper trick that let the waterfields
test modules keep every `Polygon(...)` call site unchanged cannot work for them. The two tools get a module
loader exactly like `_load_shapely`; the three test modules import inside the tests that use them, which is
the right form for a body that runs once. Annotations are the one snag: `-> Image.Image` is evaluated
outside the function body, so each test module keeps a `TYPE_CHECKING` import beside its lazy runtime one.
