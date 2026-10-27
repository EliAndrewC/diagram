"""The call-volume survey: which functions are called millions of times, and from which loop (feature 427 T01, D1).

    make perf-fanout [SEED=39] [HOUSEHOLDS="20 40"] [STAGES=all] [HOT=50000] [JOBS=3] [LABEL=adhoc]

WHY (the GM 2026-10-26, `specs/427-call-volume-refactors/request.md` 2): "places where functions are being called just an
absolutely insane number of times, you know, hundreds of thousands or millions of times, even though the maps and things that
we're placing are putting down just a relatively small number of items on the map". A hamlet's time is not one slow function -
a profile sorted by time shows 0.3-0.8 s items - but about 62.8 million Python calls at 40 households, from loops that multiply
(the feature's `research/measurements.md`, observed 2026-10-26). Call counts are exact and deterministic per seed where wall
time drifts with the machine's load, so a chain's count falling is the proof that its multiplier is gone. The survey that found
every hotspot was a hand-run loop of 46 `make perf-profile` calls and a scratch script; this is that script as a tool, its chain
walk kept as the feature's `tooling-perf-fanout.md` records it.

WHAT IT PRINTS, per stage: the Python-level calls at each size and their growth exponent, `log2` of the larger size's calls over
the smaller's; the MULTIPLIER CHAINS - from every non-builtin function
called `HOT` times or more, up the caller edge giving the most calls (a lambda or comprehension reached only through a builtin
steps to the `def` that encloses it), to an ancestor called `ANCHOR` times or fewer, grouped by that anchor - for every stage,
with no floor on its total (SC-001: every chain of 50,000 calls or more); and the fastest growers between the sizes. The report goes to `dev/perf-log/<stamp>-fanout-<label>.txt`, the `.prof` files to gitignored
`dev/perf-raw/` (`perf_profile`). It is a by-hand diagnostic, never a gate: what is watched is the call count `make perf` records
(the feature's User Story 5).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import pstats
import time
from collections import defaultdict
from collections.abc import Mapping
from concurrent.futures import ProcessPoolExecutor
from typing import Any

from l7r.diagram.tools import perf_profile

#: a function called this many times or more starts a chain (the survey of 2026-10-26)
HOT = 50_000
#: a chain stops at an ancestor called this many times or fewer - the loop it hangs from
ANCHOR = 300
#: a function grows "fast" only past this many calls at the larger size
GROWER = 20_000
#: the stage profiles run side by side: a CONVENTION held to the containers' shared 10 GB memory cap (observed 2026-10-26,
#: method: the laptop memory watch's notices read 9.1-9.3 GB in use; five at once held only with the others near 4 GB)
JOBS = 3
ANON = ("<lambda>", "<genexpr>", "<listcomp>", "<dictcomp>", "<setcomp>")

Key = tuple[str, int, str]
Stats = dict[Key, tuple[Any, ...]]


def short(k: Key) -> str:
    """`file:line:name`, the engine's files relative to `l7r/diagram/`; a builtin by its name."""
    fn, ln, name = k
    if fn == "~":
        return name.replace("<built-in method ", "").replace("<method ", "").rstrip(">")[:40]
    fn = fn.split("/l7r/diagram/")[-1] if "/l7r/diagram/" in fn else os.path.basename(fn)
    return f"{fn}:{ln}:{name}"


def enclosing(stats: Stats, k: Key) -> Key | None:
    """The `def` a lambda or comprehension is written in: the nearest named function above it in the same file."""
    fn, ln, _ = k
    best = None
    for f2, l2, n2 in stats:
        if f2 == fn and l2 <= ln and n2 not in ANON and (best is None or l2 > best[1]):
            best = (f2, l2, n2)
    return best


def next_up(stats: Stats, k: Key) -> Key | None:
    """The caller giving `k` the most calls; a lambda reached only through builtins steps to its enclosing `def`."""
    callers = {c: v for c, v in stats[k][4].items() if c in stats}
    if not callers:
        return None
    real = {c: v for c, v in callers.items() if c[0] != "~"}
    if k[2] in ANON and not real:
        return enclosing(stats, k)
    pool = real or callers
    return max(pool, key=lambda c: pool[c][1])


def chain(stats: Stats, k: Key) -> list[tuple[Key, int]]:
    """`k` and its ancestors up the heaviest caller edges, each with its call count, ending at the anchor."""
    out, seen = [(k, stats[k][1])], {k}
    while (c := next_up(stats, k)) is not None and c not in seen:
        seen.add(c)
        out.append((c, stats[c][1]))
        k = c
        if stats[c][1] <= ANCHOR:
            break
    return out


def anchors(stats: Stats, hot: int = HOT) -> dict[Key, list[list[tuple[Key, int]]]]:
    """{anchor: [chain, ...]} for every non-builtin function called `hot` times or more."""
    by: dict[Key, list[list[tuple[Key, int]]]] = defaultdict(list)
    for k, v in stats.items():
        if v[1] >= hot and k[0] != "~":
            ch = chain(stats, k)
            by[ch[-1][0]].append(ch)
    return dict(by)


def total(stats: Stats) -> int:
    return sum(v[1] for v in stats.values())


def exponent(small: int, large: int, ratio: float) -> float:
    """How calls grow with size: log of the call ratio over log of the size ratio (1 is linear, 2 quadratic)."""
    return math.log(large / small) / math.log(ratio) if small and large and ratio > 1 else float("nan")


def growers(small: Stats, large: Stats, top: int = 8) -> list[tuple[float, Key, int, int]]:
    """The functions whose calls grew most between the sizes, of `GROWER` calls or more at the larger."""
    out = [(v[1] / small[k][1], k, small[k][1], v[1]) for k, v in large.items() if v[1] >= GROWER and k in small and small[k][1]]
    return sorted(out, key=lambda r: -r[0])[:top]


