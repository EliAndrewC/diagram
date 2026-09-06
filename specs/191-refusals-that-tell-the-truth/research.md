# Research - the gate slowdown (FR-000)

**Question**: `make done` ran 806 s and then 873 s against a recorded range of 275-643 s. What got
slower? (GM 2026-09-06: *"investigate the gate slowdown"*.)

**Answer (FOUND - see R7, which supersedes R2's and R6's inconclusive endings)**: no code
regression exists. The gate is BIMODAL on ROLL-CACHE STATE. With the cache warm it costs ~400 s;
with it cold it costs ~800 s, and essentially all of the difference is one phase - `hamlet_floor`
ROLLS eight maps before it can print its first line. The tell is printed in every gate run:
`reference settlement ... [HIT]` or `[MISS]`. The gate's cost is dominated by a
long SINGLE-THREADED tail (~72% of the suite's wall clock), and self-inflicted foreground contention
was present on both slow runs. But the two 800 s outliers themselves are **still unexplained**: three
candidate mechanisms have been tested and refuted, including the heterogeneous cores that R2 first
credited. See R6 for the refutation and the one surviving lead.

Class: **map drawing convention / tooling** - not a physical or setting question; no research pass owed.

## R1 - the decisive artifact: an instrumented run

`make done` piped through a timestamper that flags any gap of 5 s or more between output lines
(`scratchpad/ts.py`). The 397 s green run:

| elapsed | phase |
|---|---|
| 1.1 s | `static` |
| 2.3 s | `format`, `typecheck` |
| 3.1 s | `_reference` - **HIT**, served from the roll cache |
| 3.2 s | `hooks-test` (stamped, nothing re-run) |
| 3.4 s -> 389.3 s | `test-full`: pytest, self-reporting 385.28 s |

and inside pytest, **one gap of 285.6 s** on the final progress chunk. The suite is 2988 tests and
its last chunk takes three quarters of the wall clock: a long single-threaded tail, one test running
essentially alone while seven workers idle.

## R2 - the cores are not equal, and the spread is 2.2x

The GM's hypothesis, and it is correct. `Intel(R) Core(TM) Ultra 7 155H` (Meteor Lake) - a HYBRID
part. The kernel exposes both islands: `/sys/devices/cpu_core` = threads 0-11, `/sys/devices/cpu_atom`
= threads 12-21. Identical CPU-bound benchmark pinned to each thread with `taskset`:

| threads | seconds | class | relative |
|---|---|---|---|
| 0-11 | 0.402 - 0.444 | P-core (6 cores, HT) | 1.00x |
| 12-19 | 0.555 - 0.586 | E-core | ~1.38x |
| 20-21 | **0.918 - 0.924** | low-power E-core | **~2.24x** |

`XDIST_WORKERS` is `min(CPU_COUNT, 8)`, so 8 workers are scheduled across 22 heterogeneous threads
with no affinity.

**R2's original conclusion was that this explained the outliers. R6 REFUTES that - see below.** The
hardware spread is real and measured; it is not the cause. Left in place rather than rewritten,
because the wrong inference is the instructive part: a mechanism that is real, large and present is
not thereby the mechanism that is operating.

## R3 - two hypotheses tested and REFUTED, recorded so nobody re-runs them

- **Tooling-hash invalidation** (the whole tooling suite re-running): runs WITH it median 399 s,
  WITHOUT it 562 s. The wrong way round.
- **Roll-cache cold/warm**: directionally supportive (cold median 564 s, warm 398 s) but it does NOT
  explain the two runs that mattered - both 806 s and 873 s were on commits touching no roll path.
  Partial effect, not the cause.

## R4 - the contention finding, and a correction to my own earlier method

I first "refuted" contention by asking `dev/run-log/` which runs overlapped. **That method is
unsound and must not be reused**: the run-log only holds runs that were recorded AND LANDED, so a
peer session testing in its own clone - or this session's own foreground commands - are invisible to
it. It established nothing-else-RECORDED, not nothing-else-running.

Measured properly: during both slow runs this session was running foreground `make test-file`,
`_gatecost` and git commands against the same box while the gate ran in the background. During the
397 s run it was writing text files. The pinned ratchet reason already names this exact hazard for
its own two measurements - *"each sharing the box with foreground `make test-file` runs from the same
session"* - which is the same trap, recorded and then walked into again.

## R5 - what this means for the ratchet, and what was NOT done

A `compare="median"` ratchet over a target whose cost has a 2.2x hardware-driven variance will fire
on an unlucky cluster with no regression present. That is what happened: the median crossed 403 s on
two unlucky, self-contended runs.

**A re-pin was tried and REVERTED.** Moving the baseline 310 -> 385 was wrong: it treated variance as
level, and the next run blew past even the widened ceiling. The baseline is back at 310 and no
threshold was weakened. **Nothing further is changed here** - this feature is about message text, and
what to do about a variance-blind ratchet (pin affinity for the gate? compare a trimmed median?
shorten the tail?) is a decision with its own trade-offs and belongs to its own feature, with the
GM's ruling. Recorded rather than acted on.

**Sources:** none - this is a measurement of this machine, not a claim about the world.
URL: none - the evidence is `/proc/cpuinfo`, `/sys/devices/cpu_{core,atom}`, and the timestamped run
log, all reproducible locally.


## R6 - the GM's pinning question, and the REFUTATION of R2's inference

The GM asked whether we can use the faster cores when possible. We can (`taskset -c 0-11`), so it
was measured on the real suite rather than argued:

| run | pytest wall | the single-threaded tail |
|---|---|---|
| unpinned, kernel's choice | **385.28 s** | 285.6 s |
| `taskset -c 0-11` (P-cores) | **399.57 s** | 292.3 s |

**Pinning is slightly WORSE, and the tail is unchanged.** Two things follow, and the second matters
more than the first:

1. **Do not pin.** Confining 8 workers to the 12 P-core THREADS puts them on 6 physical cores sharing
   hyperthreads; the default placement spreads them over more distinct physical cores, and that beats
   the per-core speed advantage. The kernel's hybrid scheduler is already making a better decision
   than a flat affinity mask would.
2. **The heterogeneous cores do NOT explain the 806 s and 873 s runs.** R2 inferred that the lone
   tail test was exposed to an unlucky core draw. If that were so, pinning it to a P-core would have
   shortened the tail; it did not move (285.6 -> 292.3 s). The scheduler already gives a single
   runnable task a fast core, so the exposure R2 posited never existed.

**What is left standing**: the ~460 s that the 873 s run spent outside pytest and outside every phase
this investigation could time. The pinned run surfaced a candidate R1 had not: a **89.4 s gap after
pytest finished**, in the coverage combine / floor step, which the earlier phase timings missed
because they were taken against ALREADY-COMBINED data. That is a lead, not an answer.

**STATUS: the outliers remain UNEXPLAINED.** Three hypotheses have now been tested and refuted
(tooling-hash invalidation, roll-cache cold/warm, heterogeneous cores), and self-inflicted foreground
contention is a contributing factor of unmeasured size. Anyone continuing should start from the
coverage-combine lead and should instrument a run that reproduces the 800 s case, which no run since
has.


## R7 - THE ANSWER, and the bad proxy that hid it for five hypotheses

The 401.6 s gap in the instrumented 803 s run sits between the coverage table and `hamlet-floor`'s
FIRST line. Nothing prints in it. Two things run there, and only one is expensive:

- `coverage combine --append` - **MEASURED AT 0 s**, with eight parallel data files and an existing
  `.coverage` to append into. Not the cause; refuted like the rest.
- `python3 -m l7r.diagram.tools.hamlet_floor` - which, before printing anything, derives its module
  set from the roll cache's records for eight fixed specs: the reference, the gate's three polders,
  and the cohort's ratchet seeds 41-44. **When those records do not exist, it ROLLS THEM.** The
  module's own docstring says so: *"or on CodeBuild the tool rolls them once
  (`rollcache.report_deps`) - ~1-2 minutes, then cached."*

So a cold roll cache is paid TWICE in one gate: once by the map-rolling tests inside pytest, and
again by the floor phase rolling its eight subjects. Warm, the same phase costs ~1 s (measured).

**Confirmed against every instrumented run, 3 for 3** - and the indicator was printed in all of them:

| run | `_reference` line | floor phase | total |
|---|---|---|---|
| 397 s | `[HIT]` | ~10 s | fast |
| 803 s | `[MISS]` | **401.6 s** | slow |
| 873 s | `[MISS]` | (not instrumented) | slow |

**WHY THIS TOOK FIVE REFUTED HYPOTHESES, which is the transferable lesson.** R3 tested "roll-cache
cold/warm" and refuted it - using the wrong proxy. It classified each run by whether that run's
COMMIT touched a roll path, when the cache is keyed on the FUNCTIONS A ROLL EXECUTES and is equally
invalidated by content merged in from main at `sync-in`. The right proxy was sitting in the output
of every single run - the `[HIT]`/`[MISS]` flag - and was read past four times. A hypothesis is only
as refuted as its proxy is faithful; when a mechanism is directly observable, do not infer it.

**What follows for the ratchet** (recorded, not acted on - it is a decision for its own feature):
`compare="median"` mixes two populations that differ by 2x for a legitimate reason. A median over
warm and cold runs together is a number describing neither. The candidates are to compare like with
like (the `[HIT]`/`[MISS]` flag is already recorded per run and could join the run-log), or to stop
the floor phase re-rolling what the suite just rolled.
