#!/usr/bin/env python3
"""THE OVERLAP CENSUS: how many things each check of a roll compares against, per call - and which compare against too many.

    python3 -m l7r.diagram.tools.overlap_census                     # the pool's hamlets and the reference at 40 households
    python3 -m l7r.diagram.tools.overlap_census --gens a.gen.py --households 0

WHY THIS EXISTS (the GM, 2026-10-02, feature 306): *"We should just make sure in general that anytime we are doing overlap
checks with more than a certain number of other things, it means that we have not correctly drawn a bounding box or a
segmented line to stay on the right side of"* - the shape the scrub's blades and the marsh's reeds once had, tens of thousands
of checks against things no box held. Its first run flagged nine checks from 5,048 to 111,700 comparisons a call; each was
given its index (specs/306-seat-by-packing/research.md R10, R13).

WHAT A COMPARISON IS: one call of a pairwise geometry measure - `settlement/_geom/primitives.py`'s (`point_in_poly`,
`seg_dist`, `segments_cross`, ...), `_geom/overlap.py`'s public predicates, or a shapely geometry's binary predicates and
`distance` - counted at the OUTERMOST such call (a measure inside a measure is one comparison). It is charged to the nearest
NAMED function outside `settlement/_geom/` and shapely (a comprehension or lambda is its function's), whose calls are counted
from its first comparison on: `sys.monitoring` arms the primitives' code objects at the start and each charged function's
once it is first charged, so nothing else in the roll pays the hook. A check's comparisons over its calls is what it measures.

WHAT IT DOES NOT SEE: comparisons in C (a numpy raster test, shapely's own vectorized functions on arrays) - those are the
boxes and rasters this rule asks for, not the scans it is after.

`CENSUS_FLAG` is the knee of the first run's distribution (research R10: nine checks over 5,000, the next at 3,859, the bulk
under 1,500). `make census` runs it; `make perf` runs it after its snapshot, so a new scan of this shape shows when it lands.
It REPORTS; it refuses nothing.
"""

from __future__ import annotations

import argparse
import collections
import glob
import io
import os
import sys
from collections.abc import Callable, Iterable, Sequence
from contextlib import redirect_stdout
from types import CodeType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if SKILL not in sys.path:
    sys.path.insert(0, SKILL)

#: Comparisons per call over which a check is flagged (research R10's knee).
CENSUS_FLAG = 5000

#: The reference spec the census rolls at a village's size beside the pool (feature 304's scaling leg's largest).
REFERENCE_HOUSEHOLDS = 40

#: Where a frame is the measure's own, not a check's: the geometry package and shapely.
_INSIDE = (os.sep + os.path.join("settlement", "_geom") + os.sep, os.sep + "shapely" + os.sep)
_ANON = ("<genexpr>", "<lambda>", "<listcomp>", "<dictcomp>", "<setcomp>")
_SHAPELY = ("intersects", "distance", "contains", "within", "touches", "crosses", "overlaps", "covers", "covered_by", "disjoint", "dwithin")
_PRIMITIVES = ("point_in_poly", "seg_closest", "seg_dist", "segments_cross", "seg_intersect", "poly_seg_dist", "edge_dist", "ring_touches", "ring_meets_ellipse")


def primitives() -> list[Callable[..., Any]]:
    """Every measure a comparison is a call of (see the module docstring)."""
    from shapely.geometry.base import BaseGeometry

    from l7r.diagram.settlement._geom import overlap, primitives as prim

    out: list[Callable[..., Any]] = [getattr(prim, n) for n in _PRIMITIVES]
    out += [f for n, f in vars(overlap).items() if callable(f) and not n.startswith("_") and getattr(f, "__module__", "") == overlap.__name__ and hasattr(f, "__code__")]
    out += [getattr(BaseGeometry, n) for n in _SHAPELY if hasattr(BaseGeometry, n)]
    return out


def inside(filename: str) -> bool:
    """Is a frame of this file a measure's own (the geometry package, shapely)?"""
    return any(k in filename for k in _INSIDE)


