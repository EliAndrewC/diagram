"""Feature 297's harness (284's, with this feature's buckets): per pool hamlet, the stage times (unprofiled) and one profiled FULL regeneration.

    make spec-harness SPEC=specs/297-placement-by-construction OUT=<dir>

Run as a test node (the engine refuses in-process calls outside make). Per hamlet: the faster of two unprofiled rolls
with every stage timed (render off - the placement cost alone), one unprofiled full regeneration into a scratch directory
(the svg, png and interactive page - what `make map` costs), and that same full regeneration under cProfile, saved as
`<dir>/<hamlet>.prof` so the hotspots are read from the profile rather than guessed. Seconds move with the host's load;
the profile's call counts do not.
"""

from __future__ import annotations

import cProfile
import json
import os
import re
import tempfile
import time
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/h297")

MAPS = ("inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada")


def _spec_kwargs(key: str) -> dict:
    """The pool generator's own literal HamletSpec arguments - every map read from its gen, so the harness rolls exactly
    what `make map` rolls (284's table had drifted from Inashiro's gen: no settlement_form, no shrine)."""
    here = Path(__file__).resolve()
    skill = next(p for p in [here.parent, *here.parents] if (p / "Makefile").exists() and (p / "pool").exists())
    text = (skill / "pool" / "hamlets" / key / f"{key}.gen.py").read_text()
    m = re.search(r"HamletSpec\((.*?)\)\s*,\s*out_base", text, re.S)
    assert m, f"{key}'s spec"
    return eval(f"dict({m.group(1)})")  # noqa: S307 - our own committed generator's literal arguments


def _stage_times(spec) -> dict:
    from l7r.diagram.hamletgen import driver, generate

    acc: dict[str, float] = {}
    before = driver.STAGES

    def timed(fn):
        def run(*a, **k):
            t = time.perf_counter()
            try:
                return fn(*a, **k)
            finally:
                acc[fn.__name__] = acc.get(fn.__name__, 0.0) + time.perf_counter() - t

        run.__name__ = fn.__name__
        return run

    driver.STAGES = tuple(timed(f) for f in before)
    try:
        t = time.perf_counter()
        generate(spec, render=False)
        total = time.perf_counter() - t
    finally:
        driver.STAGES = before
    return {"roll_s": round(total, 3), "stages": {k: round(v, 3) for k, v in sorted(acc.items(), key=lambda kv: -kv[1])}}


def _full(spec, key: str, profile: bool) -> float:
    from l7r.diagram.hamletgen import generate

    with tempfile.TemporaryDirectory() as d:
        pr = cProfile.Profile() if profile else None
        t = time.perf_counter()
        if pr:
            pr.enable()
        generate(spec, out_base=str(Path(d) / key))
        if pr:
            pr.disable()
            pr.dump_stats(str(OUT / f"{key}.prof"))
        return round(time.perf_counter() - t, 3)


# THE ENTRY BUCKETS (plan C). A count credited to a primitive's DIRECT caller reads zero once a change moves the call under
# a new caller (an index's method, a new builder), whatever the new code costs. So every call made anywhere beneath a
# mechanism's entry functions - Python or built-in, at any depth - is counted against that mechanism's bucket, by callee
# name; the innermost entry on the stack takes the count. An entry absent from the tree measured (a builder only the new
# code has) is skipped. (bucket, module, attribute path) - a path through `Settlement` names a mixin method.
ENTRIES: tuple[tuple[str, str, str], ...] = (
    # lever 1: the homestead seats
    ("seats", "l7r.diagram.hamletgen.homesteads.stages", "seat_every_household"),
    ("corridor", "l7r.diagram.settlement.rolling.access", "access_corridor"),
    ("bundle", "l7r.diagram.settlement", "Settlement._bundle_geom"),
    ("mats", "l7r.diagram.settlement.homestead_parts.yards", "mat_cells"),
    # lever 2: region-then-fill
    ("marsh", "l7r.diagram.settlement", "Settlement.marsh"),
    ("grove", "l7r.diagram.settlement", "Settlement.village_grove"),
    ("open_ground", "l7r.diagram.hamletgen.hinterland.parcels", "open_ground_patches"),
    ("commons", "l7r.diagram.settlement", "Settlement.commons"),
    # lever 3: the lane law
    ("web", "l7r.diagram.hamletgen.ways.settle", "settle_the_web"),
    ("law", "l7r.diagram.hamletgen.ways.last_resort", "last_resort"),
    ("law", "l7r.diagram.hamletgen.ways.settle", "unsettled"),
    # the field, as the GM asked of it
    ("field", "l7r.diagram.hamletgen.water.fit", "fit_field"),
    ("hem", "l7r.diagram.waterfields.banks", "hem_to_bank"),
    ("seams", "l7r.diagram.waterfields.seams.close", "close_seams"),
    # the page
    ("page", "l7r.diagram.interactive.page", "write_html"),
)


