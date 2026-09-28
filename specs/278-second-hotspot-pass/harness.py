"""Feature 278's measurement harness: per pool hamlet, the stage times (unprofiled) and the mechanism counts (profiled).

    make spec-harness SPEC=specs/278-second-hotspot-pass OUT=<json>

Run as a test node (the engine refuses in-process calls outside make). Two passes per hamlet: one UNPROFILED roll with
every stage timed - the seconds - and one roll under cProfile read only for CALL COUNTS, which do not depend on the
machine's load (feature 276 measured the same scenario up to twice as slow at a load of 8.7). The counts are the
mechanisms the spec names: the router's cell tests, the doorstep index lookups, the footbridge segment tests, the well
pool's sort keys, the comb carves, the notice board's fit probes, the windbreak's candidate tests, the commons' sparse
tests, and how many times each hamlet is built (a stranded farmhouse re-rolls the map).
"""

from __future__ import annotations

import cProfile
import json
import os
import pstats
import time
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/h278.json")

SPECS = {
    "inashiro": dict(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond", fixtures_min={"shrine": 1}),
    "kashikawa": dict(name="Kashikawa", seed=3, households=20, down_deg=315, water_sink="offmap", brook_side=-1, bamboo="both"),
    "kuwabata": dict(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry"),
    "mizuguchi": None,  # read from its gen below
    "sawada": dict(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys"),
}

# (label, pstats function key suffix) - a count is the number of calls to that function over the roll
COUNTS = {
    "route_calls": ("route.py", "_route"),
    "cell_fouled": ("clearance.py", "fouled"),
    "brook_band": ("route.py", "in_brook_band"),
    "fabric_index_calls": ("clearance.py", "fabric_index"),
    "quad_hits_seg": ("overlap.py", "quad_hits_seg"),
    "carve_comb": ("comb.py", "carve_comb"),
    "house_fits": ("houses.py", "_fits"),
    "grove_too_near": ("grove_blocks.py", "too_near"),
    "commons_sparse": ("cover.py", "_sparse"),
    "builds": ("driver.py", "build"),
    "finishes": ("finish.py", "finish"),
    "wells_key": ("wells.py", "_key"),
    "field_pip": ("frame.py", "_pip"),
    "grid_near": ("indexes.py", "near"),
    "random_uniform": ("random.py", "uniform"),
    "quad_hits_poly": ("overlap.py", "quad_hits_poly"),
    "seg_dist": ("primitives.py", "seg_dist"),
    "page_hits": ("page.py", "_hits"),
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


def _counts(spec) -> dict:
    from l7r.diagram.hamletgen import generate

    pr = cProfile.Profile()
    pr.enable()
    generate(spec, render=False)
    pr.disable()
    stats = pstats.Stats(pr).stats  # type: ignore[attr-defined]
    out = {}
    for label, (fname, func) in COUNTS.items():
        out[label] = sum(v[1] for (f, _line, name), v in stats.items() if f.endswith(fname) and name == func)
    return out


def test_harness_278() -> None:
    from l7r.diagram.hamletgen import HamletSpec

    result = {}
    for key, kw in SPECS.items():
        spec = HamletSpec(**(kw if kw is not None else _mizuguchi()))
        best = None
        for _ in range(2):  # the faster of two unprofiled rolls
            row = _stage_times(spec)
            if best is None or row["roll_s"] < best["roll_s"]:
                best = row
        result[key] = {**(best or {}), "counts": _counts(spec)}
    OUT.write_text(json.dumps(result, indent=2))
