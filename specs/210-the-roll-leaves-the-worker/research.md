# Research - 210 The roll leaves the worker

TOOLING research, nothing physical. Measured in the container on 2026-09-07 with the heap census (a
pytest plugin loaded through `PYTEST_ADDOPTS`: RSS split from `/proc/self/status`, glibc `mallinfo2`
through ctypes, a `gc` type histogram, every module-level container in the engine with its deep size
with `__slots__` descended, and the objects reachable from each).

## R1. What a worker's resting memory is made of (after feature 208)

Per worker, MiB, eight workers plus a 188 MB controller; `make test-full`, 3,033 tests, 328 s:

| component | at collection | at the end |
|---|---|---|
| resident | 106 | 197 to 266 |
| file-backed (mapped libraries) | 25 | 29 |
| `hamletgen.clearance._MEMO` (deep, slots descended) | 0 | 46 with 53 of its 64 entries; ~55 at the cap |
| glibc freed-but-retained (`mallinfo2.fordblks`) | 2 | 14 to 68 |
| glibc in use | 24 | 30 to 37 |
| the rest: Python heap - live objects and pymalloc arenas left fragmented by freed rolls | 55 | 60 to 80 |

No `Settlement`, `Report` or manifest dict was alive at the end of any worker: the module-scoped fixtures
release their rolls, and the roll cache's in-process store (`rollcache._SHARED_BYPASS`, the FULL run's
share of pickled rolls) held two entries totaling 0.7 MB. The GM's "rolled manifests they hold" is not
where the memory is.

**The memo is.** Measured on one file with two rolls, one worker: 165,447 objects reachable from
`_MEMO` - all 7,195 `RingIndex` and 7,195 `PointGrid` alive, 109,779 of the process's 112,491 lists,
14,444 dicts, 26,781 tuples - 46 MB deep. The memo (feature 138) caches a `FabricIndex` per set of
obstacle polygons so the lane router's thousands of clearance queries within ONE roll share an index;
it is keyed by the polygons' object identities (`id(o)`, length, end points), so a later roll can never
hit an earlier roll's entries, and it evicts oldest-first only at 64 entries - a roll fills about 25.

## R2. The file cache the GM asked about

`memory.stat` at the time: `file` 2,954 MiB, of which `inactive_file` 2,107 and `active_file` 846;
`file_mapped` 166; `file_dirty` 0; `shmem` 0. So: not tmpfs (that would be `shmem`; `/tmp` here is on
the overlay root), and not anything a process holds. It is the kernel's PAGE CACHE - the contents of
files read or written today kept in otherwise-free RAM: git pack files across the mirror and four
clones, the pool's renders and pages (a Kuwabata page is 6 MB, the PNGs a few MB each, times every map
times every clone), `.pyc` files, the roll cache's pickles, coverage data files, Chromium and resvg
binaries. A cgroup charges it to `memory.current`, which is why the container reads 3.7 GiB "used" at
idle, but it is clean (nothing dirty) and reclaimable: under pressure the kernel drops these pages
before it kills anything, which is what the 3,455 `max` events recorded when two gates met the cap. The
number that decides a kill is `anon` plus what cannot be reclaimed, and that was 3.7 GiB at the gate's
peak, 1.1 GiB of it the three Claude processes.

## R3. The three levers, and why the third is a subprocess rather than `os.fork`

1. **Clear the memo when a roll ends.** No speed cost: the next roll's polygons are new objects and
   cannot hit. `clearance.reset()` from `generate()`'s end. About 46 MB per worker.
