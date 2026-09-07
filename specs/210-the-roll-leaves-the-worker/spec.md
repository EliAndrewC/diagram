# Feature 210 - the roll leaves the worker

**Status**: FAITHFUL (`spec-fidelity`, round 5 of 5 - the cap) - implemented; the gate green with the
after numbers in research R5 (a worker on a roll-heavy file 242 -> 90 MB; the gate's Python 2.4 -> 2.2 GiB,
no `FabricIndex` alive anywhere at the end). Rounds 1-4 each found the roll-out list or the "every roll" boundary short of what the code holds: `generate()` alone, then `build()` alone, then the regen site, then the three tools that iterate `STAGES`, then a token form that missed `enumerate(STAGES, 1)`. Every miss was the same shape - a surface enumerated by hand rather than derived - and the fix each time was to derive it (the callers of `generate`/`build`/`STAGES`; loops by what they DO). Watched per CLAUDE.md: a feature reaching five rounds says the drafting is the problem.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - the heap census, the file cache, the three levers, why a
subprocess.
**Predecessors**: 208 (the raster is a render; the picture in a child); 138 (the clearance memo); 135/147/192
(the roll cache and the FULL run's shared rolls); 026/145 (the pool sweep's coverage-recording child).

## Summary

The GM, on the census: *"I agree that we should clear the clearance memo at the end of a roll and that we
should do the malloc_trim after a roll. it seems like we should also roll in a forked child as well ...
test out by trying it in one place and then making sure that that is solid and that there are no
undesirable side effects ... then we can roll it out to the rest."* Three changes: every roll clears the
clearance memo and trims the heap when it ends; and in ONE place - `rollcache.hamlet()`, the gate
fixtures' rolls - the roll runs in a coverage-recording child process and only its picklable result
enters the worker. Everything else rolls in-process as before.

## Functional requirements

