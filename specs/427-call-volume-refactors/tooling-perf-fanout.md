# Tooling: `make perf-fanout`, the call-volume survey as a target

**Load this file when:** you build the target, the first task of this feature.

## Why

Wall time drifts with machine load; call counts do not. They are exact and deterministic per seed. The survey that
found every hotspot in `research/` was a hand-run loop of 46 `make perf-profile` calls plus a scratch script. As a target,
it can:

1. show after each refactor whether a chain's count fell, which is the proof that the multiplier is gone, independent of
   load;
2. show whether a chain came back later;
3. find the next ones without a session rebuilding the script.

## What it does

`make perf-fanout [SEED=39] [HOUSEHOLDS="20 40"] [STAGES=all] [HOT=50000]`:

1. For each household count and stage, profile that stage once. Reuse `tools/perf_profile.py`'s `profile_stage`, which
   already runs the stages before it unprofiled and dumps the `.prof`. Run the (stage, size) pairs in parallel across
   worker processes, bounded by the host memory cap: five at a time held on 2026-10-26, with the containers near their
   shared 10 GB cap.
2. Print, per stage: total Python-level calls at each size, and the growth exponent `log2(calls@40 / calls@20)`.
3. For each stage over a floor (300k calls at the larger size), print the **multiplier chains**:
   - Start from every NON-builtin function called `HOT` times or more.
   - Walk up the caller edge that contributes the most calls.
   - When a lambda or generator expression is reached only through a builtin (`min`, `sorted`, `any`), step to the function
     that defines it: the nearest `def` above it in the same file.
   - Stop at an ancestor called 300 times or fewer (the anchor).
   - Group chains by anchor; print each level as `file:line:name [calls@40|@20 calls@20]`.
4. Print, per stage, the fastest growers between the two sizes (functions with 20k+ calls at the larger size).
5. Write the report to `dev/perf-log/<stamp>-fanout-<label>.txt`, committed like the snapshots. The `.prof` files stay in
   gitignored `dev/perf-raw/`.

## Reference implementation of the analysis

This is the survey script as run on 2026-10-26. The chain walk is the part worth keeping exactly; its output is
`research/fanout-2026-10-26.txt`. It reads `pstats` data only, so as a tool module it needs no engine import.

```python
import math, os, pstats
from collections import defaultdict

HOT, ANCHOR = 50_000, 300
ANON = ("<lambda>", "<genexpr>", "<listcomp>", "<dictcomp>", "<setcomp>")

def short(k):
    fn, ln, name = k
    if fn == "~":
        return name.replace("<built-in method ", "").replace("<method ", "").rstrip(">")[:40]
    fn = fn.split("/l7r/diagram/")[-1] if "/l7r/diagram/" in fn else os.path.basename(fn)
    return f"{fn}:{ln}:{name}"

def enclosing(stats, k):  # the def a lambda / comprehension is written in
    fn, ln, _ = k
    best = None
    for f2, l2, n2 in stats:
        if f2 == fn and l2 <= ln and n2 not in ANON and (best is None or l2 > best[1]):
            best = (f2, l2, n2)
    return best

def next_up(stats, k):
    callers = {c: v for c, v in stats[k][4].items() if c in stats}
    if not callers:
        return None
    real = {c: v for c, v in callers.items() if c[0] != "~"}
    if k[2] in ANON and not real:
        return enclosing(stats, k)
    pool = real or callers
    return max(pool, key=lambda c: pool[c][1])

def chain(stats, k):
    out, seen = [(k, stats[k][1])], {k}
    while (c := next_up(stats, k)) is not None and c not in seen:
        seen.add(c); out.append((c, stats[c][1])); k = c
        if stats[c][1] <= ANCHOR:
            break
    return out

def anchors(stats):  # {anchor: [chain, ...]} for every hot non-builtin function
    by = defaultdict(list)
    for k, v in stats.items():
        if v[1] >= HOT and k[0] != "~":
            ch = chain(stats, k)
            by[ch[-1][0]].append(ch)
    return by
# totals: sum(v[1] for v in stats.values()); exponent: math.log2(calls40 / calls20)
```

## The project's rules it must meet

- A new tool owes 100% coverage the day it lands (`l7r/diagram/tools/CLAUDE.md`). Test the analysis on a synthetic
  `pstats` dict, and stub the profiling seam as `perf_profile`'s own tests do.
- A `##` help line in the Makefile; a row in `tools/CLAUDE.md`'s table ("Which functions are called millions of times,
  and from which loop?").
- It is a by-hand diagnostic, never a gate (performance is a flag, feature 375 amendment 5).
- It lands as tooling (`make land-tooling`), separate from any engine change.

## A possible refinement (for the GM to decide)

Call counts are noise-free, so `make perf` could record a stage's total calls beside its seconds. `make perf-report` would
then show the call trend, and a call-count jump would be a FLAG at landing, as the time band is now. A multiplier that comes
back would show up as a number, not hidden in load noise.
