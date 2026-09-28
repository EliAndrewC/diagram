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
    (OUT / "times.json").write_text(json.dumps(result, indent=2))