- **FR-001 The memo is cleared when a roll ends - every roll.** `hamletgen/clearance.py` gains `reset()`,
  and `hamletgen/driver.py` gains a `roll_scope()` context manager whose exit, success or failure, calls it
  (and FR-002's trim). Every loop over `STAGES` runs inside it: `build()` (so a roll made by `generate()` -
  each attempt of its re-roll loop, not only the last - by `rollcache.hamlet()`, by a test's produce
  closure calling `build()` directly, by the pool gens under regen, by `cohort_audit` and `mapcheck`),
  and the three tools that iterate `STAGES` themselves rather than calling `build()` -
  `tools/perf_snapshot.py` `measure()` (the perf bookend in `make done FULL=1`), `tools/perf_profile.py`
  `profile_stage()`, `tools/placement_stages.py` `build_page()`. A test proves every `STAGES` loop that RUNS a stage in the
  engine is inside the scope, so a fourth cannot appear outside it unnoticed. Within a roll nothing changes
  (the memo still serves the router's repeated queries); across rolls nothing was ever served (R1), and
  between re-roll attempts nothing can be either (each attempt's plan is a deep copy, so its polygons are
  new objects) - the stricter placement is also free.
- **FR-002 The heap is trimmed when a roll ends - every roll.** A `trim_heap()` helper calls glibc's
  `malloc_trim(0)` through ctypes and returns whether it ran; where libc or the symbol is absent it
  returns False and raises nothing. `roll_scope()`'s exit calls it beside FR-001.
- **FR-003 `hamlet()` rolls in a child.** `rollcache.hamlet()`'s production - plan, build, finish - runs
  in a subprocess: a driver script in a scratch directory, the spec passed by pickle, the plan and
  manifest and the roll's dependency record (`gencache.record`) returned by pickle. When the parent is
  under coverage (`COV_CORE_SOURCE` in the environment) the child runs under `coverage run
  --parallel-mode` with the parent's coverage hooks stripped from its environment and its data file
  published into the skill directory's `.coverage.*` glob, exactly as `gate_obtain` does; otherwise it
  runs plain. A failing child raises with its stderr. Every serving mode of `obtain` is unchanged: a
  HIT still serves from disk in-process; a MISS and the FULL run's produce paths call the child; the
  dependency record stored with a MISS is the child's.
- **FR-004 Nothing else rolls in a child - and the rest is LISTED.** By the GM's staging (*"trying it in one
  place ... then we can roll it out to the rest"*), every other in-process roll site is untouched here and
  enumerated, derived by walking the callers of `hamletgen.generate`, `hamletgen.build` AND
  `hamletgen.driver.STAGES` (three tools iterate the stages without calling `build()`) rather than written
  from memory, so the roll-out has its list:
  `pipeline/regen.py` `regen()` -> `gencache.run_and_record()` -> `runpy.run_path`, which rolls each of the
  five pool hamlet gens (`pool/hamlets/{inashiro,kuwabata,kashikawa,sawada,mizuguchi}/*.gen.py`, each a
  direct `generate(...)`) IN THE REGEN WORKER'S PROCESS - the site behind `make map`, `make maps` and
  render-sync, and the largest in-process roll site in the repository; `rollcache.report()` and
  `rollcache.report_deps()` (the FULL run's `report:` rolls; `test_villages`' immune test and the cohort
  ratchet read them); `driver.cohort()` (the hamletgen CLI's `--batch`, and the cohort tests) and
  `driver.main()` (the hamletgen CLI, `make hamlet`); `tools/cohort_audit.py` (two sites; `make cohort`)
  and `tools/mapcheck.py`; the three tools that iterate `STAGES` directly - `tools/perf_snapshot.py`
  `measure()` (several seeds in one process; the perf bookend of `make done FULL=1`), `tools/perf_profile.py`
  `profile_stage()`, `tools/placement_stages.py` `build_page()`; the gate tests whose produce closures call
  `build()` directly - `tests/gate/hamletgen/test_homesteads.py` (three), `test_sink.py`,
  `test_woodland_shrink_147.py` - and the two that call `generate()` directly in
  `tests/gate/hamletgen/test_driver.py`. Two caller sites the same walk finds are NOT candidates, stated so
  they are not dropped silently: `gencache.gate_obtain` already rolls in a coverage-recording subprocess
  (it is the shape FR-003 copies), and `tests/hamletgen/test_driver.py`'s three `build()` calls run stubbed
  stages and roll no map. Each candidate takes the same child once `hamlet()` has proven solid; the two
  `report` paths first, since they run in every full gate, then the regen site.
- **FR-005 Tests.** `reset()` empties the memo; `trim_heap()` reports True here and False when libc is
  unavailable (monkeypatched); after a `build()` the memo is empty, and after a `build()` that raises it is
  empty too; a static test over the engine's source (AST, not text) asserts that every loop under `l7r/`
  whose iterable references `STAGES` and whose body CALLS a stage - `for stage in STAGES`, `for i, stage in
  enumerate(STAGES, 1)`, or any other form - sits inside a `roll_scope()`, and names the one excluded
  shape in the test with its reason: a comprehension that only reads stage attributes (`perf_profile.py`'s
  `names = [...]`) runs no stage and must not be wrapped; the child returns the same plan
  and manifest a direct in-process production returns for the same spec (manifests compared as JSON);
  a failing child raises naming the failure; with `COV_CORE_SOURCE` set the child leaves a
  `.coverage.rollchild-*` file in the skill directory and without it none; the gate's coverage floor
  holds at 100% with the hamlet path's lines now executed in the child.
- **FR-006 Measured before and after.** Per worker at the end of a full run: resident, the memo's deep
  size, glibc retained (R1 before); the gate's Python at its peak (2.4 GiB before); one roll-heavy file on
  one worker (242 MB resting before). After, in research R5.
- **FR-007 The record.** The why at each point of change; `pipeline/CLAUDE.md`'s roll cache row and
  `dev/performance.md`'s memory section extended; the roll-out list is FR-004's enumeration.

## Success criteria

- **SC-001** After a full run, a worker whose rolls all came through `hamlet()` rests near its collection
  baseline; no worker holds a `FabricIndex` at the end.
- **SC-002** `make done` green with the 100% floors; the hamlet-path floor (feature 145) unchanged.
- **SC-003** The after numbers recorded against R1.

## Decisions Recorded

- **D1 - a subprocess, not `os.fork`** (R3): coverage, the parent's monitoring tool and execnet state, and
  the dependency record all argue for the pool sweep's proven shape.
- **D2 - one place first: `hamlet()`.** The gate fixtures' rolls are the bulk and the payload already
  pickles; `report()` and `report_deps()` wait for the roll-out.
- **D3 - the memo is cleared, not shrunk.** A smaller cap would still hold the LAST roll's geometry for the
  life of the process; clearing at the roll's end holds nothing and costs nothing within a roll.
