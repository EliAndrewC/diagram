# Research - feature 321

## R1 - A pre-existing red found at the gate: `test_open_questions.py::test_the_real_tree` (2026-10-04)

`make hooks-test` failed on `make open-questions took 15.3 s` (and 10.4 s, 12.0 s on later runs) against the 10 s bound of
feature 285's SC-003 (observed 2026-10-04; method: `/usr/bin/time` user CPU and the test's own `getrusage` on this host). Nothing this feature changes is read by that test; the baseline worktree passed the same run.

Measured on this host (22 logical CPUs, load average 10-17 from other sessions' gates, ~6 GB free) (observed 2026-10-04; method: `/usr/bin/time` user CPU and the test's own `getrusage` on this host):

| when | `_open_questions.py` user CPU | a pure-arithmetic reference (3M squares) |
|---|---|---|
| quieter (load ~10) | 3.0-3.9 s | - (observed 2026-10-04; method: `/usr/bin/time`) |
| loaded (load ~13-17) | 9.4-11.5 s | 0.49-0.55 s |

The test's comment (feature 315) says CPU time is a bound "on the work, which contention does not change". On this host that
does not hold: the run is memory-bound (it scans the 7 MB engine twice per open question, 425 questions), and its CPU time
triples under memory-bandwidth contention while an arithmetic reference does not move - so a calibration against such a
reference cannot normalize it either (observed 2026-10-04; method: `/usr/bin/time` user CPU and the test's own `getrusage` on this host).

Priced and withdrawn:

- **An index over the engine text** (`CitationIndex`: rule questions out over the deduplicated identifier runs and the
  `?`-lines first). Output byte-identical; cProfile showed `code_citations` 7.9 s -> 2.0 s, but interleaved A/B runs
  without the profiler showed ~10% (3.36/3.94/3.86 s old vs 3.05/3.71 s new, one new run at 6.64 s) - not worth the code (observed 2026-10-04; method: `/usr/bin/time` user CPU and the test's own `getrusage` on this host).
- **Scaling the bound by a reference loop measured beside it**: the reference does not inflate (table above).

**Fixed (later the same day): an exact index over the engine's identifier runs** (`cite_all`). The headings are topic
titles now, not questions, so a `?`-line filter never applies; instead every occurrence of an anchor or a heading key holds
the key's longest identifier word, and the files holding that word are found once in the deduplicated runs (316 KB, not
7 MB); `code_citations` makes the exact test on those files only. `outside_guesses` skips a file with no label in one
search. Output byte-identical to the old target; interleaved A/B at the same load: old 8.72 / 6.51 / 6.72 s, new 4.84 /
4.01 / 3.92 s (about 40% less CPU). Tests: `cite_all` equals `code_citations` per question, a quote starting mid-word
included (observed 2026-10-04; method: `/usr/bin/time` user CPU and the test's own `getrusage` on this host).

Left for the GM, superseded by the fix above: the target needs ~3.5 s of CPU on a quiet host, a third of its bound, and exceeds the bound only when the
host is saturated. The choices are a faster target (a real index that avoids the substring scans), a looser bound, or
running this one timing assertion outside the parallel gate. The bound is the GM's SC-003, so it is not changed here (observed 2026-10-04; method: `/usr/bin/time` user CPU and the test's own `getrusage` on this host).
