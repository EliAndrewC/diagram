"""Feature 281's discovery harness: per pool hamlet, the stage times (unprofiled) and one profiled FULL regeneration.

    make spec-harness SPEC=specs/281-third-hotspot-pass OUT=<dir>

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
import tempfile
import time
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/h281")

SPECS = {
    "inashiro": dict(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond", fixtures_min={"shrine": 1}),
    "kashikawa": dict(name="Kashikawa", seed=3, households=20, down_deg=315, water_sink="offmap", brook_side=-1, bamboo="both"),
    "kuwabata": dict(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry"),
    "mizuguchi": None,  # read from its gen below
    "sawada": dict(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys"),
}


def _mizuguchi() -> dict:
    import re

    here = Path(__file__).resolve()
    skill = next(p for p in [here.parent, *here.parents] if (p / "Makefile").exists() and (p / "pool").exists())
    text = (skill / "pool" / "hamlets" / "mizuguchi" / "mizuguchi.gen.py").read_text()
    m = re.search(r"HamletSpec\((.*?)\)\s*,\s*out_base", text, re.S)
    assert m, "mizuguchi's spec"
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
    ("clip", "l7r.diagram.hamletgen.ways.clearance", "clip_to_clear"),
    ("fabric", "l7r.diagram.hamletgen.clearance", "FabricIndex.__init__"),
    ("toll", "l7r.diagram.hamletgen.ways.route", "in_brook_band"),
    ("handover", "l7r.diagram.settlement.structures.fixtures._helpers", "outermost_join"),
    ("departures", "l7r.diagram.settlement.structures.fixtures._helpers", "routes_missed"),
    ("departures", "l7r.diagram.settlement.structures.fixtures._helpers", "RouteReach.__init__"),
    ("departures", "l7r.diagram.settlement.structures.fixtures._helpers", "RouteReach.missed"),
    ("home_bank", "l7r.diagram.hamletgen.ways.sweeps", "_link_home_bank"),
    ("straggler", "l7r.diagram.hamletgen.ways.serve", "_serve_stragglers"),  # a barrier: its work is not the home-bank join's
    ("route_walk", "l7r.diagram.settlement.structures.fixtures._helpers", "departure_routes"),  # a barrier, likewise
    ("stream_rect", "l7r.diagram.settlement", "Settlement._rect_on_stream"),
    ("stream_rect", "l7r.diagram.settlement.rolling.fit", "rect_touches_stream"),
    ("stream_rect", "l7r.diagram.settlement.rolling.fit", "stream_segment_index"),
    ("caption_lanes", "l7r.diagram.settlement", "Settlement.label_seat_clear"),
    ("caption_lanes", "l7r.diagram.settlement.structures.captions", "lane_seat_index"),
    ("caption_lanes", "l7r.diagram.settlement.structures.captions", "clear_of_lanes"),
    ("carve", "l7r.diagram.waterfields.carve", "_carve_sector"),
    ("grove", "l7r.diagram.settlement", "Settlement.village_grove"),
    ("marsh", "l7r.diagram.settlement", "Settlement.marsh"),
    ("marsh", "l7r.diagram.settlement.land.wet", "marsh_scatter"),
)


def _callee(fn: object) -> str:
    import types

    if isinstance(fn, type):
        return f"{fn.__qualname__}.__init__"  # a class called is a construction
    own = getattr(fn, "__self__", None)
    name = getattr(fn, "__qualname__", None) or getattr(fn, "__name__", None) or type(fn).__name__
    if own is not None and not isinstance(fn, types.MethodType):  # a built-in bound to an object or a module
        return f"{own.__name__ if isinstance(own, types.ModuleType) else type(own).__name__}.{getattr(fn, '__name__', name)}"
    return str(name)


def _entry_codes() -> dict[object, str]:
    import importlib

    codes: dict[object, str] = {}
    for bucket, mod, path in ENTRIES:
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


def _buckets(spec) -> dict[str, dict[str, int]]:
    import collections
    import sys

    from l7r.diagram.hamletgen import generate

    mon = sys.monitoring
    ev = mon.events
    tool = 4
    codes = _entry_codes()
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

    mon.use_tool_id(tool, "harness281")
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


def test_harness_281() -> None:
    from l7r.diagram.hamletgen import HamletSpec

    OUT.mkdir(parents=True, exist_ok=True)
    result = {}
    for key, kw in SPECS.items():
        spec = HamletSpec(**(kw if kw is not None else _mizuguchi()))
        best = None
        for _ in range(2):  # the faster of two unprofiled rolls
            row = _stage_times(spec)
            if best is None or row["roll_s"] < best["roll_s"]:
                best = row
        result[key] = {**(best or {}), "full_s": _full(spec, key, profile=False)}
        _full(spec, key, profile=True)
        result[key]["buckets"] = _buckets(spec)
    (OUT / "times.json").write_text(json.dumps(result, indent=2))
