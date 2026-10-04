# Research - feature 321

## R1 - A pre-existing red found at the gate: `test_open_questions.py::test_the_real_tree` (2026-10-04)

`make hooks-test` failed on `make open-questions took 15.3 s` (and 10.4 s, 12.0 s on later runs) against the 10 s bound of
feature 285's SC-003. Nothing this feature changes is read by that test; the baseline worktree passed the same run.

Measured on this host (22 logical CPUs, load average 10-17 from other sessions' gates, ~6 GB free):

| when | `_open_questions.py` user CPU | a pure-arithmetic reference (3M squares) |
|---|---|---|
| quieter (load ~10) | 3.0-3.9 s | - |
| loaded (load ~13-17) | 9.4-11.5 s | 0.49-0.55 s |

The test's comment (feature 315) says CPU time is a bound "on the work, which contention does not change". On this host that
does not hold: the run is memory-bound (it scans the 7 MB engine twice per open question, 425 questions), and its CPU time
triples under memory-bandwidth contention while an arithmetic reference does not move - so a calibration against such a
reference cannot normalize it either.

Priced and withdrawn:

- **An index over the engine text** (`CitationIndex`: rule questions out over the deduplicated identifier runs and the
  `?`-lines first). Output byte-identical; cProfile showed `code_citations` 7.9 s -> 2.0 s, but interleaved A/B runs
  without the profiler showed ~10% (3.36/3.94/3.86 s old vs 3.05/3.71 s new, one new run at 6.64 s) - not worth the code.
- **Scaling the bound by a reference loop measured beside it**: the reference does not inflate (table above).

Left for the GM: the target needs ~3.5 s of CPU on a quiet host, a third of its bound, and exceeds the bound only when the
host is saturated. The choices are a faster target (a real index that avoids the substring scans), a looser bound, or
running this one timing assertion outside the parallel gate. The bound is the GM's SC-003, so it is not changed here.
