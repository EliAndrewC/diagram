"""Feature 302's Phase 0 harness: the current comb field timed step by step, and (once written) the prototype beside it.

    make spec-harness SPEC=specs/302-field-by-construction OUT=<json>

Run as a test node (the engine refuses in-process calls outside make). Per recorded input (the pool's comb hamlets and
Inashiro's brief at 10 and 20 households): the hamlet is rolled up to its field stage, `fit_field`'s arguments are captured
there and the roll is stopped; then `fit_field` is run on fresh copies of them, fastest of three, with a wall-clock timer on
every step the carve and the finish are made of (inclusive times: a step's time contains its callees'). Nothing in the
engine is changed: the timers are monkeypatched for the test's life only.
"""

from __future__ import annotations

import copy
import json
import os
import re
import time
from pathlib import Path

import pytest

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/h302.json")
POOL = ("inashiro", "kashikawa", "mizuguchi", "sawada")  # Kuwabata is a polder (out of scope)
SCALE = (10, 20)  # Inashiro's brief at the hamlet band's two ends

# (module, attribute) - every step of the carve and the finish, timed where the caller looks it up
STEPS = (
    ("l7r.diagram.hamletgen.water.fit", "carve_comb"),
    ("l7r.diagram.hamletgen.water.fit", "finish_comb"),
    ("l7r.diagram.hamletgen.water.fit", "fan_admissible"),
    ("l7r.diagram.waterfields.comb", "_comb_skeleton"),
    ("l7r.diagram.waterfields.comb", "_comb_threads"),
    ("l7r.diagram.waterfields.comb", "_comb_march"),
    ("l7r.diagram.waterfields.comb", "_comb_drain"),
    ("l7r.diagram.waterfields.comb", "_comb_brook"),
    ("l7r.diagram.waterfields.comb", "_drain_bank"),
    ("l7r.diagram.waterfields.comb", "_comb_clip_and_cap"),
    ("l7r.diagram.waterfields.comb", "_comb_canal_pieces"),
    ("l7r.diagram.waterfields.comb", "round_channel_joints"),
    ("l7r.diagram.waterfields.comb", "_carve"),
    ("l7r.diagram.waterfields.comb", "_comb_floor_and_winding"),
    ("l7r.diagram.waterfields.comb", "anchor_trunk_ends"),
    ("l7r.diagram.waterfields.comb", "_comb_toe_and_hem"),
    ("l7r.diagram.waterfields.comb", "close_seams"),
    ("l7r.diagram.waterfields.comb", "_comb_dry_and_beans"),
)


def _spec_kwargs(key: str) -> dict:
    here = Path(__file__).resolve()
    skill = next(p for p in [here.parent, *here.parents] if (p / "Makefile").exists() and (p / "pool").exists())
    text = (skill / "pool" / "hamlets" / key / f"{key}.gen.py").read_text()
    m = re.search(r"HamletSpec\((.*?)\)\s*,\s*out_base", text, re.S)
    assert m, f"{key}'s spec"
    return eval(f"dict({m.group(1)})")  # noqa: S307 - our own committed generator's literal arguments


def inputs() -> list[tuple[str, dict]]:
    out = [(k, _spec_kwargs(k)) for k in POOL]
    base = _spec_kwargs("inashiro")
    for n in SCALE:
        out.append((f"inashiro-h{n}", {**base, "name": f"Inashiro{n}", "households": n}))
    return out


class _Captured(Exception):
    pass


def capture(spec_kwargs: dict) -> tuple[tuple, dict]:
    """Roll the hamlet up to its field stage and return `fit_field`'s (args, kwargs), deep-copied as they arrived."""
    from l7r.diagram.hamletgen import HamletSpec, generate
    from l7r.diagram.hamletgen.water import comb as stage_comb

    got: dict = {}
    real = stage_comb.fit_field

    def grab(*a, **k):  # type: ignore[no-untyped-def]
        got["call"] = (copy.deepcopy(a), copy.deepcopy(k))
        raise _Captured

    stage_comb.fit_field = grab
    try:
        with pytest.raises(_Captured):
            generate(HamletSpec(**spec_kwargs), render=False)
    finally:
        stage_comb.fit_field = real
    return got["call"]


def timed_fit(call: tuple[tuple, dict], runs: int = 3) -> dict:
    """`fit_field` on fresh copies of the captured call, fastest of `runs`, with every STEP's inclusive time and call count."""
    import importlib

    from l7r.diagram.hamletgen.water.fit import fit_field
    from l7r.diagram.sitegen.geom import net_acres
    from l7r.diagram.waterfields import CombCarve

    best: dict | None = None
    for _ in range(runs):
        acc: dict[str, float] = {}
        cnt: dict[str, int] = {}
        saved = []

        def wrap(name, fn):  # type: ignore[no-untyped-def]
            def run(*a, **k):  # type: ignore[no-untyped-def]
                t = time.perf_counter()
                try:
                    return fn(*a, **k)
                finally:
                    acc[name] = acc.get(name, 0.0) + time.perf_counter() - t
                    cnt[name] = cnt.get(name, 0) + 1

            return run

        for mod, attr in STEPS:
            m = importlib.import_module(mod)
            saved.append((m, attr, getattr(m, attr)))
            setattr(m, attr, wrap(attr, getattr(m, attr)))
        pa = CombCarve.planted_area
        CombCarve.planted_area = wrap("planted_area", pa)  # type: ignore[method-assign]
        try:
            a, k = copy.deepcopy(call)
            t = time.perf_counter()
            net = fit_field(*a, **k)
            total = time.perf_counter() - t
        finally:
            for m, attr, fn in saved:
                setattr(m, attr, fn)
            CombCarve.planted_area = pa  # type: ignore[method-assign]
        plan = a[0]
        row = {
            "fit_s": round(total, 4),
            "steps": {n: round(v, 4) for n, v in sorted(acc.items(), key=lambda kv: -kv[1])},
            "calls": dict(sorted(cnt.items())),
            "acres": round(net_acres(net, plan.ftpx), 2),
            "target_acres": round(plan.target_acres, 2),
            "plots": len(net["plots"]),
        }
        if best is None or row["fit_s"] < best["fit_s"]:
            best = row
    assert best is not None
    return best


def test_harness() -> None:
    report: dict = {"current": {}}
    for key, kw in inputs():
        report["current"][key] = timed_fit(capture(kw))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=1) + "\n")
