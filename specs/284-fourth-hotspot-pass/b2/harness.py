"""Feature 284 B2: the coarser router lattice, counted (plan B2, research R4).

    make spec-harness SPEC=specs/284-fourth-hotspot-pass/b2 OUT=<json>

Re-run on the engine that ships (the router in cost order, the base's field search, the re-roll resume, the connector fix;
the reviews of Amendment 1 found the first run made with A* and the probe lever in). For each cell (10, today's, then 12,
14, 16, 18) the five pool hamlets, the 10- and 20-household toys and cohort seeds 1-24 are rolled with
`route.ROUTE_CELL` set, and per map and seed the harness records the unreached houses of EVERY attempt (the driver's own
`unreached_houses`, wrapped, so a stranding the re-roll hid is counted), the attempt kept, the households seated and the
roll's seconds. Rolls fan out over forked workers; the cell is set in each child before it rolls.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import re
import time
from pathlib import Path

OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/b2-284.json")
CELLS = (10.0, 12.0, 14.0, 16.0, 18.0)

POOL = {
    "inashiro": dict(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond", fixtures_min={"shrine": 1}),
    "kashikawa": dict(name="Kashikawa", seed=3, households=20, down_deg=315, water_sink="offmap", brook_side=-1, bamboo="both"),
    "kuwabata": dict(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry"),
    "sawada": dict(name="Sawada", seed=24, households=19, down_deg=225, water_sink="offmap", intake="open", lane_web="alleys"),
}


def _mizuguchi() -> dict:
    here = Path(__file__).resolve()
    skill = next(p for p in [here.parent, *here.parents] if (p / "Makefile").exists() and (p / "pool").exists())
    text = (skill / "pool" / "hamlets" / "mizuguchi" / "mizuguchi.gen.py").read_text()
    m = re.search(r"HamletSpec\((.*?)\)\s*,\s*out_base", text, re.S)
    assert m, "mizuguchi's spec"
    return eval(f"dict({m.group(1)})")  # noqa: S307 - our own committed generator's literal arguments


def _one(job: tuple) -> dict:
    cell, key, kw = job
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec
    from l7r.diagram.hamletgen.ways import route

    route.ROUTE_CELL = cell
    counts: list[int] = []
    real = driver.unreached_houses

    def counted(M):
        got = real(M)
        counts.append(len(got))
        return got

    driver.unreached_houses = counted
    t = time.perf_counter()
    rep = driver.generate(HamletSpec(**kw) if isinstance(kw, dict) else kw, out_base=None, render=False)
    return {"cell": cell, "map": key, "per_attempt": counts, "kept_attempt": rep.attempt, "kept_unreached": counts[rep.attempt - 1], "placed": int(rep.plan.placed), "s": round(time.perf_counter() - t, 3)}


def test_b2_cells() -> None:
    from l7r.diagram.hamletgen.driver import cohort_specs

    specs: dict = dict(POOL, mizuguchi=_mizuguchi(), toy10=dict(name="Toy10", seed=1, households=10), toy20=dict(name="Toy20", seed=2, households=20))
    for sp in cohort_specs(24, first_seed=1):
        specs[f"cohort-{sp.seed:02d}"] = sp
    jobs = [(c, k, kw) for c in CELLS for k, kw in specs.items()]
    with mp.get_context("fork").Pool(12, maxtasksperchild=1) as pool:
        rows = pool.map(_one, jobs, chunksize=1)
    OUT.write_text(json.dumps(rows, indent=1))