2. **`malloc_trim(0)` when a roll ends.** glibc returns the free arena pages to the kernel; the roll
   itself leaves 14 to 68 MB retained per worker (feature 208 measured the RASTER's retention gone
   with the child, but the roll's own C allocations - the index buckets, the path lists - remain).
3. **Roll in a child, in one place first (the GM's staging).** The place is `rollcache.hamlet()`: it
   produces the rolled plan and manifest for the gate's module-scoped fixtures (`rolled`, `kuwabata`
   in `tests/gate/`), the bulk of the gate's rolls, and its payload is already the picklable pair the
   FULL run shares between workers. The child is a SUBPROCESS, not `os.fork()`, for three reasons the
   pool sweep already met (feature 026's `gencache.gate_obtain`): a forked copy of a coverage-traced
   xdist worker carries the parent's `sys.monitoring` tool, its execnet channel and pytest-cov's
   subprocess hooks, and "two recorders fight over the sys.monitoring tool id"; the child must run its
   own `coverage run --parallel-mode` and publish its data file into the session's `.coverage.*` glob
   for the Makefile's `combine --append`, exactly as `gate_obtain` does; and the dependency record the
   roll cache keys on (`gencache.record`) must come from the process that rolled. A fresh interpreter
   importing the engine costs about a second against a 25 to 50 s roll. The child runs plain when the
   parent is not under coverage (`COV_CORE_SOURCE` absent - pytest-cov's own subprocess signal).

`report()` and `report_deps()` (the FULL run's `report:` rolls, `test_villages`' immune test, the
cohort) stay in-process for now - the GM's "then we can roll it out".

## R4. What the child costs and what it saves (estimate, measured in R5)

Per `hamlet()` roll: one interpreter start and engine import (~1 s), a pickle of the plan and manifest
through a file (the FULL run already pickles the same payload), and a coverage data file copy. Saved: the
roll's whole working set - the 121 MB the roll ends at, the memo, the retained arenas, the pymalloc
fragmentation - never enters the worker. Expected worker resting level: near its 106 MB collection
baseline for workers whose rolls all came through `hamlet()`.

## R5. Measured after the change

**One roll-heavy file, one worker** (`tests/gate/test_water_junctions.py`, the FULL switch set, cache
bypassed, the same census as R1):

| | before | after |
|---|---|---|
| resting RSS at the end (anonymous) | 242 (214) | 90 (67) |
| `clearance._MEMO`, deep | 46 MB, 53 entries | absent |
| glibc in use / freed-but-retained | 31 / 41 | 18 / 3 |
| live objects | 252,047 | 84,275 |
| the highest per-test peak | 242 | 91 - the roll never entered the worker |
| the file's 7 tests | 73.9 s | 65.6 s (two child interpreters started; two rolls) |

**The full run** (the landing `make done`, the per-test plugin and the cgroup sampler; the container held
3.6 GiB idle at the start, 2.3 GiB of it file cache):

| | after 208 (the R1 profile) | after 210 (the landing gate) |
|---|---|---|
| test phase | 328 s (3,033 tests) | 341 s (3,114 tests; main had grown by 80) |
| container peak | 6,544 MiB (baseline 3,733) | 5,549 MiB (baseline 3,627) |
| Python at the peak | 2,372 MiB | 2,192 MiB |
| worker peak in a test (highest / typical) | 341 / 240-253 | 271 / 168-238 |
| worker resting at the end (range) | 197-266 | 148-213 |
| a `FabricIndex` alive at the end of any worker | every worker | none |

The highest remaining peaks are the in-process rolls the roll-out list names: the cohort test (271, four
rolls in one worker through `generate()`), the immune test (222, `report()`), and the new child-equality
test, which rolls once in-process on purpose. The pool sweep's children (`gate_obtain`, a coverage
subprocess per map) were seen at 550 MB each in the first 210 gate - the next lever after the roll-out,
since worksteal can put several of them on the clock at once.

**Two things the landing taught, recorded at the point of change:** this pytest-cov sets no
`COV_CORE_SOURCE`, so the child's cue is the worker's live `coverage.Coverage` (three lines of `water.py`
lost to the environment signal alone); and a worker rolls several hamlets, so the child's published data
file is named per child, not per worker (one more line lost to the collision).