def stage_report(stage: str, by_size: dict[int, Stats], hot: int = HOT, placed: Mapping[str, int] | None = None) -> list[str]:
    """One stage's lines: totals and growth, what it placed at the largest size and its calls per thing placed (feature 417
    T57), then its chains by anchor and its fastest growers when it is big enough."""
    sizes = sorted(by_size)
    totals = {n: total(by_size[n]) for n in sizes}
    line = f"{stage}: " + ", ".join(f"{totals[n]:,} calls @{n}" for n in sizes)
    if len(sizes) > 1:
        line += f", growth exponent {exponent(totals[sizes[0]], totals[sizes[-1]], sizes[-1] / sizes[0]):.2f}"
    out = [line]
    if placed is not None:
        things = sum(n for n in placed.values() if n > 0)
        what = ", ".join(f"{k} {n:+,}" for k, n in sorted(placed.items(), key=lambda kv: -abs(kv[1])))
        each = f"; {totals[sizes[-1]] // things:,} calls per thing placed" if things else ""
        out.append(f"  placed @{sizes[-1]}: {what or 'nothing in the manifest'}{each}")
    big = by_size[sizes[-1]]
    small = by_size[sizes[0]]
    for anchor, chains in sorted(anchors(big, hot).items(), key=lambda kv: -max(c[0][1] for c in kv[1])):
        out.append(f"  anchor {short(anchor)} [{big[anchor][1]:,}]")
        for ch in sorted(chains, key=lambda c: -c[0][1]):
            out.append("    " + " <- ".join(f"{short(k)} [{n:,}" + (f"|{small[k][1]:,}" if len(sizes) > 1 and k in small else "") + "]" for k, n in ch))
    if len(sizes) > 1:
        rows = growers(small, big)
        if rows:
            out.append(f"  fastest growers @{sizes[0]} -> @{sizes[-1]}:")
            out += [f"    x{r:.1f} {short(k)} [{a:,} -> {b:,}]" for r, k, a, b in rows]
    return out


def _profile(job: tuple[int, str, int]) -> tuple[int, str, str]:
    """One (size, stage) profile in a worker: (size, stage, the raw .prof path)."""
    seed, stage, households = job
    _table, raw = perf_profile.profile_stage(seed, stage, 1, households)
    return households, stage, raw


def placed_of(raw: str) -> dict[str, int] | None:
    """What the profiled stage placed (`perf_profile`'s `<raw>.placed.json`), or None for a profile written without it."""
    try:
        with open(raw + ".placed.json", encoding="utf-8") as fh:
            return {str(k): int(v) for k, v in json.load(fh).items()}
    except OSError:
        return None


def stage_names() -> list[str]:
    from l7r.diagram.hamletgen.driver import STAGES  # noqa: PLC0415 - the engine, only when the survey runs

    return [st.__name__.replace("stage_", "") for st in STAGES]


def survey(seed: int, sizes: list[int], stages: list[str], jobs: int, hot: int = HOT, pool_cls: Any = ProcessPoolExecutor) -> str:  # noqa: ANN401
    """Profile each (size, stage) pair once, `jobs` at a time (in processes: each stage's roll is its own), and the report."""
    work = [(seed, st, n) for n in sizes for st in stages]
    raws: dict[tuple[int, str], str] = {}
    # ...EACH JOB IN A FRESH PROCESS (feature 417 T57): a worker that rolled the 20-household stage first counted the 40-household
    # homesteads at 4,798,222 calls, a fresh one at 5,204,554 (seed 39, measured 2026-10-27) - caches that outlive a job
    fresh = {"max_tasks_per_child": 1} if pool_cls is ProcessPoolExecutor else {}
    with pool_cls(max_workers=max(1, jobs), **fresh) as pool:
        for households, stage, raw in pool.map(_profile, work):
            raws[(households, stage)] = raw
    lines = [f"perf-fanout seed {seed}, sizes {', '.join(map(str, sizes))}, HOT {hot:,}, ANCHOR {ANCHOR}", ""]
    grand = dict.fromkeys(sizes, 0)
    for stage in stages:
        by_size = {n: pstats.Stats(raws[(n, stage)]).stats for n in sizes}  # type: ignore[attr-defined]
        for n in sizes:
            grand[n] += total(by_size[n])
        lines += stage_report(stage, by_size, hot, placed_of(raws[(sizes[-1], stage)]))
    lines += ["", "all stages: " + ", ".join(f"{grand[n]:,} calls @{n}" for n in sizes)]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--seed", type=int, default=39)
    ap.add_argument("--households", default="20 40")
    ap.add_argument("--stages", default="all")
    ap.add_argument("--hot", type=int, default=HOT)
    ap.add_argument("--jobs", type=int, default=JOBS)
    ap.add_argument("--label", default="adhoc")
    a = ap.parse_args(argv)
    names = stage_names()
    stages = names if a.stages == "all" else [s for s in a.stages.replace(",", " ").split() if s]
    if unknown := [s for s in stages if s not in names]:
        raise SystemExit(f"perf-fanout: no stage {', '.join(unknown)}; the stages are: {', '.join(names)}")
    sizes = sorted({int(n) for n in a.households.replace(",", " ").split()})
    report = survey(a.seed, sizes, stages, a.jobs, a.hot)
    os.makedirs(perf_profile.LOG_DIR, exist_ok=True)
    path = os.path.join(perf_profile.LOG_DIR, f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-fanout-{a.label}.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(report)
    print(f"wrote {os.path.relpath(path, perf_profile.SKILL)}")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.perf_fanout")
    raise SystemExit(main())