# THE WHOLE HINTERLAND STAGE as one bucket, counted in a run of its own (the entries above would take its inner calls): the
# GM's "roughly 100,000 spatial-index lookups for the hinterlands" is `PointGrid.near` beneath it (spec SC-010).
STAGE_ENTRIES: tuple[tuple[str, str, str], ...] = (("hinterland_stage", "l7r.diagram.hamletgen.hinterland.stages", "stage_hinterland"),)


def _callee(fn: object) -> str:
    import types

    if isinstance(fn, type):
        return f"{fn.__qualname__}.__init__"  # a class called is a construction
    own = getattr(fn, "__self__", None)
    name = getattr(fn, "__qualname__", None) or getattr(fn, "__name__", None) or type(fn).__name__
    if own is not None and not isinstance(fn, types.MethodType):  # a built-in bound to an object or a module
        return f"{own.__name__ if isinstance(own, types.ModuleType) else type(own).__name__}.{getattr(fn, '__name__', name)}"
    return str(name)


def _entry_codes(entries: tuple[tuple[str, str, str], ...] = ENTRIES) -> dict[object, str]:
    import importlib

    codes: dict[object, str] = {}
    for bucket, mod, path in entries:
        try:
            obj: object = importlib.import_module(mod)
            for part in path.split("."):
                obj = getattr(obj, part)
        except (ImportError, AttributeError):
            continue
        code = getattr(obj, "__code__", None)
        if code is not None:
            codes[code] = bucket
    return codes


def _buckets(spec, entries: tuple[tuple[str, str, str], ...] = ENTRIES) -> dict[str, dict[str, int]]:
    import collections
    import sys

    from l7r.diagram.hamletgen import generate

    mon = sys.monitoring
    ev = mon.events
    tool = 4
    codes = _entry_codes(entries)
    stack: list[str] = []
    counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)

    def start(code, _off):
        b = codes.get(code)
        if b is not None:
            stack.append(b)
            if len(stack) == 1:
                mon.set_events(tool, ev.PY_UNWIND | ev.CALL)

    def leave(code, _off, _val):
        if codes.get(code) is not None and stack:
            stack.pop()
            if not stack:
                mon.set_events(tool, ev.PY_UNWIND)

    def call(_code, _off, fn, _arg0):
        if stack:
            c = counts[stack[-1]]
            c[_callee(fn)] += 1
            c["TOTAL"] += 1

    mon.use_tool_id(tool, "harness297")
    try:
        mon.register_callback(tool, ev.PY_START, start)
        mon.register_callback(tool, ev.PY_RETURN, leave)
        mon.register_callback(tool, ev.PY_UNWIND, leave)
        mon.register_callback(tool, ev.CALL, call)
        for code in codes:
            mon.set_local_events(tool, code, ev.PY_START | ev.PY_RETURN)
        mon.set_events(tool, ev.PY_UNWIND)
        generate(spec, render=False)
    finally:
        mon.set_events(tool, 0)
        for code in codes:
            mon.set_local_events(tool, code, 0)
        mon.free_tool_id(tool)
    return {b: dict(c) for b, c in counts.items()}


def test_harness_297() -> None:
    from l7r.diagram.hamletgen import HamletSpec

    OUT.mkdir(parents=True, exist_ok=True)
    result = {}
    for key in MAPS:
        spec = HamletSpec(**_spec_kwargs(key))
        best = None
        for _ in range(3):  # the fastest of three unprofiled rolls (two were read 0.2-0.4 s apart on one map, feature 281)
            row = _stage_times(spec)
            if best is None or row["roll_s"] < best["roll_s"]:
                best = row
        result[key] = {**(best or {}), "full_s": _full(spec, key, profile=False)}
        _full(spec, key, profile=True)
        result[key]["buckets"] = {**_buckets(spec), **_buckets(spec, STAGE_ENTRIES)}
    (OUT / "times.json").write_text(json.dumps(result, indent=2))
