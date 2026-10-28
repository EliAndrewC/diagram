"""Where a module's time is, stage by stage - its share of each stage and its callers (feature 438).

`make perf-share [MODULE=<path>] [STAGES=<a,b>] [SEED=25] [HOUSEHOLDS=40] [PROFILES=<files>]` reads each stage's KEPT raw
profile - the files `PROFILES` names, else the newest `dev/perf-raw/*-seed<S>-hh<H>-<stage>.prof` (`make perf-profile` writes
them) - and profiles a stage only where none is kept, saying so. From each profile it reads:

- the stage's profiled total, the module's own (self) time in it, and that share;
- the stage's largest self-time functions - whether the time has a hotspot at all;
- the callers of the module's functions, ranked by the module's time under each.

WHY (feature 437, `specs/437-array-geometry-trial/research/share.md`): the array geometry trial had to read where the shared
geometry's time was before choosing what to change, and did it with two ad-hoc scripts over the raw profiles; the reading
found the module held 3.5% of the four largest stages' time, which decided the trial. This is that reading, as a command.

cProfile inflates call-dense Python most, so a module of small hot functions reads larger here than it is unprofiled. It
gates nothing.
"""

from __future__ import annotations

import argparse
import collections
import glob
import os
import pstats
from collections.abc import Callable, Sequence

from l7r.diagram.tools import perf_profile

MODULE = "l7r/diagram/settlement/_geom/primitives.py"
STAGES = ("homesteads", "web", "field", "hinterland")
"""Research: plumbing - NONE: the four stages feature 437 read, the largest by time share at the 435-start bookend"""
TOP = 8
"""Research: plumbing - NONE: how many rows each list prints, deciding nothing about a place"""


def short(fn: str, ln: int, name: str) -> str:
    """A function's place, from the package down."""
    return f"{fn.split('l7r/diagram/')[-1]}:{ln}({name})"


def share(path: str, module: str, top: int = TOP) -> list[str]:
    """One stage's reading of its raw profile at `path`: the total, the module's self time and share, the largest self
    times, and the module's callers by the module's time under them."""
    st = pstats.Stats(path)
    stats = st.stats  # type: ignore[attr-defined]
    total = float(st.total_tt)  # type: ignore[attr-defined]
    mine = sum(v[2] for (fn, _ln, _name), v in stats.items() if fn.endswith(module))
    lines = [f"  profiled {total:.2f} s; {module} self {mine:.3f} s ({100 * mine / total if total else 0:.1f}%)", "  largest self time in the stage:"]
    for t, where in sorted(((v[2], short(*k)) for k, v in stats.items()), reverse=True)[:top]:
        lines.append(f"    {t:7.3f} s  {where}")
    under: collections.Counter[tuple[str, str]] = collections.Counter()
    calls: collections.Counter[tuple[str, str]] = collections.Counter()
    for (fn, _ln, name), v in stats.items():
        if not fn.endswith(module):
            continue
        for caller, cv in v[4].items():
            if caller[0].endswith(module):
                continue  # the module calling itself: its time is counted under the outside caller that reached it
            k = (name, short(*caller))
            under[k] += cv[3]
            calls[k] += cv[0]
    lines.append(f"  callers of {module.rsplit('/', 1)[-1]}, by its time under them (cumulative):")
    for (name, where), t in under.most_common(top):
        lines.append(f"    {t:7.3f} s  {calls[(name, where)]:>9,} calls  {name:<18} from {where}")
    if not under:
        lines.append("    none")
    return lines


def kept(stage: str, seed: int, households: int, named: Sequence[str], raw_dir: str | None = None) -> str | None:
    """The kept raw profile of `stage`: the named file for it (by its `-<stage>.prof` suffix), else the newest of this seed and
    size; None where neither is kept. A profile whose name holds no size (before feature 438) is read only when named.
    `raw_dir` defaults to `perf_profile.RAW_DIR` as it stands at the call (a default bound at definition kept the real
    `dev/perf-raw` under a test's patch, so the test failed on any clone holding kept profiles - feature 443)."""
    for path in named:
        if path.endswith(f"-{stage}.prof"):
            return path
    found = sorted(glob.glob(os.path.join(perf_profile.RAW_DIR if raw_dir is None else raw_dir, f"*-seed{seed}-hh{households}-{stage}.prof")))
    return found[-1] if found else None


def main(argv: list[str] | None = None, profile: Callable[..., tuple[str, str]] = perf_profile.profile_stage) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--module", default=MODULE, help=f"the module's path (default {MODULE})")
    ap.add_argument("--stages", default=",".join(STAGES), help="comma-separated stages (default the four feature 437 read)")
    ap.add_argument("--seed", type=int, default=25)
    ap.add_argument("--households", type=int, default=40)
    ap.add_argument("--profiles", default="", help="comma-separated kept raw profiles to read (each matched to its stage by name)")
    a = ap.parse_args(argv)
    stages: Sequence[str] = [s for s in a.stages.split(",") if s.strip()]
    totals: list[tuple[float, float]] = []
    for stage in stages:
        raw = kept(stage, a.seed, a.households, [p for p in a.profiles.split(",") if p.strip()])
        print(f"{stage} (seed {a.seed}, {a.households} households): {os.path.basename(raw) if raw else 'no kept profile - profiling it now'}")
        if raw is None:
            try:
                _table, raw = profile(a.seed, stage, 25, a.households)
            except Exception as err:  # a roll refused before the stage: named, and the next stage read
                print(f"  not profiled - {type(err).__name__}: {err}")
                continue
        print("\n".join(share(raw, a.module)))
        st = pstats.Stats(raw)
        totals.append((sum(v[2] for (fn, _l, _n), v in st.stats.items() if fn.endswith(a.module)), float(st.total_tt)))  # type: ignore[attr-defined]
    mine, total = sum(t[0] for t in totals), sum(t[1] for t in totals)
    print(
        f"\n{a.module}: {mine:.3f} s of {total:.2f} s profiled across {len(totals)} stage(s) ({100 * mine / total if total else 0:.1f}%) - cProfile inflates call-dense code most; read it as an upper bound"
    )
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.perf_share")
    raise SystemExit(main())