class Census:
    """`sys.monitoring` armed on the measures for the length of a `with`; `stage` labels what is rolled now."""

    def __init__(self) -> None:
        self.comparisons: collections.Counter[tuple[str, CodeType]] = collections.Counter()
        self.calls: collections.Counter[tuple[str, CodeType]] = collections.Counter()
        self.stage = "?"
        self._measures: set[CodeType] = {f.__code__ for f in primitives()}
        self._armed: set[CodeType] = set()
        self._mon = sys.monitoring
        self._tool = self._mon.PROFILER_ID

    def __enter__(self) -> Census:
        self._mon.use_tool_id(self._tool, "overlap-census")
        self._mon.register_callback(self._tool, self._mon.events.PY_START, self._start)
        for code in self._measures:
            self._mon.set_local_events(self._tool, code, self._mon.events.PY_START)
        return self

    def __exit__(self, *exc: object) -> None:
        for code in self._measures | self._armed:
            self._mon.set_local_events(self._tool, code, 0)
        self._mon.register_callback(self._tool, self._mon.events.PY_START, None)
        self._mon.free_tool_id(self._tool)

    def _start(self, code: CodeType, _offset: int) -> None:
        if code in self._armed:
            self.calls[(self.stage, code)] += 1
            return
        self.charge(sys._getframe(1))

    def charge(self, frame: Any) -> None:
        """A measure's frame began: charge it to its check - unless a measure called it (then it is part of one)."""
        if frame.f_back is None or inside(frame.f_back.f_code.co_filename):
            return
        g = frame.f_back
        while g is not None and (inside(g.f_code.co_filename) or g.f_code.co_name in _ANON):
            g = g.f_back
        if g is None:
            return
        code = g.f_code
        self.comparisons[(self.stage, code)] += 1
        if code not in self._armed and code not in self._measures:
            self._armed.add(code)
            self.calls[(self.stage, code)] += 1  # the call under way
            self._mon.set_local_events(self._tool, code, self._mon.events.PY_START)

    def rows(self) -> list[tuple[float, str, str, int, int]]:
        """Per check, most comparisons a call first: (per call, its first stage, `module:function`, calls, comparisons)."""
        by: dict[CodeType, list[Any]] = {}
        for (stage, code), n in self.comparisons.items():
            row = by.setdefault(code, [stage, 0, 0])
            row[2] += n
        for (_stage, code), n in self.calls.items():
            if code in by:
                by[code][1] += n
        out = [(tot / max(1, calls), stage, name_of(code), calls, tot) for code, (stage, calls, tot) in by.items()]
        return sorted(out, key=lambda r: (-r[0], r[2]))


def name_of(code: CodeType) -> str:
    """`package/module.py:function`, relative to the engine."""
    tail = code.co_filename.split(os.sep + os.path.join("l7r", "diagram") + os.sep)[-1]
    return f"{tail}:{code.co_name}"


def spec_of(gen: str) -> Any:
    """The spec a pool gen hands `generate`, caught before it rolls."""
    import l7r.diagram.hamletgen as hg

    class Caught(Exception):
        pass

    def catch(spec: Any, **_kw: Any) -> Any:
        raise Caught(spec)

    keep = hg.generate
    hg.generate = catch
    try:
        with open(gen, encoding="utf-8") as fh:
            exec(compile(fh.read(), gen, "exec"), {"__file__": gen, "__name__": "gen"})  # noqa: S102 - a pool gen, run to read its spec
    except Caught as e:
        return e.args[0]
    finally:
        hg.generate = keep
    raise SystemExit(f"{gen} handed generate no spec")


def roll(spec: Any, census: Census) -> None:
    """Every stage of the spec's roll, each labeled on the census (the perf tool's loop)."""
    from l7r.diagram.hamletgen import plan_site
    from l7r.diagram.hamletgen.driver import STAGES, roll_scope
    from l7r.diagram.hamletgen.plan import beyond_the_band
    from l7r.diagram.settlement import Settlement

    with beyond_the_band():
        plan = plan_site(spec)
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    with roll_scope(plan.spec):
        for st in STAGES:
            census.stage = st.__name__.replace("stage_", "")
            with redirect_stdout(io.StringIO()):
                st(s, plan)


def specs(gens: Iterable[str], households: int) -> list[Any]:
    """The pool gens' specs, and the reference at `households` (none where 0)."""
    from l7r.diagram.hamletgen import HamletSpec
    from l7r.diagram.hamletgen.plan import beyond_the_band
    from l7r.diagram.tools.perf_snapshot import REFERENCE

    out = [spec_of(g) for g in gens]
    if households:
        with beyond_the_band():
            out.append(HamletSpec(seed=4, **{**REFERENCE, "households": households}))
    return out


def report(rows: Sequence[tuple[float, str, str, int, int]], flag: int, top: int) -> str:
    """The flagged checks, then the next ones down."""
    flagged = [r for r in rows if r[0] > flag]
    lines = [f"overlap census: {len(flagged)} check(s) over {flag:,} comparisons a call (feature 306)"]
    lines.append(f"{'per call':>10}  {'stage':14} {'check':64} {'calls':>7} {'comparisons':>12}")
    for per, stage, name, calls, tot in rows[: max(top, len(flagged))]:
        lines.append(f"{per:10.1f}  {stage:14} {name:64} {calls:7} {tot:12}{'  <-- FLAGGED' if per > flag else ''}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gens", nargs="*", default=None, help="pool gens to roll (default: every pool hamlet)")
    ap.add_argument("--households", type=int, default=REFERENCE_HOUSEHOLDS, help="the reference spec's size beside them (0: none)")
    ap.add_argument("--top", type=int, default=15, help="rows to show below the flagged ones")
    a = ap.parse_args(argv)
    gens = a.gens if a.gens is not None else sorted(glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.gen.py")))
    refused: list[str] = []
    with Census() as census:
        for spec in specs(gens, a.households):
            try:
                roll(spec, census)
            except (ValueError, RuntimeError) as e:  # the generator's refusals: counted up to where it stopped, and said
                refused.append(f"{getattr(spec, 'name', spec)}: {type(e).__name__}: {str(e)[:160]}")
    print(report(census.rows(), CENSUS_FLAG, a.top))
    for line in refused:
        print(f"refused (its checks counted up to the refusal): {line}")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.tools.overlap_census")
    raise SystemExit(main())
