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


def _prototype():  # type: ignore[no-untyped-def]
    """`prototype.py`, loaded from the spec directory (the harness runs as a copied test node, so not by its own path)."""
    import importlib.util

    here = Path(__file__).resolve()
    root = next(p for p in here.parents if (p / "specs").is_dir() and (p / ".git").exists())
    spec = importlib.util.spec_from_file_location("prototype302", root / "specs" / "302-field-by-construction" / "prototype.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_current(call: tuple[tuple, dict]) -> float:
    from l7r.diagram.hamletgen.water.fit import fit_field

    a, k = copy.deepcopy(call)
    t = time.perf_counter()
    fit_field(*a, **k)
    return time.perf_counter() - t


def _run_prototype(proto, call: tuple[tuple, dict]) -> tuple[float, dict, dict, object]:  # type: ignore[no-untyped-def]
    a, k = copy.deepcopy(call)
    t = time.perf_counter()
    net, info = proto.fit_by_construction(*a, **k)
    return time.perf_counter() - t, net, info, a[0]


def validity(proto, net: dict, info: dict, plan) -> dict:  # type: ignore[no-untyped-def]
    """SC-003, measured outside the timing: the acreage band, bare ground, unshared bunds, rule-breaking plots."""
    import shapely
    from shapely.geometry import Polygon

    from l7r.diagram.hamletgen.water.fit import field_acres_in_band
    from l7r.diagram.sitegen.geom import net_acres
    from l7r.diagram.waterfields.ring_rules import ring_violations

    region = info["region"]
    raw = [Polygon(p["poly"]) for p in net["plots"]]
    invalid = sum(1 for q in raw if not q.is_valid)
    polys = [q if q.is_valid else q.buffer(0) for q in raw]
    planted = shapely.union_all(polys)
    bare = region.difference(planted).area / region.area if region.area else 1.0
    # an unshared bund: a stretch of a plot's outline that no other plot's outline and no region edge covers
    bounds = [p.boundary for p in polys]
    tree = shapely.STRtree(polys)
    # a bund is covered by a neighbor's, by the region's edge, or by a scrap left bare (as the repair leaves it); 0.6 px is the
    # slack the opening and simplification of a merged outline may move a vertex
    edge = shapely.union_all([region.boundary.buffer(0.6)] + [s[4].boundary.buffer(0.6) for s in info["scraps"]])
    unshared = 0.0
    for i, b in enumerate(bounds):
        near = [int(j) for j in tree.query(polys[i].buffer(0.5)) if int(j) != i]
        cover = shapely.union_all([bounds[j].buffer(0.6) for j in near] + [edge])
        unshared += b.difference(cover).length
    acres = net_acres(net, plan.ftpx)
    bad = [sorted(ring_violations(p["poly"], info["ctx"])) for p in net["plots"]]
    toe = sum(1 for p in net["plots"] if "toe" in proto._verdict(Polygon(p["poly"]), info["ctx"], info["plot_across"], info["cell"]))
    return {
        "acres": round(acres, 2),
        "target_acres": round(plan.target_acres, 2),
        "in_band": field_acres_in_band(acres, plan.target_acres),
        "bare_share": round(bare, 5),
        "unshared_px": round(unshared, 1),
        "rule_breaking_plots": sum(1 for b in bad if b),
        "rules_broken": sorted({r for b in bad for r in b}),
        "plots": len(net["plots"]),
        "invalid_outlines": invalid,
        "dry_plots": len(net["dry_plots"]),
        "trials": info["trials"],
        "stuck": info["stuck"],
        "toe_only": toe,
        "raw_cells": info["raw_cells"],
        "admissible": info["admissible"],
        "flooded": sum(1 for p in net["plots"] if p.get("fill") == "#93B7AC"), "low": sum(1 for p in net["plots"] if p.get("low")),
        "scraps_left_bare": len(info["scraps"]),
        "scrap_area_px": round(sum(s[1] for s in info["scraps"]), 1),
        "scraps": [s[:3] for s in info["scraps"]],
        "times": {k: round(v, 4) for k, v in info["times"].items()},
        "breakers": [(b, [round(sum(x for x, _ in p["poly"]) / len(p["poly"])), round(sum(y for _, y in p["poly"]) / len(p["poly"]))], round(abs(Polygon(p["poly"]).area))) for b, p in zip(bad, net["plots"], strict=True) if b][:60],
    }


def _rings_of(region):  # type: ignore[no-untyped-def]
    return [list(g.exterior.coords) for g in getattr(region, "geoms", [region]) if not g.is_empty]


def test_harness() -> None:
    proto = _prototype()
    which = os.environ.get("HARNESS_WHICH", "both")
    report: dict = {"current": {}, "prototype": {}, "runs": {"current": [0.0] * int(os.environ.get("HARNESS_RUNS", "3")), "prototype": [0.0] * int(os.environ.get("HARNESS_RUNS", "3"))}}
    only = os.environ.get("HARNESS_ONLY")
    runs = int(os.environ.get("HARNESS_RUNS", "3"))
    dump = os.environ.get("HARNESS_DUMP")
    for key, kw in inputs():
        if only and key not in only.split(","):
            continue
        call = capture(kw)
        if which == "breakdown":
            report["current"][key] = timed_fit(call)
            continue
        cur, pro = [], []
        last = None
        for r in range(runs):  # back to back, interleaved, so the host's load falls on both
            cur.append(_run_current(call))
            secs, net, info, plan = _run_prototype(proto, call)
            pro.append(secs)
            last = (net, info, plan)
            report["runs"]["current"][r] += cur[-1]
            report["runs"]["prototype"][r] += secs
        assert last is not None
        if dump:
            Path(dump).mkdir(parents=True, exist_ok=True)
            net, info, _plan = last
            Path(dump, f"{key}.json").write_text(json.dumps({"plots": [p["poly"] for p in net["plots"]], "region": [list(r) for r in _rings_of(info["region"])], "channels": [c["pts"] for c in net["channels"]], "scraps": [list(s[4].exterior.coords) for s in info["scraps"]], "lines": proto.LAST_LINES, "pieces": proto.PIECES}))
        report["current"][key] = {"best_s": round(min(cur), 4), "runs": [round(x, 4) for x in cur]}
        report["prototype"][key] = {"best_s": round(min(pro), 4), "runs": [round(x, 4) for x in pro], **validity(proto, *last)}
    if which != "breakdown":
        cur_t = sum(v["best_s"] for v in report["current"].values())
        pro_t = sum(v["best_s"] for v in report["prototype"].values())
        spread = max(max(v) - min(v) for v in report["runs"].values())
        report["verdict"] = {
            "current_total_s": round(cur_t, 3),
            "prototype_total_s": round(pro_t, 3),
            "ratio": round(cur_t / pro_t, 2) if pro_t else None,
            "spread_s": round(spread, 3),
            "go": cur_t - pro_t > spread,
            "stubbed": list(proto.STUBBED),
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=1, default=str) + "\n")
