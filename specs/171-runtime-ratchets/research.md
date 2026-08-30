# Feature 171 - research: how a 4x gate slowdown went unnoticed

Measured by the `diagram-testing` session on 2026-08-30, before the feature was opened. Everything here
is a measurement or a direct code reading; nothing is inferred.

## R1. THE GM WAS NOT MISREMEMBERING - the guard exists, and it covers one target

Three time-based guards exist in this repository. Two watch the GENERATOR and one watches the QUICK loop.
None watches the gate.

| guard | where | what it measures | does it fail? |
|---|---|---|---|
| `QUICK_BUDGET = 60` | `Makefile` (the `quick` recipe) | `make quick` WALL TIME | **yes** - `exit 1`, and prints "Something slow is running that should not be. Find it: `make durations`" |
| `GEN_TIME_BUDGETS` | `tests/test_villages.py` | per-map GENERATION time | yes, per map, with `DIAGRAM_ALLOW_SLOW_GENS=1` as the escape |
| `perf_snapshot` / `perf_bands` / `make perf-gate` | `l7r/diagram/tools/` | the reference hamlet across seeds - the GENERATOR | yes, banded, with a whole review ladder behind it |

The `perf_snapshot` docstring names the incident it was built for, in the GM's words: *"we often will end
up degrading performance without even realizing it"* - feature 126 moved the lane skeleton after the
houses and took one seed from 65 s to 160 s. So the concern the GM remembered is real and IS guarded;
it is guarded for map generation, not for the test suite.

## R2. `make done`'s duration has ALWAYS been recorded, and nothing has ever asserted on it

Every gate run writes `dev/run-log/<ts>-<pid>.json`:

    {"utc": "...", "target": "done", "scope": "reference", "seconds": 148, "result": "green", "commit": "..."}

`make audit` prints that history, so the data is VISIBLE - but only to someone who runs `make audit` and
reads it. Nothing compares one run against another.

**The near miss.** Feature 162 added `scripts/_gatecost.py` with `median_seconds(target, scope)` so guard
messages could quote the real cost instead of a stale hand-typed number (the motivating defect: a guard
message claimed the gate cost ~70 s while the log's median was 111 s). That function computes EXACTLY the
median that exposes this regression. It only `print`s it.

## R3. The numbers, re-derived independently

The relayed report started one day too late, which changes the framing materially. Green `make done` runs
only (`already-verified` short-circuits excluded, since they measure nothing):

| day | n | median | min | max |
|---|---|---|---|---|
| 2026-08-24 | 8 | **316 s** | 279 | 412 |
| 2026-08-25 | 16 | **301 s** | 294 | 338 |
| 2026-08-26 | 20 | **43 s** | 33 | 337 |
| 2026-08-27 | 22 | **35 s** | 32 | 138 |
| 2026-08-28 | 50 | **68 s** | 16 | 1470 |
| 2026-08-29 | 59 | **111 s** | 10 | 324 |
| 2026-08-30 | 19 | **135 s** | 25 | 334 |

**The gate is still 2.3x FASTER than it was five days ago.** What has happened is that a 7x win landed on
08-26 and has since been given back to about 2x. That is a real regression and worth chasing - but it is
"we are losing an optimization" rather than "the gate is the slowest it has ever been", and it explains
why nobody flinched: every day still felt better than the week before.

> **NOTE, added after the spec review.** The sentence below argues for a bar that "follows the best-known
> value". **The SPEC DECLINED that mechanism**: FR-003 pins the baseline and moves it only by a committed
> edit, because a baseline that follows automatically follows a degradation UPWARD as readily as downward -
> which is exactly the shape R4 describes. Read this as the argument against a FIXED CONSTANT, which it
> is, not as advocacy for a self-updating one. Where the two differ, the spec is the authority.

**This is the argument for a RATCHET rather than a fixed ceiling.** A constant chosen on 08-24 would have
been ~350 s and would still be passing today at 135 s, silently, while the gate got 4x worse than its own
best. Only a bar that follows the best-known value catches this shape.

## R4. Why it happened, structurally

Every time guard here was built REACTIVELY, to fence off the thing that had just burned somebody: the
quick loop after it hit 254 s, map generation after feature 126's 65 s -> 160 s seed, per-map budgets
after a gen went quadratic. The gate's own wall time never burned anyone LOUDLY - each individual
increase was small, and the short-circuit means many runs return in seconds, so no single run ever looks
wrong. A regression that arrives in twenty small pieces, in a number nobody asserts on, is invisible by
construction.

## R5. The same blind spot exists one target over

`QUICK_BUDGET` is an ABSOLUTE CEILING (60 s), not a ratchet. `make quick` currently runs about 11 s, so it
could drift to 59 s - a 5x regression - and never fail. This is why the GM asked for the limit to be
tightened rather than merely for the gate to be covered.

## R6. What a ratchet has to cope with here (design constraints, not requirements)

Read off the existing machinery, for whoever implements this:

- **The gate short-circuits.** `already verified` returns in seconds and records `result: already-verified`,
  not `green`. A ratchet must judge only runs that actually did the work, exactly as R3's table does.
- **Scope changes the workload legitimately.** `dev/run-log/` records `scope` (`reference` / `full`), and
  the 08-27 scope unlock is a real part of the 35 -> 68 step. A ratchet must compare like with like.
- **The box is shared.** Several sessions run gates at once (the 1470 s maximum on 08-28 is one). A
  median-of-recent, not a single run, is what survives that - which is what `_gatecost.py` already does.
- **`make done` has a cold path.** A merge from main re-keys the roll cache and the next gate is legitimately
  slower. Whatever the mechanism, a session must be able to record WHY a bar moved, the way the perf
  ladder already makes a session explain an increase.
