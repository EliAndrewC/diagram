"""Feature 287 P0: households seated today, per map, over the pool and cohort seeds 1-48 (research R5).

    make spec-harness SPEC=specs/287-placer-guarantees/p0 OUT=<json>
"""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import re
import time
import types
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/b3cmp-284.json")
POOL = {
    "inashiro": dict(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond", fixtures_min={"shrine": 1}),
    "kashikawa": dict(name="Kashikawa", seed=3, households=20, down_deg=315, water_sink="offmap", brook_side=-1, bamboo="both"),
    "kuwabata": dict(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry"),
    "sawada": dict(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys"),
}


def _mizuguchi() -> dict:
    skill = Path(__file__).resolve().parents[1]
    text = (skill / "pool" / "hamlets" / "mizuguchi" / "mizuguchi.gen.py").read_text()
    m = re.search(r"HamletSpec\((.*?)\)\s*,\s*out_base", text, re.S)
    assert m
    return eval(f"dict({m.group(1)})")  # noqa: S307 - our own committed generator's literal arguments


def _one(job):
    base, key, kw = job[0], job[1], job[2]
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec
    from l7r.diagram.hamletgen.water import fit

    t = time.perf_counter()
    rep = driver.generate(HamletSpec(**kw) if isinstance(kw, dict) else kw, out_base=None, render=False)
    M = rep.manifest or {}
    roles = [b.get("role") for b in M.get("bamboo_stands", [])]
    ways = sum(sum(math.dist(a, b) for a, b in zip(ln["pts"], ln["pts"][1:], strict=False)) for ln in M.get("lanes", []))
    return {"connectors": sum(1 for ln in M.get("lanes", []) if ln.get("connector")), "fit": "today", "pass": job[3] if len(job) > 3 else 0, "map": key, "attempt": rep.attempt, "placed": int(rep.plan.placed), "households": rep.plan.spec.households, "acres": round(rep.plan.acres, 2), "target": round(rep.plan.target_acres, 2), "homestead_bamboo": roles.count("homestead"), "thicket": roles.count("thicket"), "way_len": round(ways), "board": bool(M.get("kosatsuba")), "failures": rep.failures, "s": round(time.perf_counter() - t, 2)}


def test_b3cmp() -> None:
    from l7r.diagram.hamletgen.driver import cohort_specs

    specs: dict = dict(POOL, mizuguchi=_mizuguchi())
    for sp in cohort_specs(48, first_seed=1):
        specs[f"cohort-{sp.seed:02d}"] = sp
    jobs = [(False, k, kw, 1) for k, kw in specs.items()]
    with mp.get_context("fork").Pool(12, maxtasksperchild=1) as pool:
        rows = pool.map(_one, jobs, chunksize=1)
    OUT.write_text(json.dumps(rows, indent=1))
